import discord

from .custom_embed import CustomEmbed

discord.Embed = CustomEmbed

__all__ = ["CustomEmbed"]
