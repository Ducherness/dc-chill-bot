import asyncio
import datetime

from core import ChillBot
from discord import Embed
from discord.ext import commands

class HandlersCog(commands.Cog, name="Handlers Cog"):
    def __init__(self, bot: ChillBot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.ban_handler())

    async def ban_handler(self):
        while True:
            await self.bot.wait_until_ready()

            db = self.bot.config.DB
            async for ban in db.bans.find({'timestamp': {'$lt': int(round(datetime.datetime.now().timestamp()))}}):
                try:
                    user = await self.bot.fetch_user(ban['_id'])
                    guild_id = ban.get('guild_id')
                    guild = self.bot.get_guild(guild_id) if guild_id else None

                    if guild:
                        await guild.unban(user, reason='Истёк срок бана')

                        embed = Embed(
                            description=f"**❗️Вы были разбанены на сервере {guild.name}.**",
                            timestamp=datetime.datetime.now()
                        )
                        embed.add_field(name="Модератор:", value=f"Консоль", inline=True)
                        embed.add_field(name="Причина:", value=f"Истекло время", inline=True)
                        embed.set_footer(text="ChillBot © 2025", icon_url=self.bot.user.avatar.url)

                        try:
                            await user.send(embed=embed)
                        except Exception as e:
                            print(f"Не удалось отправить сообщение пользователю {user.id}: {e}")

                    await db.bans.delete_one({'_id': ban['_id']})
                except Exception as e:
                    await db.bans.delete_one({'_id': ban['_id']})
                    print(f"Ошибка при обработке бана для пользователя {ban['_id']}: {e}")
                    continue

            await asyncio.sleep(600)

async def setup(bot: ChillBot):
    await bot.add_cog(HandlersCog(bot))