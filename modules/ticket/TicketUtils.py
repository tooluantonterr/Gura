import nextcord
from modules.files import TicketMeta

class TicketUtils:
    async def grant_channel_access(self, channel: nextcord.abc.GuildChannel, member: nextcord.Member):
        """Выдает доступ к каналу пользователю"""
        try:
            overwrite = nextcord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
            )
            await channel.set_permissions(member, overwrite=overwrite, reason="Ticket access granted")
        except Exception:
            pass

    async def reassign_if_needed(self, guild: nextcord.Guild, channel: nextcord.abc.GuildChannel, new_member: nextcord.Member):
        """Переназначает тикет: убирает доступ у старого исполнителя и выдает новому"""
        meta = TicketMeta.get_ticket(channel.id) or {}
        old_assignee_id = int(meta.get("assignee_id", 0) or 0)
        if old_assignee_id and old_assignee_id != new_member.id:
            old_member = guild.get_member(old_assignee_id)
            if old_member is not None:
                try:
                    await channel.set_permissions(old_member, overwrite=None, reason="Ticket reassigned")
                except Exception:
                    pass
        await self.grant_channel_access(channel, new_member)

    async def send_workload_message(self, channel: nextcord.abc.Messageable, creator_id: int, assignee_id: int, level: str):
        """Отправляет сообщение о загруженности в канал"""
        user_mention = f"<@{creator_id}>"
        assigned_mention = f"<@{assignee_id}>"
        level = (level or "low").lower()

        low_line = "Предварительно предоставьте в тикет необходимую информацию по вашему обращению, если того требует ситуация!"
        med_line = "На данный момент открыто достаточно много тикетов, но мы постараемся решить ваш вопрос в ближайшее время!"
        high_line = "На данный момент решение по тикету может задерживаться из-за высокой нагрузки, пожалуйста, наберитесь терпения и не пингуйте весь состав!"

        level_text = {
            "low": low_line,
            "medium": med_line,
            "high": high_line,
        }.get(level, low_line)

        content = (
            f"Здравствуйте, {user_mention}!\n\n"
            f"Благодарим вас за обращение!\n\n"
            f"{level_text}\n\n"
            f"Вашим тикетом займётся {assigned_mention}!"
        )

        await channel.send(content)
