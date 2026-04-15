from dataclasses import dataclass
from typing import List


@dataclass
class Herb:
    main_name: str
    synonyms: List[str]
