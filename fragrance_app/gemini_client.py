
from typing import Dict
def fetch_fragrance_data(name: str) -> Dict:
    return {
        "name": name,
        "longevity": "8+ HRS",
        "projection": "2+ FEET",
        "when": ["Fall", "Winter"],
        "where": ["Evenings", "Formal", "Night Outs"],
        "profile": ["Woody", "Smoky", "Aromatic"],
        "notes": ["Cypriol", "Amyris", "Atlas Cedar"],
        "year": "2024",
        "rating": "8.1/10",
        "description": f"{name} is a rich, smoky, long-lasting evening scent built for cool weather."
    }
