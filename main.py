import os

from analysis import payback, profile_summary, simulate_battery, simulate_dsr
from load_profile import example_profile, read_profile
from pse import get_prices
from report import battery_chart, daily_profile_chart, save_excel

# ---- analysis parameters ----
YEAR = 2026
MONTHS = [7, 8, 9]
PROFILE_FILE = None  # e.g. "data/customer_profile.csv", None = example profile

# DSR
REDUCTION_KW = 400
MIN_LOAD_KW = 300          # the plant can't go below this load
REDUCTION_HOURS = 2        # how many hours per day production is shifted
CAPACITY_MARKET_RATE = 200 # PLN/kW/year - assumption, check auction results

# battery storage
BATTERY_KWH = 500
BATTERY_KW = 250
EFFICIENCY = 0.9
BATTERY_COST = 1500        # PLN/kWh - assumption
# -----------------------------

os.makedirs("results", exist_ok=True)

prices = get_prices(YEAR, MONTHS)
data = prices.to_frame()
if PROFILE_FILE:
    data = data.join(read_profile(PROFILE_FILE), how="inner")
else:
    data["load_kw"] = example_profile(data.index)

days = data.index.normalize().nunique()
print(f"Data: {len(data)} quarter-hours, {days} days\n")

summary = profile_summary(data)

# --- DSR ---
dsr = simulate_dsr(data, REDUCTION_KW, MIN_LOAD_KW, REDUCTION_HOURS)
dsr_yearly, _ = payback(dsr["profit_pln"].sum(), days, 0)
capacity_market = REDUCTION_KW * CAPACITY_MARKET_RATE

summary["DSR - zysk z przesunięcia w okresie [zł]"] = round(dsr["profit_pln"].sum())
summary["DSR - zysk z przesunięcia, szacunek roczny [zł]"] = round(dsr_yearly)
summary["DSR - Rynek Mocy, szacunek roczny [zł]"] = round(capacity_market)

# --- battery ---
battery = simulate_battery(data, BATTERY_KWH, BATTERY_KW, EFFICIENCY)
investment = BATTERY_KWH * BATTERY_COST
battery_yearly, years = payback(battery["profit_pln"].sum(), days, investment)

summary["Magazyn - liczba dni pracy"] = int((battery["profit_pln"] > 0).sum())
summary["Magazyn - zysk w okresie [zł]"] = round(battery["profit_pln"].sum())
summary["Magazyn - szacunek roczny [zł]"] = round(battery_yearly)
summary["Magazyn - nakłady [zł]"] = investment
summary["Magazyn - prosty okres zwrotu [lata]"] = round(years, 1) if years else "brak zwrotu"

for k, v in summary.items():
    print(f"{k:<50} {v}")

# --- report ---
charts = ["results/daily_profile.png", "results/battery.png"]
daily_profile_chart(data, charts[0])
battery_chart(battery, charts[1])
save_excel("results/report.xlsx", summary, dsr, battery, data, charts)
print("\nReport saved: results/report.xlsx")
