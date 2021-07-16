import aiofiles
from discord.ext import commands
from services.mongodb import find_map_by_key, set_config, set_map, set_user


from data.map import Map
from data.user import User


class Admin(commands.Cog):
    """
        Admin commands
    """

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def setkey(self, ctx, *args):
        for arg in args:
            info = arg.split(":")
            set_user(info[0], "SILVER" if len(info) < 2 else info[1])

        await ctx.reply("Database updated")

    @commands.command()
    @commands.is_owner()
    async def setkeymaps(self, ctx, *args):
        async with aiofiles.open("./public/maps.json", "rb") as f:
            map_data = await f.read()

        for arg in args:
            _map = find_map_by_key(arg)
            if not _map:
                set_map(arg, map_data)

        await ctx.reply("Database updated")

    @commands.command()
    @commands.is_owner()
    async def delkey(self, ctx, *args):
        for arg in args:
            User.objects(key=arg).delete()

        await ctx.reply("Database updated")

    @commands.command()
    @commands.is_owner()
    async def delkeymaps(self, ctx, *args):
        for arg in args:
            Map.objects(key=arg).delete()

        await ctx.reply("Database updated")

    @commands.command()
    @commands.is_owner()
    async def transferkeymaps(self, ctx, _from: str, to: str):
        from_maps = find_map_by_key(_from)
        if from_maps:
            set_map(to, from_maps.data)

        await ctx.reply("Database updated")

    @commands.command()
    @commands.is_owner()
    async def resetconfig(self, ctx, key: str):
        set_config(key, None)

        await ctx.reply("Database updated")

def setup(bot):
    bot.add_cog(Admin(bot))
