import bs4
import patoolib
import requests
import os
import platform
import shutil
import sys

SDK_BASE_URL = "https://bearware.dk/teamtalksdk"
TARGET_FOLDER_NAME = "TeamTalk_DLL"
TEMP_DIR = "ttsdk_temp"
DOWNLOAD_FILE = "ttsdk.7z"

def get_url_suffix_from_platform() -> str:
    machine = platform.machine()
    if sys.platform == "win32":
        architecture = platform.architecture()
        if machine == "AMD64" or machine == "x86":
            if architecture[0] == "64bit":
                return "win64"
            else:
                return "win32"
        else:
            sys.exit("Native Windows on ARM is not supported")
    elif sys.platform == "darwin":
        sys.exit("Darwin is not supported")
    else:
        if machine == "AMD64" or machine == "x86_64":
            return "ubuntu22_x86_64"
        elif "arm" in machine:
            return "raspbian_armhf"
        else:
            sys.exit("Your architecture is not supported")


def download_file_from_url(url: str, file_path: str) -> None:
    """Downloads a file from a URL."""
    print(f"Downloading from {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(file_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        print("Download complete.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the file: {e}", file=sys.stderr)
        sys.exit(1)


def do_download_and_extract() -> None:
    """Handles the entire process of downloading and extracting the SDK."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        print(f"Fetching available SDK versions from {SDK_BASE_URL}...")
        r = requests.get(SDK_BASE_URL, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to access the TeamTalk SDK page: {e}", file=sys.stderr)
        sys.exit(1)

    page = bs4.BeautifulSoup(r.text, features="html.parser")
    try:
        versions = page.find_all("li")
        version_link = [i for i in versions if "5.15" in i.text][-1].a
        version = version_link.get("href").strip('/')
    except (AttributeError, IndexError):
        print("Could not find a suitable SDK version (5.15x) on the page.", file=sys.stderr)
        sys.exit(1)

    download_url = f"{SDK_BASE_URL}/{version}/tt5sdk_{version}_{get_url_suffix_from_platform()}.7z"

    download_file_from_url(download_url, DOWNLOAD_FILE)

    print(f"Extracting {DOWNLOAD_FILE}...")
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)

    try:
        patoolib.extract_archive(DOWNLOAD_FILE, outdir=TEMP_DIR, verbosity=-1)
        print("Extraction complete.")
    except Exception as e:
        print(f"Failed to extract archive: {e}", file=sys.stderr)
        print("Please ensure 7-Zip is installed and accessible in your system's PATH.", file=sys.stderr)
        shutil.rmtree(TEMP_DIR)
        os.remove(DOWNLOAD_FILE)
        sys.exit(1)

    print(f"Moving '{TARGET_FOLDER_NAME}' folder...")
    extracted_subfolder = os.path.join(TEMP_DIR, os.listdir(TEMP_DIR)[0])
    source_path = os.path.join(extracted_subfolder, "Library", TARGET_FOLDER_NAME)

    if os.path.exists(TARGET_FOLDER_NAME):
        shutil.rmtree(TARGET_FOLDER_NAME)

    shutil.move(source_path, ".")
    print("Move complete.")

    print("Cleaning up temporary files...")
    os.remove(DOWNLOAD_FILE)
    shutil.rmtree(TEMP_DIR)
    print("Cleanup complete.")


def main():
    """Main script execution."""
    print("--- TeamTalk SDK Setup ---")

    if os.path.exists(TARGET_FOLDER_NAME):
        while True:
            response = input(f"The folder '{TARGET_FOLDER_NAME}' already exists. "
                             f"Would you like to replace it? [y/n]: ").lower().strip()
            if response in ['y', 'yes']:
                print(f"Proceeding with re-download. The existing folder will be replaced.")
                do_download_and_extract()
                break
            elif response in ['n', 'no']:
                print("Skipping TeamTalk SDK download as requested.")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
    else:
        do_download_and_extract()

    print("--- TeamTalk SDK Setup Finished ---")


if __name__ == "__main__":
    try:
        import requests
        import bs4
        import patoolib
    except ImportError as e:
        print(f"Missing required Python package: {e.name}", file=sys.stderr)
        print("Please install it by running: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)

    main()
