import json
import pandas as pd
from pathlib import Path

WIFI_SUMMARY_JSON_INPUT_FILE = Path("output/wifi_summary.json")
WIFI_PROFILES_INPUT_FILE = Path("output/wifi_profiles.csv")
BSSID_ENRICHED_TIMELINE_INPUT_FILE = Path("output/wifi_timeline_enriched_by_bssid.csv")
SSID_ENRICHED_TIMELINE_INPUT_FILE = Path("output/wifi_timeline_enriched_by_ssid.csv")
WIFI_LOCATION_MAP_FILE = Path("output/wifi_location_map.html")
FORENSIC_REPORT_OUTPUT_FILE = Path("output/final_report.md")


def format_dictionary_as_markdown_table(label_value_dictionary):
    if not label_value_dictionary:
        return "_No data available._"
    markdown_table_lines = ["| Name | Count |", "|------|-------|"]
    for entry_label, entry_count in label_value_dictionary.items():
        markdown_table_lines.append(f"| {entry_label} | {entry_count} |")
    return "\n".join(markdown_table_lines)


def format_dataframe_as_markdown_table(input_dataframe, column_list):
    if input_dataframe.empty:
        return "_No data available._"
    filtered_dataframe = input_dataframe[column_list].copy()
    header_row = "| " + " | ".join(column_list) + " |"
    separator_row = "| " + " | ".join(["---"] * len(column_list)) + " |"
    markdown_table_lines = [header_row, separator_row]
    for _, data_row in filtered_dataframe.iterrows():
        row_values = [
            str(data_row[column_name]) if pd.notna(data_row[column_name]) else "Unknown"
            for column_name in column_list
        ]
        markdown_table_lines.append("| " + " | ".join(row_values) + " |")
    return "\n".join(markdown_table_lines)


def load_wifi_profiles_summary(wifi_profiles_file_path):
    if not wifi_profiles_file_path.exists():
        return "_Profile data not available._", 0
    profiles_dataframe = pd.read_csv(wifi_profiles_file_path)
    profile_count = len(profiles_dataframe)
    profiles_markdown_table = format_dataframe_as_markdown_table(
        profiles_dataframe, ["ssid", "authentication", "cipher", "connection_mode"]
    )
    return profiles_markdown_table, profile_count


def load_enriched_location_summary(enriched_timeline_file_path, lookup_method_label):
    if not enriched_timeline_file_path.exists():
        return f"_No {lookup_method_label} enriched data available._", 0
    enriched_dataframe = pd.read_csv(enriched_timeline_file_path)
    located_rows_dataframe = enriched_dataframe.dropna(subset=["latitude", "longitude"])
    located_event_count = len(located_rows_dataframe)
    if located_rows_dataframe.empty:
        return f"_No locations were resolved via {lookup_method_label} lookup._", 0
    unique_located_networks_dataframe = located_rows_dataframe.drop_duplicates(
        subset=["ssid"]
    ).head(20)
    location_markdown_table = format_dataframe_as_markdown_table(
        unique_located_networks_dataframe,
        ["ssid", "bssid", "location_name", "city", "country", "latitude", "longitude"],
    )
    return location_markdown_table, located_event_count


def build_full_forensic_report_text(
    wifi_summary_dictionary,
    profiles_markdown_table,
    profile_count,
    bssid_location_table,
    bssid_located_count,
    ssid_location_table,
    ssid_located_count,
    map_was_generated,
):
    top_ssids_markdown_table = format_dictionary_as_markdown_table(
        wifi_summary_dictionary.get("top_ssids", {})
    )
    top_bssids_markdown_table = format_dictionary_as_markdown_table(
        wifi_summary_dictionary.get("top_bssids", {})
    )

    map_status_string = (
        "An interactive HTML map was successfully generated at `output/wifi_location_map.html`."
        if map_was_generated
        else "No interactive map was generated. Insufficient location data was returned from WiGLE."
    )

    forensic_report_text = f"""# Where Have You Been: Forensics Analysis of WiFi

## Executive Summary

This report presents the results of a forensic analysis of WiFi artifacts collected from an authorized system. The analysis identified {profile_count} saved wireless profiles and {wifi_summary_dictionary["total_events"]} connection events spanning from {wifi_summary_dictionary["first_observed"]} to {wifi_summary_dictionary["last_observed"]}. Geolocation enrichment was performed via the WiGLE API using both BSSID and SSID lookup methods, resolving {bssid_located_count} events by BSSID and {ssid_located_count} events by SSID. All evidence was collected from a personally owned or lab-controlled system with explicit authorization.

---

## Scope and Authorization

This analysis was conducted exclusively on an authorized system. The examiner had explicit permission to collect and analyze WiFi artifacts from the target device. No passwords or private credentials were retained in this report. All security key values were redacted prior to storage. No unauthorized network access, third-party packet capture, or private data collection was performed.

---

## Evidence Sources

- Saved WiFi profiles extracted using `netsh wlan show profiles` (Windows)
- Windows WLAN AutoConfig event logs exported via `wevtutil` from `Microsoft-Windows-WLAN-AutoConfig/Operational`
- WiGLE API geolocation lookups performed by BSSID and SSID

---

## Tools Used

| Tool | Purpose |
|------|---------|
| Python 3 | Script development and data processing |
| `subprocess` / `netsh` | WiFi profile extraction on Windows |
| `wevtutil` | WLAN AutoConfig event log export |
| `xml.etree.ElementTree` | Parsing WLAN AutoConfig XML event logs |
| `pandas` | Data cleaning, normalization, and analysis |
| `matplotlib` | WiFi activity timeline visualization |
| `folium` | Interactive HTML geolocation map |
| `requests` | WiGLE API geolocation queries |
| `json` | Summary data storage and report generation |

---

## Methodology

1. The Windows WLAN AutoConfig event log was exported automatically to `data/raw/wlan_events.xml` using `wevtutil`.
2. Saved WiFi profiles were extracted using the Windows `netsh` utility. Security keys were redacted and results written to `output/wifi_profiles.csv`.
3. The raw event log XML was decoded from UTF-16 LE, stripped of XML declarations, wrapped in a root element, and parsed to extract timestamps, event IDs, SSIDs, BSSIDs, and connection metadata. Results written to `output/wifi_timeline.csv`.
4. The raw timeline was cleaned: records with invalid timestamps were dropped, missing SSIDs and BSSIDs were labeled as "Unknown," and all events were sorted chronologically. Results written to `output/wifi_timeline_cleaned.csv`.
5. A summary JSON was produced identifying unique network counts, frequency rankings, and the observed date range. Saved to `output/wifi_summary.json`.
6. A scatter chart was generated plotting WiFi activity over time by SSID. Saved to `output/wifi_activity_timeline.png`.
7. Geolocation enrichment was performed via the WiGLE API in two passes — one lookup by BSSID and one by SSID — with results saved to separate enriched CSV files.
8. An interactive HTML map was generated from the enriched data with the most resolved locations.

---

## Summary of Findings

| Metric | Value |
|--------|-------|
| Total WiFi events analyzed | {wifi_summary_dictionary["total_events"]} |
| Unique SSIDs observed | {wifi_summary_dictionary["unique_ssids"]} |
| Unique BSSIDs observed | {wifi_summary_dictionary["unique_bssids"]} |
| First observed event | {wifi_summary_dictionary["first_observed"]} |
| Last observed event | {wifi_summary_dictionary["last_observed"]} |
| Saved WiFi profiles collected | {profile_count} |
| Events located via BSSID lookup | {bssid_located_count} |
| Events located via SSID lookup | {ssid_located_count} |

---

## Saved WiFi Profiles

The following networks are saved on the device and configured for automatic or manual connection:

{profiles_markdown_table}

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

## Location Analysis — BSSID Lookup

BSSID lookup queries WiGLE using the hardware address of the access point. This is the most precise geolocation method as BSSIDs are tied to a specific physical device. {bssid_located_count} events were resolved to approximate locations.

{bssid_location_table}

See `output/wifi_timeline_enriched_by_bssid.csv` for the full BSSID enriched timeline.

---

## Location Analysis — SSID Lookup

SSID lookup queries WiGLE using the network name. This method is less precise as the same SSID name may exist in multiple locations, but serves as a useful fallback when BSSIDs are unavailable. {ssid_located_count} events were resolved to approximate locations.

{ssid_location_table}

See `output/wifi_timeline_enriched_by_ssid.csv` for the full SSID enriched timeline.

---

## Map

{map_status_string}

---

## Limitations

- WiFi artifacts can suggest prior locations but do not independently prove that a specific person was physically present at a location.
- SSIDs are not unique identifiers. The same SSID name may be used by many different access points across different locations, making SSID-based geolocation inherently imprecise.
- Access points may have been relocated since their BSSID was registered in the WiGLE database.
- WLAN AutoConfig event logs may be incomplete, cleared, or subject to log rotation policies on the examined system.
- System timestamps must be validated against known-good time sources. Clock skew or deliberate manipulation could affect timeline accuracy.
- BSSID geolocation data from WiGLE may be stale, inaccurate, or entirely absent for a given access point.
- The presence of a saved WiFi profile does not confirm that a connection was ever successfully established.
- All BSSIDs on this device were logged as Unknown by the event log, meaning BSSID-based geolocation was not possible and SSID lookup was the primary enrichment method.

---

## Conclusion

The WiFi artifacts analyzed in this report provided useful evidence for reconstructing network connection activity and possible location history. The device was observed connecting to {wifi_summary_dictionary["unique_ssids"]} unique networks between {wifi_summary_dictionary["first_observed"]} and {wifi_summary_dictionary["last_observed"]}. Repeated connections to specific SSIDs suggest consistent patterns of device presence at identifiable locations. However, definitive conclusions about physical location require correlation with additional artifact sources.

Stronger conclusions would require corroborating evidence such as browser history, file access timestamps, GPS or cellular location data, login records, photographs with embedded metadata, cloud synchronization logs, or mobile device artifacts.

---

## Appendix

### Script Inventory

| Script | Purpose |
|--------|---------|
| `run_all.py` | Runs all scripts in order from project root |
| `scripts/collect_windows_wifi.py` | Export WLAN event log and extract saved WiFi profiles |
| `scripts/parse_wifi_profiles.py` | Parse WLAN AutoConfig XML event logs |
| `scripts/analyze_wifi_history.py` | Clean, summarize, enrich, and chart WiFi data |
| `scripts/generate_map.py` | Query WiGLE and generate interactive HTML map |
| `scripts/generate_report.py` | Produce this forensic report from all output data |

### Output File Inventory

| File | Description |
|------|-------------|
| `data/raw/wlan_events.xml` | Raw exported WLAN AutoConfig event log |
| `output/wifi_profiles.csv` | Saved WiFi profiles with redacted keys |
| `output/wifi_timeline.csv` | Raw parsed WLAN event log |
| `output/wifi_timeline_cleaned.csv` | Normalized and sorted event timeline |
| `output/wifi_summary.json` | Aggregated statistics and top network counts |
| `output/wifi_activity_timeline.png` | Scatter chart of WiFi activity by SSID |
| `output/wifi_timeline_enriched_by_bssid.csv` | Timeline enriched with WiGLE BSSID locations |
| `output/wifi_timeline_enriched_by_ssid.csv` | Timeline enriched with WiGLE SSID locations |
| `output/wifi_location_map.html` | Interactive folium map of located events |
| `output/final_report.md` | This forensic report |
"""
    return forensic_report_text.strip()


def main():
    with open(
        WIFI_SUMMARY_JSON_INPUT_FILE, "r", encoding="utf-8"
    ) as summary_json_input_file:
        loaded_wifi_summary_dictionary = json.load(summary_json_input_file)

    profiles_markdown_table, profile_count = load_wifi_profiles_summary(
        WIFI_PROFILES_INPUT_FILE
    )

    bssid_location_table, bssid_located_count = load_enriched_location_summary(
        BSSID_ENRICHED_TIMELINE_INPUT_FILE, "BSSID"
    )
    ssid_location_table, ssid_located_count = load_enriched_location_summary(
        SSID_ENRICHED_TIMELINE_INPUT_FILE, "SSID"
    )

    map_was_generated = WIFI_LOCATION_MAP_FILE.exists()

    complete_forensic_report_text = build_full_forensic_report_text(
        loaded_wifi_summary_dictionary,
        profiles_markdown_table,
        profile_count,
        bssid_location_table,
        bssid_located_count,
        ssid_location_table,
        ssid_located_count,
        map_was_generated,
    )

    FORENSIC_REPORT_OUTPUT_FILE.write_text(
        complete_forensic_report_text, encoding="utf-8"
    )
    print(f"Report saved to {FORENSIC_REPORT_OUTPUT_FILE}")


if __name__ == "__main__":
    main()
