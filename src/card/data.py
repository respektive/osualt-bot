import requests
import time
from card.image import draw_card
from card.embed import get_card_embed
from sql.db import Database

db = Database()

def get_avatar_url_from_id(user_id):
    return f"https://a.ppy.sh/{user_id}?{int(time.time())}"


def get_image_data_from_url(image_url):
    response = requests.get(image_url)
    image_data = response.content
    return image_data


async def get_user_data(user_id):
    rows = await db.execute_query(f"SELECT * FROM users2 WHERE user_id = {user_id}")
    if len(rows) < 1:
        raise ValueError(f"Couldn't find user with user_id: {user_id}")
    
    return rows[0]


async def get_card(user_id):
    user_data = await get_user_data(user_id)
    avatar_url = get_avatar_url_from_id(user_id)
    avatar_data = get_image_data_from_url(avatar_url)
    filepath = draw_card(user_data, avatar_data)
    embed, file = get_card_embed(filepath)
    return embed, file
