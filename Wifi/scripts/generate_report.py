import json
from pathlib import Path

WIFI_SUMMARY_JSON_INPUT_FILE = Path("output/wifi_summary.json")
FORENSIC_REPORT_OUTPUT_FILE = Path("output/final_report.md")


def format_dictionary_as_markdown_table(label_value_dictionary):
    if not label_value_dictionary:
        return "_No data available._"

    markdown_table_lines = ["| Name | Count |", "|------|-------|"]
    for entry_label, entry_count in label_value_dictionary.items():
        markdown_table_lines.append(f"| {entry_label} | {entry_count} |")

    return "\n".join(markdown_table_lines)


def build_full_forensic_report_text(wifi_summary_dictionary):
    top_ssids_markdown_table = format_dictionary_as_markdown_table(wifi_summary_dictionary.get("top_ssids", {}))
    top_bssids_markdown_table = format_dictionary_as_markdown_table(wifi_summary_dictionary.get("top_bssids", {}))

    forensic_report_text = f"""# Where Have You Been: Forensics Analysis of WiFi

## Executive Summary

This report presents the results of a forensic analysis of WiFi artifacts collected from an authorized system. The analysis identified saved wireless profiles, connection activity, and available metadata that may help reconstruct prior device locations. All evidence was collected from a personally owned or lab-controlled system with explicit authorization. No unauthorized network access, third-party packet capture, or private data collection was performed.

---

## Scope and Authorization

This analysis was conducted exclusively on an authorized system. The examiner had explicit permission to collect and analyze WiFi artifacts from the target device. No passwords or private credentials were retained in this report. All security key values were redacted prior to storage.

---

## Evidence Sources

- Saved WiFi profiles extracted using `netsh wlan show profiles` (Windows)
- Windows WLAN AutoConfig event logs exported from `Microsoft-Windows-WLAN-AutoConfig/Operational`
- Optional: Instructor-provided mock BSSID geolocation lookup table

---

## Tools Used

| Tool | Purpose |
|------|---------|
| Python 3 | Script development and data processing |
| `subprocess` / `netsh` | WiFi profile extraction on Windows |
| `xml.etree.ElementTree` | Parsing WLAN AutoConfig XML event logs |
| `pandas` | Data cleaning, normalization, and analysis |
| `matplotlib` | WiFi activity timeline visualization |
| `folium` | Interactive HTML geolocation map (if location data available) |
| `json` | Summary data storage and report generation |

---

## Methodology

1. Saved WiFi profiles were extracted using the Windows `netsh` utility and written to CSV.
2. WLAN AutoConfig event logs were exported as XML and parsed to extract timestamps, event IDs, SSIDs, BSSIDs, and connection metadata.
3. The raw timeline was cleaned: records with invalid timestamps were dropped, missing SSIDs and BSSIDs were labeled as "Unknown," and all events were sorted chronologically.
4. A summary JSON was produced identifying unique networks, frequency counts, and the observed date range.
5. Where a mock BSSID geolocation lookup file was available, the timeline was enriched with approximate location metadata.
6. A scatter chart was generated to visualize WiFi activity over time by SSID.
7. If enriched location data was available, an interactive HTML map was produced.

---

## Summary of Findings

| Metric | Value |
|--------|-------|
| Total WiFi events analyzed | {wifi_summary_dictionary["total_events"]} |
| Unique SSIDs observed | {wifi_summary_dictionary["unique_ssids"]} |
| Unique BSSIDs observed | {wifi_summary_dictionary["unique_bssids"]} |
| First observed event | {wifi_summary_dictionary["first_observed"]} |
| Last observed event | {wifi_summary_dictionary["last_observed"]} |

---

## Most Frequently Observed SSIDs

{top_ssids_markdown_table}

---

## Most Frequently Observed BSSIDs

{top_bssids_markdown_table}

---

## Timeline of WiFi Activity

See `output/wifi_timeline_cleaned.csv` for the full chronological event log. See `output/wifi_activity_timeline.png` for the visual scatter chart of activity by SSID over time.

---

## Location Analysis

Where BSSID geolocation data was available (via instructor-provided mock lookup or open-source database), approximate physical locations were associated with observed connection events. These locations represent the likely position of the wireless access point at the time of last known registration and should not be treated as definitive proof of device presence.

See `output/wifi_timeline_enriched.csv` for the enriched timeline and `output/wifi_location_map.html` for the interactive map, if generated.

---

## Limitations

- WiFi artifacts can suggest prior locations but do not independently prove that a specific person was physically present at a location.
- SSIDs are not unique identifiers. The same SSID name may be used by many different access points across different locations.
- Access points may have been relocated since their BSSID was registered in any geolocation database.
- WLAN AutoConfig event logs may be incomplete, cleared, or subject to log rotation policies.
- System timestamps must be validated against known-good time sources. Clock skew or manipulation could affect timeline accuracy.
- BSSID geolocation data from public databases may be stale, inaccurate, or entirely absent for a given access point.
- The presence of a saved WiFi profile does not confirm that a connection was ever successfully established.

---

## Conclusion

The WiFi artifacts analyzed in this report provided useful evidence for reconstructing network connection activity and possible location history over the observed time period. Repeated connections to specific SSIDs and BSSIDs suggest patterns of device presence that may corroborate other evidence. However, definitive conclusions about physical location require correlation with additional artifact sources.

Stronger conclusions would require corroborating evidence such as browser history, file access timestamps, GPS or cellular location data, login records, photographs with embedded metadata, cloud synchronization logs, or mobile device artifacts.

---

## Appendix

### Script Inventory

| Script | Purpose |
|--------|---------|
| `scripts/collect_windows_wifi.py` | Extract saved WiFi profiles using netsh |
| `scripts/parse_wifi_profiles.py` | Parse WLAN AutoConfig XML event logs |
| `scripts/analyze_wifi_history.py` | Clean, summarize, enrich, and chart WiFi data |
| `scripts/generate_map.py` | Generate interactive HTML map from enriched data |
| `scripts/generate_report.py` | Produce this forensic report from summary data |

### Output File Inventory

| File | Description |
|------|-------------|
| `output/wifi_profiles.csv` | Saved WiFi profiles with redacted keys |
| `output/wifi_timeline.csv` | Raw parsed WLAN event log |
| `output/wifi_timeline_cleaned.csv` | Normalized and sorted event timeline |
| `output/wifi_summary.json` | Aggregated statistics and top network counts |
| `output/wifi_timeline_enriched.csv` | Timeline with geolocation metadata merged |
| `output/wifi_activity_timeline.png` | Scatter chart of WiFi activity by SSID |
| `output/wifi_location_map.html` | Interactive folium map of known locations |
| `output/final_report.md` | This forensic report |
"""
    return forensic_report_text.strip()


def main():
    with open(WIFI_SUMMARY_JSON_INPUT_FILE, "r", encoding="utf-8") as summary_json_input_file:
        loaded_wifi_summary_dictionary = json.load(summary_json_input_file)

    complete_forensic_report_text = build_full_forensic_report_text(loaded_wifi_summary_dictionary)

    FORENSIC_REPORT_OUTPUT_FILE.write_text(complete_forensic_report_text, encoding="utf-8")
    print(f"Report saved to {FORENSIC_REPORT_OUTPUT_FILE}")


if __name__ == "__main__":
    main()
