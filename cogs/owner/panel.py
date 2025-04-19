import discord

from core import ChillBot
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

class PanelCog(commands.Cog, name="Panel Cog"):
    def __init__(self, bot: ChillBot):
        self.bot = bot
        
    @commands.command(
        name="sync",
        description="Синхронизирует слеш-команды.",
    )
    @app_commands.describe(scope="Сфера должна быть `global` или `guild`.")
    @commands.is_owner()
    async def sync(self, context: Context, scope: str) -> None:
        if scope == "global":
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Слеш-команды были успешно синхронизированы во всех серверах.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed)
            return
        
        elif scope == "guild":
            context.bot.tree.copy_global_to(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description="Слеш-команды были успешно синхронизированы в данном сервере.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed)
            return
        
        embed = discord.Embed(
            description="Сфера должна быть `global` или `guild`.", color=0xE02B2B
        )
        await context.send(embed=embed)

    @commands.command(
        name="unsync",
        description="Рассинхронизирует слеш-команды.",
    )
    @app_commands.describe(scope="Сфера рассинхронизации. Может быть `global` или `guild`")
    @commands.is_owner()
    async def unsync(self, context: Context, scope: str) -> None:
        if scope == "global":
            context.bot.tree.clear_commands(guild=None)
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Слеш-команды были успешно рассинхронизированы во всех серверах.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed)
            return
        
        elif scope == "guild":
            context.bot.tree.clear_commands(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description="Слеш-команды были успешно рассинхронизированы в данном сервере.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed)
            return
        
        embed = discord.Embed(
            description="Сфера должна быть `global` или `guild`.", color=0xE02B2B)
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="load",
        description="Загрузить ког.",
    )
    @app_commands.describe(cog="Полный путь для загрузки кога (т.е., 'events.christmas')")
    @commands.is_owner()
    async def load(self, context: Context, cog: str) -> None:
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            embed = discord.Embed(
                description=f"Успешно загрузил ког `{cog}`.", color=0xBEBEFE
            )
        except Exception as e:
            embed = discord.Embed(
                description=f"Не смог загрузить ког `{cog}`. Ошибка: {e}", color=0xE02B2B
            )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="unload",
        description="Отгрузить ког.",
    )
    @app_commands.describe(cog="Полный путь для отгрузки кога (т.е., 'events.christmas')")
    @commands.is_owner()
    async def unload(self, context: Context, cog: str) -> None:
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            embed = discord.Embed(
                description=f"Успешно отгрузил ког `{cog}`.", color=0xBEBEFE
            )
        except Exception as e:
            embed = discord.Embed(
                description=f"Не смог отгрузить ког `{cog}`. Ошибка: {e}", color=0xE02B2B
            )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="reload",
        description="Перезагрузить ког.",
    )
    @app_commands.describe(cog="Полный путь для перезагрузки кога (т.е., 'events.christmas')")
    @commands.is_owner()
    async def reload(self, context: Context, cog: str) -> None:
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            embed = discord.Embed(
                description=f"Успешно перезагрузил ког `{cog}`", color=0xBEBEFE
            )
        except Exception as e:
            embed = discord.Embed(
                description=f"Не смог перезагрузить ког `{cog}`. Ошибка: {e}", color=0xE02B2B
            )
        await context.send(embed=embed)

async def setup(bot: ChillBot):
    await bot.add_cog(PanelCog(bot))