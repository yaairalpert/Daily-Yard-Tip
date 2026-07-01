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

## WhatsApp delivery (optional)

The workflow will also WhatsApp you the tip each morning via
[CallMeBot](https://www.callmebot.com/) (free, personal-use API) — if you set
it up. Skipped silently if not configured.

1. Save **+34 644 91 96 80** as a contact in your phone (any name).
2. From WhatsApp, message that contact: `I allow callmebot to send me messages`
3. Wait for a reply containing your API key (usually under 2 minutes; if
   nothing arrives, try again after 24 hours).
4. In your GitHub repo: **Settings → Secrets and variables → Actions →
   New repository secret**. Add two secrets:
   - `CALLMEBOT_PHONE` — your WhatsApp number with country code, e.g. `+12015551234`
   - `CALLMEBOT_APIKEY` — the key CallMeBot sent you
5. Re-run the workflow manually (Actions tab → Run workflow) to test it —
   you should get a WhatsApp message within a few seconds of the run finishing.

## Changing location

Edit the constants at the top of `scripts/generate_tip.py`
(`LATITUDE`, `LONGITUDE`, `LOCATION_LABEL`, `ZIP_LABEL`) and push — the next
run will use the new location.

## Adjusting the schedule

Edit the `cron` lines in `.github/workflows/update-tip.yml`. GitHub Actions
cron runs in UTC and doesn't auto-adjust for daylight saving, which is why
there are two schedule lines (one for EDT months, one for EST months).
