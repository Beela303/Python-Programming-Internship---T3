from pathlib import Path

def project_paths(root: Path) -> dict[str, Path]:
    return {
        "raw": root / "data" / "raw",
        "processed": root / "data" / "processed",
        "exports": root / "exports",
    }
