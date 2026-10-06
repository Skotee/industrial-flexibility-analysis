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
