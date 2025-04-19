import time
import config
import asyncio
import discord
import schedule

from core import ChillBot
from discord import Activity, ActivityType, AllowedMentions, Intents, Status, MemberCacheFlags
from discord.ext import commands
from colorama import Back, Fore, Style, init

init()

bot = ChillBot(
    owner_ids=[622465815287169045, 953224156810453012],
    command_prefix=commands.when_mentioned_or('ct.', 'Ct.', 'cT.', 'CT.'),
    case_insensitive=True,
    intents=Intents().all(),
    help_command=None,
    shard_count=2,
    allowed_mentions=AllowedMentions(
        everyone=False
    ),
    member_cache_flags=MemberCacheFlags.all(),
    activity=Activity(type=ActivityType.custom, name="IP", state='play.chilltime.su'),
    status=Status.online,
    enable_debug_events=True,
    chunk_guilds_at_startup=True
)

@bot.event
async def on_ready():
    try:
        await bot.config.DB.cooldowns.delete_many({})

        current_time = (
            Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S") + Fore.BLUE + " CUR" + Back.RESET + Fore.WHITE + Style.BRIGHT
        )
        print(current_time + Fore.GREEN + f" Bot is ready! Logged in as {bot.user.name} (ID: {bot.user.id})")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    bot.run(config.Config.TOKEN)