import functools

from core import ChillBot
from discord import Interaction, Embed
from typing import Literal, Callable, Coroutine
from ..cooldowns import is_cooldown, set_cooldown

CooldownType = Literal['global', 'local']

def cooldown_decorator(type: CooldownType, system: str, time: str) -> Callable:
    def wrapper(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        @functools.wraps(func)
        async def inner(self, interaction: Interaction, *args, **kwargs):
            bot: ChillBot = self.bot
            user_id = interaction.user.id

            if user_id in bot.owner_ids:
                return await func(self, interaction, *args, **kwargs)

            remaining_time = await is_cooldown(bot, type, system, user_id)
            if remaining_time is not None:       
                minutes, seconds = divmod(remaining_time, 60)
                embed = Embed(
                    description=f"**Подождите `{minutes}` мин `{seconds}` сек перед повторным использованием команды!**"
                    )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            await set_cooldown(bot, type, system, user_id, time)
            return await func(self, interaction, *args, **kwargs)

        return inner
    return wrapper
