# canvas-file-downloader

Get your token from
https://cursos.canvas.{your_institution}/profile/settings
https://cursos.canvas.uc.cl/profile/settings
`config.json` example for PUC.
```json
{
  "api_token": "YOUR_TOKEN",
  "canvas_domain": "https://cursos.canvas.uc.cl",
  "download_terms_ids": [273],
  "course_whitelist": [""],
  "course_blacklist": ["ETI195-1"],
  "extension_blacklist": [],
  "extension_whitelist": [],
  "default_download_dir": "",
  "create_course_dir": true
}
```