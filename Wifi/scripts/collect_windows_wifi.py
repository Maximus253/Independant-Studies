import subprocess
import re
import csv
from pathlib import Path

WIFI_PROFILES_OUTPUT_FILE = Path("output/wifi_profiles.csv")
WIFI_PROFILES_OUTPUT_FILE.parent.mkdir(exist_ok=True)


def execute_shell_command(shell_command_string):
    shell_command_result = subprocess.run(
        shell_command_string,
        capture_output=True,
        text=True,
        shell=True,
        encoding="utf-8",
        errors="ignore"
    )
    return shell_command_result.stdout


def retrieve_all_saved_wifi_profile_names():
    netsh_profiles_output = execute_shell_command("netsh wlan show profiles")
    extracted_profile_names = re.findall(r"All User Profile\s*:\s*(.*)", netsh_profiles_output)
    return [profile_name.strip() for profile_name in extracted_profile_names]


def retrieve_single_profile_details(wifi_profile_name):
    netsh_detail_command = f'netsh wlan show profile name="{wifi_profile_name}" key=clear'
    netsh_detail_output = execute_shell_command(netsh_detail_command)

    profile_detail_dictionary = {
        "ssid": wifi_profile_name,
        "authentication": None,
        "cipher": None,
        "security_key": None,
        "connection_mode": None
    }

    field_regex_pattern_map = {
        "authentication": r"Authentication\s*:\s*(.*)",
        "cipher": r"Cipher\s*:\s*(.*)",
        "security_key": r"Security key\s*:\s*(.*)",
        "connection_mode": r"Connection mode\s*:\s*(.*)"
    }

    for profile_field_name, regex_pattern_string in field_regex_pattern_map.items():
        regex_match_result = re.search(regex_pattern_string, netsh_detail_output)
        if regex_match_result:
            profile_detail_dictionary[profile_field_name] = regex_match_result.group(1).strip()

    if profile_detail_dictionary.get("security_key") and profile_detail_dictionary["security_key"].lower() not in ("absent", "none", ""):
        profile_detail_dictionary["security_key"] = "[REDACTED]"

    return profile_detail_dictionary


def main():
    all_saved_profile_names = retrieve_all_saved_wifi_profile_names()
    all_profile_detail_rows = [retrieve_single_profile_details(profile_name) for profile_name in all_saved_profile_names]

    with open(WIFI_PROFILES_OUTPUT_FILE, "w", newline="", encoding="utf-8") as csv_output_file:
        csv_column_fieldnames = ["ssid", "authentication", "cipher", "security_key", "connection_mode"]
        csv_dict_writer = csv.DictWriter(csv_output_file, fieldnames=csv_column_fieldnames)
        csv_dict_writer.writeheader()
        csv_dict_writer.writerows(all_profile_detail_rows)

    print(f"Collected {len(all_profile_detail_rows)} WiFi profiles.")
    print(f"Saved results to {WIFI_PROFILES_OUTPUT_FILE}")


if __name__ == "__main__":
    main()
