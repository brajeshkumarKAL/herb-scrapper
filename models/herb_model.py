from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Herb:
    main_name: str
    synonyms: List[str]
    query_results: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
