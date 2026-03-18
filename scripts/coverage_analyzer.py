#!/usr/bin/env python3
"""
Site24x7 API Coverage Analyzer

Compares the Site24x7 REST API catalog against the Terraform provider to
determine how much of the API surface is covered by Terraform resources.

Uses only Python standard library — no external dependencies required.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _extract_map_block(content: str, map_name: str) -> str | None:
    """
    Extract the body of a Go map literal for ResourcesMap or DataSourcesMap,
    correctly handling nested braces so inner struct literals don't terminate
    the match prematurely.
    """
    # Find the start position of the map literal opening brace.
    start_pattern = re.compile(
        rf'{re.escape(map_name)}\s*:\s*map\[string\]\*schema\.Resource\s*\{{',
        re.DOTALL,
    )
    m = start_pattern.search(content)
    if not m:
        return None

    # Walk forward from the opening brace, counting nesting depth.
    pos = m.end()  # position just after the opening '{'
    depth = 1
    start = pos
    while pos < len(content) and depth > 0:
        ch = content[pos]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        pos += 1

    if depth != 0:
        return None  # unbalanced braces

    return content[start : pos - 1]  # body without surrounding braces


def parse_provider_go(provider_go_path: str) -> tuple[dict[str, str], dict[str, str]]:
    """
    Parse provider.go and return (resources_map, datasources_map).

    Each map is  {terraform_resource_name: function_call_string}.
    Lines whose first non-whitespace characters are '//' are treated as
    comments and skipped.
    """
    with open(provider_go_path, encoding="utf-8") as fh:
        content = fh.read()

    resources: dict[str, str] = {}
    datasources: dict[str, str] = {}

    entry_pattern = re.compile(
        r'^\s*"(site24x7_[^"]+)"\s*:\s*([^,\n]+)',
        re.MULTILINE,
    )

    for map_name, target in (
        ("ResourcesMap", resources),
        ("DataSourcesMap", datasources),
    ):
        block_body = _extract_map_block(content, map_name)
        if block_body is None:
            continue

        for line in block_body.splitlines():
            # Skip lines that are purely comments (// is first non-whitespace token)
            stripped = line.lstrip()
            if stripped.startswith("//"):
                continue
            entry_match = entry_pattern.match(line)
            if entry_match:
                name = entry_match.group(1)
                func = entry_match.group(2).strip().rstrip(",").strip()
                target[name] = func

    return resources, datasources


def parse_docs_listing(listing_path: str | None) -> set[str]:
    """
    Parse a GitHub API directory-listing JSON file and return the set of
    documented resource/datasource names (file stems without .md extension).
    Returns an empty set if path is None or the file cannot be parsed.
    """
    if not listing_path or not os.path.exists(listing_path):
        return set()

    try:
        with open(listing_path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return set()

    if not isinstance(data, list):
        return set()

    names: set[str] = set()
    for item in data:
        if isinstance(item, dict):
            filename = item.get("name", "")
            if filename.endswith(".md"):
                names.add(filename[:-3])  # strip .md
    return names


# ---------------------------------------------------------------------------
# Coverage analysis
# ---------------------------------------------------------------------------

def determine_coverage_status(
    entry: dict,
    resources: dict[str, str],
    datasources: dict[str, str],
    docs_resources: set[str],
) -> tuple[str, bool, bool, bool]:
    """
    Return (status, has_resource, has_datasource, has_docs).

    status is one of: "full", "partial", "missing"
    """
    res_name = entry.get("terraform_resource_name")
    ds_name = entry.get("terraform_datasource_name")

    has_resource = bool(res_name and res_name in resources)
    has_datasource = bool(ds_name and ds_name in datasources)
    has_docs = bool(res_name and res_name.removeprefix("site24x7_") in docs_resources)

    if has_resource and has_docs:
        status = "full"
    elif has_resource or has_datasource:
        status = "partial"
    else:
        status = "missing"

    return status, has_resource, has_datasource, has_docs


def analyze(
    provider_go_path: str,
    catalog_path: str,
    docs_resources_path: str | None,
    docs_datasources_path: str | None,
    provider_repo: str,
    provider_branch: str,
) -> dict:
    """Run the full coverage analysis and return a structured result dict."""
    resources, datasources = parse_provider_go(provider_go_path)
    docs_resources = parse_docs_listing(docs_resources_path)
    # docs_datasources is parsed but currently informational only
    parse_docs_listing(docs_datasources_path)

    with open(catalog_path, encoding="utf-8") as fh:
        catalog: list[dict] = json.load(fh)

    generated_at = datetime.now(timezone.utc).isoformat()

    results: list[dict] = []
    categories: dict[str, dict] = {}

    total = len(catalog)
    full_count = partial_count = missing_count = 0

    for entry in catalog:
        status, has_resource, has_datasource, has_docs = determine_coverage_status(
            entry, resources, datasources, docs_resources
        )

        if status == "full":
            full_count += 1
        elif status == "partial":
            partial_count += 1
        else:
            missing_count += 1

        category = entry.get("category", "Other")
        if category not in categories:
            categories[category] = {
                "full": 0, "partial": 0, "missing": 0, "total": 0
            }
        categories[category][status] += 1
        categories[category]["total"] += 1

        results.append(
            {
                "name": entry["name"],
                "category": category,
                "api_path": entry.get("api_path", ""),
                "priority": entry.get("priority", "medium"),
                "terraform_resource_name": entry.get("terraform_resource_name"),
                "terraform_datasource_name": entry.get("terraform_datasource_name"),
                "coverage_status": status,
                "has_resource": has_resource,
                "has_datasource": has_datasource,
                "has_docs": has_docs,
                "doc_url": entry.get("doc_url", ""),
                "description": entry.get("description", ""),
            }
        )

    covered = full_count + partial_count
    coverage_pct = round(covered / total * 100, 1) if total else 0.0
    full_pct = round(full_count / total * 100, 1) if total else 0.0

    summary = {
        "total": total,
        "full": full_count,
        "partial": partial_count,
        "missing": missing_count,
        "covered": covered,
        "coverage_percentage": coverage_pct,
        "full_percentage": full_pct,
    }

    return {
        "generated_at": generated_at,
        "provider_repo": provider_repo,
        "provider_branch": provider_branch,
        "summary": summary,
        "categories": categories,
        "results": results,
        "resources": sorted(resources.keys()),
        "datasources": sorted(datasources.keys()),
    }


# ---------------------------------------------------------------------------
# Badge generation
# ---------------------------------------------------------------------------

def build_badge(coverage_pct: float) -> dict:
    """Return a Shields.io endpoint badge JSON object."""
    if coverage_pct >= 80:
        color = "brightgreen"
    elif coverage_pct >= 60:
        color = "yellow"
    elif coverage_pct >= 40:
        color = "orange"
    else:
        color = "red"

    return {
        "schemaVersion": 1,
        "label": "API Coverage",
        "message": f"{coverage_pct}%",
        "color": color,
    }


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def _progress_bar(value: int, total: int, width: int = 20) -> str:
    """Return an ASCII progress bar string."""
    if total == 0:
        return "[" + " " * width + "]"
    filled = int(round(value / total * width))
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def _emoji_bar(pct: float) -> str:
    """Return a compact emoji progress bar (5 blocks)."""
    filled = int(round(pct / 100 * 5))
    return "🟩" * filled + "⬜" * (5 - filled)


def render_markdown_report(data: dict) -> str:
    """Render the full Markdown coverage report."""
    s = data["summary"]
    results = data["results"]
    categories = data["categories"]
    generated_at = data["generated_at"]
    provider_repo = data["provider_repo"]
    provider_branch = data["provider_branch"]
    resources = data["resources"]
    datasources_list = data["datasources"]

    ts = generated_at.replace("T", " ").split(".")[0] + " UTC"
    pct = s["coverage_percentage"]
    bar = _progress_bar(s["covered"], s["total"], width=30)

    lines: list[str] = []

    # --- Header ---
    lines += [
        "# 📊 Site24x7 Terraform Provider — API Coverage Report",
        "",
        f"**Generated:** {ts}  ",
        f"**Provider:** [{provider_repo}](https://github.com/{provider_repo})  ",
        f"**Branch:** `{provider_branch}`",
        "",
    ]

    # --- Summary table ---
    lines += [
        "## 📈 Summary",
        "",
        "| Metric | Count | Percentage |",
        "|--------|------:|:-----------|",
        f"| Total API Endpoints | {s['total']} | 100% |",
        f"| ✅ Full Coverage (resource + docs) | {s['full']} | {s['full_percentage']}% |",
        f"| ⚠️ Partial Coverage (resource or datasource) | {s['partial']} | {round(s['partial']/s['total']*100, 1) if s['total'] else 0}% |",
        f"| ❌ Missing | {s['missing']} | {round(s['missing']/s['total']*100, 1) if s['total'] else 0}% |",
        f"| **Overall Covered** | **{s['covered']}** | **{pct}%** |",
        "",
    ]

    # --- Progress bar ---
    lines += [
        "### Coverage Progress",
        "",
        f"```",
        f"Overall: {bar} {pct}%",
        f"         {s['covered']} / {s['total']} endpoints covered",
        f"```",
        "",
    ]

    # --- Category breakdown ---
    lines += [
        "## 📂 Coverage by Category",
        "",
        "| Category | Total | ✅ Full | ⚠️ Partial | ❌ Missing | Progress |",
        "|----------|------:|-------:|-----------:|-----------:|:---------|",
    ]
    for cat, stats in sorted(categories.items()):
        cat_pct = round((stats["full"] + stats["partial"]) / stats["total"] * 100, 0) if stats["total"] else 0
        emoji = _emoji_bar(cat_pct)
        lines.append(
            f"| {cat} | {stats['total']} | {stats['full']} | {stats['partial']} | {stats['missing']} | {emoji} {int(cat_pct)}% |"
        )
    lines.append("")

    # --- Missing APIs by priority ---
    missing = [r for r in results if r["coverage_status"] == "missing"]
    high_missing = [r for r in missing if r["priority"] == "high"]
    medium_missing = [r for r in missing if r["priority"] == "medium"]
    low_missing = [r for r in missing if r["priority"] == "low"]

    def _missing_table(items: list[dict]) -> list[str]:
        tbl = [
            "| API Name | Category | Resource Name | Priority | API Docs |",
            "|----------|----------|---------------|----------|----------|",
        ]
        for item in items:
            res = item["terraform_resource_name"] or item["terraform_datasource_name"] or "—"
            tbl.append(
                f"| {item['name']} | {item['category']} | `{res}` | {item['priority']} | [docs]({item['doc_url']}) |"
            )
        return tbl

    lines += [
        "## 🚨 Missing APIs",
        "",
        "### 🔴 High Priority",
        "",
    ]
    if high_missing:
        lines += _missing_table(high_missing)
    else:
        lines.append("_No high-priority APIs missing!_ 🎉")
    lines.append("")

    lines += ["<details>", "<summary>🟡 Medium Priority Missing APIs</summary>", ""]
    if medium_missing:
        lines += _missing_table(medium_missing)
    else:
        lines.append("_None_")
    lines += ["", "</details>", ""]

    lines += ["<details>", "<summary>🟢 Low Priority Missing APIs</summary>", ""]
    if low_missing:
        lines += _missing_table(low_missing)
    else:
        lines.append("_None_")
    lines += ["", "</details>", ""]

    # --- Implemented resources ---
    lines += [
        "<details>",
        f"<summary>✅ Implemented Resources ({len(resources)})</summary>",
        "",
        "| Resource Name |",
        "|---------------|",
    ]
    for r in resources:
        lines.append(f"| `{r}` |")
    lines += ["", "</details>", ""]

    # --- Implemented datasources ---
    lines += [
        "<details>",
        f"<summary>✅ Implemented Data Sources ({len(datasources_list)})</summary>",
        "",
        "| Data Source Name |",
        "|------------------|",
    ]
    for ds in datasources_list:
        lines.append(f"| `{ds}` |")
    lines += ["", "</details>", ""]

    # --- Footer ---
    lines += [
        "---",
        "",
        f"*Report generated automatically by [site24x7-api-terraform-coverage](https://github.com/vinoth-kanagaraj-14883/site24x7-api-terraform-coverage) · {ts}*",
        "",
    ]

    return "\n".join(lines)


def render_summary_markdown(data: dict) -> str:
    """Render a shorter summary-only Markdown snippet."""
    s = data["summary"]
    ts = data["generated_at"].replace("T", " ").split(".")[0] + " UTC"
    pct = s["coverage_percentage"]
    bar = _progress_bar(s["covered"], s["total"], width=20)

    lines = [
        "## 📊 Site24x7 API Coverage",
        "",
        f"| | |",
        f"|---|---|",
        f"| **Generated** | {ts} |",
        f"| **Total Endpoints** | {s['total']} |",
        f"| **Fully Covered** | {s['full']} ({s['full_percentage']}%) |",
        f"| **Partially Covered** | {s['partial']} |",
        f"| **Missing** | {s['missing']} |",
        f"| **Overall Coverage** | **{pct}%** |",
        "",
        f"```",
        f"{bar} {pct}%",
        f"```",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------

def print_console_summary(data: dict) -> None:
    """Print a summary box to stdout."""
    s = data["summary"]
    pct = s["coverage_percentage"]
    bar = _progress_bar(s["covered"], s["total"], width=30)
    sep = "═" * 60

    print(f"\n╔{sep}╗")
    print(f"║  📊 Site24x7 API Coverage Analysis{'':>23}║")
    print(f"╠{sep}╣")
    print(f"║  Provider : {data['provider_repo']:<46}║")
    print(f"║  Branch   : {data['provider_branch']:<46}║")
    print(f"╠{sep}╣")
    print(f"║  Total Endpoints  : {s['total']:<39}║")
    print(f"║  ✅ Full Coverage : {s['full']:<39}║")
    print(f"║  ⚠️  Partial       : {s['partial']:<39}║")
    print(f"║  ❌ Missing       : {s['missing']:<39}║")
    print(f"╠{sep}╣")
    print(f"║  Overall: {bar} {pct}% {'':>4}║")
    print(f"╚{sep}╝\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze Site24x7 Terraform provider API coverage",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--provider-file", required=True, help="Path to provider.go")
    parser.add_argument("--api-catalog", required=True, help="Path to site24x7_api_catalog.json")
    parser.add_argument("--docs-resources", default=None, help="Path to docs/resources JSON listing")
    parser.add_argument("--docs-datasources", default=None, help="Path to docs/data-sources JSON listing")
    parser.add_argument("--output-dir", required=True, help="Directory for report output")
    parser.add_argument(
        "--provider-repo",
        default="site24x7/terraform-provider-site24x7",
        help="Terraform provider repository slug",
    )
    parser.add_argument("--provider-branch", default="main", help="Provider branch name")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    # Validate inputs
    for path, label in [
        (args.provider_file, "--provider-file"),
        (args.api_catalog, "--api-catalog"),
    ]:
        if not os.path.exists(path):
            print(f"ERROR: {label} not found: {path}", file=sys.stderr)
            return 1

    os.makedirs(args.output_dir, exist_ok=True)

    print("Analyzing coverage…")
    data = analyze(
        provider_go_path=args.provider_file,
        catalog_path=args.api_catalog,
        docs_resources_path=args.docs_resources,
        docs_datasources_path=args.docs_datasources,
        provider_repo=args.provider_repo,
        provider_branch=args.provider_branch,
    )

    # Write outputs
    out = args.output_dir

    report_md = render_markdown_report(data)
    summary_md = render_summary_markdown(data)

    def _write(filename: str, content: str) -> None:
        path = os.path.join(out, filename)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"  Written: {path}")

    _write("coverage_report.md", report_md)
    _write("coverage_summary.md", summary_md)
    _write(
        "coverage_data.json",
        json.dumps(data, indent=2, ensure_ascii=False),
    )
    _write(
        "coverage_badge.json",
        json.dumps(build_badge(data["summary"]["coverage_percentage"]), indent=2),
    )

    print_console_summary(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
