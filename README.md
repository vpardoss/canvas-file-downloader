# canvas-file-downloader

canvas-file-downloader is a powerful, multi-threaded Python tool to automate downloading and organizing files from your Canvas LMS courses. It supports smart duplicate handling, course filtering, and automatic categorization of files into organized subfolders.

## Features

* **Multi-threaded Downloading**: Fast, parallel downloading to save time.
* **Smart File Tracking**: Uses a local tracking file (`.downloaded_files`) and performs byte-level comparison to detect updated files and save them as new versions, avoiding redundant downloads.
* **Auto-Categorization**: Optionally sorts downloaded files into specific directories (e.g., *Clase*, *Ayudantías*, *Apuntes*) based on file name keywords.
* **Flexible Filtering**: Whitelist or blacklist specific courses, terms, or file extensions.
* **CLI & JSON Configuration**: Easily configure the tool globally via a JSON file or override settings per-run using command-line arguments.

## Requirements

* Python 3.6+
* `requests` library

Install dependencies using:

```bash
pip install requests
```

## Setup

1. **Get your Canvas API Token**:
   * Log into your Canvas account.
   * Go to **Account** -> **Settings**.
   * Scroll down to **Approved Integrations** and click **+ New Access Token**.
   * Copy the generated token.

2. **Configure the script**:
   Create a `config.json` file in the same directory as the script.

### Example `config.json`

```json
{
  "api_token": "YOUR_API_TOKEN_HERE",
  "canvas_domain": "[https://cursos.canvas.uc.cl](https://cursos.canvas.uc.cl)",
  "download_terms_ids": [273],
  "course_whitelist": [],
  "course_blacklist": [],
  "extension_blacklist": [],
  "extension_whitelist": [],
  "default_download_dir": "Archivos-Canvas",
  "create_course_dir": true
}
```

#### Configuration Options
* `api_token`: Your Canvas API access token.
* `canvas_domain`: The base URL of your institution's Canvas site.
* `download_terms_ids`: List of Term IDs to download from (e.g., your current semester ID).
* `course_whitelist`: Array of course codes to strictly download (ignores all others).
* `course_blacklist`: Array of course codes to skip.
* `extension_whitelist` / `extension_blacklist`: Filter specific file types (e.g., `[".pdf", ".docx"]`).
* `default_download_dir`: The main folder where all files will be saved.
* `create_course_dir`: If `true`, creates a subfolder for each course inside the main download directory.

## Usage

Run the script using Python:

```bash
python main.py
```

### Command-Line Arguments (Flags)

You can override the settings in `config.json` dynamically using the following CLI flags:

| Flag | Description |
|------|-------------|
| `--api-token <TOKEN>` | Override the Canvas API token. |
| `--terms-id <ID> [<ID>...]` | Override the course term IDs. |
| `--course-whitelist <COURSE> [<COURSE>...]` | Only download files from these specific courses. |
| `--course-blacklist <COURSE> [<COURSE>...]` | Do not download files from these courses. |
| `--extension-whitelist <EXT> [<EXT>...]` | Only download files with these extensions. |
| `--extension-blacklist <EXT> [<EXT>...]` | Do not download files with these extensions. |
| `--no-byte-checking` | Skip downloading if a file with the same name already exists (disables byte-level content checking for updated files). |
| `--use-file-categorizer` | Run the file categorizer script after downloading to organize files into subdirectories. |

**Example with flags:**
```bash
python main.py --no-byte-checking --use-file-categorizer --course-whitelist "IMT2230-1" "MAT1610"
```

## How File Categorization Works

If you enable the `--use-file-categorizer` flag, `file_categorizer.py` will scan your downloaded course files and move them into categorized subfolders based on keywords found in the filename:

* **Ayudantías**: Matches `ayudantía`, `tarea`, `ayudantia`, or `ay` (when followed by a number).
* **Clase**: Matches `clase`, `clases`.
* **Guias de Ejercicios**: Matches `ejercicio`, `quiz`, `ejercicios`.
* **Apuntes**: Matches `recursos`, `material`, `apuntes`, `apunte`.
* **Actividades**: Matches `actividad`, `actividades`.
* **Talleres**: Matches `taller`, `talleres`.

If a file matches a category, a folder for that category is created automatically within the course directory, and the file is cleanly moved inside.

