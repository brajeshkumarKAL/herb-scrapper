import json
import re
import pandas as pd
from pathlib import Path
from config.settings import settings


def normalize_filename(name: str) -> str:
    """
    Normalize a query name for use as a filename.
    Converts to lowercase, replaces spaces/hyphens with underscores, removes invalid chars.
    """
    # Convert to lowercase
    normalized = name.lower()
    # Replace spaces and hyphens with underscores
    normalized = re.sub(r'[\s\-]+', '_', normalized)
    # Remove invalid filename characters (keep alphanumeric, underscore, dot)
    normalized = re.sub(r'[^\w\.]', '', normalized)
    # Ensure it's not empty
    if not normalized:
        normalized = "unnamed_query"
    return normalized


def save_query_to_json(query_name: str, associations: list, output_dir: str = "data/output/json/") -> str:
    """
    Save associations for a single query to a JSON file.
    
    Args:
        query_name: The query string used for scraping
        associations: List of association dictionaries
        output_dir: Directory to save JSON files
    
    Returns:
        Path to the created JSON file
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Normalize filename
    filename = f"{normalize_filename(query_name)}.json"
    file_path = output_path / filename
    
    # Write JSON with proper formatting
    try:
        indent = settings.json_indent if hasattr(settings, "json_indent") else 2
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(associations, f, indent=indent, ensure_ascii=False)
        return str(file_path)
    except Exception as e:
        raise IOError(f"Failed to write JSON file {file_path}: {e}")


def save_all_queries_to_json(processed_data: dict, output_dir: str = None) -> list[str]:
    """
    Save all query results to individual JSON files.
    
    Args:
        processed_data: Dict of {query_name: associations}
        output_dir: Directory to save JSON files (uses settings.json_output_dir if None)
    
    Returns:
        List of created file paths
    """
    if output_dir is None:
        output_dir = settings.json_output_dir
    created_files = []
    for query_name, associations in processed_data.items():
        try:
            file_path = save_query_to_json(query_name, associations, output_dir)
            created_files.append(file_path)
        except Exception as e:
            print(f"Warning: Failed to save data for query '{query_name}': {e}")
            continue
    return created_files


def save_to_csv(processed_data, output_path: str = "data/output/output.csv"):
    """
    Legacy CSV export function for backward compatibility.
    Expects processed_data in the old format (list of dicts).
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(processed_data)
    df.to_csv(path, index=False, encoding="utf-8")
    return str(path)
