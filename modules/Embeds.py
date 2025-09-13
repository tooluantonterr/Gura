import nextcord
from datetime import datetime
from typing import List, Optional
from config.settings import EMBED_COLORS, TICKET_FORM
from config.constants import EMOJIS, SUCCESS_MESSAGES
from utils.logger import ticket_logger

class EmbedBuilder:
    @staticmethod
    def create_ticket() -> nextcord.Embed:
        embed = nextcord.Embed(color=EMBED_COLORS["default"])
        embed.set_image(url="attachment://new_ticket.jpg")
        return embed

    @staticmethod
    def ticket_welcome(category_name: str, form: Optional[List[str]] = None, user: Optional[nextcord.Member] = None) -> nextcord.Embed:
        form = form or TICKET_FORM
        form_text = "\n".join([f"{i + 1}. {line}" for i, line in enumerate(form)])

        embed = nextcord.Embed(
            title=f"{EMOJIS['ticket']} **{category_name}**",
            description=f"**{form_text}**",
            color=EMBED_COLORS["info"]
        )
        
        if user:
            embed.add_field(
                name="Создатель тикета",
                value=f"{user.mention}",
                inline=True
            )
        
        embed.add_field(
            name="Время создания",
            value=f"<t:{int(datetime.now().timestamp())}:F>",
            inline=True
        )
        
        if category_name.strip().lower() == "внутриигровые вопросы":
            embed.set_image(url="attachment://server_ticket.jpg")
        embed.set_footer(text="Опишите вашу проблему подробно")
        return embed

    @staticmethod
    def ticket_assigned(assigned_user: nextcord.Member, assigner: nextcord.Member) -> nextcord.Embed:
        embed = nextcord.Embed(
            title=f"{EMOJIS['assign']} Тикет назначен",
            description=SUCCESS_MESSAGES["ticket_assigned"].format(
                user=assigned_user.mention,
                assigner=assigner.mention
            ),
            color=EMBED_COLORS["success"]
        )
        embed.add_field(
            name="Время назначения",
            value=f"<t:{int(datetime.now().timestamp())}:F>",
            inline=True
        )
        embed.set_footer(text=f"ID назначенного: {assigned_user.id}")
        return embed

    @staticmethod
    def ticket_taken(user: nextcord.Member) -> nextcord.Embed:
        embed = nextcord.Embed(
            title=f"{EMOJIS['assign']} Тикет взят в работу",
            description=SUCCESS_MESSAGES["ticket_taken"].format(user=user.mention),
            color=EMBED_COLORS["success"]
        )
        embed.add_field(
            name="Время взятия",
            value=f"<t:{int(datetime.now().timestamp())}:F>",
            inline=True
        )
        embed.set_footer(text=f"ID пользователя: {user.id}")
        return embed

    @staticmethod
    def ticket_moved(category_name: str) -> nextcord.Embed:
        embed = nextcord.Embed(
            title=f"{EMOJIS['move']} Тикет перенесен",
            description=SUCCESS_MESSAGES["ticket_moved"].format(category=category_name),
            color=EMBED_COLORS["success"]
        )
        embed.add_field(
            name="Время переноса",
            value=f"<t:{int(datetime.now().timestamp())}:F>",
            inline=True
        )
        return embed

    @staticmethod
    def error(message: str) -> nextcord.Embed:
        embed = nextcord.Embed(
            title=f"{EMOJIS['error']} Ошибка",
            description=message,
            color=EMBED_COLORS["error"]
        )
        return embed

    @staticmethod
    def warning(message: str) -> nextcord.Embed:
        embed = nextcord.Embed(
            title=f"{EMOJIS['warning']} Предупреждение",
            description=message,
            color=EMBED_COLORS["warning"]
        )
        return embed

    @staticmethod
    def info(message: str) -> nextcord.Embed:
        embed = nextcord.Embed(
            title=f"{EMOJIS['info']} Информация",
            description=message,
            color=EMBED_COLORS["info"]
        )
        return embed

class Embeds:
    @staticmethod
    def create_ticket():
        return EmbedBuilder.create_ticket()
    
    @staticmethod
    def ticket_welcome(category_name: str, form: List[str], user: nextcord.Member):
        return EmbedBuilder.ticket_welcome(category_name, form, user)