import discord
import datetime
import asyncio

from core import ChillBot
from config import Config
from discord import app_commands, Embed, Member, User, Interaction
from discord.ext import commands
from modules import convert_time_to_seconds
from modules.decorators import has_access
from modules.personal import get_permissions, set_permissions
from modules.utilities import delete_ban, set_ban
from modules.cooldowns import set_cooldown, is_cooldown

class SystemCog(commands.Cog, name="System Cog"):
    def __init__(self, bot: ChillBot):
        self.bot = bot

    @app_commands.command(name="perm", description="Выдать технические права к боту ChillBot.")
    @app_commands.describe(member="пользователь", lvl="уровень")
    @has_access(administrator=True)
    async def perm(self, interaction: Interaction, member: Member, lvl: int = 0):
        user_permission = await get_permissions(self.bot, interaction.user)
        if user_permission < next(iter(Config.Roles.curator.values())) and interaction.user.id not in self.bot.owner_ids:
            return await interaction.response.send_message(embed=Embed(description="У вас недостаточно прав для выполнения данной команды!"), delete_after=15)

        if member is None:
            return await interaction.response.send_message(embed=Embed(description="Вы не указали пользователя, которому хотите изменить права!"), delete_after=15)
        
        if lvl < 0 or lvl > 4:
            return await interaction.response.send_message(embed=Embed(description="Указано некорректное значение прав!"), delete_after=15)
        
        if lvl >= user_permission and interaction.user.id not in self.bot.owner_ids:
            return await interaction.response.send_message(embed=Embed(description="Вы не можете выдавать данные уровень прав!"), delete_after=15)
    
        await set_permissions(self.bot, member, lvl)
        await interaction.response.send_message(embed=Embed(description=f"Успешно установлен уровень прав **` {lvl} `** пользователю **{member}** `[{member.id}]`"))

    @app_commands.command(name="clear", description="Очистить чат от сообщений.")
    @app_commands.describe(amount="Количество сообщений для удаления", member="Пользователь, чьи сообщения нужно удалить")
    @app_commands.guild_only()
    @has_access(manage_messages=True)
    async def clear(self, interaction: Interaction, amount: int, member: Member = None) -> None:
        if amount <= 0 or amount > 100:
            return await interaction.response.send_message("❌ Количество сообщений должно быть от 1 до 100.", ephemeral=True)

        await interaction.response.defer()

        temp_message = await interaction.followup.send(embed=Embed(title="🧹 Очищаем сообщения..."))

        def check(message):
            return (member is None or message.author.id == member.id) and message.id != temp_message.id

        try:
            deleted = await interaction.channel.purge(limit=amount+1, check=check)

            embed = Embed(
                description=f"**✅ Удалено `{len(deleted)}` сообщений**"
                + (f" от пользователя {member.mention}" if member else ""),
                color=0x2ECC71
            )
            await temp_message.edit(content=None, embed=embed)

            await asyncio.sleep(15)
            try:
                await temp_message.delete()
            except:
                pass
        except Exception as e:
            await temp_message.edit(content=f"❌ Произошла ошибка при удалении сообщений: `{e}`")

    @app_commands.command(name="kick", description="Выгнать пользователя.")
    @app_commands.describe(member="пользователь", reason="причина")
    @app_commands.guild_only()
    async def kick(self, interaction: Interaction, member: Member, reason: str = "Не указана") -> None:
        user_permission = await get_permissions(self.bot, interaction.user)
        if user_permission < next(iter(Config.Roles.moderator.values())):
            return await interaction.response.send_message(embed=Embed(description="У вас недостаточно прав для выполнения данной команды!"), delete_after=15)

        if user_permission < next(iter(Config.Roles.chief_moderator.values())):
            remaining_time = await is_cooldown(self.bot, "local", "kick", interaction.user.id)
            if remaining_time is not None:
                minutes, seconds = divmod(remaining_time, 60)
                return await interaction.response.send_message(embed=Embed(description=f"**Подождите `{minutes}` мин `{seconds}` сек перед повторным использованием команды!**"), delete_after=15)
            else:
                await set_cooldown(self.bot, "local", "kick", interaction.user.id, 60)

        if member.bot:
            await interaction.response.send_message("Нельзя кикнуть бота.", ephemeral=True)
            return

        try:
            embed = Embed(
                description=f"**✅ Пользователь {member.mention} был успешно кикнут!**",
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Модератор:", value=f"{interaction.user.mention}\n{interaction.user.name}", inline=True)
            embed.add_field(name="Причина:", value=f"{reason}", inline=True)

            await interaction.guild.kick(member, reason=f'{reason} ({interaction.user})')
            await interaction.response.send_message(embed=embed, delete_after=30)
        except discord.HTTPException:
            await interaction.response.send_message("Произошла ошибка при попытке выгнать участника!", ephemeral=True)

        try:
            embed = Embed(
                description=f"**❗️Вы были кикнуты с сервера {interaction.guild.name}.**",
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Модератор:", value=f"{interaction.user.mention}\n{interaction.user.name}", inline=True)
            embed.add_field(name="Причина:", value=f"{reason}", inline=True)

            await member.send(embed=embed)
        except discord.HTTPException:
            pass

    @app_commands.command(name="ban", description="Забанить пользователя.")
    @app_commands.describe(member="пользователь", duration="длительность", reason="причина")
    @app_commands.guild_only()
    async def ban(self, interaction: Interaction, member: Member, duration: str, reason: str = "Не указана") -> None:
        user_permission = await get_permissions(self.bot, interaction.user)
        if user_permission < next(iter(Config.Roles.moderator.values())):
            return await interaction.response.send_message(embed=Embed(description="У вас недостаточно прав для выполнения данной команды!"), delete_after=15)

        if user_permission < next(iter(Config.Roles.chief_moderator.values())):
            remaining_time = await is_cooldown(self.bot, "local", "ban", interaction.user.id)
            if remaining_time is not None:
                minutes, seconds = divmod(remaining_time, 60)
                return await interaction.response.send_message(embed=Embed(description=f"**Подождите `{minutes}` мин `{seconds}` сек перед повторным использованием команды!**"), delete_after=15)
            else:
                await set_cooldown(self.bot, "local", "ban", interaction.user.id, 60)

        if member.bot:
            await interaction.response.send_message("Нельзя выдать бан боту.", ephemeral=True)
            return

        time = convert_time_to_seconds(duration)
        if time is None:
            await interaction.response.send_message("Неверный формат времени.", ephemeral=True)
            return

        if time > 2419200:
            time = 2000000

        endtime = round((datetime.datetime.now() + datetime.timedelta(seconds=time)).timestamp())

        try:
            embed = Embed(
                description=f"**✅ Пользователь {member.mention} был успешно забанен!**",
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Модератор:", value=f"{interaction.user.mention}\n{interaction.user.name}", inline=True)
            embed.add_field(name="Окончание:", value=f"<t:{endtime}>\n**Длительность:** {duration}", inline=True)
            embed.add_field(name="Причина:", value=f"{reason}", inline=True)

            await interaction.guild.ban(member, reason=f'{reason} ({interaction.user})')
            await set_ban(self.bot, member, interaction.user, endtime, reason)
            await interaction.response.send_message(embed=embed, delete_after=30)
        except discord.HTTPException:
            await interaction.response.send_message("Произошла ошибка при попытке выдать бан участнику!", ephemeral=True)

        try:
            embed = Embed(
                description=f"**❗️Вы были забанены в сервере {interaction.guild.name}.**",
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Модератор:", value=f"{interaction.user.mention}\n{interaction.user.name}", inline=True)
            embed.add_field(name="Окончание:", value=f"<t:{endtime}>\n**Длительность:** {duration}", inline=True)
            embed.add_field(name="Причина:", value=f"{reason}", inline=True)

            await member.send(embed=embed)
        except discord.HTTPException:
            pass

    @app_commands.command(name="unban", description="Разбанить пользователя.")
    @app_commands.describe(member="пользователь", reason="причина")
    @app_commands.guild_only()
    async def unban(self, interaction: Interaction, member: Member, reason: str = "Не указана") -> None:
        user_permission = await get_permissions(self.bot, interaction.user)
        if user_permission < next(iter(Config.Roles.moderator.values())):
            return await interaction.response.send_message(embed=Embed(description="У вас недостаточно прав для выполнения данной команды!"), delete_after=15)

        if user_permission < next(iter(Config.Roles.curator.values())):
            remaining_time = await is_cooldown(self.bot, "local", "unban", interaction.user.id)
            if remaining_time is not None:
                minutes, seconds = divmod(remaining_time, 60)
                return await interaction.response.send_message(embed=Embed(description=f"**Подождите `{minutes}` мин `{seconds}` сек перед повторным использованием команды!**"), delete_after=15)
            else:
                await set_cooldown(self.bot, "local", "unban", interaction.user.id, 60)

        if member.bot:
            await interaction.response.send_message("Нельзя снять с бана бота.", ephemeral=True)
            return

        try:
            embed = Embed(
                description=f"**✅ Пользователь {member.mention} был успешно разбанен!**",
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Модератор:", value=f"{interaction.user.mention}\n{interaction.user.name}", inline=True)
            embed.add_field(name="Причина:", value=f"{reason}", inline=True)

            await interaction.guild.unban(member, reason=f'{reason} ({interaction.user})')
            await delete_ban(self.bot, member)
            await interaction.response.send_message(embed=embed, delete_after=30)
        except discord.HTTPException:
            await interaction.response.send_message("Произошла ошибка при попытке снять бан с участника!", ephemeral=True)

        try:
            embed = Embed(
                description=f"**❗️Вы были разбанены в сервере {interaction.guild.name}.**",
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Модератор:", value=f"{interaction.user.mention}\n{interaction.user.name}", inline=True)
            embed.add_field(name="Причина:", value=f"{reason}", inline=True)

            await member.send(embed=embed)
        except discord.HTTPException:
            pass

    @app_commands.command(name="mute", description="Кинуть в тайм-аут пользователя.")
    @app_commands.describe(member="пользователь", duration="длительность", reason="причина")
    @app_commands.guild_only()
    async def mute(self, interaction: Interaction, member: Member, duration: str, reason: str = "Не указана") -> None:
        user_permission = await get_permissions(self.bot, interaction.user)
        if user_permission < next(iter(Config.Roles.helper.values())):
            return await interaction.response.send_message(embed=Embed(description="У вас недостаточно прав для выполнения данной команды!"), delete_after=15)

        if user_permission < next(iter(Config.Roles.moderator.values())):
            remaining_time = await is_cooldown(self.bot, "local", "mute", interaction.user.id)
            if remaining_time is not None:
                minutes, seconds = divmod(remaining_time, 60)
                return await interaction.response.send_messagey(embed=Embed(description=f"**Подождите `{minutes}` мин `{seconds}` сек перед повторным использованием команды!**"), delete_after=15)
            else:
                await set_cooldown(self.bot, "local", "mute", interaction.user.id, 30)
            
        if member.bot:
            await interaction.response.send_message("Нельзя выдать мьют боту.", ephemeral=True)
            return

        time = convert_time_to_seconds(duration)
        if time is None:
            await interaction.response.send_message("Неверный формат времени.", ephemeral=True)
            return

        if time > 2419200:
            time = 2000000

        endtime = round((datetime.datetime.now() + datetime.timedelta(seconds=time)).timestamp())

        try:
            embed = Embed(
                description=f"**✅ Пользователь {member.mention} был успешно замьючен!**",
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Модератор:", value=f"{interaction.user.mention}\n{interaction.user.name}", inline=True)
            embed.add_field(name="Окончание:", value=f"<t:{endtime}>\n**Длительность:** {duration}", inline=True)
            embed.add_field(name="Причина:", value=f"{reason}", inline=True)

            await member.timeout(datetime.timedelta(seconds=time), reason=reason)
            await interaction.response.send_message(embed=embed, delete_after=30)
        except discord.HTTPException:
            await interaction.response.send_message("Произошла ошибка при попытке выдать мьют!", ephemeral=True)

        try:
            embed = Embed(
                description=f"**❗️Вы были замьючены в сервере {interaction.guild.name}.**",
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Модератор:", value=f"{interaction.user.mention}\n{interaction.user.name}", inline=True)
            embed.add_field(name="Окончание:", value=f"<t:{endtime}>\n**Длительность:** {duration}", inline=True)
            embed.add_field(name="Причина:", value=f"{reason}", inline=True)

            await member.send(embed=embed)
        except discord.HTTPException:
            pass

    @app_commands.command(name="unmute", description="Снять пользователя с тайм-аута.")
    @app_commands.describe(member="пользователь", reason="причина")
    @app_commands.guild_only()
    async def unmute(self, interaction: Interaction, member: Member, reason: str = "Не указана") -> None:
        user_permission = await get_permissions(self.bot, interaction.user)
        if user_permission < next(iter(Config.Roles.helper.values())):
            return await interaction.response.send_message(embed=Embed(description="У вас недостаточно прав для выполнения данной команды!"), delete_after=15)

        if user_permission < next(iter(Config.Roles.moderator.values())):
            remaining_time = await is_cooldown(self.bot, "local", "unmute", interaction.user.id)
            if remaining_time is not None:
                minutes, seconds = divmod(remaining_time, 60)
                return await interaction.response.send_message(embed=Embed(description=f"**Подождите `{minutes}` мин `{seconds}` сек перед повторным использованием команды!**"), delete_after=15)
            else:
                await set_cooldown(self.bot, "local", "unmute", interaction.user.id, 30)

        if member.bot:
            await interaction.response.send_message("Нельзя снять с мьюта бота.", ephemeral=True)
            return

        try:
            embed = Embed(
                description=f"**✅ Пользователь {member.mention} был успешно размьючен!**",
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Модератор:", value=f"{interaction.user.mention}\n{interaction.user.name}", inline=True)
            embed.add_field(name="Причина:", value=f"{reason}", inline=True)

            await member.timeout(datetime.timedelta(seconds=0), reason=reason)
            await interaction.response.send_message(embed=embed, delete_after=30)
        except discord.HTTPException:
            await interaction.response.send_message("Произошла ошибка при попытке убрать мьют!", ephemeral=True)

        try:
            embed = Embed(
                description=f"**❗️Вы были размьючены в сервере {interaction.guild.name}.**",
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Модератор:", value=f"{interaction.user.mention}\n{interaction.user.name}", inline=True)
            embed.add_field(name="Причина:", value=f"{reason}", inline=True)

            await member.send(embed=embed)
        except discord.HTTPException:
            pass

async def setup(bot: ChillBot):
    await bot.add_cog(SystemCog(bot))