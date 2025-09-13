import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from config.settings import (
    ROLES_FILE, PERMISSIONS_LEVELS_FILE, 
    TICKET_CATEGORIES_FILE, TICKET_COUNT_FILE
)
from utils.logger import bot_logger
from utils.exceptions import DataError

class DataManager:
    @staticmethod
    def load_json(file_path: Path) -> Dict[str, Any]:
        try:
            if not file_path.exists():
                bot_logger.warning(f"Файл {file_path} не найден")
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            bot_logger.error(f"Ошибка парсинга JSON файла {file_path}: {e}")
            raise DataError(f"Ошибка парсинга JSON файла: {e}")
        except Exception as e:
            bot_logger.error(f"Ошибка загрузки файла {file_path}: {e}")
            raise DataError(f"Ошибка загрузки файла: {e}")
    
    @staticmethod
    def save_json(file_path: Path, data: Dict[str, Any]) -> None:
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            bot_logger.error(f"Ошибка сохранения файла {file_path}: {e}")
            raise DataError(f"Ошибка сохранения файла: {e}")
    
    @staticmethod
    def load_text(file_path: Path) -> str:
        try:
            if not file_path.exists():
                return ""
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            bot_logger.error(f"Ошибка загрузки текстового файла {file_path}: {e}")
            raise DataError(f"Ошибка загрузки текстового файла: {e}")
    
    @staticmethod
    def save_text(file_path: Path, content: str) -> None:
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            bot_logger.error(f"Ошибка сохранения текстового файла {file_path}: {e}")
            raise DataError(f"Ошибка сохранения текстового файла: {e}")

class TicketDataManager(DataManager):
    @staticmethod
    def load_categories() -> Dict[str, Any]:
        return DataManager.load_json(TICKET_CATEGORIES_FILE)
    
    @staticmethod
    def load_ticket_count() -> int:
        try:
            content = DataManager.load_text(TICKET_COUNT_FILE)
            return int(content) if content.isdigit() else 0
        except ValueError:
            bot_logger.warning("Неверный формат счетчика тикетов, возвращаем 0")
            return 0
    
    @staticmethod
    def save_ticket_count(count: int) -> None:
        DataManager.save_text(TICKET_COUNT_FILE, str(count))
    
    @staticmethod
    def increment_ticket_count() -> int:
        count = TicketDataManager.load_ticket_count()
        count += 1
        TicketDataManager.save_ticket_count(count)
        return count

class PermissionDataManager(DataManager):
    @staticmethod
    def load_roles() -> Dict[str, int]:
        return DataManager.load_json(ROLES_FILE)
    
    @staticmethod
    def load_permission_levels() -> Dict[str, int]:
        return DataManager.load_json(PERMISSIONS_LEVELS_FILE)
