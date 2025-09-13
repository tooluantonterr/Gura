import json
import os
from typing import Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ALIASES_FILE = os.path.join(BASE_DIR, "data", "aliases.json")


def _ensure_file():
    os.makedirs(os.path.dirname(ALIASES_FILE), exist_ok=True)
    if not os.path.exists(ALIASES_FILE):
        with open(ALIASES_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)


def load_aliases() -> Dict[str, str]:
    _ensure_file()
    try:
        with open(ALIASES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_aliases(data: Dict[str, str]) -> None:
    _ensure_file()
    with open(ALIASES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def list_alias_names() -> List[str]:
    return list(load_aliases().keys())


def get_alias(name: str) -> Optional[str]:
    return load_aliases().get(name)


def set_alias(name: str, text: str) -> None:
    data = load_aliases()
    data[name] = text
    save_aliases(data)


