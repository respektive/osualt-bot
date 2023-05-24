import io
import discord


def get_card_embed(image, user_data, avatar_url):
    author_string = f"""{user_data["username"]} - {user_data["pp"]:,}pp (#{user_data["global_rank"]:,}) ({user_data["country_code"]}#{user_data["country_rank"]:,})"""

    embed = discord.Embed(colour=discord.Colour(0xCC5288))
    embed.set_author(
        name=author_string,
        icon_url=avatar_url,
        url=f"https://osu.ppy.sh/users/{user_data['user_id']}",
    )

    image_data = io.BytesIO()
    image.save(image_data, format="PNG")
    image_data.seek(0)

    file = discord.File(image_data, filename="card.png")

    embed.set_image(url="attachment://card.png")

    return embed, file
