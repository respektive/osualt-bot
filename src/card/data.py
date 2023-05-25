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


async def get_user_data(user_id, kwargs):
    rows = await db.execute_query(
        f"""WITH beatmaps_count_cte AS (
            SELECT COUNT(DISTINCT beatmap_id) AS beatmaps_count
            FROM beatmaps
            WHERE mode = 0 AND approved IN (1, 2{', 4' if "-loved" in kwargs and kwargs["-loved"] == 'true' else ''})
        ), scores_count_cte AS (
            SELECT
                COUNT(DISTINCT beatmaps.beatmap_id) AS scores_count,
                COUNT(CASE WHEN scores.rank = 'X' THEN 1 END) AS grade_x_count,
                COUNT(CASE WHEN scores.rank = 'XH' THEN 1 END) AS grade_xh_count,
                COUNT(CASE WHEN scores.rank = 'S' THEN 1 END) AS grade_s_count,
                COUNT(CASE WHEN scores.rank = 'SH' THEN 1 END) AS grade_sh_count,
                COUNT(CASE WHEN scores.rank = 'A' THEN 1 END) AS grade_a_count,
                COUNT(CASE WHEN scores.rank = 'B' THEN 1 END) AS grade_b_count,
                COUNT(CASE WHEN scores.rank = 'C' THEN 1 END) AS grade_c_count,
                COUNT(CASE WHEN scores.rank = 'D' THEN 1 END) AS grade_d_count
            FROM scores
            LEFT JOIN beatmaps ON beatmaps.beatmap_id = scores.beatmap_id
            WHERE scores.user_id = {user_id} AND beatmaps.mode = 0
            AND beatmaps.approved IN (1, 2{', 4' if "-loved" in kwargs and kwargs["-loved"] == 'true' else ''})
        ), ranked_score_rank_cte AS (
            SELECT
                user_id,
                ranked_score,
                RANK() OVER (ORDER BY ranked_score DESC) AS score_rank
            FROM users2
        ), medal_count_cte AS (
            SELECT
                COUNT(*) AS medal_count
            FROM user_achievements
            WHERE user_id = {user_id}
        )
        SELECT
            users2.*,
            beatmaps_count_cte.*,
            scores_count_cte.*,
            medal_count_cte.medal_count,
            ranked_score_rank_cte.score_rank
        FROM users2
        CROSS JOIN beatmaps_count_cte
        CROSS JOIN scores_count_cte
        CROSS JOIN medal_count_cte
        JOIN ranked_score_rank_cte ON ranked_score_rank_cte.user_id = users2.user_id
        WHERE users2.user_id = {user_id}"""
    )
    if len(rows) < 1:
        raise ValueError(f"Couldn't find user with user_id: {user_id}")

    return rows[0]


async def get_card(user_id, kwargs):
    query_start_time = time.time()

    user_data = await get_user_data(user_id, kwargs)
    # Fallback to generating an avatar_url if for some reason the url is not set
    avatar_url = user_data["avatar_url"] or get_avatar_url_from_id(user_id)
    avatar_data = get_image_data_from_url(avatar_url)
    image = draw_card(user_data, avatar_data)
    embed, file = get_card_embed(image, user_data, avatar_url)

    query_end_time = time.time()
    query_execution_time = round(query_end_time - query_start_time, 2)

    embed.set_footer(
        text=f"Based on Scores in the database • took {query_execution_time}s",
        icon_url="https://pek.li/maj7qa.png",
    )

    return embed, file
