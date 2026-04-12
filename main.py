import concurrent.futures
import filecmp
import json
import os
from urllib.request import urlretrieve

import requests

CONFIG_FILE = "config.json"

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

API_TOKEN = config.get("api_token")
CANVAS_DOMAIN = config.get("canvas_domain")
CURRENT_TERM_ID = config.get("current_term_id")
BLACKLIST = config.get("course_blacklist", [])
DEFAULT_DOWNLOAD_DIR = config.get("default_download_dir", ".")
CREATE_COURSE_DIR = config.get("create_course_dir", True)
API_URL = f"{CANVAS_DOMAIN}/api/v1/courses"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}


def get_unique_filename(filepath, original_filepath=None, counter=1):
    if not os.path.exists(filepath):
        return filepath
    if original_filepath is None:
        original_filepath = filepath
    filename, extension = os.path.splitext(original_filepath)
    new_filepath = f"{filename} ({counter}){extension}"
    return get_unique_filename(new_filepath, original_filepath, counter + 1)


def process_single_file(file_data, course_code):
    display_name = file_data["display_name"]
    download_url = file_data["url"]
    if not CREATE_COURSE_DIR:
        original_file_path = display_name
    else:
        original_file_path = f"{course_code}/{display_name}"

    try:
        if not os.path.exists(original_file_path):
            urlretrieve(download_url, original_file_path)
            return f"File downloaded: {original_file_path}"

        temp_file_path = f"{original_file_path}.tmp"
        urlretrieve(download_url, temp_file_path)

        if filecmp.cmp(original_file_path, temp_file_path, shallow=False):
            os.remove(temp_file_path)
            return f"Skipped {original_file_path} as an identical file exists"
        else:
            unique_name = get_unique_filename(original_file_path)
            os.rename(temp_file_path, unique_name)
            return f"A file with the same name already exists but its different. Saved as: {unique_name}"

    except Exception as e:
        return f"Failed to process {display_name}: {e}"


# Main execution
print(
    "Welcome to Canvas Downloader!\nBlacklisted courses: " + ", ".join(BLACKLIST) + "\n"
)

if DEFAULT_DOWNLOAD_DIR != "":
    if not os.path.exists(DEFAULT_DOWNLOAD_DIR):
        os.makedirs(DEFAULT_DOWNLOAD_DIR)
    os.chdir(DEFAULT_DOWNLOAD_DIR)
    print(f"Download path: {os.getcwd()}")
else:
    print(f"default_download_dir not set in config, defaulting to path: {os.getcwd()}")

r = requests.get(API_URL, headers=HEADERS)

if r.status_code == 200:
    courses = r.json()

    courses_list = [
        course
        for course in courses
        if course.get("enrollment_term_id") == CURRENT_TERM_ID
        and course.get("course_code") not in BLACKLIST
    ]

    if not courses_list:
        if BLACKLIST:
            print("No courses found. Check your blacklist.")
            exit()
        print("No courses found.")
        exit()

    for course in courses_list:
        files_url = f"{CANVAS_DOMAIN}/api/v1/courses/{course['id']}/files?per_page=100"
        r = requests.get(files_url, headers=HEADERS)

        if r.status_code == 200:
            files = r.json()
            course_code = course["course_code"]
            print(f"\nCurrent course: {course_code} - {course['name']}")

            if CREATE_COURSE_DIR:
                if not os.path.exists(course_code):
                    os.mkdir(course_code)

            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                # Submit all files to the executor
                futures = [
                    executor.submit(process_single_file, file_data, course_code)
                    for file_data in files
                ]

                # Print results as each thread finishes
                for future in concurrent.futures.as_completed(futures):
                    print(future.result())

else:
    print(f"ERROR {r.status_code}, INFO: {r.text}")
    print(
        "Perhaps the API token is invalid or the domain is incorrect. Check your config."
    )
