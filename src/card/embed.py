import io
import discord


def get_card_embed(filepath):
    embed = discord.Embed(colour=discord.Colour(0xcc5288))

    with open(filepath, "rb") as file:
        image_data = file.read()

    file = discord.File(io.BytesIO(image_data), filename="card.png")

    embed.set_image(url="attachment://card.png")

    return embed, file