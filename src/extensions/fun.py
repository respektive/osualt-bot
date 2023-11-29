from discord.ext import commands
import discord


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def streamin(self, ctx):
        """he stinks"""
        await ctx.reply("stinks")

    @commands.command()
    async def kilgar(self, ctx):
        """ostrich"""
        embed = discord.Embed(color=0x3498DB)
        embed.set_image(url="https://pek.li/xnmvtt.png")
        await ctx.reply(embed=embed)

    @commands.command()
    async def raglik(self, ctx):
        """hcirtso"""
        embed = discord.Embed(color=0x3498DB)
        embed.set_image(url="https://pek.li/z9xb4l.png")
        await ctx.reply(embed=embed)

    @commands.command()
    async def abababa(self, ctx):
        """abababa"""
        embed = discord.Embed(color=0xC85050)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/653927651618193428.gif?size=96"
        )
        await ctx.reply(embed=embed)

    @commands.command(name="!", aliases=["skillissue", "skill"])
    async def skillissue(self, ctx):
        """skill issue"""
        embed = discord.Embed(
            title="Skill issue",
            description="did you know\nstreamin smells a lot\nand showers once a month",
            color=0xF3B4EF,
        )
        embed.set_thumbnail(url="https://pek.li/1jv44n.gif")
        await ctx.reply(embed=embed)

    @commands.command()
    async def hitogata(self, ctx):
        """hey human"""
        embed = discord.Embed(
            title="Hey, Human...",
            description="Tell us the Secret of Life!!",
            color=0xDA0E4D,
        )
        embed.set_thumbnail(url="https://b.ppy.sh/thumb/942714l.jpg")
        await ctx.reply(embed=embed)

    @commands.command()
    async def crawl(self, ctx):
        """lalala"""
        embed = discord.Embed(title="Crawl", description="lalalala~~", color=0xDCCB93)
        embed.set_thumbnail(url="https://b.ppy.sh/thumb/2443l.jpg")
        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Fun(bot))
