from pathlib import Path
import hashlib
import pandas as pd

def load_inputs(raw_dir: Path) -> dict[str, pd.DataFrame]:
    return {
        "orders": pd.read_csv(raw_dir / "orders.csv"),
        "customers": pd.read_csv(raw_dir / "customers.csv"),
        "products": pd.read_csv(raw_dir / "products.csv"),
    }

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()
