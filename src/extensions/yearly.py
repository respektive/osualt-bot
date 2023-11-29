import datetime
from discord.ext import commands
from utils.helpers import get_args
from sql.queries import check_tables


class Yearly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["yearly"])
    async def yeartodate(self, ctx, *args):
        """Returns a leaderboard for the current year."""
        kwargs = get_args(args)
        kwargs["-start"] = f"{datetime.datetime.now().year}-01-01 00:00:00"

        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

    @commands.command()
    async def monthly(self, ctx, *args, kwargs=None):
        """Returns Score, SS, FC and Clears leaderboards for the current month."""
        if kwargs == None:
            kwargs = get_args(args)
        day = 1
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year
        if kwargs.get("-month"):
            month = kwargs["-month"]
        if kwargs.get("-y"):
            kwargs["-year"] = kwargs["-y"]
        if kwargs.get("-year"):
            year = kwargs["-year"]
        if int(month) < 12:
            next_month = int(month) + 1
            next_year = year
        else:
            next_month = 1
            next_year = int(year) + 1
        kwargs["-end"] = str(next_year) + "-" + str(next_month) + "-01 00:00:00"

        if kwargs.get("-day"):
            day = kwargs["-day"]
            end = int(day) + 1

        if int(day) < 10:
            day = "0" + str(day)
            if kwargs.get("-day"):
                end = "0" + str(end)
        if not kwargs.get("-registered"):
            kwargs["-registered"] = "true"
        kwargs["-start"] = str(year) + "-" + str(month) + "-" + str(day) + " 00:00:01"
        if kwargs.get("-day"):
            kwargs["-end"] = str(year) + "-" + str(month) + "-" + str(end) + " 00:00:00"

        operation = "sum(scores.score)"
        month_name = datetime.date(1900, int(month), 1).strftime("%B")
        await check_tables(
            ctx,
            operation,
            "scores",
            kwargs,
            "Score for " + month_name + " " + str(year),
        )

        operation = "count(*)"
        kwargs["-is_ss"] = "true"
        await check_tables(
            ctx,
            operation,
            "scores",
            kwargs,
            "SS Count for " + month_name + " " + str(year),
        )

        del kwargs["-is_ss"]
        kwargs["-is_fc"] = "true"
        kwargs["-is_ht"] = "false"
        kwargs["-is_ez"] = "false"
        await check_tables(
            ctx,
            operation,
            "scores",
            kwargs,
            "FC Count for " + month_name + " " + str(year),
        )

        del kwargs["-is_fc"]
        del kwargs["-is_ht"]
        del kwargs["-is_ez"]
        await check_tables(
            ctx,
            operation,
            "scores",
            kwargs,
            "Clears for " + month_name + " " + str(year),
        )

    @commands.command(aliases=["jan"])
    async def january(self, ctx, *args):
        """Returns Score, SS, FC and Clears leaderboards for January of the current year."""
        kwargs = get_args(args)
        kwargs["-month"] = 1

        await ctx.invoke(self.bot.get_command("monthly"), kwargs=kwargs)

    @commands.command(aliases=["feb"])
    async def february(self, ctx, *args):
        """Returns Score, SS, FC and Clears leaderboards for February of the current year."""
        kwargs = get_args(args)
        kwargs["-month"] = 2

        await ctx.invoke(self.bot.get_command("monthly"), kwargs=kwargs)

    @commands.command(aliases=["mar"])
    async def march(self, ctx, *args):
        """Returns Score, SS, FC and Clears leaderboards for March of the current year."""
        kwargs = get_args(args)
        kwargs["-month"] = 3

        await ctx.invoke(self.bot.get_command("monthly"), kwargs=kwargs)

    @commands.command(aliases=["apr"])
    async def april(self, ctx, *args):
        """Returns Score, SS, FC and Clears leaderboards for April of the current year."""
        kwargs = get_args(args)
        kwargs["-month"] = 4

        await ctx.invoke(self.bot.get_command("monthly"), kwargs=kwargs)

    @commands.command()
    async def may(self, ctx, *args):
        """Returns Score, SS, FC and Clears leaderboards for May of the current year."""
        kwargs = get_args(args)
        kwargs["-month"] = 5

        await ctx.invoke(self.bot.get_command("monthly"), kwargs=kwargs)

    @commands.command(aliases=["jun"])
    async def june(self, ctx, *args):
        """Returns Score, SS, FC and Clears leaderboards for June of the current year."""
        kwargs = get_args(args)
        kwargs["-month"] = 6

        await ctx.invoke(self.bot.get_command("monthly"), kwargs=kwargs)

    @commands.command(aliases=["jul"])
    async def july(self, ctx, *args):
        """Returns Score, SS, FC and Clears leaderboards for July of the current year."""
        kwargs = get_args(args)
        kwargs["-month"] = 7

        await ctx.invoke(self.bot.get_command("monthly"), kwargs=kwargs)

    @commands.command(aliases=["aug"])
    async def august(self, ctx, *args):
        """Returns Score, SS, FC and Clears leaderboards for August of the current year."""
        kwargs = get_args(args)
        kwargs["-month"] = 8

        await ctx.invoke(self.bot.get_command("monthly"), kwargs=kwargs)

    @commands.command(aliases=["sep"])
    async def september(self, ctx, *args):
        """Returns Score, SS, FC and Clears leaderboards for September of the current year."""
        kwargs = get_args(args)
        kwargs["-month"] = 9

        await ctx.invoke(self.bot.get_command("monthly"), kwargs=kwargs)

    @commands.command(aliases=["oct"])
    async def october(self, ctx, *args):
        """Returns Score, SS, FC and Clears leaderboards for October of the current year."""
        kwargs = get_args(args)
        kwargs["-month"] = 10

        await ctx.invoke(self.bot.get_command("monthly"), kwargs=kwargs)

    @commands.command(aliases=["nov"])
    async def november(self, ctx, *args):
        """Returns Score, SS, FC and Clears leaderboards for November of the current year."""
        kwargs = get_args(args)
        kwargs["-month"] = 11

        await ctx.invoke(self.bot.get_command("monthly"), kwargs=kwargs)

    @commands.command(aliases=["dec"])
    async def december(self, ctx, *args):
        """Returns Score, SS, FC and Clears leaderboards for December of the current year."""
        kwargs = get_args(args)
        kwargs["-month"] = 12

        await ctx.invoke(self.bot.get_command("monthly"), kwargs=kwargs)


async def setup(bot):
    await bot.add_cog(Yearly(bot))
