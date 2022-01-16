from discord.ext import commands
from typing import Union


class Cog(commands.Converter):
    async def convert(self, ctx: commands.Context, name: str) -> Union[commands.Cog, str]:
        name = name.lower()
        cog = ctx.bot.get_cog(name)
        if cog is not None:
            return None if getattr(cog, "hidden", False) else cog
        return name
