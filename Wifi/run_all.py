import subprocess
import sys
from pathlib import Path

PROJECT_ROOT_DIRECTORY_PATH = Path(__file__).parent
SCRIPTS_DIRECTORY_PATH = PROJECT_ROOT_DIRECTORY_PATH / "scripts"

ORDERED_SCRIPT_EXECUTION_LIST = [
    (
        "Collect Windows WiFi Profiles",
        SCRIPTS_DIRECTORY_PATH / "collect_windows_wifi.py",
    ),
    (
        "Parse WLAN Event Log XML",
        SCRIPTS_DIRECTORY_PATH / "parse_wifi_profiles.py",
    ),
    (
        "Analyze Wifi History",
        SCRIPTS_DIRECTORY_PATH / "analyze_wifi_history.py",
    ),
    ("Generate Map", SCRIPTS_DIRECTORY_PATH / "generate_map.py"),
    (
        "Generate Report",
        SCRIPTS_DIRECTORY_PATH / "generate_report.py",
    ),
]


def run_single_script(step_label_string, script_file_path):
    print(f"\n{'='*60}")
    print(f"  {step_label_string}")
    print(f"  Running: {script_file_path}")
    print(f"{'='*60}")
    script_process_result = subprocess.run(
        [sys.executable, str(script_file_path)],
        cwd=PROJECT_ROOT_DIRECTORY_PATH,
        capture_output=False,
    )
    if script_process_result.returncode != 0:
        print(
            f"\n[ERROR] {step_label_string} failed with exit code {script_process_result.returncode}."
        )
        print("Halting execution. Fix the error above before continuing.")
        sys.exit(script_process_result.returncode)
    print(f"\n[OK] {step_label_string} completed successfully.")


def main():
    print("\n" + "=" * 60)
    print("  WiFi Analysis")
    print("=" * 60)
    print("Running all scripts in order...\n")
    for step_label_string, script_file_path in ORDERED_SCRIPT_EXECUTION_LIST:
        run_single_script(step_label_string, script_file_path)
    print(f"\n{'='*60}")
    print("  All steps completed.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
