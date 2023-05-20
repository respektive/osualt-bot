import os
from discord.ext import commands
from utils.helpers import get_args
from sql.queries import get_queue_length, register_user, get_user_id, insert_into_scorequeue
from utils.misc import generateosdb, getfile
from card.data import get_card

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def queuelength(self, ctx):
        """Checks how long the !queue will take"""
        length = await get_queue_length()
        await ctx.reply(length)

    @commands.command()
    async def register(self, ctx, *, args=""):
        """Registers a player for more frequent updates"""
        if not args or not args.isnumeric():
            await ctx.reply("Please specify a user_id.")
            return
        user_id = args.split()[0]
        await register_user(user_id)
        await ctx.reply("Registered!")

    @commands.command()
    async def scorequeue(self, ctx, *args):
        """Queues up a single beatmap for a single player."""
        kwargs = get_args(args)
        if not kwargs.get("-b") or not kwargs["-b"].isnumeric():
            await ctx.reply("Please specify a beatmap_id.")
            return
        user_id = await get_user_id(ctx, kwargs)
        beatmap_id = int(kwargs["-b"])
        await insert_into_scorequeue(beatmap_id, user_id)
        await ctx.reply("Queued!")

    @commands.command()
    async def generateosdb(self, ctx, *args):
        """Uses the specified filters to create an osu collection. Best imported using collection manager."""
        kwargs = get_args(args)
        await generateosdb(ctx, kwargs)

    @commands.command()
    async def getfile(self, ctx, *args):
        """Returns the entire list in a file, if discord allows it."""
        kwargs = get_args(args)
        await getfile(ctx, kwargs)

    @commands.command()
    async def card(self, ctx, *args):
        """Generates a user card image."""
        kwargs = get_args(args)
        user_id = await get_user_id(ctx, kwargs)
        embed, file = await get_card(user_id)
        await ctx.reply(embed=embed, file=file)
        # Clean up files after sending to discord
        os.remove(f"card_{user_id}.svg")
        os.remove(f"card_{user_id}.png")

async def setup(bot):
    await bot.add_cog(Misc(bot))