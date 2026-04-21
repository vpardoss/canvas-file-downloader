import os
import argparse

import concurrent.futures # threads
import filecmp
import json

from urllib.request import urlretrieve
import requests

parse = argparse.ArgumentParser()
parse.add_argument("--api-token",
                   metavar='API_TOKEN (str)', help='your CANVAS TOKEN', type=str, nargs=1, required=False)
parse.add_argument("--terms-id",
                   metavar='COURSE_CODE (int)', help='course code', type=int, nargs='+', required=False)
parse.add_argument("--course-whitelist",
                   metavar='Courses (str)', help='Courses to download, if empty will download all but blacklisted',
                   type=str, nargs='+', required=False)
parse.add_argument("--course-blacklist",
                   metavar='Courses (str)',
                   help='Courses to not download if whitelist is empty, else download all but blacklisted',
                   type=str, nargs='+', required=False)
parse.add_argument("--extension-whitelist",
                   metavar='File extensions (str)', help='Extensions to download, if empty will download all but blacklisted',
                   type=str, nargs='+', required=False)
parse.add_argument("--extension-blacklist",
                   metavar='File extensions (str)',
                   help='Extension to not download if whitelist is empty, else download all but blacklisted',
                   type=str, nargs='+', required=False)

CONFIG_FILE = "config.json"

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

API_TOKEN = config.get("api_token")
CANVAS_DOMAIN = config.get("canvas_domain")
TERMS_ID = config.get("download_terms_ids", [])
COURSE_WHITELIST = config.get("course_whitelist")
if len(COURSE_WHITELIST) != 0:
    COURSE_BLACKLIST = []
else:
    COURSE_BLACKLIST = config.get("course_blacklist", [])

EXTENSION_WHITELIST = config.get("extension_whitelist")
if len(EXTENSION_WHITELIST) != 0:
    EXTENSION_BLACKLIST = []
else:
    EXTENSION_BLACKLIST = config.get("extension_blacklist", [])

DEFAULT_DOWNLOAD_DIR = config.get("default_download_dir", ".")
CREATE_COURSE_DIR = config.get("create_course_dir", True)
API_URL = f"{CANVAS_DOMAIN}/api/v1/courses"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

args = parse.parse_args()
if args.api_token:
    API_TOKEN = args.api_token
if args.terms_id:
    TERMS_ID = args.terms_id[0]
if args.course_whitelist:
    COURSE_WHITELIST = args.course_whitelist
    COURSE_BLACKLIST = []
elif args.course_blacklist:
    COURSE_BLACKLIST = args.course_blacklist

if args.extension_whitelist:
    EXTENSION_WHITELIST = args.extension_whitelist
    EXTENSION_BLACKLIST = []
elif args.extension_blacklist:
    EXTENSION_BLACKLIST = args.extension_blacklist


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


def change_terminal_dir():
    if DEFAULT_DOWNLOAD_DIR != "":
        if not os.path.exists(DEFAULT_DOWNLOAD_DIR):
            os.makedirs(DEFAULT_DOWNLOAD_DIR)
        os.chdir(DEFAULT_DOWNLOAD_DIR)
        print(f"Download path: {os.getcwd()}")
    else:
        print(f"default_download_dir not set in config, defaulting to path: {os.getcwd()}")


def connect_to_api(get_from_request="COURSES", COURSE_LIST=None):
    if get_from_request == "COURSES":
        r = requests.get(API_URL, headers=HEADERS)

        if r.status_code == 200:
            courses = r.json()

            if TERMS_ID is not None:
                COURSE_LIST = [course for course in courses if course["enrollment_term_id"] in TERMS_ID]

            if COURSE_WHITELIST is None:
                COURSE_LIST = [course for course in COURSE_LIST if course["course_code"] not in COURSE_BLACKLIST]
            else:
                COURSE_LIST = [course for course in COURSE_LIST if course["course_code"] in COURSE_WHITELIST]

            COURSE_LIST = [course for course in COURSE_LIST if (
                    COURSE_WHITELIST is not None and course.get("course_code") in COURSE_WHITELIST
                    or course["course_code"] not in COURSE_BLACKLIST
            )]

            if not COURSE_LIST:
                if COURSE_BLACKLIST:
                    print("No courses found. Check your blacklist.")
                    exit()
                print("No courses found.")
                exit()

            return COURSE_LIST

        else:
            print(f"ERROR {r.status_code}, INFO: {r.text}")
            print(
                "Perhaps the API token is invalid or the domain is incorrect. Check your config."
            )
            exit()

    if get_from_request == "FILES":
        for course in COURSE_LIST:
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
                print("IDK bro, something went wrong idk what tho")


# Main execution

if __name__ == "__main__":
    print(
        "Welcome to Canvas Downloader!\nCourses to download: "
    )

    courses = connect_to_api("COURSES")
    connect_to_api("FILES", courses)

# TO DO: Add canvas files from subfolders recursively
# TO DO: Do the extensions part
# OPTIONAL: Chrome extension