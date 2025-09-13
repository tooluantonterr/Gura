import nextcord
import os
import io
from datetime import datetime, timezone, timedelta
from modules.files import TicketMeta

class TicketCloseHandler:
    async def handle_close(self, interaction: nextcord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            pass
        
        channel = interaction.channel
        transcript_text = await self._generate_transcript(channel)

        await self._send_transcript(interaction, channel, transcript_text)

        await self._send_dm_transcript(interaction, channel, transcript_text)

        try:
            await channel.delete(reason=f"Тикет закрыт пользователем {interaction.user}")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Транскрипт отправлен, но не удалось удалить канал: {e}", ephemeral=True)

    async def _generate_transcript(self, channel) -> str:
        lines = []
        async for message in channel.history(limit=None, oldest_first=True):
            tz_msk = timezone(timedelta(hours=3))
            timestamp = message.created_at.astimezone(tz_msk).strftime("%d/%m/%Y %H:%M:%S")
            username = message.author.name
            discr = getattr(message.author, "discriminator", None)
            author_name = f"{username}#{discr}" if discr and discr != "0" else username
            
            content_lines = message.content.split("\n") if message.content else [""]
            if content_lines and content_lines[0] == "":
                content_lines = [""]
            
            first_line_prefix = f"{timestamp} | {author_name}: "
            if content_lines:
                lines.append(first_line_prefix + content_lines[0])
                for extra in content_lines[1:]:
                    lines.append(extra)
            else:
                lines.append(first_line_prefix)

            for att in message.attachments:
                try:
                    lines.append(att.url)
                except Exception:
                    pass

        return "\n".join(lines) if lines else f"Транскрипт пуст. Канал: {channel.name}"

    async def _send_transcript(self, interaction: nextcord.Interaction, channel, transcript_text: str):
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            transcript_path = os.path.join(project_root, "data", "transcript_channel_id.txt")
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript_channel_id_str = f.read().strip()
            transcript_channel_id = int(transcript_channel_id_str)
        except Exception as e:
            return await interaction.followup.send(f"❌ Не удалось прочитать transcript_channel_id: {e}", ephemeral=True)

        transcript_channel = interaction.guild.get_channel(transcript_channel_id)
        if not isinstance(transcript_channel, nextcord.TextChannel):
            return await interaction.followup.send("❌ Канал для транскриптов не найден или имеет неверный тип.", ephemeral=True)

        filename = f"{channel.name}.txt"
        file_obj = io.BytesIO(transcript_text.encode("utf-8-sig"))
        file_obj.seek(0)
        
        try:
            info_embed = await self._create_ticket_info_embed(interaction, channel)
            await transcript_channel.send(embed=info_embed, file=nextcord.File(file_obj, filename=filename))

            await self._send_backup_transcript(interaction, transcript_text, info_embed, filename)
            
        except Exception as e:
            return await interaction.followup.send(f"❌ Не удалось отправить транскрипт: {e}", ephemeral=True)

    async def _create_ticket_info_embed(self, interaction: nextcord.Interaction, channel) -> nextcord.Embed:
        category_text = "Неизвестно"
        created_by_text = "Неизвестно"

        async for message in channel.history(limit=1, oldest_first=True):
            if message.embeds:
                em = message.embeds[0]
                if em.title:
                    category_text = em.title.replace("**", "").strip()
                if em.fields:
                    for fld in em.fields:
                        if (fld.name or "").strip().lower().startswith("создатель"):
                            created_by_text = fld.value
                            break
            break

        if category_text == "Неизвестно" or created_by_text == "Неизвестно":
            meta = TicketMeta.get_ticket(channel.id) or {}
            if category_text == "Неизвестно":
                category_text = meta.get("category", category_text)
            if created_by_text == "Неизвестно":
                creator = interaction.guild.get_member(int(meta.get("creator_id", 0))) if meta.get("creator_id") else None
                if creator:
                    created_by_text = creator.mention

        tz_msk = timezone(timedelta(hours=3))
        now_ts = int(datetime.now(tz=tz_msk).timestamp())
        info_lines = [
            f"#️⃣ **Тикет:** `{channel.name}`",
            f"📋 **Категория:** **{category_text}**",
            f"✅ **Создатель:** {created_by_text}",
            f"🔒 **Закрыл:** {interaction.user.mention}",
            f"🕖 **Время:** <t:{now_ts}:R>",
        ]
        return nextcord.Embed(title="Информация о тикете", description="\n".join(info_lines), color=0x2b2d31)

    async def _send_backup_transcript(self, interaction: nextcord.Interaction, transcript_text: str, info_embed: nextcord.Embed, filename: str):
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            backup_path = os.path.join(project_root, "data", "transcript_backup_channel_id.txt")
            if os.path.exists(backup_path):
                with open(backup_path, "r", encoding="utf-8") as f:
                    backup_id_raw = f.read().strip()
                if backup_id_raw:
                    backup_channel = interaction.guild.get_channel(int(backup_id_raw))
                    if isinstance(backup_channel, nextcord.TextChannel):
                        backup_buf = io.BytesIO(transcript_text.encode("utf-8-sig"))
                        backup_buf.seek(0)
                        await backup_channel.send(embed=info_embed, file=nextcord.File(backup_buf, filename=filename))
        except Exception as e:
            try:
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                transcript_path = os.path.join(project_root, "data", "transcript_channel_id.txt")
                with open(transcript_path, "r", encoding="utf-8") as f:
                    transcript_channel_id_str = f.read().strip()
                transcript_channel = interaction.guild.get_channel(int(transcript_channel_id_str))
                if isinstance(transcript_channel, nextcord.TextChannel):
                    await transcript_channel.send(f"⚠️ Не удалось отправить транскрипт в канал бэкапов: {e}")
            except Exception:
                pass

    async def _send_dm_transcript(self, interaction: nextcord.Interaction, channel, transcript_text: str):
        meta = TicketMeta.get_ticket(channel.id) or {}
        dm_allowed = (int(meta.get("dm_transcript", 1)) == 1)
        creator_member = interaction.guild.get_member(int(meta.get("creator_id", 0))) if meta.get("creator_id") else None

        if dm_allowed and creator_member:
            try:
                filename = f"{channel.name}.txt"
                dm_file = io.BytesIO(transcript_text.encode("utf-8-sig"))
                dm_file.seek(0)
                await creator_member.send(
                    content=f"Ваш тикет #{channel.name} был закрыт. Ниже прикреплён транскрипт.",
                    file=nextcord.File(dm_file, filename=filename)
                )
            except Exception as e:
                try:
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                    transcript_path = os.path.join(project_root, "data", "transcript_channel_id.txt")
                    with open(transcript_path, "r", encoding="utf-8") as f:
                        transcript_channel_id_str = f.read().strip()
                    transcript_channel = interaction.guild.get_channel(int(transcript_channel_id_str))
                    if isinstance(transcript_channel, nextcord.TextChannel):
                        await transcript_channel.send(f"⚠️ Не удалось отправить транскрипт в ЛС {creator_member.mention if creator_member else ''}: {e}")
                except Exception:
                    pass
