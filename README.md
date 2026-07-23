# NACOS FCIT Opportunities Bot

Scrapes job/internship listings, classifies them with an LLM (remote/onsite/hybrid,
skills, relevance), stores them, and serves them via an API for the Opportunities
page on the faculty website.

## Project layout

```
opportunities-bot/
├── sources/
│   ├── base.py                  # shared adapter interface
│   ├── remotive.py               # Remotive API adapter
│   ├── arbeitnow.py              # Arbeitnow API adapter
│   └── template_html_source.py   # copy this to add a scraped source later
├── pipeline/
│   └── classify.py               # LLM tagging + relevance scoring
├── db/
│   ├── database.py                # engine/session setup
│   ├── models.py                   # Listing table
│   └── crud.py                      # dedupe, save, query
├── api/
│   └── main.py                      # FastAPI app -> /api/opportunities
├── run_scraper.py                    # entrypoint: fetch -> classify -> save
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 1. Install prerequisites (Windows)

1. **Install Python 3.11+**
   Download from https://www.python.org/downloads/ — during install, tick
   **"Add python.exe to PATH"** on the first screen. Verify in a terminal:
   ```
   python --version
   ```

2. **Install VS Code** (if not already) from https://code.visualstudio.com/

3. **Install the VS Code Python extension**
   Open VS Code → Extensions (`Ctrl+Shift+X`) → search "Python" (by Microsoft) → Install.

---

## 2. Get the project into VS Code

1. Unzip the project folder somewhere convenient, e.g. `C:\Users\<you>\Projects\opportunities-bot`
2. Open VS Code → `File > Open Folder...` → select that folder.

---

## 3. Create a virtual environment

Open a terminal in VS Code (`` Ctrl+` ``), then:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

If PowerShell blocks the activation script with an execution policy error, run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

then try activating again. You'll know it worked when your terminal prompt shows `(venv)` at the start.

VS Code may also pop up "Select a Python Interpreter" — choose the one inside `venv`.

---

## 4. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## 5. Set up environment variables

Copy the example file:

```powershell
copy .env.example .env
```

Open `.env` and fill in:

- `GROQ_API_KEY` — get a free one from https://console.groq.com/keys
- `DATABASE_URL` — leave as the default SQLite line for now; you don't need Postgres to get started

---

## 6. Run the scraper

```powershell
python run_scraper.py
```

You should see output like:

```
remotive: fetched 40 listings
arbeitnow: fetched 25 listings
Saved: Frontend Developer Intern @ Google Africa
...
Done. 6 new listing(s) saved.
```

This creates `opportunities.db` (a SQLite file) in your project folder with the classified listings inside it.

---

## 7. Run the API

```powershell
uvicorn api.main:app --reload --port 8000
```

Visit `http://localhost:8000/api/opportunities` in your browser — you should see JSON back.
FastAPI also gives you free interactive docs at `http://localhost:8000/docs`.

---

## 8. Connect it to the Vite frontend

In the Opportunities page component, replace the hardcoded card with a fetch:

```js
useEffect(() => {
  fetch("http://localhost:8000/api/opportunities")
    .then((res) => res.json())
    .then(setOpportunities);
}, []);
```

Once deployed, swap `http://localhost:8000` for your live API URL.

---

## 9. Running the scraper to update the live site

The scraper does **not** need to run 24/7 — only the API does (the website queries it
at any time of day). Once the API is deployed and pointed at a shared Postgres database
(see below), just run `python run_scraper.py` from your own machine, on your own
schedule, whenever you want fresh listings to show up on the site. No server or cron
job required for this part.

---

## 10. Deploying (free tier, no VPS)

Two pieces, one shared database:

- **Database — Neon or Supabase (free tier)**
  1. Create a free Postgres project at https://neon.tech or https://supabase.com
  2. Copy its connection string (looks like `postgresql://user:password@host/dbname`)
  3. Put it in **both**:
     - your local `.env` as `DATABASE_URL=...` (so `run_scraper.py` writes to it)
     - Render's environment variables for the web service below (so the API reads from it)

  This replaces local SQLite once you deploy — SQLite is a single file and can't be
  shared between your machine and a hosted API.

- **API — Render free web service**
  1. Push this repo to GitHub (already done if you're reading this from the deployed repo)
  2. In the Render dashboard: New → Blueprint → connect this GitHub repo. Render will
     read `render.yaml` in this repo and set up the web service automatically.
  3. Fill in the `GROQ_API_KEY` and `DATABASE_URL` values when prompted (they're left
     blank in `render.yaml` on purpose — never commit real secrets to git).
  4. Render gives you a URL like `https://opportunities-bot-api.onrender.com` — point
     the frontend's fetch call at that instead of `localhost:8000`.

  Free tier note: the service sleeps after 15 minutes of no traffic and takes ~30-50s
  to wake up on the next request. Fine for a low-traffic opportunities page.

Never commit `.env` to git (it's already in `.gitignore`).

---

## Adding a new source later

1. Copy `sources/template_html_source.py` (or `remotive.py` if the new site has an API)
2. Rename the class and fill in the actual endpoint or CSS selectors
3. Import it and add an instance to the `SOURCES` list in `run_scraper.py`

That's the only file you need to touch to add a new source — everything downstream
(classification, dedup, storage, API) already handles it automatically.
