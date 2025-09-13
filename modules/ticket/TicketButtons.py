import nextcord
from modules.ticket.TicketClose import TicketCloseHandler
from modules.ticket.TicketManage import TicketManageHandler

class TicketButtons(nextcord.ui.View):
    def __init__(self, categories: dict):
        super().__init__(timeout=None)
        self.categories = categories
        self.close_handler = TicketCloseHandler()
        self.manage_handler = TicketManageHandler(categories)

    @nextcord.ui.button(label="Закрыть", style=nextcord.ButtonStyle.primary, custom_id="ticket_close")
    async def close_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.close_handler.handle_close(interaction)

    @nextcord.ui.button(label="Управление", style=nextcord.ButtonStyle.primary, custom_id="ticket_manage")
    async def manage_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.manage_handler.handle_manage(interaction)
