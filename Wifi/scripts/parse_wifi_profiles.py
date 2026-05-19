import xml.etree.ElementTree as ET
import csv
import re
from pathlib import Path

WLAN_EVENTS_INPUT_FILE = Path("data/raw/wlan_events.xml")
WIFI_TIMELINE_OUTPUT_FILE = Path("output/wifi_timeline.csv")
WIFI_TIMELINE_OUTPUT_FILE.parent.mkdir(exist_ok=True)

WINDOWS_EVENT_XML_NAMESPACE = {"ns": "http://schemas.microsoft.com/win/2004/08/events/event"}


def decode_wlan_xml_file_bytes(xml_file_path):
    raw_file_bytes = xml_file_path.read_bytes()

    if raw_file_bytes[:2] == b"\xff\xfe":
        decoded_content_string = raw_file_bytes.decode("utf-16-le").lstrip("\ufeff")
    elif raw_file_bytes[:2] == b"\xfe\xff":
        decoded_content_string = raw_file_bytes.decode("utf-16-be").lstrip("\ufeff")
    else:
        decoded_content_string = raw_file_bytes.decode("utf-8", errors="ignore").lstrip("\ufeff")

    return decoded_content_string


def load_wlan_xml_root_element(xml_file_path):
    decoded_xml_content_string = decode_wlan_xml_file_bytes(xml_file_path)
    xml_declaration_stripped_string = re.sub(r"<\?xml[^?]*\?>", "", decoded_xml_content_string)
    wrapped_xml_content_string = "<WlanEventRoot>" + xml_declaration_stripped_string + "</WlanEventRoot>"
    return ET.fromstring(wrapped_xml_content_string)


def parse_single_wlan_event_element(wlan_event_element):
    system_element = wlan_event_element.find("ns:System", WINDOWS_EVENT_XML_NAMESPACE)

    extracted_event_id = system_element.find("ns:EventID", WINDOWS_EVENT_XML_NAMESPACE).text
    extracted_system_timestamp = system_element.find("ns:TimeCreated", WINDOWS_EVENT_XML_NAMESPACE).attrib.get("SystemTime")

    event_data_element = wlan_event_element.find("ns:EventData", WINDOWS_EVENT_XML_NAMESPACE)
    event_data_field_dictionary = {}

    if event_data_element is not None:
        for data_child_element in event_data_element.findall("ns:Data", WINDOWS_EVENT_XML_NAMESPACE):
            data_field_name = data_child_element.attrib.get("Name", "unknown")
            event_data_field_dictionary[data_field_name] = data_child_element.text

    parsed_event_record = {
        "timestamp_utc": extracted_system_timestamp,
        "event_id": extracted_event_id,
        "ssid": event_data_field_dictionary.get("SSID"),
        "bssid": event_data_field_dictionary.get("BSSSID") or event_data_field_dictionary.get("BSSID"),
        "interface_guid": event_data_field_dictionary.get("InterfaceGuid"),
        "connection_mode": event_data_field_dictionary.get("ConnectionMode"),
        "reason": event_data_field_dictionary.get("Reason"),
        "raw_fields": str(event_data_field_dictionary)
    }

    return parsed_event_record


def main():
    wlan_xml_root = load_wlan_xml_root_element(WLAN_EVENTS_INPUT_FILE)

    all_wlan_event_elements = wlan_xml_root.findall("ns:Event", WINDOWS_EVENT_XML_NAMESPACE)
    all_parsed_event_rows = [parse_single_wlan_event_element(event_element) for event_element in all_wlan_event_elements]

    with open(WIFI_TIMELINE_OUTPUT_FILE, "w", newline="", encoding="utf-8") as csv_output_file:
        csv_column_fieldnames = [
            "timestamp_utc",
            "event_id",
            "ssid",
            "bssid",
            "interface_guid",
            "connection_mode",
            "reason",
            "raw_fields"
        ]
        csv_dict_writer = csv.DictWriter(csv_output_file, fieldnames=csv_column_fieldnames)
        csv_dict_writer.writeheader()
        csv_dict_writer.writerows(all_parsed_event_rows)

    print(f"Parsed {len(all_parsed_event_rows)} WLAN events.")
    print(f"Saved timeline to {WIFI_TIMELINE_OUTPUT_FILE}")


if __name__ == "__main__":
    main()