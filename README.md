# update_news_excel

Small Flask service to append and sort news links into an Excel sheet.

**Files**
- [Dockerfile](Dockerfile) — image build
- [docker-compose.yml](docker-compose.yml) — compose service stub (uses external `n8n` network and `NAS` volume)
- [app.py](app.py) — Flask entrypoint and background worker
- [checked_added_url.py](checked_added_url.py) - Check added news helper
- [update_csv.py](update_csv.py) — Excel update helpers
- [.dockerignore](.dockerignore) — build context exclusions
- [csv_template.csv](csv_template.csv) - Csv template with header

**Prerequisites**
- Docker / Docker Compose OR Python 3.11 and pip
- If using compose: an external Docker network named `n8n` and a volume named `NAS` (or edit `docker-compose.yml` accordingly)

Quick commands to create missing items if needed:
```bash
# create network + volume (only if they don't already exist)
docker network create n8n
docker volume create NAS
```

**Build & run with Docker (manual)**
```bash
# build image locally
docker build -t cc-web-scrape .

# run container (maps container 5000 to host 5000)
docker run --rm -p 5000:5000 \
  -v NAS:/app/nas_data \
  --env-file stack.env \
  cc-web-scrape
```

**Run with docker-compose (recommended for stack)**
From the repository root (where `docker-compose.yml` is):
```bash
# build and start in background
docker compose up -d --build

# view logs
docker compose logs -f scraper

# stop / remove
docker compose down
```
Note: The provided `docker-compose.yml` currently uses `image: "cc-web-scrape"` and maps host port `5001` → container `5000`. If you prefer Compose to build the local `Dockerfile`, edit the service to use `build: .` (and remove or keep `image:` as desired) then run `docker compose up -d --build`.

**Local development (no Docker)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Service will listen on `0.0.0.0:5000`.

**API — endpoint**
- POST `/run` — Launch a background job to append data to the Excel sheet. 
- field:
  -  `date` is required (string, e.g. `20250905`). 
  - `callback_url` is required. The service will POST a JSON payload to that URL when the job succeeds/fails.
  - `input` is a list of objects with `article_url`, `title`, `date`, `website_source` field.
- Functionality: Update daily scraped news details. It will first check if the news are already added by checking `added_url_{date}.txt` file to prevent duplications. After the news are added into the `daily_news_{date}.csv` file, `added_url_{date}.txt` file would also be updated.
- Example payload:
```json
{
  "callback_url": "https://example.com/webhook",
  "date": "20250905",
  "input": [
    {"title": "Title 1", "date": "2025-12-19", "article_url": "https://...", "website_source": "source"}
  ]
}
```

- POST `/check_added_url` — Check which input items are not recorded in the `added_url_{date}.txt` file.
- Purpose: return only items whose `article_url` are not present in the target added-URL file for the given date. If the file does not exist or cannot be read, the original input list is returned.
- field:
  - `date` is required (string, e.g. `20250905`). 
  - `callback_url` is required. The service will POST a JSON payload to that URL when the job succeeds/fails.
  - `input` is a list of objects with an `article_url` field.
- Functionality: Check if the article is already added. It will return the item that article_url are not found in daily sheet. No files will be updated by calling this api endpoint.
- Example request body:
```json
{
  "callback_url": "",
  "date": "20250905",
  "input": [
    {
      "content": "...",
      "title": "演藝學院：有關部門內部溝通未盡完善 團隊汲取經驗",
      "date": "2025-09-05",
      "article_url": "https://news.rthk.hk/rthk/ch/component/k2/1821433-20250905.htm?archive_date=2025-09-05"
    }
  ]
}
```
  - Example response (when the URL is not present in `added_url_20250905.txt`):
```json
{
  "data": [
    {
      "content": "...",
      "title": "演藝學院：有關部門內部溝通未盡完善 團隊汲取經驗",
      "date": "2025-09-05",
      "article_url": "https://news.rthk.hk/rthk/ch/component/k2/1821433-20250905.htm?archive_date=2025-09-05"
    }
  ],
  "message": "Task completed."
}
```

**Compose volume & network notes**
- `docker-compose.yml` mounts `NAS` into the container at `/app/nas_data`. Ensure that path and file permissions match your environment.
- The compose file references an external network `n8n`. If you don't use it, either create it or remove the network reference.

**Troubleshooting**
- If the container exits immediately, check `docker compose logs -f scraper`.
- If the app cannot find the Excel file, ensure `NAS` contains `csv_template.csv` at the expected path or adjust `BASE_PATH` in `app.py`/`nas_output`/`update_csv.py`.

- File structure example:

```json
/nas_output:
|   csv_template.csv
|   
+---/output
    +---/2025
        +---/05
|           added_url_20250521.txt
|           daily_news_20250521.csv
|       
```

**Next steps / optional changes**
- Switch `docker-compose.yml` to `build: .` to let compose build the image locally.
- Add a healthcheck to the `Dockerfile` or `docker-compose.yml`.
- Secure environment files and avoid committing secrets (see `.dockerignore` which excludes `stack.env`).