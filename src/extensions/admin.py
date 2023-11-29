from discord.ext import commands
from utils.helpers import get_args
import sys
import subprocess

RESTART_SCRIPT_PATH = "/home/osualt/start_bot.sh"


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def restart(self, ctx):
        """Restarts the bot"""
        stream = subprocess.run(
            [RESTART_SCRIPT_PATH], stdout=subprocess.PIPE, text=True
        )
        output = stream.stdout
        print(output)
        await ctx.message.author.send(output)
        await ctx.message.add_reaction("👍")
        sys.exit()


async def setup(bot):
    await bot.add_cog(Admin(bot))
