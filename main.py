import os
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv

from config.settings import BOT_PREFIX, BOT_INTENTS
from data.manager import TicketDataManager
from modules.Embeds import EmbedBuilder
from modules.TicketSelect import TicketView
from modules.ticket.TicketButtons import TicketButtons
from utils.logger import bot_logger

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = nextcord.Intents.default()
for intent_name, enabled in BOT_INTENTS.items():
    setattr(intents, intent_name, enabled)

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

@bot.command()
async def appeal(ctx):
    try:
        categories = TicketDataManager.load_categories()
        view = TicketView(categories)
        await ctx.send(view=view, file=nextcord.File("assets/new_ticket.jpg", filename="new_ticket.jpg"))
        bot_logger.debug(f"Команда appeal выполнена пользователем {ctx.author}")
    except Exception as e:
        bot_logger.error(f"Ошибка в команде appeal: {e}")
        await ctx.send(embed=EmbedBuilder.error("Ошибка при создании тикета"))

@bot.event
async def on_ready():
    bot_logger.info(f"Бот запущен как {bot.user}")

    try:
        categories = TicketDataManager.load_categories()
        bot.add_view(TicketView(categories))
        bot.add_view(TicketButtons(categories))
        bot_logger.info("View компоненты успешно загружены")
    except Exception as e:
        bot_logger.error(f"Ошибка при загрузке view: {e}")

@bot.event
async def on_command_error(ctx, error):
    bot_logger.error(f"Ошибка команды {ctx.command}: {error}")
    if not ctx.response.is_done():
        await ctx.send(embed=EmbedBuilder.error("Произошла ошибка при выполнении команды"))

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        bot_logger.error(f"Критическая ошибка запуска бота: {e}")
        raise
