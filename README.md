# Fleet Daily Operations Dashboard

Static dashboard (single `index.html`, no server needed) built from the fleet MIS sheet.

## Files
- `index.html` – the dashboard (what gets deployed)
- `template.html` – dashboard layout/code with placeholders
- `build.py` – reads the CSV in `data/` and writes `index.html`
- `data/Fleet - Sheet37.csv` – current data (01–27 Sep 2026)

## Deploy on GitHub Pages
1. Create a new repo on GitHub and upload all these files (keep the folder structure).
2. Repo **Settings → Pages → Build and deployment → Source: Deploy from a branch**, branch `main`, folder `/ (root)` → Save.
3. After a minute the site is live at `https://<your-username>.github.io/<repo-name>/`.

## Update with new data
Replace the CSV in `data/`, then run:

    pip install pandas
    python build.py

Commit the new `index.html` – Pages redeploys automatically.
(Or send the new sheet to Claude and commit the `index.html` it returns.)

## Data rules used
- Total Earnings = Net Earning + MG Amount only where `MG Received? = Yes`
- MG Receivable = MG Amount where `MG Received? = No`
- Expenses = `Total Expenses` if filled, else Toll + Other Expense
- Vehicle `2043` is treated as a note, not a fleet vehicle (`NON_FLEET` in build.py)
- Utilisation = ran days ÷ planned days (weekly-off and note rows excluded)
