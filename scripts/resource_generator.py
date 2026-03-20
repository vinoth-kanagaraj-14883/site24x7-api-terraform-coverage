#!/usr/bin/env python3
"""
Agent 02 – Terraform Resource Scaffold Generator
=================================================
Reads reports/LATEST_DATA.json (coverage output from Agent 01) and
config/site24x7_api_catalog.json, then generates Go scaffold files for a
selected missing API so they are ready to be contributed upstream to
site24x7/terraform-provider-site24x7.

Usage:
    python scripts/resource_generator.py \
        --coverage-data  reports/LATEST_DATA.json \
        --api-catalog    config/site24x7_api_catalog.json \
        --target-api     "SMTP Mail Monitor" \
        --priority       high \
        --output-dir     generated/ \
        --provider-repo  site24x7/terraform-provider-site24x7
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _to_snake(name: str) -> str:
    """Convert a human-readable API name to a snake_case resource suffix.

    E.g. "SMTP Mail Monitor" -> "smtp_mail_monitor"
    """
    # Lower-case and replace non-alphanumeric runs with underscores
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_")
    return s


def _to_pascal(snake: str) -> str:
    """Convert snake_case to PascalCase.

    E.g. "smtp_mail_monitor" -> "SmtpMailMonitor"
    """
    return "".join(part.capitalize() for part in snake.split("_"))


def _to_camel(snake: str) -> str:
    """Convert snake_case to camelCase.

    E.g. "smtp_mail_monitor" -> "smtpMailMonitor"
    """
    parts = snake.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _resource_short_name(terraform_resource_name: str) -> str:
    """Strip the 'site24x7_' prefix.

    E.g. "site24x7_smtp_monitor" -> "smtp_monitor"
    """
    prefix = "site24x7_"
    if terraform_resource_name and terraform_resource_name.startswith(prefix):
        return terraform_resource_name[len(prefix):]
    return terraform_resource_name or "unknown_resource"


def _go_package(category: str) -> str:
    """Map a catalog category to an appropriate Go package name."""
    mapping = {
        "Monitors": "monitors",
        "Cloud Monitors": "monitors",
        "APM": "monitors",
        "Logs": "monitors",
        "Network": "monitors",
        "Infrastructure": "monitors",
        "Monitor Groups": "monitors",
        "Profiles": "api",
        "Users": "api",
        "Tags": "api",
        "Automation": "api",
        "Maintenance": "api",
        "Configuration": "api",
        "Reports": "api",
        "Integrations": "integration",
        "Status Pages": "api",
        "Dashboards": "api",
        "MSP": "api",
        "Security": "api",
    }
    return mapping.get(category, "api")


# ---------------------------------------------------------------------------
# Selection logic
# ---------------------------------------------------------------------------

def load_missing_entries(coverage_data_path: str):
    """Return all missing entries sorted high → medium → low."""
    with open(coverage_data_path, encoding="utf-8") as fh:
        data = json.load(fh)
    missing = [r for r in data.get("results", []) if r.get("coverage_status") == "missing"]
    missing.sort(key=lambda r: PRIORITY_ORDER.get(r.get("priority", "low"), 2))
    return missing


def select_target(missing: list, target_api: str, priority_filter: str) -> dict:
    """Choose the API entry to scaffold.

    If *target_api* is non-empty, find by case-insensitive partial match on
    ``name``.  Otherwise auto-pick the first entry whose priority is ≤
    *priority_filter* in the ordering high > medium > low.
    """
    if target_api:
        needle = target_api.strip().lower()
        for entry in missing:
            if needle in entry.get("name", "").lower():
                return entry
        raise ValueError(
            f"No missing API matched '{target_api}'. "
            f"Available: {[e['name'] for e in missing]}"
        )

    # Auto-pick
    max_rank = PRIORITY_ORDER.get(priority_filter, 2)
    for entry in missing:
        if PRIORITY_ORDER.get(entry.get("priority", "low"), 2) <= max_rank:
            return entry

    raise ValueError(
        f"No missing API found with priority ≤ '{priority_filter}'. "
        "Try --priority low to include all priorities."
    )


def enrich_from_catalog(entry: dict, catalog_path: str) -> dict:
    """Return a copy of *entry* enriched with catalog fields (description, doc_url, …)."""
    with open(catalog_path, encoding="utf-8") as fh:
        catalog = json.load(fh)
    for item in catalog:
        if item.get("name", "").lower() == entry.get("name", "").lower():
            merged = {**item, **entry}   # entry fields take precedence
            return merged
    return dict(entry)


# ---------------------------------------------------------------------------
# Code generators
# ---------------------------------------------------------------------------

def _common_schema_fields(is_monitor: bool) -> str:
    """Return the Go source lines for the common schema map fields."""
    lines = [
        '\t\t"display_name": {',
        "\t\t\tType:         schema.TypeString,",
        "\t\t\tRequired:     true,",
        "\t\t\tValidateFunc: validation.NoZeroValues,",
        "\t\t},",
        '\t\t"type": {',
        "\t\t\tType:     schema.TypeString,",
        "\t\t\tComputed: true,",
        "\t\t},",
        '\t\t"location_profile_id": {',
        "\t\t\tType:         schema.TypeString,",
        "\t\t\tOptional:     true,",
        "\t\t\tComputed:     true,",
        "\t\t},",
        '\t\t"location_profile_name": {',
        "\t\t\tType:         schema.TypeString,",
        "\t\t\tOptional:     true,",
        "\t\t\tComputed:     true,",
        "\t\t},",
        '\t\t"notification_profile_id": {',
        "\t\t\tType:         schema.TypeString,",
        "\t\t\tOptional:     true,",
        "\t\t\tComputed:     true,",
        "\t\t},",
        '\t\t"notification_profile_name": {',
        "\t\t\tType:         schema.TypeString,",
        "\t\t\tOptional:     true,",
        "\t\t\tComputed:     true,",
        "\t\t},",
        '\t\t"threshold_profile_id": {',
        "\t\t\tType:         schema.TypeString,",
        "\t\t\tOptional:     true,",
        "\t\t\tComputed:     true,",
        "\t\t},",
        '\t\t"monitor_groups": {',
        "\t\t\tType: schema.TypeList,",
        "\t\t\tElem: &schema.Schema{",
        "\t\t\t\tType: schema.TypeString,",
        "\t\t\t},",
        "\t\t\tOptional: true,",
        "\t\t},",
        '\t\t"user_group_ids": {',
        "\t\t\tType: schema.TypeList,",
        "\t\t\tElem: &schema.Schema{",
        "\t\t\t\tType: schema.TypeString,",
        "\t\t\t},",
        "\t\t\tOptional: true,",
        "\t\t\tComputed: true,",
        "\t\t},",
        '\t\t"user_group_names": {',
        "\t\t\tType: schema.TypeList,",
        "\t\t\tElem: &schema.Schema{",
        "\t\t\t\tType: schema.TypeString,",
        "\t\t\t},",
        "\t\t\tOptional: true,",
        "\t\t\tComputed: true,",
        "\t\t},",
        '\t\t"tag_ids": {',
        "\t\t\tType: schema.TypeSet,",
        "\t\t\tElem: &schema.Schema{",
        "\t\t\t\tType: schema.TypeString,",
        "\t\t\t},",
        "\t\t\tOptional: true,",
        "\t\t\tComputed: true,",
        "\t\t},",
        '\t\t"tag_names": {',
        "\t\t\tType: schema.TypeList,",
        "\t\t\tElem: &schema.Schema{",
        "\t\t\t\tType: schema.TypeString,",
        "\t\t\t},",
        "\t\t\tOptional: true,",
        "\t\t\tComputed: true,",
        "\t\t},",
        '\t\t"third_party_service_ids": {',
        "\t\t\tType: schema.TypeList,",
        "\t\t\tElem: &schema.Schema{",
        "\t\t\t\tType: schema.TypeString,",
        "\t\t\t},",
        "\t\t\tOptional: true,",
        "\t\t},",
        '\t\t"check_frequency": {',
        "\t\t\tType:     schema.TypeString,",
        "\t\t\tOptional: true,",
        "\t\t\tDefault:  \"5\", // polling interval in minutes; Site24x7 default is 5",
        "\t\t},",
    ]
    if is_monitor:
        lines += [
            '\t\t"use_name_server": {',
            "\t\t\tType:     schema.TypeBool,",
            "\t\t\tOptional: true,",
            "\t\t},",
            '\t\t"up_status_codes": {',
            "\t\t\tType:     schema.TypeString,",
            "\t\t\tOptional: true,",
            "\t\t},",
        ]
    return "\n".join(lines)


def generate_resource_go(entry: dict) -> str:
    """Generate resource.go content for the given API entry."""
    terraform_name = entry.get("terraform_resource_name") or _to_snake(entry["name"])
    short = _resource_short_name(terraform_name)
    pascal = _to_pascal(short)
    camel = _to_camel(short)
    package = _go_package(entry.get("category", ""))
    api_path = entry.get("api_path", "/monitors")
    is_monitor = "/monitors" in api_path
    schema_fields = _common_schema_fields(is_monitor)
    name = entry.get("name", short)
    doc_url = entry.get("doc_url", "https://www.site24x7.com/help/api/")

    return f"""\
// Code generated by Agent 02 – resource_generator.py
// Source: {name}
// API path: {api_path}
// Doc: {doc_url}
//
// TODO: Fill in the struct fields, API calls, and schema attributes below.
// Reference an existing resource (e.g. api/monitors/website.go) for patterns.

package {package}

import (
\t"github.com/hashicorp/terraform-plugin-sdk/helper/schema"
\t"github.com/hashicorp/terraform-plugin-sdk/helper/validation"
\t"github.com/site24x7/terraform-provider-site24x7/api"
\t// TODO: uncomment when implementing Read/Exists:
\t// apierrors "github.com/site24x7/terraform-provider-site24x7/api/errors"
\t"github.com/site24x7/terraform-provider-site24x7/site24x7"
)

var {camel}Schema = map[string]*schema.Schema{{
{schema_fields}
}}

// ResourceSite24x7{pascal} returns the *schema.Resource for {name}.
func ResourceSite24x7{pascal}() *schema.Resource {{
\treturn &schema.Resource{{
\t\tCreate: {camel}Create,
\t\tRead:   {camel}Read,
\t\tUpdate: {camel}Update,
\t\tDelete: {camel}Delete,
\t\tExists: {camel}Exists,
\t\tImporter: &schema.ResourceImporter{{
\t\t\tState: schema.ImportStatePassthrough,
\t\t}},
\t\tSchema: {camel}Schema,
\t}}
}}

func {camel}Create(d *schema.ResourceData, meta interface{{}}) error {{
\tclient := meta.(site24x7.Client)
\t// TODO: Convert resource data to API struct and call client.{pascal}s().Create(...)
\t_ = client
\treturn {camel}Read(d, meta)
}}

func {camel}Read(d *schema.ResourceData, meta interface{{}}) error {{
\tclient := meta.(site24x7.Client)
\t// TODO: Call client.{pascal}s().Get(d.Id()) and populate resource data
\t// Example:
\t//   resource, err := client.{pascal}s().Get(d.Id())
\t//   if apierrors.IsNotFound(err) {{
\t//       d.SetId("")
\t//       return nil
\t//   }}
\t//   if err != nil {{
\t//       return err
\t//   }}
\t//   update{pascal}ResourceData(d, resource)
\t_ = client
\treturn nil
}}

func {camel}Update(d *schema.ResourceData, meta interface{{}}) error {{
\tclient := meta.(site24x7.Client)
\t// TODO: Convert resource data to API struct and call client.{pascal}s().Update(...)
\t_ = client
\treturn {camel}Read(d, meta)
}}

func {camel}Delete(d *schema.ResourceData, meta interface{{}}) error {{
\tclient := meta.(site24x7.Client)
\t// TODO: Call client.{pascal}s().Delete(d.Id())
\t_ = client
\treturn nil
}}

func {camel}Exists(d *schema.ResourceData, meta interface{{}}) (bool, error) {{
\tclient := meta.(site24x7.Client)
\t// TODO: Call client.{pascal}s().Get(d.Id()) and return whether it exists
\t_ = client
\treturn true, nil
}}

// resourceDataTo{pascal} converts Terraform resource data to the API struct.
func resourceDataTo{pascal}(d *schema.ResourceData) *api.{pascal} {{
\t// TODO: Populate and return an api.{pascal} struct from resource data fields
\treturn &api.{pascal}{{
\t\tDisplayName: d.Get("display_name").(string),
\t}}
}}

// update{pascal}ResourceData populates resource data from the API struct.
func update{pascal}ResourceData(d *schema.ResourceData, {camel} *api.{pascal}) {{
\t// TODO: Set each schema field from the API struct, e.g.:
\t// d.Set("display_name", {camel}.DisplayName)
\t_ = {camel}
}}
"""


def generate_resource_test_go(entry: dict) -> str:
    """Generate resource_test.go content."""
    terraform_name = entry.get("terraform_resource_name") or _to_snake(entry["name"])
    short = _resource_short_name(terraform_name)
    pascal = _to_pascal(short)
    camel = _to_camel(short)
    package = _go_package(entry.get("category", ""))
    name = entry.get("name", short)

    # Build list of expected schema keys
    keys = [
        "display_name", "type", "location_profile_id", "location_profile_name",
        "notification_profile_id", "notification_profile_name", "threshold_profile_id",
        "monitor_groups", "user_group_ids", "user_group_names",
        "tag_ids", "tag_names", "third_party_service_ids", "check_frequency",
    ]
    api_path = entry.get("api_path", "/monitors")
    if "/monitors" in api_path:
        keys += ["use_name_server", "up_status_codes"]

    key_checks = "\n".join(
        f'\t\t\t"{k}",' for k in keys
    )

    return f"""\
// Code generated by Agent 02 – resource_generator.py
// Source: {name}
//
// TODO: Add acceptance tests once the resource implementation is complete.
// Reference an existing *_test.go file (e.g. api/monitors/website_test.go).

package {package}_test

import (
\t"testing"

\t"github.com/hashicorp/terraform-plugin-sdk/helper/schema"
)

// TestNew{pascal}Schema validates that all expected schema keys are present.
func TestNew{pascal}Schema(t *testing.T) {{
\texpectedKeys := []string{{
{key_checks}
\t}}

\t// Build a minimal resource just to inspect its schema
\tres := &schema.Resource{{Schema: {camel}Schema}}
\tfor _, key := range expectedKeys {{
\t\tif _, ok := res.Schema[key]; !ok {{
\t\t\tt.Errorf("expected schema key %q not found", key)
\t\t}}
\t}}
}}

// TODO: Add TestAccSite24x7{pascal}Basic acceptance test using providerFactories
// and a Terraform configuration HCL string, following existing monitor tests.
"""


def generate_doc_md(entry: dict) -> str:
    """Generate Terraform registry-style Markdown documentation."""
    terraform_name = entry.get("terraform_resource_name") or _to_snake(entry["name"])
    short = _resource_short_name(terraform_name)
    name = entry.get("name", short)
    description = entry.get("description", f"Manage {name} resources in Site24x7.")
    doc_url = entry.get("doc_url", "https://www.site24x7.com/help/api/")
    category = entry.get("category", "Monitors")
    api_path = entry.get("api_path", "/monitors")
    is_monitor = "/monitors" in api_path

    extra_args = ""
    if is_monitor:
        extra_args = """\
* `use_name_server` - (Optional) Set to true to use the name server for DNS resolution.
* `up_status_codes` - (Optional) Comma-separated list of HTTP status codes that represent "up" status.
"""

    return f"""\
---
layout: "site24x7"
page_title: "Site24x7: {terraform_name}"
sidebar_current: "docs-site24x7-resource-{short.replace('_', '-')}"
description: |-
  {description}
---

# Resource: {terraform_name}

{description}

## Example Usage

```hcl
resource "{terraform_name}" "example" {{
  display_name = "My {name}"

  # Optional profile overrides
  # location_profile_id      = "<profile-id>"
  # notification_profile_id  = "<profile-id>"
  # threshold_profile_id     = "<profile-id>"

  # Optional grouping / tagging
  # monitor_groups           = ["<group-id>"]
  # tag_ids                  = ["<tag-id>"]
  # user_group_ids           = ["<group-id>"]
}}
```

## Argument Reference

The following arguments are supported:

* `display_name` - (Required) Display name for the monitor.
* `type` - (Computed) Monitor type identifier set by the provider.
* `location_profile_id` - (Optional, Computed) ID of the location profile.
* `location_profile_name` - (Optional, Computed) Name of the location profile.
* `notification_profile_id` - (Optional, Computed) ID of the notification profile.
* `notification_profile_name` - (Optional, Computed) Name of the notification profile.
* `threshold_profile_id` - (Optional, Computed) ID of the threshold profile.
* `monitor_groups` - (Optional) List of monitor group IDs this monitor belongs to.
* `user_group_ids` - (Optional, Computed) List of user group IDs for alerts.
* `user_group_names` - (Optional, Computed) List of user group names (resolved automatically).
* `tag_ids` - (Optional, Computed) Set of tag IDs to associate with this monitor.
* `tag_names` - (Optional, Computed) List of tag names (resolved automatically).
* `third_party_service_ids` - (Optional) List of third-party service integration IDs.
* `check_frequency` - (Optional) Polling interval in minutes. Default: `"5"`.
{extra_args}
## Attributes Reference

In addition to the arguments listed above, the following computed attributes are exported:

* `id` - The ID of the {name} resource.

## Import

{name} resources can be imported using the monitor ID:

```sh
terraform import {terraform_name}.example <monitor-id>
```

---

See also: [Site24x7 API – {category}]({doc_url})
"""


def generate_provider_registration(entry: dict) -> str:
    """Generate the provider_registration.txt snippet."""
    terraform_name = entry.get("terraform_resource_name") or _to_snake(entry["name"])
    short = _resource_short_name(terraform_name)
    pascal = _to_pascal(short)
    package = _go_package(entry.get("category", ""))
    name = entry.get("name", short)

    return f"""\
// Add the following line to the ResourcesMap in provider/provider.go:
//
//   "{terraform_name}": {package}.ResourceSite24x7{pascal}(),
//
// Also ensure the import block at the top of provider.go includes the package:
//   "{package}" "github.com/site24x7/terraform-provider-site24x7/{package}"
//
// Source API: {name}
// Catalog category: {entry.get("category", "unknown")}
// Priority: {entry.get("priority", "unknown")}
"""


def generate_summary_md(entry: dict, output_dir: str) -> str:
    """Generate a GitHub Actions job summary in Markdown."""
    terraform_name = entry.get("terraform_resource_name") or _to_snake(entry["name"])
    short = _resource_short_name(terraform_name)
    pascal = _to_pascal(short)
    camel = _to_camel(short)
    name = entry.get("name", short)
    category = entry.get("category", "unknown")
    priority = entry.get("priority", "unknown")
    doc_url = entry.get("doc_url", "")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    files = [
        f"`{output_dir}/{short}/resource.go`",
        f"`{output_dir}/{short}/resource_test.go`",
        f"`{output_dir}/{short}/doc.md`",
        f"`{output_dir}/{short}/provider_registration.txt`",
    ]
    file_list = "\n".join(f"- {f}" for f in files)

    return f"""\
## 🤖 Agent 02 — Terraform Resource Scaffold Generation

| Field | Value |
|---|---|
| **API** | {name} |
| **Terraform resource** | `{terraform_name}` |
| **Go function** | `ResourceSite24x7{pascal}()` |
| **Go schema var** | `{camel}Schema` |
| **Category** | {category} |
| **Priority** | {priority} |
| **Generated at** | {ts} |

### Generated files

{file_list}

### Next steps

1. Review and complete the `TODO` items in `{short}/resource.go`.
2. Add the line from `{short}/provider_registration.txt` to `provider/provider.go`.
3. Write acceptance tests in `{short}/resource_test.go`.
4. Update `{short}/doc.md` with real attribute descriptions.
5. Open a PR to `site24x7/terraform-provider-site24x7`.

{"See also: " + doc_url if doc_url else ""}
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate Terraform provider scaffold for a missing Site24x7 API."
    )
    parser.add_argument("--coverage-data", required=True,
                        help="Path to LATEST_DATA.json (Agent 01 output)")
    parser.add_argument("--api-catalog", required=True,
                        help="Path to site24x7_api_catalog.json")
    parser.add_argument("--target-api", default="",
                        help="API name (partial match, case-insensitive) to scaffold. "
                             "Leave empty to auto-pick highest-priority missing API.")
    parser.add_argument("--priority", default="high",
                        choices=["high", "medium", "low"],
                        help="Minimum priority for auto-pick (default: high)")
    parser.add_argument("--output-dir", default="generated",
                        help="Directory to write generated files into")
    parser.add_argument("--provider-repo", default="site24x7/terraform-provider-site24x7",
                        help="Upstream provider repository slug (informational only)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    print(f"[resource_generator] Reading coverage data from: {args.coverage_data}")
    missing = load_missing_entries(args.coverage_data)
    print(f"[resource_generator] Found {len(missing)} missing APIs.")

    entry = select_target(missing, args.target_api.strip(), args.priority)
    print(f"[resource_generator] Selected API: {entry['name']} (priority={entry.get('priority')})")

    entry = enrich_from_catalog(entry, args.api_catalog)

    terraform_name = entry.get("terraform_resource_name") or _to_snake(entry["name"])
    short = _resource_short_name(terraform_name)

    resource_dir = os.path.join(args.output_dir, short)
    os.makedirs(resource_dir, exist_ok=True)
    print(f"[resource_generator] Writing files to: {resource_dir}/")

    files = {
        os.path.join(resource_dir, "resource.go"): generate_resource_go(entry),
        os.path.join(resource_dir, "resource_test.go"): generate_resource_test_go(entry),
        os.path.join(resource_dir, "doc.md"): generate_doc_md(entry),
        os.path.join(resource_dir, "provider_registration.txt"): generate_provider_registration(entry),
    }
    for path, content in files.items():
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"[resource_generator]   wrote {path}")

    # Write top-level helper files
    summary_path = os.path.join(args.output_dir, "generation_summary.md")
    with open(summary_path, "w", encoding="utf-8") as fh:
        fh.write(generate_summary_md(entry, args.output_dir))
    print(f"[resource_generator]   wrote {summary_path}")

    api_name_path = os.path.join(args.output_dir, ".api_name")
    with open(api_name_path, "w", encoding="utf-8") as fh:
        fh.write(entry["name"])
    print(f"[resource_generator]   wrote {api_name_path}")

    print("[resource_generator] Done.")


if __name__ == "__main__":
    sys.exit(main())
