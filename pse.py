# Downloading RCE prices (Rynkowa Cena Energii - market energy price) from the PSE reports API
# docs: https://api.raporty.pse.pl
import os

import pandas as pd
import requests

URL = "https://api.raporty.pse.pl/api/rce-pln"


def fetch_month(year, month):
    start = pd.Timestamp(year, month, 1)
    end = start + pd.offsets.MonthEnd(0)

    params = {
        "$filter": f"business_date ge '{start:%Y-%m-%d}' and business_date le '{end:%Y-%m-%d}'",
        "$select": "dtime,rce_pln",
        "$first": 5000,  # by default the API returns only 100 records
    }
    resp = requests.get(URL, params=params, timeout=60)
    resp.raise_for_status()
    return pd.DataFrame(resp.json()["value"])


def get_prices(year, months, path="data/rce_prices.csv"):
    # cache prices in a csv so the API isn't called on every run
    if os.path.exists(path):
        print("Loading prices from", path)
        prices = pd.read_csv(path, index_col=0, parse_dates=True)
        return prices["price"]

    parts = []
    for m in months:
        print(f"Downloading RCE prices {year}-{m:02d}...")
        parts.append(fetch_month(year, m))
    df = pd.concat(parts)

    # on DST change days PSE returns values like "02a:15" - skip those rows
    df["time"] = pd.to_datetime(df["dtime"], errors="coerce")
    df = df.dropna(subset=["time"])

    # dtime is the end of the quarter-hour, I prefer the start
    df["time"] = df["time"] - pd.Timedelta(minutes=15)
    df = df.drop_duplicates(subset="time").set_index("time").sort_index()

    prices = df["rce_pln"].astype(float).rename("price")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    prices.to_csv(path)
    return prices
