from config import Config
from discord import app_commands, Interaction, Embed
from discord.app_commands.errors import CheckFailure

def has_access(**perms):
    async def predicate(interaction: Interaction):
        if not interaction.guild:
            raise CheckFailure("Отказано в доступе.")

        permissions = interaction.user.guild_permissions
        missing_perms = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

        db = Config.MONGO_CLIENT[str(interaction.guild.id)].parameters
        command_name = interaction.command.name
        command_data = await db.find_one(
            {"_id": interaction.guild.id},
            {f"commands.{command_name}": 1}
        )

        if not command_data or "commands" not in command_data or command_name not in command_data["commands"]:
            if missing_perms:
                raise CheckFailure(f"Недостаточно прав: {', '.join(missing_perms)}")
            return True

        if missing_perms:
            raise CheckFailure(f"Недостаточно прав: {', '.join(missing_perms)}")
        return True

    return app_commands.check(predicate)