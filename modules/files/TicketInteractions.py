import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def load_ticket_categories():
    FILE_PATH = os.path.join(BASE_DIR, "data", "ticket_categories.json")
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_ticket_count() -> int:
    FILE_PATH = os.path.join(BASE_DIR, "data", "ticket_count.txt")
    if not os.path.exists(FILE_PATH):
        return 0
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        line = f.readline().strip()
        return int(line) if line.isdigit() else 0


def save_ticket_count(count: int):
    FILE_PATH = os.path.join(BASE_DIR, "data", "ticket_count.txt")
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(str(count))

def add_new_ticket() -> int:
    count = load_ticket_count()
    count += 1
    save_ticket_count(count)
    return count
