import pandas as pd
import json
import matplotlib.pyplot as plt
from pathlib import Path

RAW_WIFI_TIMELINE_INPUT_FILE = Path("output/wifi_timeline.csv")
CLEANED_WIFI_TIMELINE_OUTPUT_FILE = Path("output/wifi_timeline_cleaned.csv")
WIFI_ACTIVITY_SUMMARY_OUTPUT_FILE = Path("output/wifi_summary.json")
BSSID_LOCATION_LOOKUP_INPUT_FILE = Path("data/raw/mock_bssid_lookup.csv")
ENRICHED_WIFI_TIMELINE_OUTPUT_FILE = Path("output/wifi_timeline_enriched.csv")
WIFI_ACTIVITY_CHART_OUTPUT_FILE = Path("output/wifi_activity_timeline.png")


def clean_and_normalize_wifi_timeline(raw_timeline_dataframe):
    working_dataframe = raw_timeline_dataframe.copy()

    working_dataframe["timestamp_utc"] = pd.to_datetime(working_dataframe["timestamp_utc"], errors="coerce")
    working_dataframe = working_dataframe.dropna(subset=["timestamp_utc"])
    working_dataframe["ssid"] = working_dataframe["ssid"].fillna("Unknown")
    working_dataframe["bssid"] = working_dataframe["bssid"].fillna("Unknown")
    working_dataframe = working_dataframe.sort_values("timestamp_utc")

    return working_dataframe


def build_wifi_activity_summary_dictionary(cleaned_timeline_dataframe):
    wifi_activity_summary = {
        "total_events": len(cleaned_timeline_dataframe),
        "unique_ssids": int(cleaned_timeline_dataframe["ssid"].nunique()),
        "unique_bssids": int(cleaned_timeline_dataframe["bssid"].nunique()),
        "first_observed": str(cleaned_timeline_dataframe["timestamp_utc"].min()),
        "last_observed": str(cleaned_timeline_dataframe["timestamp_utc"].max()),
        "top_ssids": cleaned_timeline_dataframe["ssid"].value_counts().head(10).to_dict(),
        "top_bssids": cleaned_timeline_dataframe["bssid"].value_counts().head(10).to_dict()
    }
    return wifi_activity_summary


def enrich_timeline_with_bssid_geolocation(cleaned_timeline_dataframe, bssid_location_lookup_dataframe):
    enriched_timeline_dataframe = cleaned_timeline_dataframe.merge(
        bssid_location_lookup_dataframe,
        how="left",
        on=["bssid", "ssid"]
    )
    return enriched_timeline_dataframe


def generate_wifi_activity_scatter_chart(cleaned_timeline_dataframe):
    chart_dataframe = cleaned_timeline_dataframe.copy()
    chart_dataframe = chart_dataframe.dropna(subset=["timestamp_utc"])

    top_ten_ssids_by_frequency = chart_dataframe["ssid"].value_counts().head(10).index
    chart_filtered_dataframe = chart_dataframe[chart_dataframe["ssid"].isin(top_ten_ssids_by_frequency)]

    plt.figure(figsize=(12, 6))

    for individual_ssid_name in top_ten_ssids_by_frequency:
        ssid_specific_events_dataframe = chart_filtered_dataframe[chart_filtered_dataframe["ssid"] == individual_ssid_name]
        plt.scatter(
            ssid_specific_events_dataframe["timestamp_utc"],
            [individual_ssid_name] * len(ssid_specific_events_dataframe),
            label=individual_ssid_name
        )

    plt.xlabel("Timestamp UTC")
    plt.ylabel("SSID")
    plt.title("WiFi Activity Timeline")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(WIFI_ACTIVITY_CHART_OUTPUT_FILE)
    plt.close()

    print(f"Timeline chart saved to {WIFI_ACTIVITY_CHART_OUTPUT_FILE}")


def main():
    raw_wifi_timeline_dataframe = pd.read_csv(RAW_WIFI_TIMELINE_INPUT_FILE)

    cleaned_wifi_timeline_dataframe = clean_and_normalize_wifi_timeline(raw_wifi_timeline_dataframe)
    cleaned_wifi_timeline_dataframe.to_csv(CLEANED_WIFI_TIMELINE_OUTPUT_FILE, index=False)
    print(f"Cleaned timeline saved to {CLEANED_WIFI_TIMELINE_OUTPUT_FILE}")
    print(cleaned_wifi_timeline_dataframe.head(10))

    wifi_summary_dictionary = build_wifi_activity_summary_dictionary(cleaned_wifi_timeline_dataframe)
    with open(WIFI_ACTIVITY_SUMMARY_OUTPUT_FILE, "w", encoding="utf-8") as summary_json_output_file:
        json.dump(wifi_summary_dictionary, summary_json_output_file, indent=4)
    print(f"\nSummary saved to {WIFI_ACTIVITY_SUMMARY_OUTPUT_FILE}")
    print(json.dumps(wifi_summary_dictionary, indent=4))

    if BSSID_LOCATION_LOOKUP_INPUT_FILE.exists():
        bssid_location_lookup_dataframe = pd.read_csv(BSSID_LOCATION_LOOKUP_INPUT_FILE)
        enriched_wifi_timeline_dataframe = enrich_timeline_with_bssid_geolocation(
            cleaned_wifi_timeline_dataframe,
            bssid_location_lookup_dataframe
        )
        enriched_wifi_timeline_dataframe.to_csv(ENRICHED_WIFI_TIMELINE_OUTPUT_FILE, index=False)
        print(f"Enriched timeline saved to {ENRICHED_WIFI_TIMELINE_OUTPUT_FILE}")
    else:
        print(f"No BSSID lookup file found at {BSSID_LOCATION_LOOKUP_INPUT_FILE}. Skipping geolocation enrichment.")

    generate_wifi_activity_scatter_chart(cleaned_wifi_timeline_dataframe)


if __name__ == "__main__":
    main()
