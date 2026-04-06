# 📊 Site24x7 Terraform Provider — API Coverage Report

**Generated:** 2026-04-06 09:01:06 UTC  
**Provider:** [site24x7/terraform-provider-site24x7](https://github.com/site24x7/terraform-provider-site24x7)  
**Branch:** `main`

## 📈 Summary

| Metric | Count | Percentage |
|--------|------:|:-----------|
| Total API Endpoints | 65 | 100% |
| ✅ Full Coverage (resource + docs) | 38 | 58.5% |
| ⚠️ Partial Coverage (resource or datasource) | 5 | 7.7% |
| ❌ Missing | 22 | 33.8% |
| **Overall Covered** | **43** | **66.2%** |

### Coverage Progress

```
Overall: [████████████████████░░░░░░░░░░] 66.2%
         43 / 65 endpoints covered
```

## 📂 Coverage by Category

| Category | Total | ✅ Full | ⚠️ Partial | ❌ Missing | Progress |
|----------|------:|-------:|-----------:|-----------:|:---------|
| APM | 1 | 0 | 0 | 1 | ⬜⬜⬜⬜⬜ 0% |
| Automation | 1 | 1 | 0 | 0 | 🟩🟩🟩🟩🟩 100% |
| Cloud Monitors | 4 | 3 | 1 | 0 | 🟩🟩🟩🟩🟩 100% |
| Configuration | 1 | 0 | 1 | 0 | 🟩🟩🟩🟩🟩 100% |
| Dashboards | 1 | 0 | 0 | 1 | ⬜⬜⬜⬜⬜ 0% |
| Infrastructure | 2 | 0 | 1 | 1 | 🟩🟩⬜⬜⬜ 50% |
| Integrations | 9 | 7 | 0 | 2 | 🟩🟩🟩🟩⬜ 78% |
| Logs | 1 | 0 | 0 | 1 | ⬜⬜⬜⬜⬜ 0% |
| MSP | 2 | 1 | 1 | 0 | 🟩🟩🟩🟩🟩 100% |
| Maintenance | 1 | 1 | 0 | 0 | 🟩🟩🟩🟩🟩 100% |
| Monitor Groups | 2 | 2 | 0 | 0 | 🟩🟩🟩🟩🟩 100% |
| Monitors | 21 | 16 | 0 | 5 | 🟩🟩🟩🟩⬜ 76% |
| Network | 1 | 0 | 0 | 1 | ⬜⬜⬜⬜⬜ 0% |
| Profiles | 5 | 4 | 0 | 1 | 🟩🟩🟩🟩⬜ 80% |
| Reports | 7 | 0 | 1 | 6 | 🟩⬜⬜⬜⬜ 14% |
| Security | 1 | 0 | 0 | 1 | ⬜⬜⬜⬜⬜ 0% |
| Status Pages | 1 | 0 | 0 | 1 | ⬜⬜⬜⬜⬜ 0% |
| Tags | 1 | 1 | 0 | 0 | 🟩🟩🟩🟩🟩 100% |
| Users | 3 | 2 | 0 | 1 | 🟩🟩🟩⬜⬜ 67% |

## ✅ Covered Endpoints

### ✅ Fully Covered

| API Name | Category | Resource Name | Data Source | Has Docs | Coverage | API Docs |
|----------|----------|---------------|-------------|----------|----------|----------|
| Website Monitor | Monitors | `site24x7_website_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#website) |
| SSL Certificate Monitor | Monitors | `site24x7_ssl_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#ssl-certificate) |
| REST API Monitor | Monitors | `site24x7_rest_api_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#rest-api) |
| REST API Transaction Monitor | Monitors | `site24x7_rest_api_transaction_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#rest-api-transaction) |
| Web Page Speed Monitor | Monitors | `site24x7_web_page_speed_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#web-page-speed) |
| Web Transaction (Browser) Monitor | Monitors | `site24x7_web_transaction_browser_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#web-transaction-browser) |
| DNS Server Monitor | Monitors | `site24x7_dns_server_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#dns-server) |
| Domain Expiry Monitor | Monitors | `site24x7_domain_expiry_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#domain-expiry) |
| FTP Transfer Monitor | Monitors | `site24x7_ftp_transfer_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#ftp-transfer) |
| Port (Custom Protocol) Monitor | Monitors | `site24x7_port_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#port) |
| PING Monitor | Monitors | `site24x7_ping_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#ping) |
| SOAP Web Service Monitor | Monitors | `site24x7_soap_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#soap) |
| Heartbeat Monitor | Monitors | `site24x7_heartbeat_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#heartbeat) |
| Cron Monitor | Monitors | `site24x7_cron_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#cron) |
| ISP Monitor | Monitors | `site24x7_isp_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#isp) |
| Server Monitor | Monitors | `site24x7_server_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#server) |
| Amazon (AWS) Monitor | Cloud Monitors | `site24x7_amazon_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#amazon) |
| Google Cloud Platform Monitor | Cloud Monitors | `site24x7_gcp_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#gcp) |
| Azure Monitor | Cloud Monitors | `site24x7_azure_monitor` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#azure) |
| Monitor Group | Monitor Groups | `site24x7_monitor_group` | `site24x7_monitor_group` | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#monitor-groups) |
| Subgroup | Monitor Groups | `site24x7_subgroup` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#subgroups) |
| Threshold Profile | Profiles | `site24x7_threshold_profile` | `site24x7_threshold_profile` | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#threshold-profiles) |
| Location Profile | Profiles | `site24x7_location_profile` | `site24x7_location_profile` | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#location-profiles) |
| Notification Profile | Profiles | `site24x7_notification_profile` | `site24x7_notification_profile` | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#notification-profiles) |
| Credential Profile | Profiles | `site24x7_credential_profile` | `site24x7_credential_profile` | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#credential-profiles) |
| User Group | Users | `site24x7_user_group` | `site24x7_user_group` | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#user-groups) |
| User | Users | `site24x7_user` | `site24x7_user` | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#users) |
| Tag | Tags | `site24x7_tag` | `site24x7_tag` | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#tags) |
| IT Automation (URL Action) | Automation | `site24x7_url_action` | `site24x7_it_automation` | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#it-automation) |
| Maintenance Window | Maintenance | `site24x7_schedule_maintenance` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#maintenance) |
| OpsGenie Integration | Integrations | `site24x7_opsgenie_integration` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#opsgenie) |
| Slack Integration | Integrations | `site24x7_slack_integration` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#slack) |
| Webhook Integration | Integrations | `site24x7_webhook_integration` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#webhook) |
| PagerDuty Integration | Integrations | `site24x7_pagerduty_integration` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#pagerduty) |
| ServiceNow Integration | Integrations | `site24x7_servicenow_integration` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#servicenow) |
| ConnectWise Integration | Integrations | `site24x7_connectwise_integration` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#connectwise) |
| Telegram Integration | Integrations | `site24x7_telegram_integration` | — | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#telegram) |
| MSP Customer | MSP | `site24x7_customer` | `site24x7_customer` | ✅ | ✅ Full | [docs](https://www.site24x7.com/help/api/#msp-customers) |

### ⚠️ Partially Covered

| API Name | Category | Resource Name | Data Source | Has Docs | Coverage | API Docs |
|----------|----------|---------------|-------------|----------|----------|----------|
| Business Hours | Configuration | `site24x7_businesshour` | — | ❌ | ⚠️ Partial | [docs](https://www.site24x7.com/help/api/#business-hours) |
| Schedule Report | Reports | `site24x7_schedule_report` | — | ❌ | ⚠️ Partial | [docs](https://www.site24x7.com/help/api/#schedule-reports) |
| MSP | MSP | — | `site24x7_msp` | ❌ | ⚠️ Partial | [docs](https://www.site24x7.com/help/api/#msp) |
| AWS External ID | Cloud Monitors | — | `site24x7_aws_external_id` | ❌ | ⚠️ Partial | [docs](https://www.site24x7.com/help/api/#aws-external-id) |
| Device Key | Infrastructure | — | `site24x7_device_key` | ❌ | ⚠️ Partial | [docs](https://www.site24x7.com/help/api/#device-key) |

## 🚨 Missing APIs

### 🔴 High Priority

| API Name | Category | Resource Name | Priority | API Docs |
|----------|----------|---------------|----------|----------|
| SMTP Mail Monitor | Monitors | `site24x7_smtp_monitor` | high | [docs](https://www.site24x7.com/help/api/#smtp) |
| Real Browser Monitor (RBM) | Monitors | `site24x7_real_browser_monitor` | high | [docs](https://www.site24x7.com/help/api/#real-browser) |
| Real User Monitoring (RUM) | Monitors | `site24x7_rum_monitor` | high | [docs](https://www.site24x7.com/help/api/#rum) |
| APM Insight Application | APM | `site24x7_apm_insight_monitor` | high | [docs](https://www.site24x7.com/help/api/#apm-insight) |
| Alert Contact | Users | `site24x7_alert_contact` | high | [docs](https://www.site24x7.com/help/api/#alert-contacts) |
| Microsoft Teams Integration | Integrations | `site24x7_msteams_integration` | high | [docs](https://www.site24x7.com/help/api/#msteams) |
| Status Page | Status Pages | `site24x7_status_page` | high | [docs](https://www.site24x7.com/help/api/#status-page) |

<details>
<summary>🟡 Medium Priority Missing APIs</summary>

| API Name | Category | Resource Name | Priority | API Docs |
|----------|----------|---------------|----------|----------|
| POP Monitor | Monitors | `site24x7_pop_monitor` | medium | [docs](https://www.site24x7.com/help/api/#pop) |
| IMAP Monitor | Monitors | `site24x7_imap_monitor` | medium | [docs](https://www.site24x7.com/help/api/#imap) |
| AppLogs | Logs | `site24x7_applogs_monitor` | medium | [docs](https://www.site24x7.com/help/api/#applogs) |
| Network Device Monitor | Network | `site24x7_network_device_monitor` | medium | [docs](https://www.site24x7.com/help/api/#network-devices) |
| On-Premise Poller | Infrastructure | `site24x7_on_premise_poller` | medium | [docs](https://www.site24x7.com/help/api/#on-premise-poller) |
| Custom Dashboard | Dashboards | `site24x7_custom_dashboard` | medium | [docs](https://www.site24x7.com/help/api/#custom-dashboard) |

</details>

<details>
<summary>🟢 Low Priority Missing APIs</summary>

| API Name | Category | Resource Name | Priority | API Docs |
|----------|----------|---------------|----------|----------|
| Location Template | Profiles | `site24x7_location_template` | low | [docs](https://www.site24x7.com/help/api/#location-template) |
| ManageEngine SDP Integration | Integrations | `site24x7_sdp_integration` | low | [docs](https://www.site24x7.com/help/api/#sdp) |
| Availability Report | Reports | `site24x7_availability_report` | low | [docs](https://www.site24x7.com/help/api/#availability-report) |
| Performance Report | Reports | `site24x7_performance_report` | low | [docs](https://www.site24x7.com/help/api/#performance-report) |
| Summary Report | Reports | `site24x7_summary_report` | low | [docs](https://www.site24x7.com/help/api/#summary-report) |
| Top N Report | Reports | `site24x7_top_n_report` | low | [docs](https://www.site24x7.com/help/api/#topn-report) |
| SLA Report | Reports | `site24x7_sla_report` | low | [docs](https://www.site24x7.com/help/api/#sla-report) |
| Alert Log | Reports | `site24x7_alert_log` | low | [docs](https://www.site24x7.com/help/api/#alert-logs) |
| IP Restriction | Security | `site24x7_ip_restriction` | low | [docs](https://www.site24x7.com/help/api/#ip-restrictions) |

</details>

<details>
<summary>✅ Implemented Resources (40)</summary>

| Resource Name |
|---------------|
| `site24x7_amazon_monitor` |
| `site24x7_azure_monitor` |
| `site24x7_businesshour` |
| `site24x7_connectwise_integration` |
| `site24x7_credential_profile` |
| `site24x7_cron_monitor` |
| `site24x7_customer` |
| `site24x7_dns_server_monitor` |
| `site24x7_domain_expiry_monitor` |
| `site24x7_ftp_transfer_monitor` |
| `site24x7_gcp_monitor` |
| `site24x7_heartbeat_monitor` |
| `site24x7_isp_monitor` |
| `site24x7_location_profile` |
| `site24x7_monitor_group` |
| `site24x7_notification_profile` |
| `site24x7_opsgenie_integration` |
| `site24x7_pagerduty_integration` |
| `site24x7_ping_monitor` |
| `site24x7_port_monitor` |
| `site24x7_rest_api_monitor` |
| `site24x7_rest_api_transaction_monitor` |
| `site24x7_schedule_maintenance` |
| `site24x7_schedule_report` |
| `site24x7_server_monitor` |
| `site24x7_servicenow_integration` |
| `site24x7_slack_integration` |
| `site24x7_soap_monitor` |
| `site24x7_ssl_monitor` |
| `site24x7_subgroup` |
| `site24x7_tag` |
| `site24x7_telegram_integration` |
| `site24x7_threshold_profile` |
| `site24x7_url_action` |
| `site24x7_user` |
| `site24x7_user_group` |
| `site24x7_web_page_speed_monitor` |
| `site24x7_web_transaction_browser_monitor` |
| `site24x7_webhook_integration` |
| `site24x7_website_monitor` |

</details>

<details>
<summary>✅ Implemented Data Sources (15)</summary>

| Data Source Name |
|------------------|
| `site24x7_aws_external_id` |
| `site24x7_credential_profile` |
| `site24x7_customer` |
| `site24x7_device_key` |
| `site24x7_it_automation` |
| `site24x7_location_profile` |
| `site24x7_monitor` |
| `site24x7_monitor_group` |
| `site24x7_monitors` |
| `site24x7_msp` |
| `site24x7_notification_profile` |
| `site24x7_tag` |
| `site24x7_threshold_profile` |
| `site24x7_user` |
| `site24x7_user_group` |

</details>

---

*Report generated automatically by [site24x7-api-terraform-coverage](https://github.com/vinoth-kanagaraj-14883/site24x7-api-terraform-coverage) · 2026-04-06 09:01:06 UTC*
