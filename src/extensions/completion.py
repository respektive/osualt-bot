from discord.ext import commands
from utils.helpers import get_args
from sql.queries import get_completion, get_pack_completion

class Completion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=["ac", "arc"])
    async def ar_completion(self, ctx, *args):
        """AR completion board for a single user"""
        kwargs = get_args(args)
        await get_completion(ctx, "ar", kwargs)

    @commands.command(aliases=["cc", "csc"])
    async def cs_completion(self, ctx, *args):
        """CS completion board for a single user"""
        kwargs = get_args(args)
        await get_completion(ctx, "cs", kwargs)

    @commands.command(aliases=["oc", "odc"])
    async def od_completion(self, ctx, *args):
        """OD completion board for a single user"""
        kwargs = get_args(args)
        await get_completion(ctx, "od", kwargs)

    @commands.command(aliases=["star_completion", "sr_complation", "sc"])
    async def stars_completion(self, ctx, *args):
        """Stars completion board for a single user"""
        kwargs = get_args(args)
        await get_completion(ctx, "stars", kwargs)

    @commands.command(aliases=["maxcombo_completion", "coc"])
    async def combo_completion(self, ctx, *args):
        """Combo completion board for a single user"""
        kwargs = get_args(args)
        await get_completion(ctx, "combo", kwargs)

    @commands.command(aliases=["lc"])
    async def length_completion(self, ctx, *args):
        """Length completion board for a single user"""
        kwargs = get_args(args)
        await get_completion(ctx, "length", kwargs)

    @commands.command(aliases=["rank_completion", "letter_completion", "gc", "rc"])
    async def grade_completion(self, ctx, *args):
        """Grade completion board for a single user"""
        kwargs = get_args(args)
        await get_completion(ctx, "grade", kwargs)

    @commands.command(aliases=["rank_breakdown", "letter_breakdown", "letters", "ranks", "grades"])
    async def grade_breakdown(self, ctx, *args):
        """Grade Breakdown board for a single user"""
        kwargs = get_args(args)
        await get_completion(ctx, "grade_breakdown", kwargs)

    @commands.command(aliases=["yc"])
    async def yearly_completion(self, ctx, *args):
        """Yearly completion board for a single user"""
        kwargs = get_args(args)
        await get_completion(ctx, "yearly", kwargs)

    @commands.command(aliases=["packs_completion", "pac"])
    async def pack_completion(self, ctx, *args):
        """Pack completion board for a single user"""
        kwargs = get_args(args)
        await get_pack_completion(ctx, kwargs)

async def setup(bot):
    await bot.add_cog(Completion(bot))