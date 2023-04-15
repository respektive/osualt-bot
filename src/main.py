import discord
from discord.ext import commands
import os
import sys
import traceback
from dotenv import load_dotenv
from utils.misc import updatelists

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
allowed_mentions = discord.AllowedMentions(
        users=True,         # Whether to ping individual user @mentions
        everyone=False,      # Whether to ping @everyone or @here mentions
        roles=True,         # Whether to ping role @mentions
        replied_user=True,  # Whether to ping on replies to messages
    )
bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents, allowed_mentions=allowed_mentions, help_command=None)

@bot.event
async def setup_hook() -> None:
    extensions_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'extensions'))
    for filename in os.listdir(extensions_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            await bot.load_extension(f'extensions.{filename[:-3]}')

@bot.event 
async def on_ready():
    print('Python Version: ' + sys.version)
    print('Ready')

@bot.event
async def on_member_join(member):
    print(f'{member} just joined the server.')

@bot.event
async def on_command_error(ctx, error):
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    if isinstance(error, commands.MissingPermissions):
        error = "You don't have permission to use this command!"
    elif isinstance(error, ValueError):
        error = error.original
    else:
        error = error

    embed = discord.Embed(title = "Error", colour=discord.Colour(0xcc5288))
    embed.description = "```\n" + f'{error}' + "\n```"

    await ctx.reply(embed=embed)

@bot.event
async def on_command_completion(ctx):
    await updatelists(bot)

bot.run(DISCORD_TOKEN)