import nextcord
from typing import Optional
from data.manager import PermissionDataManager
from config.settings import MIN_PERMISSION_LEVELS
from utils.logger import permission_logger
from utils.exceptions import PermissionError

class PermissionManager:
    @staticmethod
    def get_user_permission_level(user: nextcord.Member) -> int:
        roles = PermissionDataManager.load_roles()
        permission_levels = PermissionDataManager.load_permission_levels()
        max_level = 0
        
        for role in user.roles:
            for role_name, role_id in roles.items():
                if role.id == role_id:
                    level = permission_levels.get(role_name, 0)
                    max_level = max(max_level, level)
                    permission_logger.debug(f"Пользователь {user} имеет роль {role_name} (уровень {level})")
                    break

        permission_logger.debug(f"Максимальный уровень прав пользователя {user}: {max_level}")
        return max_level
    
    @staticmethod
    def has_permission_level(user: nextcord.Member, required_level: int) -> bool:
        user_level = PermissionManager.get_user_permission_level(user)
        has_permission = user_level >= required_level
        
        permission_logger.debug(f"Проверка прав: {user} (уровень {user_level}) >= {required_level} = {has_permission}")
        return has_permission
    
    @staticmethod
    def is_senior_admin(user: nextcord.Member) -> bool:
        return PermissionManager.has_permission_level(user, MIN_PERMISSION_LEVELS["assign_ticket"])
    
    @staticmethod
    def can_manage_ticket(user: nextcord.Member) -> bool:
        return PermissionManager.has_permission_level(user, MIN_PERMISSION_LEVELS["manage_ticket"])
    
    @staticmethod
    def can_close_ticket(user: nextcord.Member) -> bool:
        return PermissionManager.has_permission_level(user, MIN_PERMISSION_LEVELS["close_ticket"])
    
    @staticmethod
    def can_send_transcript(user: nextcord.Member) -> bool:
        return PermissionManager.has_permission_level(user, MIN_PERMISSION_LEVELS["send_transcript"])
    
    @staticmethod
    def require_permission_level(user: nextcord.Member, required_level: int, action: str = "выполнить это действие") -> None:
        if not PermissionManager.has_permission_level(user, required_level):
            raise PermissionError(f"Недостаточно прав для {action}")
    
    @staticmethod
    def get_user_level(user: nextcord.Member) -> int:
        return PermissionManager.get_user_permission_level(user)

def is_senior_admin(user: nextcord.Member) -> bool:
    return PermissionManager.is_senior_admin(user)

def has_permission_level(user: nextcord.Member, required_level: int) -> bool:
    return PermissionManager.has_permission_level(user, required_level)

def get_user_level(user: nextcord.Member) -> int:
    return PermissionManager.get_user_level(user)