from analysis import profile_summary
from load_profile import example_profile, read_profile
from pse import get_prices

# ---- analysis parameters ----
YEAR = 2026
MONTHS = [7, 8, 9]
PROFILE_FILE = None  # e.g. "data/customer_profile.csv", None = example profile
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

for k, v in summary.items():
    print(f"{k:<50} {v}")
