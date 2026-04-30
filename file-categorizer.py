import os
import re
from os import listdir
from sys import argv

# Common categories
CATEGORIES = {
    "Ayudantias": ["ayudantía", "tarea", "ayudantia", "ay"],
    "Clase": ["clase", "clases"],
    "Guias de Ejercicios": ["ejercicio", "quiz", "ejercicios"],
    "Apuntes": ["recursos", "material", "apuntes", "apunte"],
    "Actividades": ["actividad", "actividades"],
}


def categorize_files(directory):
    if not os.path.exists(directory):
        return "Directory does not exist"

    for filename in listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            # Check if the file matches any category
            for category, keywords in CATEGORIES.items():
                keyword_list = [
                    keyword for keyword in keywords if keyword in filename.lower()
                ]
                if keyword_list:
                    if "ay" in keyword_list:
                        match = re.search(r"ay", filename.lower())
                        index_to_check = match.start() + 2
                        if filename.lower()[index_to_check].isnumeric():
                            category = "Ayudantías"
                        else:
                            category = "Extras"

                    # Move the file to the category folder
                    category_dir = os.path.join(directory, category)
                    os.makedirs(category_dir, exist_ok=True)
                    os.rename(file_path, os.path.join(category_dir, filename))

                else:
                    category = "Extras"
                    category_dir = os.path.join(directory, category)
                    os.makedirs(category_dir, exist_ok=True)
                    os.rename(file_path, os.path.join(category_dir, filename))
                break


if __name__ == "__main__":
    # Usage: python file-categorizer.py <directory>
    directory = argv[1]
    categorize_files(directory)
