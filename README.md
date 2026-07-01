# Daily Yard Tip

Auto-updating single-page site with a daily lawn/garden maintenance tip for
South Orange, NJ (07079), based on the live 3-day weather forecast
([Open-Meteo](https://open-meteo.com/), free, no API key) and the current
season. Runs entirely on GitHub's infrastructure — no desktop app or computer
needs to stay on.

## How it works

- `scripts/generate_tip.py` fetches the forecast and writes `docs/index.html`.
- `.github/workflows/update-tip.yml` runs that script every morning
  (~6:05am ET) via GitHub Actions, then commits the updated page.
- GitHub Pages serves `docs/index.html` as a live URL.

## One-time setup

1. **Create the repo.** On github.com, click **New repository**. Name it
   anything (e.g. `daily-yard-tip`). Keep it **Public** (required for free,
   unlimited Actions minutes). Don't initialize with a README — you already
   have one here.

2. **Push this folder to it.** From a terminal, inside this folder:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

3. **Allow the workflow to push commits.** In the repo on GitHub:
   Settings → Actions → General → Workflow permissions → select
   **Read and write permissions** → Save.

4. **Enable GitHub Pages.** Settings → Pages → under **Build and
   deployment**, set Source to **Deploy from a branch**, branch **main**,
   folder **/docs** → Save. GitHub will give you a URL like
   `https://<your-username>.github.io/<your-repo>/` — that's your live tip
   page, bookmark it.

5. **Run it once manually.** Go to the **Actions** tab → **Update Daily
   Yard Tip** → **Run workflow**. Wait ~30 seconds, refresh your Pages URL —
   you should see today's real tip instead of the placeholder.

After that, it updates itself every morning automatically. No further action
needed.

## Changing location

Edit the constants at the top of `scripts/generate_tip.py`
(`LATITUDE`, `LONGITUDE`, `LOCATION_LABEL`, `ZIP_LABEL`) and push — the next
run will use the new location.

## Adjusting the schedule

Edit the `cron` lines in `.github/workflows/update-tip.yml`. GitHub Actions
cron runs in UTC and doesn't auto-adjust for daylight saving, which is why
there are two schedule lines (one for EDT months, one for EST months).
