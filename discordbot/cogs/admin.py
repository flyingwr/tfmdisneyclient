from discord.ext import commands
from services.mongodb import find_map_by_key, find_soft_by_key, find_user_by_key, \
    set_config, set_map, set_soft, set_user, set_user_browser_token
from typing import Optional, Union


from data.map import Map
from data.soft import Soft
from data.user import User
from utils import cryptjson


import aiofiles


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
    async def setkeymaps(self, ctx, key: str):
        async with aiofiles.open("./public/maps.json", "r") as f:
            set_map(key, cryptjson.maps_decode(await f.read()))

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

    @commands.command()
    @commands.is_owner()
    async def resetbrowsertoken(self, ctx, key: str):
        if key == "all":
            for user in User.objects:
                user.update(browser_access=True, browser_access_token=None)
        else:
            set_user_browser_token(key)

        await ctx.reply("Database updated")

    @commands.command()
    @commands.is_owner()
    async def resetsoftmaps(self, ctx, key: str):
        set_soft(key)

        await ctx.reply("Database updated")


    @commands.command()
    @commands.is_owner()
    async def setconnlimit(self, ctx, key: str, limit: Optional[int] = 1):
        user = find_user_by_key(key)
        if user:
            user.update(connection_limit=limit)
            await ctx.reply("Database updated")
        else:
            await ctx.reply("User not found")

    @commands.command()
    @commands.is_owner()
    async def formatmaps(self, ctx, key: str):
        print("[MongoDB] Formatting maps...")

        if key == "all":
            for _map in Map.objects:
                print(f"[MongoDB] Formatting maps from key `{key}`")
                if find_user_by_key(_map.key):
                    if isinstance(_map.data, bytes):
                        _map.update(data=cryptjson.maps_decode(_map.data))
                else:
                    print(f"[MongoDB] Deleted maps from key `{key}` because it was not found in users document")
                    _map.delete()
        else:
            _map = find_map_by_key(key)
            if _map:
                _map.update(data=cryptjson.maps_decode(_map.data))

        await ctx.reply("Database updated")

    @commands.command()
    @commands.is_owner()
    async def killunusedmaps(self, ctx):
        print("[MongoDB] Formatting maps...")
        for _map in Map.objects().only("key"):
            if not find_user_by_key(_map.key):
                print(f"[MongoDB] Deleted maps from key `{key}` because it was not found in users document")
                _map.delete()
                
        await ctx.reply("Database updated")

def setup(bot):
    bot.add_cog(Admin(bot))
