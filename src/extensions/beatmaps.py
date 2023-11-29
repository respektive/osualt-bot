import datetime
from discord.ext import commands
from utils.helpers import get_args
from sql.queries import check_beatmaps, get_beatmap_list


class Beatmaps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["b"])
    async def beatmaps(self, ctx, *args):
        """Returns statistics of a set of beatmaps"""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        answer = await check_beatmaps(ctx, kwargs, None, False)
        await ctx.reply(answer)

    @commands.command(aliases=["bs", "bsets"])
    async def beatmapsets(self, ctx, *args):
        """Returns statistics of beatmap sets"""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        answer = await check_beatmaps(ctx, kwargs, None, True)
        await ctx.reply(answer)

    @commands.command(aliases=["bl"])
    async def beatmaplist(self, ctx, *args):
        """Lists every osu! standard map"""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if kwargs.get("-order"):
            if kwargs["-order"] == "score":
                kwargs["-order"] = "top_score"

        await get_beatmap_list(ctx, kwargs)

    @commands.command(aliases=["bsl"])
    async def beatmapsetlist(self, ctx, *args):
        """Lists every osu! standard mapset"""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"

        await get_beatmap_list(ctx, kwargs, None, True)

    @commands.command()
    async def longestwait(self, ctx, *args):
        """Displays mapsets with a difference in days between submitted date and ranked date"""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        kwargs["-order"] = "bonuscolumn"
        if not (kwargs.get("-direction") or kwargs.get("-dir")):
            kwargs["-direction"] = "desc"

        await get_beatmap_list(
            ctx,
            kwargs,
            None,
            True,
            "DATE_PART('day', beatmaps.approved_date - submit_date)",
        )

    @commands.command()
    async def leastplayed(self, ctx, *args):
        """Displays map difficulties with the least playcount (broken)"""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        kwargs["-order"] = "playcount"

        await get_beatmap_list(ctx, kwargs)

    @commands.command()
    async def toprated(self, ctx, *args):
        """Returns maps in the database with the highest user ratings"""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        kwargs["-order"] = "bonuscolumn"
        if not (kwargs.get("-direction") or kwargs.get("-dir")):
            kwargs["-direction"] = "desc"

        await get_beatmap_list(ctx, kwargs, None, True, "rating")

    @commands.command()
    async def maxscore(self, ctx, *args):
        """Outputs the sum of the best play on each map contained in the filter."""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        kwargs["-o"] = "score"
        answer = await check_beatmaps(ctx, kwargs, None, False)
        await ctx.reply(f"Max score: {answer:,}")

    @commands.command()
    async def nomodscore(self, ctx, *args):
        """Outputs the sum of the best nomod play on each map contained in the filter."""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        kwargs["-o"] = "nomodscore"
        answer = await check_beatmaps(ctx, kwargs, None, False)
        await ctx.reply(f"Max nomod score: {answer:,}")

    @commands.command()
    async def maxcombo(self, ctx, *args):
        """Combines the combo of every map."""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        kwargs["-o"] = "maxcombo"
        answer = await check_beatmaps(ctx, kwargs, None, False)
        await ctx.reply(f"Max combo: {answer:,}")

    @commands.command(aliases=["nbss"])
    async def neverbeenssed(self, ctx, *args):
        """Returns a list of maps that have never been SSed that are at least 30 days old."""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if not kwargs.get("-end"):
            kwargs["-end"] = (
                datetime.datetime.today() - datetime.timedelta(days=29)
            ).strftime("%Y-%m-%d")

        await get_beatmap_list(ctx, kwargs, ["neverbeenssed"])

    @commands.command(aliases=["nbfc"])
    async def neverbeenfced(self, ctx, *args):
        """Returns a list of maps that have never been FCed that are at least 7 days old."""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if not kwargs.get("-end"):
            kwargs["-end"] = (
                datetime.datetime.today() - datetime.timedelta(days=6)
            ).strftime("%Y-%m-%d")

        await get_beatmap_list(ctx, kwargs, ["neverbeenfced"])

    @commands.command(aliases=["nbdt"])
    async def neverbeendted(self, ctx, *args):
        """Returns a list of maps that have never been DTed."""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if not kwargs.get("-end"):
            kwargs["-end"] = (
                datetime.datetime.today() - datetime.timedelta(days=6)
            ).strftime("%Y-%m-%d")

        await get_beatmap_list(ctx, kwargs, ["neverbeendted"])

    @commands.command()
    async def numberones(self, ctx, *args):
        """Selected number ones"""
        kwargs = get_args(args)
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"

        await get_beatmap_list(ctx, kwargs, ["top_score"])

    @commands.command()
    async def nomodnumberones(self, ctx, *args):
        """Selected nomod number ones"""
        kwargs = get_args(args)
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"

        await get_beatmap_list(ctx, kwargs, ["top_score_nomod"])

    @commands.command()
    async def hiddennumberones(self, ctx, *args):
        """Selected hidden number ones (not 100% accurate)"""
        kwargs = get_args(args)
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"

        await get_beatmap_list(ctx, kwargs, ["top_score_hidden"])

    @commands.command()
    async def least_fced(self, ctx, *args):
        """Returns a list of beatmaps ordered by their FC count (starts at 0)."""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if not kwargs.get("-end"):
            kwargs["-end"] = (
                datetime.datetime.today() - datetime.timedelta(days=29)
            ).strftime("%Y-%m-%d")
        if not kwargs.get("-order"):
            kwargs["-order"] = "fc_count, stars"

        await get_beatmap_list(ctx, kwargs, ["fc_count"], False, "fc_count")

    @commands.command()
    async def least_ssed(self, ctx, *args):
        """Returns a list of beatmaps ordered by their SS count (starts at 0)."""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        kwargs["-leastssed"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if not kwargs.get("-end"):
            kwargs["-end"] = (
                datetime.datetime.today() - datetime.timedelta(days=29)
            ).strftime("%Y-%m-%d")
        if not kwargs.get("-order"):
            kwargs["-order"] = "ss_count, stars"

        await get_beatmap_list(ctx, kwargs, ["ss_count"], False, "ss_count")

    @commands.command()
    async def worst_acc(self, ctx, *args):
        """Returns maps in the database for the worst acc on the global leaderboards."""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if not kwargs.get("-end"):
            kwargs["-end"] = (
                datetime.datetime.today() - datetime.timedelta(days=29)
            ).strftime("%Y-%m-%d")
        if not kwargs.get("-order"):
            kwargs["-order"] = "avg_acc"

        await get_beatmap_list(ctx, kwargs, ["avg_acc"], False, "avg_acc")

    @commands.command()
    async def most_static(self, ctx, *args):
        """Returns maps in the database with the least amount of movement in the top 50 leaderboard. (Currently Broken)"""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if not kwargs.get("-end"):
            kwargs["-end"] = (
                datetime.datetime.today() - datetime.timedelta(days=29)
            ).strftime("%Y-%m-%d")
        if not kwargs.get("-order"):
            kwargs["-order"] = "days"
        if not kwargs.get("-direction"):
            kwargs["-order"] = "desc"

        await get_beatmap_list(ctx, kwargs, ["most_static"], False, "days")

    @commands.command()
    async def capped(self, ctx, *args):
        """Returns maps where the #1 score is a capped 4mod SS. (Currently Broken)"""
        kwargs = get_args(args)
        kwargs["-notscorestable"] = "true"
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if not kwargs.get("-end"):
            kwargs["-end"] = (
                datetime.datetime.today() - datetime.timedelta(days=29)
            ).strftime("%Y-%m-%d")
        if not kwargs.get("-order"):
            kwargs["-order"] = "stars"
        if not kwargs.get("-direction"):
            kwargs["-order"] = "desc"

        await get_beatmap_list(ctx, kwargs, ["capped"], False)


async def setup(bot):
    await bot.add_cog(Beatmaps(bot))
