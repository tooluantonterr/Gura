import json
import os

import nextcord

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def load_roles():
    FILE_PATH = os.path.join(BASE_DIR, "data", "roles.json")
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_permission_levels():
    FILE_PATH = os.path.join(BASE_DIR, "data", "permissions_levels.json")
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_user_permission_level(user: nextcord.Member) -> int:
    permission_levels = load_permission_levels()
    roles = load_roles()
    max_level = 0
    
    for role in user.roles:
        for role_name, role_id in roles.items():
            if role.id == role_id:
                level = permission_levels.get(role_name, 0)
                max_level = max(max_level, level)
                break
    
    return max_level