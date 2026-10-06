# Customer load profile - either from a file or a generated example
import numpy as np
import pandas as pd


def example_profile(index, base_kw=300, production_kw=900):
    """Factory working 2 shifts (6-22) Monday to Friday.
    Outside the shifts only continuous loads run (cooling, compressors etc.)."""
    np.random.seed(42)

    workday = index.dayofweek < 5
    shift = (index.hour >= 6) & (index.hour < 22)

    load = np.full(len(index), float(base_kw))
    load[workday & shift] += production_kw

    # some noise so it's not perfectly flat
    load = load * np.random.normal(1, 0.05, len(index))

    return pd.Series(load.round(1), index=index, name="load_kw")


def read_profile(path):
    df = pd.read_csv(path, sep=";", parse_dates=["time"], index_col="time")
    return df["load_kw"]
