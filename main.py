from analysis import payback, profile_summary, simulate_battery
from load_profile import example_profile, read_profile
from pse import get_prices

# ---- analysis parameters ----
YEAR = 2026
MONTHS = [7, 8, 9]
PROFILE_FILE = None  # e.g. "data/customer_profile.csv", None = example profile

# battery storage
BATTERY_KWH = 500
BATTERY_KW = 250
EFFICIENCY = 0.9
BATTERY_COST = 1500        # PLN/kWh - assumption
# -----------------------------

prices = get_prices(YEAR, MONTHS)
data = prices.to_frame()
if PROFILE_FILE:
    data = data.join(read_profile(PROFILE_FILE), how="inner")
else:
    data["load_kw"] = example_profile(data.index)

days = data.index.normalize().nunique()
print(f"Data: {len(data)} quarter-hours, {days} days\n")

summary = profile_summary(data)

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
