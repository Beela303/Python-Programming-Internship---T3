"""Exploratory scratchpad. Run from the repository root; not part of production pipeline."""
from pathlib import Path
import pandas as pd
import numpy as np

orders = pd.read_csv(Path("data/raw/orders.csv"))
print(orders.head())
print(orders.info())
print("\nMissing values by column:")
print(orders.isna().sum().sort_values(ascending=False))

# Example exploratory question: how does order quantity vary?
quantities = pd.to_numeric(orders["quantity"], errors="coerce").dropna().to_numpy()
if quantities.size:
    print("Quantity percentiles:", np.percentile(quantities, [25, 50, 75, 95]))
    print("Potential outliers above 3 standard deviations:",
          quantities[quantities > quantities.mean() + 3 * quantities.std()])
