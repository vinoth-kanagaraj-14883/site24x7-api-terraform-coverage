# 📊 Site24x7 Terraform Provider — API Coverage Analyzer

[![API Coverage](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fvinoth-kanagaraj-14883%2Fsite24x7-api-terraform-coverage%2Fmain%2Freports%2FLATEST_BADGE.json&cacheSeconds=3600)](reports/LATEST_REPORT.md)
[![Coverage Workflow](https://github.com/vinoth-kanagaraj-14883/site24x7-api-terraform-coverage/actions/workflows/api-coverage-report.yml/badge.svg)](https://github.com/vinoth-kanagaraj-14883/site24x7-api-terraform-coverage/actions/workflows/api-coverage-report.yml)

Automated GitHub Actions workflow that tracks how much of the [Site24x7 REST API](https://www.site24x7.com/help/api/) is covered by the [Terraform Provider](https://github.com/site24x7/terraform-provider-site24x7).

---

## ✨ Features

- **Automated weekly analysis** — runs every Monday at 08:00 UTC
- **Manual dispatch** — trigger from the Actions tab with custom repo/branch inputs
- **Triggered on change** — re-runs automatically when `scripts/` or `config/` are updated
- **Rich Markdown reports** — summary tables, category breakdowns, prioritised missing APIs, collapsible sections
- **Shields.io badge** — embed a live coverage badge in any README
- **JSON data export** — machine-readable results for downstream tooling
- **Git-committed latest reports** — `reports/LATEST_*.{md,json}` always reflect the most recent run
- **Issue tracking** — optional GitHub Issue creation / updates with coverage status

---

## 📁 Project Structure

```
.github/
  workflows/
    api-coverage-report.yml   # GitHub Actions workflow
scripts/
  coverage_analyzer.py        # Python analyzer (stdlib only, requires Python 3.10+)
config/
  site24x7_api_catalog.json   # API catalog (~65 endpoints)
reports/
  .gitkeep                    # Directory placeholder
  LATEST_REPORT.md            # Latest full report (auto-committed)
  LATEST_DATA.json            # Latest structured data (auto-committed)
  LATEST_BADGE.json           # Latest Shields.io badge (auto-committed)
requirements.txt              # No pip dependencies required
.gitignore
README.md
```

---

## 🚀 Usage

### Run via GitHub Actions

**Scheduled:** The workflow runs automatically every Monday at 08:00 UTC.

**Manual trigger:**

1. Go to **Actions → Site24x7 API Coverage Report → Run workflow**
2. Optionally override:
   - **Provider repo** (default: `site24x7/terraform-provider-site24x7`)
   - **Provider branch** (default: `main`)
   - **Create tracking issue** (default: `false`)

### Run Locally

```bash
# Requires Python 3.10+ (tested with Python 3.11)
# Clone this repository
git clone https://github.com/vinoth-kanagaraj-14883/site24x7-api-terraform-coverage.git
cd site24x7-api-terraform-coverage

# Download provider source
mkdir -p /tmp/provider_source
curl -sL "https://raw.githubusercontent.com/site24x7/terraform-provider-site24x7/main/provider/provider.go" \
     -o /tmp/provider_source/provider.go

# Run the analyzer
python3 scripts/coverage_analyzer.py \
  --provider-file /tmp/provider_source/provider.go \
  --api-catalog config/site24x7_api_catalog.json \
  --output-dir reports/

# View the report
cat reports/coverage_report.md
```

---

## 📊 Coverage Badge

Add the live badge to any repository's README:

```markdown
[![API Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/vinoth-kanagaraj-14883/site24x7-api-terraform-coverage/main/reports/LATEST_BADGE.json)](https://github.com/vinoth-kanagaraj-14883/site24x7-api-terraform-coverage/blob/main/reports/LATEST_REPORT.md)
```

Badge colour thresholds:
- 🟢 **Bright green** — ≥ 80% coverage
- 🟡 **Yellow** — ≥ 60% coverage
- 🟠 **Orange** — ≥ 40% coverage
- 🔴 **Red** — < 40% coverage

---

## ⚙️ How It Works

```
provider.go (ResourcesMap / DataSourcesMap)
        │
        ▼
coverage_analyzer.py  ◄── site24x7_api_catalog.json
        │
        ▼
 ┌──────────────────────────────────────┐
 │  For each catalog entry:             │
 │  • has_resource   → in ResourcesMap? │
 │  • has_datasource → in DataSourcesMap?│
 │  • has_docs       → .md in docs/resources│
 │  ─────────────────────────────────── │
 │  full    = resource + resource docs  │
 │  partial = resource or datasource    │
 │  missing = neither                   │
 └──────────────────────────────────────┘
        │
        ▼
 coverage_report.md  coverage_summary.md
 coverage_data.json  coverage_badge.json
```

The analyzer:
1. Scans `provider.go` to locate the `ResourcesMap` and `DataSourcesMap` blocks via a brace-counting walk, then applies a regex per line inside those blocks to extract entries
2. Loads the API catalog (`config/site24x7_api_catalog.json`)
3. Optionally cross-references the `docs/resources` directory listing from GitHub
4. Emits four output files into `--output-dir`

---

## 🗂️ Extending the API Catalog

To track a new Site24x7 API endpoint, add an entry to `config/site24x7_api_catalog.json`:

```json
{
  "name": "My New Monitor",
  "category": "Monitors",
  "api_path": "/monitors",
  "description": "Brief description of what this API does.",
  "doc_url": "https://www.site24x7.com/help/api/#my-new-monitor",
  "operations": ["GET", "POST", "PUT", "DELETE"],
  "priority": "high",
  "terraform_resource_name": "site24x7_my_new_monitor",
  "terraform_datasource_name": null
}
```

| Field | Values | Notes |
|-------|--------|-------|
| `priority` | `"high"` / `"medium"` / `"low"` | Drives report section placement |
| `terraform_resource_name` | string or `null` | Set once the TF resource is implemented |
| `terraform_datasource_name` | string or `null` | Set once the TF datasource is implemented |

---

## 📜 License

MIT © 2024 [vinoth-kanagaraj-14883](https://github.com/vinoth-kanagaraj-14883)
