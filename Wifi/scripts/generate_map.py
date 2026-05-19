import pandas as pd
import folium
from pathlib import Path

ENRICHED_WIFI_TIMELINE_INPUT_FILE = Path("output/wifi_timeline_enriched.csv")
WIFI_LOCATION_MAP_OUTPUT_FILE = Path("output/wifi_location_map.html")


def build_popup_html_text(dataframe_row):
    popup_html_string = (
        f"SSID: {dataframe_row.get('ssid', 'Unknown')}<br>"
        f"BSSID: {dataframe_row.get('bssid', 'Unknown')}<br>"
        f"Location: {dataframe_row.get('location_name', 'Unknown')}<br>"
        f"Time: {dataframe_row.get('timestamp_utc', 'Unknown')}"
    )
    return popup_html_string


def main():
    enriched_timeline_dataframe = pd.read_csv(ENRICHED_WIFI_TIMELINE_INPUT_FILE)
    location_valid_rows_dataframe = enriched_timeline_dataframe.dropna(subset=["latitude", "longitude"])

    if location_valid_rows_dataframe.empty:
        print("No location data available. Cannot generate map.")
        return

    map_starting_latitude = location_valid_rows_dataframe["latitude"].iloc[0]
    map_starting_longitude = location_valid_rows_dataframe["longitude"].iloc[0]

    wifi_folium_map = folium.Map(location=[map_starting_latitude, map_starting_longitude], zoom_start=12)

    for _, enriched_event_row in location_valid_rows_dataframe.iterrows():
        marker_popup_html = build_popup_html_text(enriched_event_row)
        folium.Marker(
            location=[enriched_event_row["latitude"], enriched_event_row["longitude"]],
            popup=marker_popup_html
        ).add_to(wifi_folium_map)

    wifi_folium_map.save(WIFI_LOCATION_MAP_OUTPUT_FILE)
    print(f"Map saved to {WIFI_LOCATION_MAP_OUTPUT_FILE}")


if __name__ == "__main__":
    main()
