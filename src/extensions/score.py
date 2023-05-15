from discord.ext import commands
from utils.helpers import get_args
from sql.queries import get_beatmap_list

class Score(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['avgscore'])
    async def averagescore(self, ctx, *args):
        """Average score leaderboard"""
        kwargs = get_args(args)
        kwargs["-float"] = "false"
        if not kwargs.get("-o"):
            kwargs["-o"] = "avg(score)"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title="Average score")

    @commands.command()
    async def scorepersecond(self, ctx, *args):
        """Score per second"""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        kwargs["-order"] = "score_per_second"
        if not (kwargs.get("-direction") or kwargs.get("-dir")):
            kwargs["-direction"] = "desc"
        if not kwargs.get("-o"):
            kwargs["-o"] = "score"
        if kwargs["-o"] == "nomodscore":
            await get_beatmap_list(ctx, kwargs, None, False, "(top_score_nomod.top_score_nomod / length) as score_per_second")
        else:
            await get_beatmap_list(ctx, kwargs, None, False, "(top_score.top_score / length) as score_per_second")

    @commands.command()
    async def scoreperclear(self, ctx, *args):
        """Score per clear leaderboard"""
        kwargs = get_args(args)
        kwargs["-o"] = "sum(score)/count(*)"
        kwargs["-float"] = "false"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title="Score per Clear")

    @commands.command()
    async def fcscore(self, ctx, *args):
        """Score only on maps a player has FCed"""
        kwargs = get_args(args)
        kwargs["-o"] = "score"
        kwargs["-is_fc"] = "true"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

    @commands.command()
    async def notfcscore(self, ctx, *args):
        """Score only on maps a player has not FCed"""
        kwargs = get_args(args)
        kwargs["-o"] = "score"
        kwargs["-is_fc"] = "false"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

    @commands.command()
    async def lazerscore(self, ctx, *args):
        """Score leaderboard using the lazer scoring formula"""
        kwargs = get_args(args)
        kwargs["-o"] = "lazerscore"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

    @commands.command()
    async def weighted_score(self, ctx, *args):
        """Ranked score leaderboard if it was weighted like pp"""
        kwargs = get_args(args)
        kwargs["-o"] = "weighted_score"
        if kwargs.get("-registered") and kwargs["-registered"] == "false":
            await ctx.reply("NO")
            return
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

    @commands.command()
    async def xasumascore(self, ctx, *args):
        """Score only on maps xasuma has played when he finished the game. (April 28th, 2019)"""
        kwargs = get_args(args)
        if not kwargs.get("-o"):
            kwargs["-o"] = "score"
        kwargs["-end"] = "2019-04-28"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

    @commands.command()
    async def przegranyscore(self, ctx, *args):
        """Score only on maps Przegrany has played when he finished the game. (August 11th, 2021)"""
        kwargs = get_args(args)
        if not kwargs.get("-o"):
            kwargs["-o"] = "score"
        kwargs["-end"] = "2021-08-11"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

    @commands.command(aliases=['EEEEEEEEEEEEEEEscore'])
    async def momoscore(self, ctx, *args):
        """Score only on maps EEEEEEEEEEEEEEE has played when he finished the game. (March 12th, 2023)"""
        kwargs = get_args(args)
        if not kwargs.get("-o"):
            kwargs["-o"] = "score"
        kwargs["-end"] = "2023-03-12"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

    @commands.command(aliases=['highestscore'])
    async def topscore(self, ctx, *args):
        """Top score leaderboard"""
        kwargs = get_args(args)
        kwargs["-o"] = "max(score)"
        kwargs["-float"] = "false"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title="Top Score")

    @commands.command()
    async def lovedscore(self, ctx, *args):
        """Score only on loved maps"""
        kwargs = get_args(args)
        kwargs["-o"] = "score"
        kwargs["-a"] = "4"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

    @commands.command()
    async def ssscore(self, ctx, *args):
        """Score only on maps a player has SSed"""
        kwargs = get_args(args)
        kwargs["-o"] = "score"
        kwargs["-is_ss"] = "true"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

    @commands.command()
    async def notssscore(self, ctx, *args):
        """Score only on maps a player has not SSed"""
        kwargs = get_args(args)
        kwargs["-o"] = "score"
        kwargs["-is_ss"] = "false"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

    @commands.command()
    async def agedscore(self, ctx, *args):
        """Score multiplied by the years since ranked"""
        kwargs = get_args(args)
        kwargs["-o"] = "agedscore"
        kwargs["-float"] = "false"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

    @commands.command()
    async def scorev0(self, ctx, *args):
        """Score but taken only the the top score of a mapset"""
        kwargs = get_args(args)
        kwargs["-o"] = "scorev0"
        kwargs["-float"] = "false"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

async def setup(bot):
    await bot.add_cog(Score(bot))