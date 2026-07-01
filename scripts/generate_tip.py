#!/usr/bin/env python3
"""
Generates docs/index.html: a daily lawn/garden maintenance tip for a fixed
location, based on the current 3-day forecast (Open-Meteo, free/no API key)
and the current season. Designed to be run daily by a GitHub Actions cron job.

To change location: update LATITUDE / LONGITUDE / LOCATION_LABEL below.
(Current values: South Orange, NJ 07079)
"""
import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

# ---- Location config ------------------------------------------------------
LATITUDE = 40.7459
LONGITUDE = -74.2607
LOCATION_LABEL = "South Orange, NJ"
ZIP_LABEL = "07079"
TIMEZONE = "America/New_York"

FORECAST_URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}&longitude={LONGITUDE}"
    "&daily=weather_code,temperature_2m_max,temperature_2m_min,"
    "precipitation_sum,precipitation_probability_max,wind_speed_10m_max,"
    "relative_humidity_2m_max"
    "&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch"
    f"&timezone={TIMEZONE}&forecast_days=3"
)

WEATHER_CODE_MAP = {
    0: ("Clear", "☀️"),
    1: ("Mostly clear", "\U0001F324️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "\U0001F32B️"),
    48: ("Freezing fog", "\U0001F32B️"),
    51: ("Light drizzle", "\U0001F326️"),
    53: ("Drizzle", "\U0001F326️"),
    55: ("Dense drizzle", "\U0001F326️"),
    56: ("Freezing drizzle", "\U0001F326️"),
    57: ("Freezing drizzle", "\U0001F326️"),
    61: ("Light rain", "\U0001F327️"),
    63: ("Rain", "\U0001F327️"),
    65: ("Heavy rain", "\U0001F327️"),
    66: ("Freezing rain", "\U0001F327️"),
    67: ("Heavy freezing rain", "\U0001F327️"),
    71: ("Light snow", "❄️"),
    73: ("Snow", "❄️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Rain showers", "\U0001F326️"),
    81: ("Rain showers", "\U0001F326️"),
    82: ("Violent showers", "\U0001F327️"),
    85: ("Snow showers", "\U0001F328️"),
    86: ("Snow showers", "\U0001F328️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm w/ hail", "⛈️"),
    99: ("Thunderstorm w/ hail", "⛈️"),
}


def fetch_forecast():
    with urllib.request.urlopen(FORECAST_URL, timeout=20) as resp:
        return json.loads(resp.read().decode())


def season_for_month(month: int) -> str:
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "fall"


def build_days(daily: dict):
    days = []
    for i in range(min(3, len(daily["time"]))):
        code = daily["weather_code"][i]
        label, icon = WEATHER_CODE_MAP.get(code, ("Mixed", "\U0001F326️"))
        days.append({
            "date": daily["time"][i],
            "hi": round(daily["temperature_2m_max"][i]),
            "lo": round(daily["temperature_2m_min"][i]),
            "precip_in": daily["precipitation_sum"][i],
            "precip_prob": daily["precipitation_probability_max"][i],
            "wind_mph": daily["wind_speed_10m_max"][i],
            "humidity": daily["relative_humidity_2m_max"][i],
            "code": code,
            "label": label,
            "icon": icon,
        })
    return days


# ---- Tip rules (priority order) -------------------------------------------
def tip_heavy_rain(days, season):
    if any(d["precip_in"] >= 1.0 or d["precip_prob"] >= 70 for d in days):
        return {
            "headline": "Heavy rain in the forecast — protect the lawn, don't feed into it",
            "steps": [
                "Hold off on mowing until the ground firms back up — wet-soil mowing compacts soil and tears grass instead of cutting it.",
                "Skip any fertilizer, pesticide, or herbicide application until at least a day after the rain clears — it washes off before it can work.",
                "Walk the property during or right after the rain and flag any pooling near the foundation, downspouts, or low spots in the yard.",
                "Clear gutters and downspout extensions now, before the heavier rain hits, so water has somewhere to go.",
            ],
            "why": "Standing water and compacted wet soil are the two most common causes of lawn damage after a storm — both are avoidable if you just wait a day.",
        }
    return None


def tip_extreme_heat(days, season):
    if any(d["hi"] >= 90 for d in days):
        return {
            "headline": "Heat spike coming — adjust watering and mowing height",
            "steps": [
                "Water deeply (about 1 inch) before 9am, not in the evening — overnight moisture on hot leaves invites fungus.",
                "Raise the mower deck a notch — taller grass shades its own roots and holds moisture better in a heat spike.",
                "Check new/young plantings and container plants twice a day — they dry out fastest and show stress first.",
                "Avoid mowing during the hottest part of the day — it stresses grass that's already fighting heat.",
            ],
            "why": "Grass and young plants lose far more moisture than they can take up once highs push past 90°F, so watering timing and mower height matter more than usual.",
        }
    return None


def tip_frost_risk(days, season):
    if season in ("spring", "fall") and any(d["lo"] <= 34 for d in days):
        return {
            "headline": "Frost risk overnight — protect tender plants",
            "steps": [
                "Cover tender annuals, seedlings, and any newly planted material with a sheet or frost cloth before dusk.",
                "Bring potted plants that aren't cold-hardy indoors or into a garage overnight.",
                "Hold off on any new planting of frost-sensitive material until overnight lows clear 40°F consistently.",
                "Don't prune anything tonight — fresh cuts are more vulnerable to frost damage.",
            ],
            "why": "A single overnight dip near freezing can wipe out a season's worth of tender growth in one night — covering plants for a few hours is cheap insurance.",
        }
    return None


def tip_winter_cold(days, season):
    if season == "winter" and any(d["hi"] <= 34 or d["code"] in (71, 73, 75, 77, 85, 86) for d in days):
        return {
            "headline": "Cold/snow on the way — protect shrubs and hardscape",
            "steps": [
                "Brush heavy, wet snow off shrub branches and small evergreens with an upward sweep before it freezes solid — don't shake ice-coated branches, they snap.",
                "Use calcium chloride or a pet-safe deicer near plant beds instead of rock salt — salt spray and runoff burn roots and turf come spring.",
                "Keep deicer and shoveled snow off the lawn itself where possible — pile snow on pavement/mulch beds, not turf.",
                "Check that gutters are clear — ice dams from clogged gutters are the #1 cause of winter roof and fascia damage.",
            ],
            "why": "Most winter landscape damage in NJ isn't the cold itself — it's salt burn and snow-load breakage, both preventable with how you handle the snow.",
        }
    return None


def tip_high_wind(days, season):
    if any(d["wind_mph"] >= 25 for d in days):
        return {
            "headline": "Windy stretch ahead — secure and inspect before it hits",
            "steps": [
                "Stake or re-stake any young trees and top-heavy perennials before the wind picks up.",
                "Secure or store loose items — pots, furniture, trellises — that could become debris.",
                "After the wind passes, walk the property for broken branches or leaning limbs, especially over walkways and the roofline.",
                "Check that any recently mulched beds haven't blown clear — re-top if needed once it calms down.",
            ],
            "why": "Wind damage is almost always cheaper to prevent (five minutes of staking) than to fix (a snapped young tree or a punched-in fence panel).",
        }
    return None


def tip_fungus_risk(days, season):
    if any(d["humidity"] >= 80 and d["hi"] >= 75 for d in days):
        return {
            "headline": "Humid and warm — watch for fungal disease",
            "steps": [
                "Water early morning only, and only at the base of plants — avoid wetting foliage in the evening.",
                "Scout the lawn for brown patch (circular tan/brown rings) and garden beds for powdery mildew on leaves.",
                "Thin out crowded plantings or perennials if you see any — airflow is the best fungicide you have.",
                "Hold off on nitrogen-heavy fertilizer this week — it pushes soft new growth that's more disease-prone in humid heat.",
            ],
            "why": "This exact combination — high humidity plus warm temps — is the single biggest driver of lawn and plant fungal outbreaks in NJ summers.",
        }
    return None


def tip_dry_stretch(days, season):
    if all(d["precip_in"] < 0.05 for d in days) and any(d["hi"] >= 75 for d in days):
        return {
            "headline": "Dry stretch — get ahead of it with deep, infrequent watering",
            "steps": [
                "Water deeply 1-2 times this week (about 1 inch total) rather than a little every day — it drives roots deeper and builds drought resistance.",
                "Water early morning to minimize evaporation and fungal risk.",
                "Check mulch depth in garden beds — top up to 2-3 inches where it's thin to hold soil moisture.",
                "Prioritize new plantings and containers first — they have the shallowest roots and dry out fastest.",
            ],
            "why": "Deep, infrequent watering during dry stretches builds a more drought-resistant root system than frequent light watering — and uses less water overall.",
        }
    return None


SEASONAL_DEFAULTS = {
    "spring": [
        {
            "headline": "Prime window for pre-emergent and bed cleanup",
            "steps": [
                "Apply pre-emergent crabgrass control now if soil temps are consistently above 50°F — timing matters more than the product you use.",
                "Cut back last year's perennial stalks and clear winter debris from beds before new growth fills in.",
                "Edge garden beds now while soil is workable — it's easier before everything greens up and roots interlock.",
                "Refresh mulch to 2-3 inches once beds are clean, keeping it pulled back from stems and trunks.",
            ],
            "why": "Spring cleanup done before green-up is faster, cleaner, and sets up the whole season — waiting means working around growth you'll accidentally damage.",
        },
        {
            "headline": "Good day to check for winter damage before mowing season ramps up",
            "steps": [
                "Walk the lawn for bare or thin patches from winter salt, snow mold, or plow damage and note where overseeding is needed.",
                "Inspect shrubs and small trees for broken or dead branches from winter weight or wind, and prune those out now.",
                "Test soil pH or send a sample out if it's been more than 2-3 years — spring is the best window to adjust before planting.",
                "Sharpen or replace mower blades before the first cut — a dull blade tears grass and invites disease all season.",
            ],
            "why": "Catching winter damage now, before the season's growth covers it up, is the difference between a quick fix and a bare patch that lingers all summer.",
        },
    ],
    "summer": [
        {
            "headline": "Mid-summer maintenance check",
            "steps": [
                "Mow at the higher end of your grass type's recommended height — it shades roots and out-competes weeds.",
                "Deadhead spent blooms on annuals and perennials to keep them flowering through the season.",
                "Check irrigation heads/hoses for clogs or misalignment now, before a dry stretch makes gaps in coverage obvious the hard way.",
                "Inspect for early signs of pest damage (chewed leaves, sawdust-like frass, holes) while it's still a small problem.",
            ],
            "why": "Summer lawn and plant stress compounds fast — a five-minute check now catches problems while they're still a quick fix.",
        },
    ],
    "fall": [
        {
            "headline": "Prime window for aeration, overseeding, and bulb planting",
            "steps": [
                "Aerate and overseed cool-season lawns now — soil is still warm enough for germination but the heat stress is over.",
                "Start mulching fallen leaves into the lawn with the mower instead of bagging — shredded leaves feed the soil for free.",
                "Plant spring-flowering bulbs (daffodils, tulips, crocus) once soil temps drop below 60°F.",
                "Cut back on fertilizing woody plants now so new growth has time to harden off before frost.",
            ],
            "why": "Fall is the single best window for lawn repair in the Northeast — grass seed planted now gets a full season to establish roots before summer stress returns.",
        },
    ],
    "winter": [
        {
            "headline": "Dormant-season tasks worth doing now",
            "steps": [
                "Prune dormant deciduous trees and shrubs (not spring bloomers) while there's no leaf cover to hide structure.",
                "Check stored mowers/tools and get blades sharpened before the spring rush hits every shop at once.",
                "Inspect hardscape (walkways, retaining walls) for winter heave or cracking while it's easy to spot against bare ground.",
                "Plan this year's bed layout or plant orders now — popular varieties sell out well before planting season.",
            ],
            "why": "Winter is the only season where the to-do list is about planning and prep, not reacting — worth using the downtime.",
        },
    ],
}


def default_tip(season: str, day_index: int):
    options = SEASONAL_DEFAULTS[season]
    return options[day_index % len(options)]


RULES = [
    tip_heavy_rain,
    tip_extreme_heat,
    tip_winter_cold,
    tip_frost_risk,
    tip_high_wind,
    tip_fungus_risk,
    tip_dry_stretch,
]


def choose_tip(days, season, day_index):
    for rule in RULES:
        result = rule(days, season)
        if result:
            return result
    return default_tip(season, day_index)


DAY_LABELS = ["Today", "Tomorrow", "Day 3"]


def render_html(days, season, tip, generated_at: datetime) -> str:
    weather_cards = ""
    for i, d in enumerate(days):
        precip = f'{d["precip_prob"]}% rain' if d["precip_prob"] >= 15 else d["label"]
        weather_cards += f"""
    <div class="day-card">
      <div class="day-label">{DAY_LABELS[i]}</div>
      <div class="icon">{d["icon"]}</div>
      <div class="temps">{d["hi"]}° / {d["lo"]}°</div>
      <div class="precip">{precip}</div>
    </div>"""

    steps_html = "".join(f"      <li>{s}</li>\n" for s in tip["steps"])
    date_label = generated_at.strftime("%b %-d, %Y")
    season_label = season.capitalize()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Today's Yard Tip — {LOCATION_LABEL}</title>
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: #ffffff;
    color: #1f2a1f;
    padding: 20px;
  }}
  .wrap {{ max-width: 640px; margin: 0 auto; }}
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
    flex-wrap: wrap;
    gap: 8px;
  }}
  .title {{ font-size: 20px; font-weight: 700; color: #2f5233; margin: 0; }}
  .subtitle {{ font-size: 13px; color: #6b7a6b; margin-top: 2px; }}
  .badge {{
    background: #eaf3ea;
    color: #2f5233;
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
  }}
  .weather-strip {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 20px;
  }}
  .day-card {{
    background: #f7faf7;
    border: 1px solid #e3ece3;
    border-radius: 12px;
    padding: 12px 10px;
    text-align: center;
  }}
  .day-card .day-label {{ font-size: 11px; font-weight: 700; text-transform: uppercase; color: #6b7a6b; letter-spacing: 0.04em; }}
  .day-card .icon {{ font-size: 26px; margin: 6px 0 4px; }}
  .day-card .temps {{ font-size: 14px; font-weight: 700; color: #1f2a1f; }}
  .day-card .precip {{ font-size: 11px; color: #4a7a4a; margin-top: 2px; }}
  .tip-card {{
    background: linear-gradient(135deg, #2f5233, #3d6b42);
    border-radius: 16px;
    padding: 20px 22px;
    color: #fff;
    margin-bottom: 16px;
  }}
  .tip-card .tip-label {{
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    opacity: 0.85;
    font-weight: 700;
    margin-bottom: 6px;
  }}
  .tip-card h2 {{ font-size: 17px; margin: 0 0 12px; line-height: 1.35; }}
  .tip-card ol {{ margin: 0; padding-left: 20px; }}
  .tip-card li {{ margin-bottom: 8px; font-size: 14px; line-height: 1.45; }}
  .tip-card li:last-child {{ margin-bottom: 0; }}
  .why {{
    background: #f7faf7;
    border: 1px solid #e3ece3;
    border-radius: 12px;
    padding: 14px 16px;
    font-size: 13px;
    color: #445544;
    line-height: 1.5;
    margin-bottom: 14px;
  }}
  .why b {{ color: #2f5233; }}
  .footer {{
    font-size: 11px;
    color: #93a293;
    text-align: center;
    margin-top: 10px;
    line-height: 1.5;
  }}
</style>
</head>
<body>
<div class="wrap">

  <div class="header">
    <div>
      <p class="title">Today's Yard Tip</p>
      <p class="subtitle">{LOCATION_LABEL} &middot; {ZIP_LABEL} &middot; {season_label}</p>
    </div>
    <span class="badge">Updated {date_label}</span>
  </div>

  <div class="weather-strip">{weather_cards}
  </div>

  <div class="tip-card">
    <div class="tip-label">Do this today</div>
    <h2>{tip["headline"]}</h2>
    <ol>
{steps_html}    </ol>
  </div>

  <div class="why">
    <b>Why:</b> {tip["why"]}
  </div>

  <div class="footer">
    Auto-generated daily from the live 3-day forecast for {ZIP_LABEL}, current season, and NJ lawn/garden best practices.<br>
    Refreshes every morning — just reload this page.
  </div>

</div>
</body>
</html>
"""


def main():
    data = fetch_forecast()
    days = build_days(data["daily"])
    now = datetime.now(ZoneInfo(TIMEZONE))
    season = season_for_month(now.month)
    day_index = now.timetuple().tm_yday
    tip = choose_tip(days, season, day_index)
    html = render_html(days, season, tip, now)

    import os
    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote docs/index.html — season={season}, tip='{tip['headline']}'")


if __name__ == "__main__":
    main()
