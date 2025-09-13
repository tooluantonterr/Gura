
import nextcord
from typing import Optional, Dict, Any
from config.settings import UI_TIMEOUTS, EMBED_COLORS
from config.constants import CUSTOM_IDS, EMOJIS
from utils.logger import ticket_logger
from utils.exceptions import TicketBotException

class BaseView(nextcord.ui.View):
    def __init__(self, timeout: Optional[int] = UI_TIMEOUTS["default"], **kwargs):
        super().__init__(timeout=timeout)
        self.logger = ticket_logger
        self._setup_view(**kwargs)
    
    def _setup_view(self, **kwargs):
        pass
    
    async def on_error(self, interaction: nextcord.Interaction, error: Exception, item: nextcord.ui.Item):
        self.logger.error(f"Ошибка в {self.__class__.__name__}: {error}")
        
        if not interaction.response.is_done():
            embed = self._create_error_embed(str(error))
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = self._create_error_embed(str(error))
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    def _create_error_embed(self, error_message: str) -> nextcord.Embed:
        embed = nextcord.Embed(
            title=f"{EMOJIS['error']} Ошибка",
            description=f"Произошла ошибка: {error_message}",
            color=EMBED_COLORS["error"]
        )
        return embed

class BaseSelect(nextcord.ui.Select):
    def __init__(self, custom_id: str, placeholder: str, **kwargs):
        super().__init__(custom_id=custom_id, placeholder=placeholder, **kwargs)
        self.logger = ticket_logger
    
    async def callback(self, interaction: nextcord.Interaction):
        pass

class BaseButton(nextcord.ui.Button):
    def __init__(self, custom_id: str, label: str, style: nextcord.ButtonStyle = nextcord.ButtonStyle.primary, **kwargs):
        super().__init__(custom_id=custom_id, label=label, style=style, **kwargs)
        self.logger = ticket_logger
    
    async def callback(self, interaction: nextcord.Interaction):
        pass

class BaseModal(nextcord.ui.Modal):
    def __init__(self, title: str, **kwargs):
        super().__init__(title=title, **kwargs)
        self.logger = ticket_logger
    
    async def on_submit(self, interaction: nextcord.Interaction):
        pass
