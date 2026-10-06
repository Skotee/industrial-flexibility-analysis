import pandas as pd

QUARTER = 0.25  # h


def profile_summary(data):
    load = data["load_kw"]
    energy_mwh = load.sum() * QUARTER / 1000
    cost = (load * QUARTER / 1000 * data["price"]).sum()

    return {
        "Okres analizy": f"{data.index.min():%Y-%m-%d} - {data.index.max():%Y-%m-%d}",
        "Zużycie energii [MWh]": round(energy_mwh, 1),
        "Moc szczytowa [kW]": round(load.max()),
        "Moc minimalna [kW]": round(load.min()),
        "Moc średnia [kW]": round(load.mean()),
        "Współczynnik obciążenia [%]": round(load.mean() / load.max() * 100, 1),
        "Średnia cena RCE [zł/MWh]": round(data["price"].mean(), 2),
        "Średnia ważona cena zakupu [zł/MWh]": round(cost / energy_mwh, 2),
        "Koszt energii wg RCE [zł]": round(cost),
    }


def simulate_battery(data, capacity_kwh, power_kw, efficiency=0.9):
    """Simplest arbitrage: one cycle per day.
    Charge in the cheapest quarter-hours of the day, discharge in the most expensive."""
    n = int(capacity_kwh / power_kw * 4)  # how many quarter-hours a full charge takes
    energy = power_kw * QUARTER / 1000  # MWh per quarter-hour

    results = []
    for day, d in data.groupby(data.index.date):
        if len(d) < 2 * n:
            continue

        prices = d["price"].sort_values()
        cost = prices.iloc[:n].sum() * energy
        revenue = prices.iloc[-n:].sum() * energy * efficiency
        profit = revenue - cost

        # if the price spread is too small, the battery stays idle that day
        if profit < 0:
            cost, revenue, profit = 0, 0, 0

        results.append({
            "day": pd.Timestamp(day),
            "min_price": prices.iloc[0],
            "max_price": prices.iloc[-1],
            "charging_cost_pln": cost,
            "revenue_pln": revenue,
            "profit_pln": profit,
        })

    return pd.DataFrame(results).set_index("day")


def payback(profit_in_period, days, investment_pln):
    yearly_profit = profit_in_period / days * 365
    if yearly_profit <= 0:
        return yearly_profit, None
    return yearly_profit, investment_pln / yearly_profit
