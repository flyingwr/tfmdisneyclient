from .converters import Cog

from discord.ext import commands

from discord import Color, Embed
from typing import Optional


class Help(commands.Cog, name="help"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

        self.hidden: bool = True


    @commands.command()
    async def help(self, ctx, cog: Optional[Cog] = None):
        prefix = self.bot.command_prefix
        embed = Embed(
            title=f"Lista de comandos. Prefixo: `{prefix}`",
            color=Color.blue(),
            description=f"Use `{prefix}help <categoria>` pra ter mais informações "
                        "sobre uma categoria"
        )

        if isinstance(cog, commands.Cog):
            embed = Embed(
                title=f"{cog.qualified_name} - Comandos",
                color=Color.dark_blue(), description=cog.__doc__)

            for command in cog.get_commands():
                if not command.hidden:
                    if command.aliases:
                        aliases = " ou {}".format(" ou ".join(
                                    (
                                        f"`{prefix}{alias}`"
                                        for alias in command.aliases
                                    )))
                    else:
                        aliases = ""

                    embed.add_field(name=f"`{prefix}{command.name}`{aliases}",
                                    value=command.help)
        else:
            command = self.bot.get_command(cog or "")
            if cog is None or command is None:
                cogs_desc = "\n".join(
                    (
                        f"`{cog}` {self.bot.get_cog(cog).__doc__}"
                        for cog in self.bot.cogs if not getattr(
                            self.bot.get_cog(cog), "hidden", False
                        )
                    )
                )

                embed.add_field(name="Categories", value=cogs_desc)
            elif isinstance(command, commands.Command) and not command.hidden:
                embed = Embed(
                    title=f"{command.qualified_name}",
                    color=Color.dark_blue(), description=command.help or "Sem descrição")
                if command.aliases:
                    embed.add_field(
                        name=f"Alternativos",
                        value=', '.join(
                            (f"`{prefix}{alias}`" for alias in command.aliases)
                        ))
                if command.cog_name:
                    embed.add_field(name="Categoria", value=command.cog_name)
                if command.usage:
                    embed.add_field(name="Modo de uso", value=command.usage)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))