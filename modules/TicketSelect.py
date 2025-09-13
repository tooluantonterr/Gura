import asyncio

import nextcord

from config.settings import TICKET_FORM

from modules.Embeds import Embeds
from modules.files import TicketMeta
from modules.ticket.TicketButtons import TicketButtons
from modules.files import TicketInteractions

TICKET_CATEGORIES = TicketInteractions.load_ticket_categories()

class TicketSelect(nextcord.ui.Select):
    def __init__(self, categories: dict):
        self.categories = categories
        options = [
            nextcord.SelectOption(
                label=label,
                description=data.get("description", "Создать обращение"),
                emoji=data.get("emoji", "📩")
            )
            for label, data in categories.items()
        ]

        super().__init__(
            placeholder="Выберите причину",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_select"
        )

    async def callback(self, interaction: nextcord.Interaction):
        try:
            await interaction.response.defer()
        except Exception:
            pass

        global TICKET_CATEGORIES
        TICKET_CATEGORIES = TicketInteractions.load_ticket_categories()

        choice = self.values[0]
        user = interaction.user
        config = TICKET_CATEGORIES[choice]

        category = interaction.guild.get_channel(config["category_id"])

        overwrites = {
            interaction.guild.default_role: nextcord.PermissionOverwrite(view_channel=False),
            user: nextcord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        await asyncio.sleep(1)
        for role_id in config["roles"]:
            role = interaction.guild.get_role(role_id)
            if role:
                overwrites[role] = nextcord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await category.create_text_channel(
            f"ticket-{TicketInteractions.load_ticket_count()}",
            overwrites=overwrites
        )

        TicketInteractions.add_new_ticket()
        TicketMeta.set_ticket(channel.id, {
            "category": choice,
            "creator_id": user.id,
            "dm_transcript": 1
        })

        if choice.strip().lower() == "внутриигровые вопросы":
            await channel.send(
                content=f"{user.mention}",
                view=TicketButtons(categories=self.categories),
                file=nextcord.File("assets/server_ticket.jpg", filename="server_ticket.jpg")
            )
        else:
            welcome = Embeds.ticket_welcome(choice, TICKET_FORM, user)
            await channel.send(
                content=f"{user.mention}",
                embed=welcome,
                view=TicketButtons(categories=self.categories)
            )

        new_view = TicketView(TICKET_CATEGORIES)
        try:
            await interaction.edit_original_message(view=new_view)
        except Exception:
            try:
                msg = await interaction.original_message()
                await msg.edit(view=new_view)
            except Exception:
                pass


class TicketView(nextcord.ui.View):
    def __init__(self, categories: dict):
        super().__init__(timeout=None)
        self.add_item(TicketSelect(categories))
