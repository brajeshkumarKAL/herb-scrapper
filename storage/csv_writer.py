import pandas as pd
from pathlib import Path


def save_to_csv(processed_data, output_path: str = "data/output/output.csv"):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(processed_data)
    df.to_csv(path, index=False, encoding="utf-8")
    return str(path)
