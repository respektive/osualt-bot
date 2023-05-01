from discord.ext import commands
import discord
from utils.command_params import COMMAND_FLAGS, COG_FLAGS, SPECIAL_COMMAND_PARAMS, EXTRA_COMMAND_FLAGS

FUN_PARAMS = ["me", "you", "abababa", "kilgar", "respektive"]

def get_fun_embed(param):
    embed = discord.Embed(colour=0xcc5288)
    if param == "me":
        embed.title = "You can't be helped."
    elif param == "you":
        embed.title = "who"
    elif param == "abababa":
        embed.color=0xc85050 
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/653927651618193428.gif?size=96")
    elif param == "kilgar":
        embed.color=0x3498db 
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/931703750983299072.webp?size=96&quality=lossless")
    elif param == "respektive":
        embed.color=0xc85050
        embed.title = "罗纳德 respektive 麦当劳 clown 精神错乱 incident"

    return embed

class HelpView(discord.ui.View):
    def __init__(self, bot, user):
        super().__init__()

        self.bot = bot
        self.user = user

        # Dynamically create select menu options based on cogs
        cog_names = [cog.__class__.__name__.capitalize() for cog in bot.cogs.values()]
        select_options = [discord.SelectOption(label=name, value=name.lower()) for name in cog_names]

        # Create a select menu with options for each category
        self.category_select = discord.ui.Select(
            placeholder="Select a category",
            options=select_options
        )

        # Add the select menu to the view
        self.add_item(self.category_select)

        # Define an event listener for the select menu
        self.category_select.callback = self.on_select

    async def on_select(self, interaction: discord.Interaction):
        # Check if the user who issued the command is the one who made the selection
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("You can't select this option.", ephemeral=True)

        # Get the selected category
        selected_category = interaction.data["values"][0]

        # Get the corresponding cog and its commands
        cog = self.bot.get_cog(selected_category.capitalize())
        commands = sorted(cog.get_commands(), key=lambda c: c.name)

        # Create a list of command names and descriptions
        command_list = []
        for command in commands:
            name = f"`!{command.name}`"
            if command.help:
                help_text = command.help
            else:
                help_text = "No help available."
            command_list.append(f"{name}: {help_text}")

        # Create an embed with the list of commands
        embed = discord.Embed(title=f"{selected_category.capitalize()} Commands", colour=0xcc5288)
        embed.description = "\n".join(command_list)

        # Add a note to the description
        embed.description += "\n\nUse `!help command-name` for more information about a specific command."

        # Update the message with the embed
        await interaction.response.edit_message(embed=embed)


class ParametersView(discord.ui.View):
    def __init__(self, bot, user):
        super().__init__()

        self.bot = bot
        self.user = user

        # Dynamically create select menu options based on categories
        select_options = [
            discord.SelectOption(label=COMMAND_FLAGS[category]["name"], value=category.lower())
            for category in COMMAND_FLAGS
        ]

        # Create a select menu with options for each category
        self.category_select = discord.ui.Select(
            placeholder="Select a category",
            options=select_options
        )

        # Add the select menu to the view
        self.add_item(self.category_select)

        # Define an event listener for the select menu
        self.category_select.callback = self.on_select

    async def on_select(self, interaction: discord.Interaction):
        # Check if the user who issued the command is the one who made the selection
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("You can't select this option.", ephemeral=True)

        # Get the selected category
        selected_category = interaction.data["values"][0]

        # Get the corresponding parameters for the selected category
        category_params = COMMAND_FLAGS[selected_category]["value"]

        # Create an embed with the list of parameters
        embed = discord.Embed(title=COMMAND_FLAGS[selected_category]['name'], colour=0xcc5288)
        embed.description = category_params

        # Update the message with the embed
        await interaction.response.edit_message(embed=embed)


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, command_name: str = None):
        """Command for seeing every command"""
        command_name = command_name.lower() if command_name else None # ensure lowercase
        if command_name is None:
            # Show the category select dropdown
            embed = discord.Embed(title="Help", colour=0xcc5288)
            embed.description = "Select a category to see the available commands or request help for a specific command using `!help command-name`."
            view = HelpView(self.bot, ctx.author)
            await ctx.reply(embed=embed, view=view)
        elif command_name == "parameters":
            # Show the category select dropdown
            embed = discord.Embed(title="Parameters", colour=0xcc5288)
            embed.description = "Select a category to see the available parameters."
            view = ParametersView(self.bot, ctx.author)
            await ctx.reply(embed=embed, view=view)
        elif command_name in FUN_PARAMS:
            embed = get_fun_embed(command_name)
            await ctx.reply(embed=embed)
        else:
            # Show the help for the specific command
            command = self.bot.get_command(command_name)
            if command is None:
                embed = discord.Embed(title = "Error", colour=discord.Colour(0xcc5288))
                embed.description = "```\n" + f"Command \"{command_name}\" is not found" + "\n```"

                await ctx.reply(embed=embed)
                return
            embed = discord.Embed(title=f"Help: !{command.name}", description=command.help, colour=0xcc5288)

            # Check if the command has special parameters
            special_params = SPECIAL_COMMAND_PARAMS.get(command.name)
            if special_params is not None:
                embed.add_field(name="Special Parameters", value=special_params)

            # Check if the command's cog has associated flags
            cog_flags = COG_FLAGS.get(command.cog_name.lower())
            if cog_flags:
                for flag in cog_flags:
                    embed.add_field(name=COMMAND_FLAGS[flag]["name"], value=COMMAND_FLAGS[flag]["value"], inline=False)

            # Check if the command has associated flags
            command_flags = EXTRA_COMMAND_FLAGS.get(command.name)
            if command_flags:
                for flag in command_flags:
                    embed.add_field(name=COMMAND_FLAGS[flag]["name"], value=COMMAND_FLAGS[flag]["value"], inline=False)

            # Add a field for aliases, if the command has any
            if command.aliases:
                aliases_text = ", ".join([f"`!{alias}`" for alias in command.aliases])
                embed.add_field(name="Aliases", value=aliases_text, inline=False)

            await ctx.reply(embed=embed)
    
    @commands.command(aliases=["about", "github"])
    async def info(self, ctx):
        """Displays information about the bot"""
        embed = discord.Embed(title=f"Info", description="The prefix for this bot is `!`. **Bot is standard only**.\nPermanent Server Invite: https://discord.gg/osualt", color=0xcc5288)

        embed.add_field(name="Read #info", value=" Read <#792857827219079208> to get an idea on how the bot works and how to register.", inline=False)
        embed.add_field(name="Commands", value="Request help for a specific command using `!help command-name` and help for filters can be requested using `!help parameters`.\nFor a full list of every command use `!help`.", inline=False)
        embed.add_field(name="GitHub", value="The Discord portion of the bot is open-source and can be found on GitHub [here](https://github.com/respektive/osualt-bot).\nThe tracker is made by Ciuriya#0037 and can be found on GitHub [here](https://github.com/Ciuriya/osualt-play-tracker).\nThe backend that is fetching all the stats and scores is currently not open-source.", inline=False)
        embed.add_field(name="Scores inspector", value="The scores inspector is made by Amayakase#9198 and has access to the bots database and generates statistics and graphs from it. It can be found [here](https://darkchii.nl/score/).", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))