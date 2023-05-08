from discord.ext import commands
from utils.helpers import get_args
from sql.queries import get_profile_leaderboard, get_ppv1_leaderboard

class Performance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def pp(self, ctx, *args):
        """pp leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "pp", "Performance Points", **kwargs)

    @commands.command(aliases=["avgpp"])
    async def averagepp(self, ctx, *args):
        """Average pp leaderboard"""
        kwargs = get_args(args)
        kwargs["-o"] = "avg(scores.pp)"
        kwargs["-float"] = "true"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title="Average pp")

    @commands.command()
    async def fcpp(self, ctx, *args):
        """FC only pp leaderboard"""
        kwargs = get_args(args)
        kwargs["-o"] = "pp"
        kwargs["-is_fc"] = "true"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title="FC pp")

    @commands.command(aliases=['topplay', 'highestpp', 'topplays'])
    async def toppp(self, ctx, *args):
        """Top pp leaderboard"""
        kwargs = get_args(args)
        kwargs["-o"] = "max(scores.pp)"
        kwargs["-float"] = "true"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title="Top pp")

    @commands.command()
    async def totalpp(self, ctx, *args):
        """Total pp leaderboard"""
        kwargs = get_args(args)
        kwargs["-o"] = "totalpp"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

    @commands.command()
    async def ppv1(self, ctx, *args):
        """ppv1 leaderboard, not realtime"""
        kwargs = get_args(args)
        kwargs["-float"] = "true"
        stat = "ppv1"
        if "-o" in kwargs and (kwargs["-o"] == "acc" or kwargs["-o"] == "accuracy"):
            kwargs["-percentage"] = "true"
            stat = "accuracyv1"
        
        await get_ppv1_leaderboard(ctx, stat, "ppv1", **kwargs)

    @commands.command()
    async def accv1(self, ctx, *args):
        """Profile acc if ppv1"""
        kwargs = get_args(args)
        kwargs["-float"] = "true"
        kwargs["-percentage"] = "true"

        await get_ppv1_leaderboard(ctx, "accuracyv1", "ppv1 Accuracy", **kwargs)

async def setup(bot):
    await bot.add_cog(Performance(bot))