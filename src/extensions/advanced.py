import datetime
from discord.ext import commands
from discord.utils import escape_markdown
from utils.helpers import get_args
from sql.queries import get_user_id, get_beatmap_list, check_tables, check_weighted_pp, check_weighted_score, check_beatmaps, get_beatmap_ids, insert_into_queue, get_queue_length

class Advanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['scores', 'gs'])
    async def getscores(self, ctx, *args):
        """Returns maps in the database for a user based on specific criteria."""
        kwargs = get_args(args)
        kwargs["discord_id"] = ctx.message.author.id
        user_id = await get_user_id(ctx, kwargs)
        if user_id is None:
            raise ValueError("Please specify a user using '-u'. If username doesn't work, try using the user_id instead.")
        kwargs["-user"] = user_id
        if not kwargs.get("-registered"):
            kwargs["-registered"] = "false"

        if kwargs.get("-unplayed"):
            await get_beatmap_list(ctx, kwargs, ["fc_count", "ss_count"])
        else:
            await get_beatmap_list(ctx, kwargs, ["scores", "mods", "fc_count", "ss_count"])

    @commands.command()
    async def missingscore(self, ctx, *args):
        """Returns an ordered list of plays based on how much score you're msising compared to the #1 play on the map."""
        kwargs = get_args(args)
        kwargs["discord_id"] = ctx.message.author.id
        user_id = await get_user_id(ctx, kwargs)
        if user_id is None:
            raise ValueError("Please specify a user using '-u'. If username doesn't work, try using the user_id instead.")
        kwargs["-user"] = user_id
        if not kwargs.get("-registered"):
            kwargs["-registered"] = "false"
        if not kwargs.get("-order"):
            kwargs["-order"] = "missing_score"
        if not (kwargs.get("-dir") or kwargs.get("-direction")):
            kwargs["-direction"] = kwargs["-dir"] = "desc"

        if kwargs.get("-unplayed"):
            if kwargs.get("-o") and kwargs["-o"] == "nomodscore":
                await get_beatmap_list(ctx, kwargs, None, False, ("max(top_score_nomod) as missing_score"), True)
            else:
                await get_beatmap_list(ctx, kwargs, None, False, ("max(top_score) as missing_score"), True)
        else:
            if kwargs.get("-o") and kwargs["-o"] == "nomodscore":
                await get_beatmap_list(ctx, kwargs, ["scores"], False, ("max(top_score_nomod - score) as missing_score"), True)
            else:
                await get_beatmap_list(ctx, kwargs, ["scores"], False, ("max(top_score - score) as missing_score"), True)

    @commands.command(aliases=["q"])
    async def query(self, ctx, *args, kwargs=None, title=None):
        """Allows for precise star rating filtering on typical leaderboards for registered users"""
        if kwargs == None:
            kwargs = get_args(args)
        if not kwargs.get("-registered"):
            kwargs["-registered"] = "true"

        standardised = "(((((50 * scores.count50 + 100 * scores.count100 + 300 * scores.count300) / (300 * scores.count50 + 300 * scores.count100 + 300 * scores.count300 + 300 * scores.countmiss)::float) * 300000) + ((scores.combo/beatmaps.maxcombo::float)*700000)) * mods.multiplier)"
        standardised_nomod = "((((50 * scores.count50 + 100 * scores.count100 + 300 * scores.count300) / (300 * scores.count50 + 300 * scores.count100 + 300 * scores.count300 + 300 * scores.countmiss)::float) * 300000) + ((scores.combo/beatmaps.maxcombo::float)*700000))"
        max_score = "1000000"
        totalHitObjects = "(beatmaps.circles + beatmaps.spinners + beatmaps.sliders)"
 
        if kwargs.get("-o"):
            if title == "Result":
                title = escape_markdown(kwargs["-o"])
            if kwargs["-o"] == "completion" or kwargs["-o"] == "%":
                beatmap_count = str(int(await check_beatmaps(ctx, kwargs.copy())))
                await check_tables(ctx, "round((cast(count(*) * 100::float / " +  beatmap_count + " as numeric)), 3)", "scores", kwargs, "Completion")
                
            elif kwargs["-o"] == "length_completion":
                kwargs["-noformat"] = True
                beatmap_length = str(int(await check_beatmaps(ctx, kwargs.copy())))
                await check_tables(ctx, "round((cast(sum(beatmaps.length) * 100::float / " +  beatmap_length + " as numeric)), 3)", "scores", kwargs, "Length Completion")
                
            elif kwargs["-o"] == "length":
                await check_tables(ctx, "sum(beatmaps.length)", "scores", kwargs, "Sum of beatmaps length")
                
            elif kwargs["-o"] == "score" or kwargs["-o"] == "scoer":
                await check_tables(ctx, "sum(scores.score)", "scores", kwargs, kwargs["-o"].upper())
                
            elif kwargs["-o"] == "lazerscore":
                await check_tables(ctx, f"SUM((POW((({standardised} / {max_score}) * {totalHitObjects}), 2) * 36)::int)", "scores", kwargs, "Lazer Classic Score")
                
            elif kwargs["-o"] == "lazerscore_nomod":
                await check_tables(ctx, f"SUM(POW((({standardised_nomod} / {max_score}) * {totalHitObjects}), 2) * 36)", "scores", kwargs, "Lazer Classic Score without mod multipliers")
                
            elif kwargs["-o"] == "lazerscore_standard":
                kwargs["-o"] = "lazerscore"
                await check_tables(ctx, f"SUM({standardised})", "scores", kwargs, "Lazer Standardised Score")
                
            elif kwargs["-o"] == "lazerscore_standard_nomod":
                await check_tables(ctx, f"SUM({standardised_nomod})", "scores", kwargs, "Lazer Standardised Score without mod multipliers")
                
            elif kwargs["-o"] == "lazerscore_test":
                kwargs["-o"] = "lazerscore"
                await check_tables(ctx, f"SUM(POW((({standardised} / {max_score}) * {totalHitObjects}), 1.8) * mods.multiplier * 128)", "scores", kwargs, "Lazer Classic Score Testing")
                
            elif kwargs["-o"] == "totalpp":
                await check_tables(ctx, "sum(scores.pp)", "scores", kwargs, "Total pp")
                
            elif kwargs["-o"] == "pp" or kwargs["-o"] == "weighed_pp":
                if kwargs.get("-registered"):
                    if kwargs["-registered"] == "false" and not kwargs.get("-user"):
                        await ctx.reply("NO")
                        return
                if not kwargs.get("-weight"):
                    kwargs["-weight"] = "0.95"
                if float(kwargs["-weight"]) > 1 or float(kwargs["-weight"]) < 0:
                    await ctx.reply("NO")
                await check_weighted_pp(ctx, "(weighted_pp(pp_index, a.pp, " + str(kwargs["-weight"]) + ") + bonus_pp(count(pp_index)))", kwargs, "Weighted pp")
                
            elif kwargs["-o"] == "xexxar-old":
                if kwargs.get("-registered"):
                    if kwargs["-registered"] == "false" and not kwargs.get("-user"):
                        await ctx.reply("NO")
                        return
                if not kwargs.get("-xexxar-a"):
                    kwargs["-xexxar-a"] = 2
                if not kwargs.get("-xexxar-b"):
                    kwargs["-xexxar-b"] = 0.75
                await check_weighted_pp(ctx, "((" + str(kwargs["-xexxar-a"]) + " - 1) * weighted_pp(pp_index, a.pp, 0.95) + " + str(kwargs["-xexxar-b"]) + " * weighted_pp(pp_index, a.pp, 0.95) * (log(sum(a.pp)) / log(weighted_pp(pp_index, a.pp, 0.95)))) / " + str(kwargs["-xexxar-a"]), kwargs, "Weighted pp")
                
            elif kwargs["-o"] == "xexxar-old2":
                if kwargs.get("-registered"):
                    if kwargs["-registered"] == "false" and not kwargs.get("-user"):
                        await ctx.reply("NO")
                        return
                if not kwargs.get("-xexxar-a"):
                    kwargs["-xexxar-a"] = 5.75
                if not kwargs.get("-xexxar-b"):
                    kwargs["-xexxar-b"] = 13.5
                if not kwargs.get("-xexxar-c"):
                    kwargs["-xexxar-c"] = 1
                await check_weighted_pp(ctx, "(" + str(kwargs["-xexxar-c"]) + " * sum((" + str(kwargs["-xexxar-a"]) + " + 1) * a.pp / (least(pp_index, 100) + " + str(kwargs["-xexxar-a"]) + " + " + str(kwargs["-xexxar-b"]) + " * greatest(0, (pp_index - 100)))))", kwargs, "Weighted pp")
                
            elif kwargs["-o"] == "xexxar":
                if not kwargs.get("-xexxar-a"):
                    kwargs["-xexxar-a"] = 120
                await check_weighted_pp(ctx, "sum(a.pp * (1::float + " + str(kwargs["-xexxar-a"]) + "::float / pp_index::float) / (pp_index::float + " + str(kwargs["-xexxar-a"]) + " / pp_index::float))", kwargs, "Weighted pp")
                
            elif kwargs["-o"] == "xexxar-acc":
                if not kwargs.get("-xexxar-a"):
                    kwargs["-xexxar-a"] = 120
                await check_weighted_pp(ctx, "sum(a.accuracy * (1::float + " + str(kwargs["-xexxar-a"]) + "::float / pp_index::float) / (pp_index::float + " + str(kwargs["-xexxar-a"]) + " / pp_index::float)) / sum((1::float + " + str(kwargs["-xexxar-a"]) + "::float / pp_index::float) / (pp_index::float + " + str(kwargs["-xexxar-a"]) + " / pp_index::float))", kwargs, "Weighted pp")
                
            elif kwargs["-o"] == "billie":
                if not kwargs.get("-xexxar-a"):
                    kwargs["-xexxar-a"] = 120
                await check_weighted_pp(ctx, "sum(a.pp * greatest(1.2 * POW(0.99, pp_index) * (5.1 - pp_index::float) / (ABS(5.1 - pp_index::float)), (1::float + " + str(kwargs["-xexxar-a"]) + "::float / pp_index::float) / (pp_index::float + " + str(kwargs["-xexxar-a"]) + " / pp_index::float)))", kwargs, "Weighted pp")
                
            elif kwargs["-o"] == "xexxar-gain":
                if not kwargs.get("-xexxar-a"):
                    kwargs["-xexxar-a"] = 120
                await check_weighted_pp(ctx, "(sum(a.pp * (1::float + " + str(kwargs["-xexxar-a"]) + "::float / pp_index::float) / (pp_index::float + " + str(kwargs["-xexxar-a"]) + " / pp_index::float)) - (weighted_pp(pp_index, a.pp, 0.95) + bonus_pp(count(pp_index))))", kwargs, "Weighted pp")
                
            elif kwargs["-o"] == "weighted_score":
                if kwargs.get("-registered"):
                    if kwargs["-registered"] == "false" and not kwargs.get("-user"):
                        await ctx.reply("NO")
                        return
                await check_weighted_score(ctx, "weighted_pp(score_index, a.score, 0.95)", kwargs, "Weighted Score")
                
            elif kwargs["-o"] == "sets" or kwargs["-o"] == "mapsets":
                await check_tables(ctx, "count( distinct beatmaps.set_id )", "scores", kwargs, "Mapset Clears")
                
            else:
                await check_tables(ctx, kwargs["-o"], "scores", kwargs, title)
                
        else:
            await check_tables(ctx, "count( distinct scores.beatmap_id )", "scores", kwargs, title or "Clears")

    @commands.command()
    async def tragedy(self, ctx, *args):
        """Leaderboard for the most players who scored 1 of the parameters."""
        kwargs = get_args(args)
        title=None

        if kwargs.get("-o"):
            if kwargs["-o"] == "100":
                kwargs["-tragedy"] = "100"
                title = "1x100 from SS"
            if kwargs["-o"] == "50":
                kwargs["-tragedy"] = "50"
                title = "1x50 from SS"
            if kwargs["-o"] == "miss":
                kwargs["-tragedy"] = "miss"
                title = "1 miss from SS"
            if kwargs["-o"] == "x":
                kwargs["-tragedy"] = "x"
                title = "1 miss from FC"
            del kwargs["-o"]
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title=title)

    @commands.command(aliases=['avgstars'])
    async def averagestars(self, ctx, *args):
        """Average stars leaderboard"""
        kwargs = get_args(args)
        kwargs["-float"] = "true"
        if not kwargs.get("-o"):
            if kwargs.get("-modded") and kwargs["-modded"] == "true":
                kwargs["-o"] = "avg(moddedsr.star_rating)"
            else:
                kwargs["-o"] = "avg(stars)"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title="Average star rating of beatmaps")

    @commands.command(aliases=['avglength'])
    async def averagelength(self, ctx, *args):
        """Average length leaderboard"""
        kwargs = get_args(args)
        kwargs["-float"] = "false"
        if not kwargs.get("-o"):
            kwargs["-o"] = "avg(length)"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title="Average length of beatmaps")

    @commands.command(aliases=['avgacc'])
    async def averageacc(self, ctx, *args):
        """Average acc leaderboard"""
        kwargs = get_args(args)
        kwargs["-float"] = "true"
        if not kwargs.get("-o"):
            kwargs["-o"] = "sum(scores.count300+scores.count100*0.3333+scores.count50*0.1667)*pow(sum(scores.count300+scores.count100+scores.count50+scores.countmiss),-1)*100"
        if not kwargs.get("-precision"):
            kwargs["-precision"] = "5"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title="Average acc")

    @commands.command(aliases=['higheststars'])
    async def topstars(self, ctx, *args):
        """Top stars leaderboard"""
        kwargs = get_args(args)
        kwargs["-float"] = "true"
        if not kwargs.get("-o"):
            if kwargs.get("-modded") and kwargs["-modded"] == "true":
                kwargs["-o"] = "max(moddedsr.star_rating)"
            else:
                kwargs["-o"] = "max(stars)"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title="Top Star Rating")

    @commands.command(aliases=["fccount"])
    async def fc_count(self, ctx, *args):
        """Total FC counts for users"""
        kwargs = get_args(args)
        kwargs["-is_fc"] = "true"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs)

    @commands.command(aliases=['fcrate', 'fcefficiency', 'fc_efficiency', 'fc_ratio', 'fcratio'])
    async def fc_rate(self, ctx, *args):
        """FC ratio leaderboard"""
        kwargs = get_args(args)
        kwargs["-float"] = "true"
        if not kwargs.get("-o"):
            kwargs["-o"] = "(cast(sum(case when (countmiss = 0 and (maxcombo - combo) <= scores.count100 or rank like '%X%') then 1 else 0 end) as float)/cast(count(*) as float) * 100)"
        if not kwargs.get("-percentage"):
            kwargs["-percentage"] = "true"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title="FC Rate")

    @commands.command(aliases=['ssrate', 'ssefficiency', 'ss_efficiency', 'ss_ratio', 'ssratio'])
    async def ss_rate(self, ctx, *args):
        """SS ratio leaderboard"""
        kwargs = get_args(args)
        kwargs["-float"] = "true"
        if not kwargs.get("-o"):
            kwargs["-o"] = "(cast(sum(case when rank like '%X%' then 1 else 0 end) as float)/cast(count(*) as float) * 100)"
        if not kwargs.get("-percentage"):
            kwargs["-percentage"] = "true"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title="SS Rate")

    @commands.command(aliases=['srate', 'sefficiency', 's_efficiency', 's_ratio', 'sratio'])
    async def s_rate(self, ctx, *args):
        """S ratio leaderboard"""
        kwargs = get_args(args)
        kwargs["-float"] = "true"
        if not kwargs.get("-o"):
            kwargs["-o"] = "(cast(sum(case when rank like '%S%' then 1 else 0 end) as float)/cast(count(*) as float) * 100)"
        if not kwargs.get("-percentage"):
            kwargs["-percentage"] = "true"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title="S Rate")

    @commands.command(aliases=['arate', 'aefficiency', 'a_efficiency', 'a_ratio', 'aratio'])
    async def a_rate(self, ctx, *args):
        """A ratio leaderboard"""
        kwargs = get_args(args)
        kwargs["-float"] = "true"
        if not kwargs.get("-o"):
            kwargs["-o"] = "(cast(sum(case when rank like 'A' then 1 else 0 end) as float)/cast(count(*) as float) * 100)"
        if not kwargs.get("-percentage"):
            kwargs["-percentage"] = "true"
        
        await ctx.invoke(self.bot.get_command("query"), kwargs=kwargs, title="A Rate")

    @commands.command(aliases=['ffc'])
    async def first_fc(self, ctx, *args):
        """Generates a leaderboard of first fcs. May be inaccurate."""
        kwargs = get_args(args)
        if not kwargs.get("-time"):
            kwargs["-time"] = 1
        
        await check_tables(ctx, "count(*)", "first_fc", kwargs, "First FC Count")

    @commands.command(aliases=['fss'])
    async def first_ss(self, ctx, *args):
        """Generates a leaderboard of first ss's. May be inaccurate."""
        kwargs = get_args(args)
        
        await check_tables(ctx, "count(*)", "first_ss", kwargs, "First SS Count")

    @commands.command(aliases=['udt'])
    async def unique_dt_fc(self, ctx, *args):
        """Generates a leaderboard of players who have the only DT FC on maps."""
        kwargs = get_args(args)
        
        await check_tables(ctx, "count(*)", "unique_dt_fc", kwargs, "Unique DT FC Count")

    @commands.command(aliases=['ufc'])
    async def unique_fc(self, ctx, *args):
        """Generates a leaderboard of players who have the only FC on maps."""
        kwargs = get_args(args)
        
        await check_tables(ctx, "count(*)", "unique_fc", kwargs, "Unique FC Count")

    @commands.command()
    async def best_acc(self, ctx, *args):
        """Generates a leaderboard of players who have the best Acc on maps."""
        kwargs = get_args(args)
        
        await check_tables(ctx, "count(*)", "max_acc", kwargs, "Best acc Count")

    @commands.command(aliases=['uss'])
    async def unique_ss(self, ctx, *args):
        """Generates a leaderboard of players who have the only SS on maps."""
        kwargs = get_args(args)
        
        await check_tables(ctx, "count(*)", "unique_ss", kwargs, "Unique SS Count")

    @commands.command()
    async def ss_bounty(self, ctx, *args):
        """For each first ss a player has, they get the number of days between rank date and play date added to their total."""
        kwargs = get_args(args)
        
        await check_tables(ctx, "sum(days)", "first_ss", kwargs)

    @commands.command()
    async def best_acc_list(self, ctx, *args):
        """List of maps a player has the best Acc on."""
        kwargs = get_args(args)
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if not kwargs.get("-end"):
            kwargs["-end"] = (datetime.datetime.today() - datetime.timedelta(days=6)).strftime('%Y-%m-%d')
        
        await get_beatmap_list(ctx, kwargs, ["max_acc"])

    @commands.command(aliases=['ffcl'])
    async def first_fc_list(self, ctx, *args):
        """List of maps a player has the first FC on."""
        kwargs = get_args(args)
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if not kwargs.get("-end"):
            kwargs["-end"] = (datetime.datetime.today() - datetime.timedelta(days=6)).strftime('%Y-%m-%d')
        
        await get_beatmap_list(ctx, kwargs, ["first_fc"])

    @commands.command(aliases=['fssl'])
    async def first_ss_list(self, ctx, *args):
        """List of maps a player has the first SS on."""
        kwargs = get_args(args)
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if not kwargs.get("-end"):
            kwargs["-end"] = (datetime.datetime.today() - datetime.timedelta(days=29)).strftime('%Y-%m-%d')
        
        await get_beatmap_list(ctx, kwargs, ["first_ss"])

    @commands.command(aliases=['udtl'])
    async def unique_dt_fc_list(self, ctx, *args):
        """List of maps a player has a unique DT FC on."""
        kwargs = get_args(args)
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if not kwargs.get("-end"):
            kwargs["-end"] = (datetime.datetime.today() - datetime.timedelta(days=6)).strftime('%Y-%m-%d')
        
        await get_beatmap_list(ctx, kwargs, ["unique_dt_fc"])

    @commands.command(aliases=['ufcl'])
    async def unique_fc_list(self, ctx, *args):
        """List of maps a player has a unique FC on."""
        kwargs = get_args(args)
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if not kwargs.get("-end"):
            kwargs["-end"] = (datetime.datetime.today() - datetime.timedelta(days=6)).strftime('%Y-%m-%d')
        
        await get_beatmap_list(ctx, kwargs, ["unique_fc"])

    @commands.command(aliases=['ussl'])
    async def unique_ss_list(self, ctx, *args):
        """List of maps a player has a unique SS on."""
        kwargs = get_args(args)
        if kwargs.get("-m") or kwargs.get("-mods"):
            if not kwargs.get("-modded"):
                kwargs["-modded"] = "true"
        if not kwargs.get("-end"):
            kwargs["-end"] = (datetime.datetime.today() - datetime.timedelta(days=29)).strftime('%Y-%m-%d')
        
        await get_beatmap_list(ctx, kwargs, ["unique_ss"])

    @commands.command()
    async def queue(self, ctx, *args):
        """Queues up a player for a full check of a specified set of beatmaps. Please use extensive parameters to limit the set. \
Maximum amount of scores a user is allowed to queue is 1000. To check the queue time, use `!queuelength`."""
        kwargs = get_args(args)
        user_id = await get_user_id(ctx, kwargs)
        kwargs["-user"] = user_id

        if kwargs.get("-unplayed"):
            rows = await get_beatmap_ids(kwargs, ["fc_count", "ss_count"])
        else:
            rows = await get_beatmap_ids(kwargs, ["scores", "fc_count", "ss_count", "mods"])

        if len(rows) > 2500:
            await ctx.reply("NO")
        else:
            await insert_into_queue(rows, user_id)
            length = await get_queue_length()
            await ctx.reply(length)
        
async def setup(bot):
    await bot.add_cog(Advanced(bot))