import discord

class CustomEmbed(discord.Embed):
    DEFAULT_COLOR = 0x37373e

    def __init__(self, *args, color: int = DEFAULT_COLOR, **kwargs):
        super().__init__(*args, color=color, **kwargs)
