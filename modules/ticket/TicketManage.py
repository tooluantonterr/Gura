import nextcord
from modules import Permissions
from modules.ticket.TicketAssign import TicketAssignHandler
from modules.ticket.TicketUtils import TicketUtils

class TicketManageHandler:
    def __init__(self, categories: dict):
        self.categories = categories
        self.assign_handler = TicketAssignHandler()
        self.utils = TicketUtils()

    async def handle_manage(self, interaction: nextcord.Interaction):
        if not Permissions.has_permission_level(interaction.user, 1):
            return await interaction.response.send_message("❌ У вас нет прав для управления тикетами.", ephemeral=True)
        
        user_is_senior_admin = Permissions.is_senior_admin(interaction.user)
        from modules.files import TicketMeta
        meta = TicketMeta.get_ticket(interaction.channel.id) or {}
        dm_allowed = (int(meta.get("dm_transcript", 1)) == 1)

        options = [
            nextcord.SelectOption(
                label="Перенести в другую категорию",
                description="Переместить тикет в другую категорию",
                emoji="📁",
                value="move_category"
            ),
            nextcord.SelectOption(
                label="Быстрый ответ",
                description="Отправить преднастроенный ответ",
                emoji="⚡",
                value="fast_reply"
            ),
            nextcord.SelectOption(
                label=("Отключить отправку transcript в ЛС" if dm_allowed else "Включить отправку transcript в ЛС"),
                description="Переключить отправку транскрипта в личные сообщения",
                emoji="✅",
                value="toggle_dm_transcript"
            ),
            nextcord.SelectOption(
                label="Взять тикет",
                description="Назначить тикет на себя",
                emoji="🧩",
                value="assign_ticket_self"
            ),
        ]

        if user_is_senior_admin:
            options.insert(1, nextcord.SelectOption(
                label="Назначить тикет",
                description="Назначить тикет на пользователя (Ст.Админ+)",
                emoji="👤",
                value="assign_ticket"
            ))
            options.insert(2, nextcord.SelectOption(
                label="Добавить быстрый ответ",
                description="Создать/обновить алиас (Ст.Админ+)",
                emoji="📝",
                value="add_fast_reply"
            ))

        select = nextcord.ui.Select(
            placeholder="Выберите действие",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="manage_ticket_select"
        )

        view = nextcord.ui.View(timeout=60)
        view.add_item(select)

        async def select_callback(inter: nextcord.Interaction):
            choice = select.values[0]
            
            try:
                if choice == "move_category":
                    await self._handle_move_category(inter)
                elif choice == "assign_ticket":
                    await self.assign_handler.handle_assign_ticket(inter)
                elif choice == "assign_ticket_self":
                    await self.assign_handler.handle_assign_ticket_self(inter)
                elif choice == "fast_reply":
                    await self._handle_fast_reply(inter)
                elif choice == "add_fast_reply":
                    await self._handle_add_fast_reply(inter)
                elif choice == "toggle_dm_transcript":
                    await self._handle_toggle_dm_transcript(inter)
                else:
                    await inter.response.send_message("❌ Неизвестное действие.", ephemeral=True)
            except Exception as e:
                try:
                    await inter.response.send_message(f"❌ Ошибка при выполнении действия: {str(e)}", ephemeral=True)
                except:
                    pass

        select.callback = select_callback
        await interaction.response.send_message("Выберите действие для управления тикетом:", view=view, ephemeral=True)

    async def _handle_move_category(self, interaction: nextcord.Interaction):
        options = [
            nextcord.SelectOption(label=label, description=data.get("description", ""))
            for label, data in self.categories.items()
        ]

        select = nextcord.ui.Select(
            placeholder="Выберите новую категорию",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="move_ticket_select"
        )

        view = nextcord.ui.View(timeout=60)
        view.add_item(select)

        async def select_callback(inter: nextcord.Interaction):
            choice = select.values[0]
            config = self.categories[choice]

            new_category = inter.guild.get_channel(config["category_id"])
            if not isinstance(new_category, nextcord.CategoryChannel):
                return await inter.response.send_message("❌ Категория не найдена", ephemeral=True)

            await inter.channel.edit(category=new_category, reason=f"Перенос тикета в {choice}")
            
            try:
                from modules.Embeds import Embeds
                form = [
                    "Ваш никнейм в игре",
                    "Подробное описание вашей проблемы (Опишите ситуацию / проблему детально)",
                    "Если этого требует ситуация, предоставьте док-ва, которые будут отражать суть проблемы (Подойдут как скриншоты, так и видео)"
                ]
                async for message in inter.channel.history(limit=1, oldest_first=True):
                    if message.embeds:
                        new_embed = Embeds.ticket_welcome(choice, form, inter.user)
                        await message.edit(embed=new_embed)
                        break
            except Exception as e:
                print(f"Ошибка при обновлении embed: {e}")
            
            await inter.response.send_message(f"✅ Тикет перенесён в категорию **{choice}**", ephemeral=True)

        select.callback = select_callback
        await interaction.response.send_message("Выберите новую категорию для переноса:", view=view, ephemeral=True)

    async def _handle_fast_reply(self, interaction: nextcord.Interaction):
        from modules.files import AliasInteractions
        aliases = AliasInteractions.list_alias_names()
        if not aliases:
            return await interaction.response.send_message("❌ Список быстрых ответов пуст.", ephemeral=True)

        options = [nextcord.SelectOption(label=name, value=name) for name in aliases]
        select = nextcord.ui.Select(
            placeholder="Выберите быстрый ответ",
            min_values=1, max_values=1, options=options
        )
        view = nextcord.ui.View(timeout=60)
        view.add_item(select)

        async def select_callback(inter: nextcord.Interaction):
            name = select.values[0]
            text = AliasInteractions.get_alias(name) or ""
            if not text:
                return await inter.response.send_message("❌ Текст ответа не найден.", ephemeral=True)

            mention = ""
            if isinstance(inter.channel.topic, str):
                try:
                    parts = dict(item.split('=', 1) for item in inter.channel.topic.split('|') if '=' in item)
                    creator_id = int(parts.get('creator_id', '0'))
                    if creator_id:
                        mention = f"<@{creator_id}>\n"
                except Exception:
                    pass

            code_block = f"{mention}```{text}```"
            await inter.response.send_message(code_block, ephemeral=True)

        select.callback = select_callback
        await interaction.response.send_message(
            "Выберите быстрый ответ:",
            view=view, ephemeral=True
        )

    async def _handle_add_fast_reply(self, interaction: nextcord.Interaction):
        if not Permissions.is_senior_admin(interaction.user):
            return await interaction.response.send_message("❌ Нет прав. Требуется Ст.Админ+.", ephemeral=True)

        modal = nextcord.ui.Modal(title="Добавить быстрый ответ")
        name_input = nextcord.ui.TextInput(
            label="Ключ (alias)", placeholder="Например: rules_warning",
            required=True, max_length=64
        )
        text_input = nextcord.ui.TextInput(
            label="Текст ответа", style=nextcord.TextInputStyle.paragraph,
            required=True, max_length=2000
        )
        modal.add_item(name_input)
        modal.add_item(text_input)

        async def modal_callback(modal_inter: nextcord.Interaction):
            from modules.files import AliasInteractions
            name = name_input.value.strip()
            text = text_input.value.strip()
            AliasInteractions.set_alias(name, text)
            await modal_inter.response.send_message(f"✅ Быстрый ответ '{name}' сохранён.", ephemeral=True)

        modal.callback = modal_callback
        await interaction.response.send_modal(modal)

    async def _handle_toggle_dm_transcript(self, interaction: nextcord.Interaction):
        from modules.files import TicketMeta
        meta = TicketMeta.get_ticket(interaction.channel.id) or {}
        current = int(meta.get("dm_transcript", 1)) == 1
        TicketMeta.update_ticket(interaction.channel.id, {"dm_transcript": 0 if current else 1})
        await interaction.response.send_message(
            f"✅ Отправка transcript в ЛС теперь: {'выключена' if current else 'включена'}.",
            ephemeral=True
        )
