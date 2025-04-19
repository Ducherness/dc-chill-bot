import traceback
import discord
import math
import sys

from core import ChillBot
from discord import app_commands, Interaction, Embed
from discord.app_commands.errors import CheckFailure
from discord.ext import commands
from discord.ui import *

class ErrorHandlerCog(commands.Cog, name="Error Handler Cog"):
    def __init__(self, bot: ChillBot):
        self.bot = bot
        bot.tree.error(coro = self.__dispatch_to_app_command_handler)

    async def __dispatch_to_app_command_handler(self, interaction: Interaction, error: discord.app_commands.AppCommandError):
        self.bot.dispatch("app_command_error", interaction, error)

    @commands.Cog.listener("on_app_command_error")
    async def get_app_command_error(self, interaction: Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, CheckFailure):
            if "Недостаточно прав" in str(error):
                embed = Embed(
                    description=f"**❌ У вас недостаточно прав ( ` {str(error)} ` ) для выполнения данной команды!**"
                )
            else:
                embed = Embed(
                    description="**❌ У вас нет доступа к этой команде.**"
                )
        else:
            embed = Embed(
                description=f"**❌ ` {str(error)} ` **"
            )

        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Ошибка при отправке сообщения об ошибке: {e}")

async def setup(bot: ChillBot):
    await bot.add_cog(ErrorHandlerCog(bot))
