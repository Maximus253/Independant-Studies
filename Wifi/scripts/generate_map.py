import pandas as pd
import folium
import requests
import time
from pathlib import Path

WIGLE_API_ENCODED_TOKEN = "QUlEZTcwY2I4ZDk3YzI0MDgwOTlhOTUzYzc3ZjA5NmYxMDE6MWY1MzUxMDE3NTc3ZjExNWNiMmEwNmY2Y2NhYzZkM2M"

CLEANED_WIFI_TIMELINE_INPUT_FILE = Path("output/wifi_timeline_cleaned.csv")
BSSID_ENRICHED_TIMELINE_OUTPUT_FILE = Path("output/wifi_timeline_enriched_by_bssid.csv")
SSID_ENRICHED_TIMELINE_OUTPUT_FILE = Path("output/wifi_timeline_enriched_by_ssid.csv")
WIFI_LOCATION_MAP_OUTPUT_FILE = Path("output/wifi_location_map.html")

WIGLE_API_NETWORK_SEARCH_URL = "https://api.wigle.net/api/v2/network/search"
WIGLE_REQUEST_DELAY_SECONDS = 1.5


def build_wigle_request_headers():
    return {"Authorization": f"Basic {WIGLE_API_ENCODED_TOKEN}"}


def query_wigle_by_bssid(bssid_string):
    if not bssid_string or bssid_string == "Unknown":
        return None

    wigle_query_parameters = {"netid": bssid_string, "resultsPerPage": 1}

    try:
        wigle_api_response = requests.get(
            WIGLE_API_NETWORK_SEARCH_URL,
            headers=build_wigle_request_headers(),
            params=wigle_query_parameters,
            timeout=10,
        )

        if wigle_api_response.status_code != 200:
            print(
                f"  [WARN] WiGLE BSSID lookup returned status {wigle_api_response.status_code} for {bssid_string}"
            )
            return None

        wigle_result_list = wigle_api_response.json().get("results", [])
        if not wigle_result_list:
            return None

        first_result = wigle_result_list[0]
        return {
            "latitude": first_result.get("trilat"),
            "longitude": first_result.get("trilong"),
            "location_name": first_result.get("ssid", "Unknown"),
            "city": first_result.get("city", "Unknown"),
            "country": first_result.get("country", "Unknown"),
            "lookup_method": "bssid",
        }

    except requests.RequestException as wigle_request_exception:
        print(
            f"  [ERROR] BSSID request failed for {bssid_string}: {wigle_request_exception}"
        )
        return None


def query_wigle_by_ssid(ssid_string):
    if not ssid_string or ssid_string == "Unknown":
        return None

    wigle_query_parameters = {"ssid": ssid_string, "resultsPerPage": 1}

    try:
        wigle_api_response = requests.get(
            WIGLE_API_NETWORK_SEARCH_URL,
            headers=build_wigle_request_headers(),
            params=wigle_query_parameters,
            timeout=10,
        )

        if wigle_api_response.status_code != 200:
            print(
                f"  [WARN] WiGLE SSID lookup returned status {wigle_api_response.status_code} for {ssid_string}"
            )
            return None

        wigle_result_list = wigle_api_response.json().get("results", [])
        if not wigle_result_list:
            return None

        first_result = wigle_result_list[0]
        return {
            "latitude": first_result.get("trilat"),
            "longitude": first_result.get("trilong"),
            "location_name": first_result.get("ssid", "Unknown"),
            "city": first_result.get("city", "Unknown"),
            "country": first_result.get("country", "Unknown"),
            "lookup_method": "ssid",
        }

    except requests.RequestException as wigle_request_exception:
        print(
            f"  [ERROR] SSID request failed for {ssid_string}: {wigle_request_exception}"
        )
        return None


def build_enriched_dataframe_from_lookup_cache(
    timeline_dataframe, lookup_cache_dictionary, lookup_key_column_name
):
    latitude_values = []
    longitude_values = []
    location_name_values = []
    city_values = []
    country_values = []
    lookup_method_values = []

    for _, timeline_row in timeline_dataframe.iterrows():
        cached_location = lookup_cache_dictionary.get(
            timeline_row[lookup_key_column_name]
        )
        if cached_location:
            latitude_values.append(cached_location["latitude"])
            longitude_values.append(cached_location["longitude"])
            location_name_values.append(cached_location["location_name"])
            city_values.append(cached_location["city"])
            country_values.append(cached_location["country"])
            lookup_method_values.append(cached_location["lookup_method"])
        else:
            latitude_values.append(None)
            longitude_values.append(None)
            location_name_values.append(None)
            city_values.append(None)
            country_values.append(None)
            lookup_method_values.append(None)

    enriched_dataframe = timeline_dataframe.copy()
    enriched_dataframe["latitude"] = latitude_values
    enriched_dataframe["longitude"] = longitude_values
    enriched_dataframe["location_name"] = location_name_values
    enriched_dataframe["city"] = city_values
    enriched_dataframe["country"] = country_values
    enriched_dataframe["lookup_method"] = lookup_method_values

    return enriched_dataframe


def enrich_by_bssid(timeline_dataframe):
    unique_bssid_list = [
        bssid
        for bssid in timeline_dataframe["bssid"].unique()
        if bssid and bssid != "Unknown"
    ]

    print(f"\nLooking up {len(unique_bssid_list)} unique BSSIDs via WiGLE...")

    bssid_location_cache = {}
    for bssid_value in unique_bssid_list:
        print(f"  Querying BSSID: {bssid_value}")
        bssid_location_cache[bssid_value] = query_wigle_by_bssid(bssid_value)
        time.sleep(WIGLE_REQUEST_DELAY_SECONDS)

    return build_enriched_dataframe_from_lookup_cache(
        timeline_dataframe, bssid_location_cache, "bssid"
    )


def enrich_by_ssid(timeline_dataframe):
    unique_ssid_list = [
        ssid
        for ssid in timeline_dataframe["ssid"].unique()
        if ssid and ssid != "Unknown"
    ]

    print(f"\nLooking up {len(unique_ssid_list)} unique SSIDs via WiGLE...")

    ssid_location_cache = {}
    for ssid_value in unique_ssid_list:
        print(f"  Querying SSID: {ssid_value}")
        ssid_location_cache[ssid_value] = query_wigle_by_ssid(ssid_value)
        time.sleep(WIGLE_REQUEST_DELAY_SECONDS)

    return build_enriched_dataframe_from_lookup_cache(
        timeline_dataframe, ssid_location_cache, "ssid"
    )


def build_popup_html_text(dataframe_row):
    return (
        f"SSID: {dataframe_row.get('ssid', 'Unknown')}<br>"
        f"BSSID: {dataframe_row.get('bssid', 'Unknown')}<br>"
        f"Location: {dataframe_row.get('location_name', 'Unknown')}<br>"
        f"City: {dataframe_row.get('city', 'Unknown')}<br>"
        f"Lookup Method: {dataframe_row.get('lookup_method', 'Unknown')}<br>"
        f"Time: {dataframe_row.get('timestamp_utc', 'Unknown')}"
    )


def generate_folium_map(enriched_dataframe, map_title_string):
    location_valid_rows = enriched_dataframe.dropna(subset=["latitude", "longitude"])

    if location_valid_rows.empty:
        print(f"  No location data available for {map_title_string} map.")
        return None

    wifi_folium_map = folium.Map(
        location=[
            location_valid_rows["latitude"].iloc[0],
            location_valid_rows["longitude"].iloc[0],
        ],
        zoom_start=12,
    )

    for _, enriched_event_row in location_valid_rows.iterrows():
        folium.Marker(
            location=[enriched_event_row["latitude"], enriched_event_row["longitude"]],
            popup=build_popup_html_text(enriched_event_row),
        ).add_to(wifi_folium_map)

    return wifi_folium_map


def main():
    cleaned_timeline_dataframe = pd.read_csv(CLEANED_WIFI_TIMELINE_INPUT_FILE)

    bssid_enriched_dataframe = enrich_by_bssid(cleaned_timeline_dataframe)
    bssid_enriched_dataframe.to_csv(BSSID_ENRICHED_TIMELINE_OUTPUT_FILE, index=False)
    print(f"BSSID enriched timeline saved to {BSSID_ENRICHED_TIMELINE_OUTPUT_FILE}")

    ssid_enriched_dataframe = enrich_by_ssid(cleaned_timeline_dataframe)
    ssid_enriched_dataframe.to_csv(SSID_ENRICHED_TIMELINE_OUTPUT_FILE, index=False)
    print(f"SSID enriched timeline saved to {SSID_ENRICHED_TIMELINE_OUTPUT_FILE}")

    bssid_valid_count = bssid_enriched_dataframe.dropna(
        subset=["latitude", "longitude"]
    ).shape[0]
    ssid_valid_count = ssid_enriched_dataframe.dropna(
        subset=["latitude", "longitude"]
    ).shape[0]

    print(f"\nBSSID lookup produced {bssid_valid_count} located events.")
    print(f"SSID lookup produced {ssid_valid_count} located events.")

    best_enriched_dataframe = (
        ssid_enriched_dataframe
        if ssid_valid_count >= bssid_valid_count
        else bssid_enriched_dataframe
    )
    best_method_label = "SSID" if ssid_valid_count >= bssid_valid_count else "BSSID"

    print(
        f"\nGenerating map using {best_method_label} results (most locations found)..."
    )

    wifi_folium_map = generate_folium_map(best_enriched_dataframe, best_method_label)

    if wifi_folium_map:
        wifi_folium_map.save(WIFI_LOCATION_MAP_OUTPUT_FILE)
        print(f"Map saved to {WIFI_LOCATION_MAP_OUTPUT_FILE}")
    else:
        print(
            "No location data found from either BSSID or SSID lookups. Map not generated."
        )


if __name__ == "__main__":
    main()
