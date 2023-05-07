from discord.ext import commands
from utils.helpers import get_args
from sql.queries import get_profile_leaderboard, get_mapper_leaderboard, check_array_stats

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def a_ranks(self, ctx, *args):
        """Total A rank leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "a_count", "A Ranks", **kwargs)

    @commands.command()
    async def accuracy(self, ctx, *args):
        """Global accuracy leaderboard"""
        kwargs = get_args(args)
        kwargs["-float"] = "true"
        await get_profile_leaderboard(ctx, "hit_accuracy", "Accuracy", **kwargs)

    @commands.command()
    async def clears(self, ctx, *args):
        """Clears leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "a_count + s_count + sh_count + ss_count + ssh_count", "Clears", **kwargs)

    @commands.command()
    async def comments(self, ctx, *args):
        """Global comments leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "comments_count", "Comments", **kwargs)

    @commands.command(aliases=['firstplaces', 'first_places', '#1s'])
    async def firsts(self, ctx, *args):
        """Global #1s leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "scores_first_count", "First Places", **kwargs)

    @commands.command()
    async def followers(self, ctx, *args):
        """Global followers leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "follower_count", "Followers", **kwargs)

    @commands.command()
    async def forumposts(self, ctx, *args):
        """Global forumposts leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "post_count", "Forum Posts", **kwargs)

    @commands.command()
    async def gold_s(self, ctx, *args):
        """Golden S leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "s_count", "Gold S", **kwargs)

    @commands.command()
    async def gold_ss(self, ctx, *args):
        """Golden SS leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "ss_count", "Gold SS", **kwargs)

    @commands.command()
    async def hitsperplay(self, ctx, *args):
        """Hitsperplay leaderboard"""
        kwargs = get_args(args)
        kwargs["-float"] = "true"
        if not kwargs.get("-playcount-min"):
            kwargs["-playcount-min"] = 1
        await get_profile_leaderboard(ctx, "(total_hits::float / NULLIF(playcount,0))", "Hits per Play", **kwargs)

    @commands.command(aliases=["join_date"])
    async def joined(self, ctx, *args):
        """Global joined date leaderboard"""
        kwargs = get_args(args)
        if not kwargs.get("-dir"):
            kwargs["-dir"] = "asc"
        await get_profile_leaderboard(ctx, "join_date", "Join Date", **kwargs)

    @commands.command()
    async def level(self, ctx, *args):
        """Global level leaderboard"""
        kwargs = get_args(args)
        kwargs["-float"] = "true"
        if not kwargs.get("-totalscore"):
            kwargs["-totalscore"] = 10_000_000
        await get_profile_leaderboard(ctx, "level", "Level", **kwargs)

    @commands.command(aliases=['mapping_followers'])
    async def mappingfollowers(self, ctx, *args):
        """Global mapping followers leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "mapping_follower_count", "Mapping Followers", **kwargs)

    @commands.command(aliases=["pc"])
    async def playcount(self, ctx, *args):
        """Global Play Count leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "playcount", "Play Count", **kwargs)

    @commands.command()
    async def playtime(self, ctx, *args):
        """Global Play Time leaderboard"""
        kwargs = get_args(args)
        kwargs["-fomarttime"] = "true"
        await get_profile_leaderboard(ctx, "playtime", "Play Time", **kwargs)

    @commands.command()
    async def rankedscore(self, ctx, *args):
        """Ranked Score leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "ranked_score", "Ranked Score", **kwargs)

    @commands.command()
    async def rankedscoreperclear(self, ctx, *args):
        """Ranked Score per Clear leaderboard"""
        kwargs = get_args(args)
        if not kwargs.get("-rankedscore"):
            kwargs["-rankedscore"] = 100_000_000
        await get_profile_leaderboard(ctx, "cast(ranked_score / greatest((ssh_count + sh_count + s_count + ss_count + a_count), 1) as float)", "Ranked Score per Clear", **kwargs)

    @commands.command()
    async def rankedscoreperhit(self, ctx, *args):
        """Ranked Score per Hit leaderboard"""
        kwargs = get_args(args)
        if not kwargs.get("-rankedscore"):
            kwargs["-rankedscore"] = 100_000_000
        await get_profile_leaderboard(ctx, "cast(ranked_score / greatest((total_hits), 1) as int)", "Ranked Score per Hit", **kwargs)

    @commands.command(aliases=["scoreperplay"])
    async def rankedscoreperplay(self, ctx, *args):
        """Ranked Score per Play leaderboard"""
        kwargs = get_args(args)
        if not kwargs.get("-rankedscore"):
            kwargs["-rankedscore"] = 100_000_000
        await get_profile_leaderboard(ctx, "cast(ranked_score / greatest((playcount), 1) as int)", "Ranked Score per Play", **kwargs)

    @commands.command()
    async def replayswatched(self, ctx, *args):
        """Replays watched leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "replays_watched", "Replays watched", **kwargs)

    @commands.command()
    async def scoreratio(self, ctx, *args):
        """Ranked score to total score ratio leaderboard"""
        kwargs = get_args(args)
        kwargs["-o"] = "completion"
        if not kwargs.get("-rankedscore"):
            kwargs["-rankedscore"] = 100_000_000
        await get_profile_leaderboard(ctx, "round((cast(ranked_score::float / GREATEST(total_score, 1)::float * 100 as numeric)),3)", "Score Ratio", **kwargs)

    @commands.command()
    async def silver_s(self, ctx, *args):
        """Silver S leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "sh_count", "Silver S", **kwargs)

    @commands.command()
    async def silver_ss(self, ctx, *args):
        """Silver SS leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "ssh_count", "Silver SS", **kwargs)

    @commands.command()
    async def totalhits(self, ctx, *args):
        """Global Total Hits leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "total_hits", "Total Hits", **kwargs)

    @commands.command()
    async def totalscore(self, ctx, *args):
        """Total Score leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "total_score", "Total Score", **kwargs)

    @commands.command()
    async def totalscoreperclear(self, ctx, *args):
        """Total Score per Clear leaderboard"""
        kwargs = get_args(args)
        if not kwargs.get("-totalscore"):
            kwargs["-totalscore"] = 100_000_000
        await get_profile_leaderboard(ctx, "cast(total_score / greatest((ssh_count + sh_count + s_count + ss_count + a_count), 1) as float)", "Total Score per Clear", **kwargs)

    @commands.command()
    async def totalscoreperhit(self, ctx, *args):
        """Total Score per Hit leaderboard"""
        kwargs = get_args(args)
        if not kwargs.get("-totalscore"):
            kwargs["-totalscore"] = 100_000_000
        await get_profile_leaderboard(ctx, "cast(total_score / greatest((total_hits), 1) as int)", "Total Score per Hit", **kwargs)

    @commands.command()
    async def totalscoreperplay(self, ctx, *args):
        """Total Score per Play leaderboard"""
        kwargs = get_args(args)
        if not kwargs.get("-totalscore"):
            kwargs["-totalscore"] = 100_000_000
        await get_profile_leaderboard(ctx, "cast(total_score / greatest((playcount), 1) as int)", "Total Score per Play", **kwargs)

    @commands.command()
    async def total_s(self, ctx, *args):
        """Total S leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "sh_count + s_count", "Total S", **kwargs)

    @commands.command()
    async def total_ss(self, ctx, *args):
        """Total SS leaderboard"""
        kwargs = get_args(args)
        await get_profile_leaderboard(ctx, "ssh_count + ss_count", "Total SS", **kwargs)

    @commands.command()
    async def mapsranked(self, ctx, *args):
        """Returns a leaderboard for the most difficulties ranked by a mapper"""
        kwargs = get_args(args)
        await get_mapper_leaderboard(ctx, "beatmap_id", "Ranked Beatmaps", **kwargs)

    @commands.command()
    async def setsranked(self, ctx, *args):
        """Returns a leaderboard for the most sets ranked by a mapper"""
        kwargs = get_args(args)
        await get_mapper_leaderboard(ctx, "set_id", "Ranked Beatmapsets", **kwargs)

    @commands.command()
    async def highest_replays(self, ctx, *args):
        """Highest monthly replays"""
        kwargs = get_args(args)
        await check_array_stats(ctx, "max(count)", "user_replay_counts", "username, start_date", kwargs, "Most Replays watched")

    @commands.command()
    async def highest_playcount(self, ctx, *args):
        """Highest monthly Play Count"""
        kwargs = get_args(args)
        await check_array_stats(ctx, "max(count)", "user_playcounts", "username, start_date", kwargs, "Highest Play Count")

    @commands.command(aliases=['badges'])
    async def most_badges(self, ctx, *args):
        """Most Badges"""
        kwargs = get_args(args)
        await check_array_stats(ctx, "count(*)", "user_badges", "username", kwargs, "Most Badges")

    @commands.command(aliases=['medals'])
    async def most_medals(self, ctx, *args):
        """Most Badges"""
        kwargs = get_args(args)
        await check_array_stats(ctx, "count(*)", "user_achievements", "username", kwargs, "Medal Count")

    @commands.command()
    async def rarest_medals(self, ctx, *args):
        """Rarest Medals"""
        kwargs = get_args(args)
        await check_array_stats(ctx, "count(*)", "user_achievements", "achievement_id::text as username", kwargs, "Rarest Medals")

async def setup(bot):
    await bot.add_cog(Profile(bot))
