import nextcord
from datetime import datetime, timezone
from modules import Permissions
from modules.files import TicketMeta
from modules.Embeds import Embeds
from modules.ticket.TicketUtils import TicketUtils

class TicketAssignHandler:
    def __init__(self):
        self.utils = TicketUtils()

    async def handle_assign_ticket(self, interaction: nextcord.Interaction):
        if not Permissions.is_senior_admin(interaction.user):
            return await interaction.response.send_message("❌ У вас нет прав для назначения тикетов. Требуется роль Ст.Админа или выше.", ephemeral=True)

        channel_name = interaction.channel.name
        if False and "assigned" in channel_name.lower():
            return await interaction.response.send_message("❌ Этот тикет уже назначен на кого-то.", ephemeral=True)

        modal = nextcord.ui.Modal(title="Назначить тикет")

        user_input = nextcord.ui.TextInput(
            label="Пользователь для назначения",
            placeholder="Введите имя, никнейм, ID или @упоминание пользователя",
            required=True,
            max_length=100
        )

        modal.add_item(user_input)

        async def modal_callback(modal_interaction: nextcord.Interaction):
            user_text = user_input.value.strip()
            target_user = None

            try:
                if user_text.startswith('<@') and user_text.endswith('>'):
                    user_id = int(user_text[2:-1])
                    target_user = modal_interaction.guild.get_member(user_id)
                elif user_text.isdigit():
                    target_user = modal_interaction.guild.get_member(int(user_text))
                else:
                    target_user = self._find_user_by_name(modal_interaction.guild, user_text)

                if not target_user:
                    return await modal_interaction.response.send_message(
                        "❌ Пользователь не найден. Попробуйте:\n• Точное имя/никнейм\n• ID пользователя\n• @упоминание", 
                        ephemeral=True
                    )

                if not Permissions.has_permission_level(target_user, 1):
                    return await modal_interaction.response.send_message(
                        f"❌ У пользователя {target_user.mention} нет прав для работы с тикетами.", 
                        ephemeral=True
                    )

                await self._show_workload_selection(modal_interaction, target_user)

            except ValueError:
                await modal_interaction.response.send_message("❌ Неверный формат ID пользователя.", ephemeral=True)
            except Exception as e:
                await modal_interaction.response.send_message(f"❌ Ошибка при назначении тикета: {str(e)}", ephemeral=True)

        modal.callback = modal_callback
        await interaction.response.send_modal(modal)

    def _find_user_by_name(self, guild, user_text: str):
        """Поиск пользователя по частичному совпадению имени"""
        search_text = user_text.lower()
        candidates = []
        
        for member in guild.members:
            if member.bot:
                continue

            if (search_text in member.name.lower() or 
                search_text in member.display_name.lower() or
                search_text in member.global_name.lower() if member.global_name else False):
                candidates.append(member)
        
        if len(candidates) == 1:
            return candidates[0]
        elif len(candidates) > 1:
            candidate_list = "\n".join([f"• {m.display_name} (ID: {m.id})" for m in candidates[:5]])
            raise ValueError(f"Найдено несколько пользователей:\n{candidate_list}\n\nУточните поиск или используйте ID.")
        
        return None

    async def _show_workload_selection(self, modal_interaction: nextcord.Interaction, target_user):
        workload_options = [
            nextcord.SelectOption(label="low", value="low", description="Низкая загруженность"),
            nextcord.SelectOption(label="medium", value="medium", description="Средняя загруженность"),
            nextcord.SelectOption(label="high", value="high", description="Высокая загруженность"),
        ]
        workload_select = nextcord.ui.Select(
            placeholder="Выберите уровень загруженности",
            min_values=1, max_values=1, options=workload_options
        )
        workload_view = nextcord.ui.View(timeout=60)
        workload_view.add_item(workload_select)

        async def wl_select_callback(wl_inter: nextcord.Interaction):
            level = workload_select.values[0]

            await self.utils.reassign_if_needed(
                guild=wl_inter.guild,
                channel=wl_inter.channel,
                new_member=target_user,
            )

            TicketMeta.update_ticket(
                wl_inter.channel.id,
                {
                    "assignee_id": target_user.id,
                    "assigned_by": wl_inter.user.id,
                    "assigned_at": int(datetime.now(timezone.utc).timestamp()),
                    "workload": level,
                },
            )

            try:
                await wl_inter.channel.send(embed=Embeds.ticket_assigned(target_user, wl_inter.user))
            except Exception:
                pass

            try:
                meta2 = TicketMeta.get_ticket(wl_inter.channel.id) or {}
                creator_id2 = int(meta2.get("creator_id", wl_inter.user.id))
                await self.utils.send_workload_message(
                    channel=wl_inter.channel,
                    creator_id=creator_id2,
                    assignee_id=target_user.id,
                    level=level,
                )
            except Exception:
                pass

            await wl_inter.response.send_message(f"Назначено. Уровень загруженности: {level}", ephemeral=True)

        workload_select.callback = wl_select_callback
        await modal_interaction.response.send_message(
            f"Выбран пользователь: {target_user.mention}\nВыберите уровень загруженности:",
            view=workload_view,
            ephemeral=True
        )

    async def handle_assign_ticket_self(self, interaction: nextcord.Interaction):
        channel_name = interaction.channel.name

        try:
            meta0 = TicketMeta.get_ticket(interaction.channel.id) or {}
            current_assignee_id = int(meta0.get("assignee_id", 0) or 0)
            if current_assignee_id and current_assignee_id != interaction.user.id:
                assignee_member = interaction.guild.get_member(current_assignee_id)
                mention = assignee_member.mention if assignee_member else f"<@{current_assignee_id}>"
                return await interaction.response.send_message(f"Тикет уже назначен: {mention}", ephemeral=True)

            await self._show_self_workload_selection(interaction)
            return
        except Exception as e:
            await interaction.response.send_message(f"❌ Ошибка при проверке тикета: {str(e)}", ephemeral=True)
            return

    async def _show_self_workload_selection(self, interaction: nextcord.Interaction):
        options = [
            nextcord.SelectOption(label="low", value="low", description="Низкая загруженность"),
            nextcord.SelectOption(label="medium", value="medium", description="Средняя загруженность"),
            nextcord.SelectOption(label="high", value="high", description="Высокая загруженность"),
        ]
        select = nextcord.ui.Select(
            placeholder="Выберите уровень загруженности",
            min_values=1, max_values=1, options=options
        )
        view = nextcord.ui.View(timeout=60)
        view.add_item(select)

        async def wl_self_callback(inter: nextcord.Interaction):
            level = select.values[0]
            await self.utils.grant_channel_access(inter.channel, inter.user)

            TicketMeta.update_ticket(
                inter.channel.id,
                {
                    "assignee_id": inter.user.id,
                    "assigned_by": inter.user.id,
                    "assigned_at": int(datetime.now(timezone.utc).timestamp()),
                    "workload": level,
                },
            )

            try:
                await inter.channel.send(embed=Embeds.ticket_taken(inter.user))
            except Exception:
                pass
            try:
                meta2 = TicketMeta.get_ticket(inter.channel.id) or {}
                creator_id2 = int(meta2.get("creator_id", inter.user.id))
                await self.utils.send_workload_message(
                    channel=inter.channel,
                    creator_id=creator_id2,
                    assignee_id=inter.user.id,
                    level=level,
                )
            except Exception:
                pass

            await inter.response.send_message(f"Вы взяли тикет. Загруженность: {level}", ephemeral=True)

        select.callback = wl_self_callback
        await interaction.response.send_message(
            "Выберите уровень загруженности:",
            view=view,
            ephemeral=True
        )
