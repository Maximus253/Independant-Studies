# Where Have You Been: Forensics Analysis of WiFi

## Executive Summary

This report presents the results of a forensic analysis of WiFi artifacts collected from an authorized system. The analysis identified 3 saved wireless profiles and 55 connection events spanning from 2026-05-23 15:37:25.067390900+00:00 to 2026-05-25 03:09:52.037953600+00:00. Geolocation enrichment was performed via the WiGLE API using both BSSID and SSID lookup methods, resolving 0 events by BSSID and 55 events by SSID. All evidence was collected from a personally owned or lab-controlled system with explicit authorization.

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
| Total WiFi events analyzed | 55 |
| Unique SSIDs observed | 3 |
| Unique BSSIDs observed | 1 |
| First observed event | 2026-05-23 15:37:25.067390900+00:00 |
| Last observed event | 2026-05-25 03:09:52.037953600+00:00 |
| Saved WiFi profiles collected | 3 |
| Events located via BSSID lookup | 0 |
| Events located via SSID lookup | 55 |

---

## Saved WiFi Profiles

The following networks are saved on the device and configured for automatic or manual connection:

| ssid | authentication | cipher | connection_mode |
| --- | --- | --- | --- |
| Dolphin-284 | WPA3-Personal | GCMP-256 | Connect automatically |
| Airport Public Wi-Fi | Open | Unknown | Connect manually |
| Jones Home | WPA3-Personal | GCMP-256 | Connect automatically |

---

## Most Frequently Observed SSIDs

| Name | Count |
|------|-------|
| Jones Home | 41 |
| Airport Public Wi-Fi | 8 |
| Dolphin-284 | 6 |

---

## Most Frequently Observed BSSIDs

| Name | Count |
|------|-------|
| Unknown | 55 |

---

## Timeline of WiFi Activity

See `output/wifi_timeline_cleaned.csv` for the full chronological event log. See `output/wifi_activity_timeline.png` for the visual scatter chart of activity by SSID over time.

---

## Location Analysis — BSSID Lookup

BSSID lookup queries WiGLE using the hardware address of the access point. This is the most precise geolocation method as BSSIDs are tied to a specific physical device. 0 events were resolved to approximate locations.

_No locations were resolved via BSSID lookup._

See `output/wifi_timeline_enriched_by_bssid.csv` for the full BSSID enriched timeline.

---

## Location Analysis — SSID Lookup

SSID lookup queries WiGLE using the network name. This method is less precise as the same SSID name may exist in multiple locations, but serves as a useful fallback when BSSIDs are unavailable. 55 events were resolved to approximate locations.

| ssid | bssid | location_name | city | country | latitude | longitude |
| --- | --- | --- | --- | --- | --- | --- |
| Jones Home | Unknown | Jones home | Unknown | US | 40.54536819 | -112.3042984 |
| Airport Public Wi-Fi | Unknown | Airport Public Wi-Fi | Wichita | US | 37.65417862 | -97.43006134 |
| Dolphin-284 | Unknown | Dolphin-284 | Unknown | US | 20.97034264 | -156.68003845 |

See `output/wifi_timeline_enriched_by_ssid.csv` for the full SSID enriched timeline.

---

## Map

An interactive HTML map was successfully generated at `output/wifi_location_map.html`.

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

The WiFi artifacts analyzed in this report provided useful evidence for reconstructing network connection activity and possible location history. The device was observed connecting to 3 unique networks between 2026-05-23 15:37:25.067390900+00:00 and 2026-05-25 03:09:52.037953600+00:00. Repeated connections to specific SSIDs suggest consistent patterns of device presence at identifiable locations. However, definitive conclusions about physical location require correlation with additional artifact sources.

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