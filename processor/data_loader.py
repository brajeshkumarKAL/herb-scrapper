import json
from pathlib import Path
from typing import List

from models.herb_model import Herb


def normalize_name(name: str) -> str:
    return name.strip().lower()


def load_herb_data(file_path: str) -> List[Herb]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    try:
        with path.open("r", encoding="utf-8") as source:
            raw_data = json.load(source)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in input file: {file_path}") from error

    merged = {}
    for entry in raw_data:
        main_name = normalize_name(entry.get("main_name", ""))
        if not main_name:
            continue
        synonyms = entry.get("synonyms", []) or []
        normalized_synonyms = {
            synonym for synonym in (normalize_name(item) for item in synonyms)
            if synonym
        }
        existing = merged.setdefault(main_name, set())
        existing.update(normalized_synonyms)

    return [Herb(main_name=key, synonyms=sorted(values)) for key, values in merged.items()]
