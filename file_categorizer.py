import os
import re
from os import listdir
from sys import argv

# Common categories
CATEGORIES = {
    "Ayudantías": ["ayudantía", "tarea", "ayudantia", "ay"],
    "Clase": ["clase", "clases"],
    "Guias de Ejercicios": ["ejercicio", "quiz", "ejercicios"],
    "Apuntes": ["recursos", "material", "apuntes", "apunte"],
    "Actividades": ["actividad", "actividades"],
    "Talleres": ["taller", "talleres"],
}


def categorize_files(directory):
    if not os.path.exists(directory):
        print("Directory does not exist")
        return

    for filename in listdir(directory):
        file_path = os.path.join(directory, filename)

        # Only process files, skip directories
        if not os.path.isfile(file_path):
            continue

        lower_filename = filename.lower()

        # Check if the file matches any category
        for category, keywords in CATEGORIES.items():
            keyword_list = [
                keyword for keyword in keywords if keyword in lower_filename
            ]

            if keyword_list:
                target_category = category

                # Special logic strictly for the "ay" edge case
                if "ay" in keyword_list and len(keyword_list) == 1:
                    match = re.search(r"ay", lower_filename)
                    if match:
                        index_to_check = match.start() + 2

                        # Ensure we don't go out of bounds before checking isdigit()
                        if (
                            index_to_check < len(lower_filename)
                            and lower_filename[index_to_check].isdigit()
                        ):
                            target_category = "Ayudantías"

                # Move the file to the target category folder
                category_dir = os.path.join(directory, target_category)
                os.makedirs(category_dir, exist_ok=True)
                os.rename(file_path, os.path.join(category_dir, filename))

                break


if __name__ == "__main__":
    if len(argv) < 2:
        print("Usage: python file-categorizer.py <directory>")
    else:
        directory = argv[1]
        categorize_files(directory)
