import calendar
import datetime
import decimal
import time
import math
import discord
from .db import Database
from utils.helpers import (
    build_where_clause,
    unique_tables,
    get_mods_string,
    normalize_year,
)
from utils.format import format_leaderboard

db = Database()

blacklist = [
    "-is_fc",
    "-is_ss",
    "-is_nc",
    "-is_dt",
    "-is_fl",
    "-is_hr",
    "-is_hd",
    "-is_ht",
    "-is_nf",
    "-is_ez",
    "-is_so",
    "-is_sd",
    "-is_pf",
    "-is_td",
    "-country",
    "-registered",
    "-is_fullmod",
    "-is_nm",
    "-is",
    "-isnot",
    "-u",
    "-letter",
    "-letters",
    "-played-start",
    "-played-end",
    "-pp-min",
    "-pp-max",
    "-status",
    "-score",
    "-score-max",
    "-miss-max",
    "-miss-min",
    "-combo-min",
    "-combo-max",
    "-combo",
    "-rankedscore",
    "-rankedscore-max",
    "-country",
    "-totalscore",
    "-totalscore-max",
    "-profile-pp",
    "-profile-pp-max",
    "-playcount-min",
    "-playcount-max",
    "-playcount-range",
    "-ss-min",
    "-ss-max",
    "-ss-range",
    "-300-max",
    "-300-min",
    "-300-range",
    "-100-max",
    "-100-min",
    "-100-range",
    "-50-max",
    "-50-min",
    "-50-range",
    "-fc-max",
    "-fc-min",
    "-fc-range",
    "-s-max",
    "-s-min",
    "-s-range",
    "-a-max",
    "-a-min",
    "-a-range",
    "-clears-max",
    "-clears-min",
    "-clears-range",
    "-pp-range",
    "-combo-range",
    "-replay",
    "-tragedy",
    "-joined-start",
    "-joined-end",
    "-profile-pp-min",
    "-acc-min",
    "-acc-max",
    "-not",
    "-time",
    "-user",
    "-rank",
    "-score-min",
    "-played-date",
    "-c",
]


async def register_user(user_id):
    query = "INSERT INTO priorityuser VALUES ($1) ON CONFLICT DO NOTHING"
    await db.execute_query(query, int(user_id))


async def insert_into_scorequeue(beatmap_id, user_id):
    query = "INSERT INTO scorequeue VALUES($1, $2)"
    await db.execute_query(query, user_id, beatmap_id)


async def insert_into_queue(rows, user_id):
    query = "INSERT INTO queue VALUES($1, $2)"
    for row in rows:
        await db.execute_query(query, user_id, row[0])


async def get_queue_length():
    query = "SELECT COUNT(*) FROM queue"
    result = await db.execute_query(query)
    count = result[0][0]
    return (
        "Queue length: "
        + str(count)
        + "\nETA: ~"
        + str(math.ceil(count * 2 / 60))
        + " minutes"
    )


async def check_profile(ctx, stat, di):
    # format the base level data
    base = f"select user_id, {stat} as stat from users2 inner join users_ppv1 using (user_id)"
    base = base + build_where_clause(di)

    # build and execute the leaderboard creating query
    query = await build_leaderboard(ctx, base, di)
    print(query)
    result = await db.execute_query(query)

    return result


async def check_mappers(ctx, stat, di):
    # format the base level data
    base = f"select user_id, count(distinct {stat}) as stat from beatmaps inner join users2 on user_id = creator_id"
    base = base + build_where_clause(di)
    base = base + " group by username"

    # build and execute the leaderboard creating query
    query = await build_leaderboard(ctx, base, di)
    print(query)
    result = await db.execute_query(query)

    return result


async def get_mapper_leaderboard(ctx, stat, title, **kwargs):
    query_start_time = time.time()
    rows = await check_mappers(ctx, stat, kwargs)
    query_end_time = time.time()
    query_execution_time = round(query_end_time - query_start_time, 2)
    embed = format_leaderboard(rows, kwargs)

    embed.title = title
    embed.set_footer(
        text=f"Based on Profile Stats • took {query_execution_time}s",
        icon_url="https://pek.li/maj7qa.png",
    )

    await ctx.reply(embed=embed)


async def get_profile_leaderboard(ctx, stat, title, **kwargs):
    query_start_time = time.time()
    rows = await check_profile(ctx, stat, kwargs)
    query_end_time = time.time()
    query_execution_time = round(query_end_time - query_start_time, 2)
    embed = format_leaderboard(rows, kwargs)

    embed.title = title
    embed.set_footer(
        text=f"Based on Profile Stats • took {query_execution_time}s",
        icon_url="https://pek.li/maj7qa.png",
    )

    await ctx.reply(embed=embed)


async def get_ppv1_leaderboard(ctx, stat, title, **kwargs):
    query_start_time = time.time()
    rows = await check_profile(ctx, stat, kwargs)
    query_end_time = time.time()
    query_execution_time = round(query_end_time - query_start_time, 2)
    embed = format_leaderboard(rows, kwargs)

    embed.title = title
    embed.set_footer(
        text=f"Updated every ~30min • took {query_execution_time}s",
        icon_url="https://pek.li/maj7qa.png",
    )

    await ctx.reply(embed=embed)


async def check_array_stats(ctx, operation, table, aggregate, di, title=None):
    base = f"select {aggregate}, {operation} as stat from {table} inner join users2 on {table}.user_id = users2.user_id"
    base = base + build_where_clause(di)
    if aggregate == "achievement_id::text as username":
        aggregate = "achievement_id"
    base = base + " group by " + aggregate

    query = await build_leaderboard(ctx, base, di)
    print(query)
    query_start_time = time.time()
    rows = await db.execute_query(query)
    query_end_time = time.time()
    query_execution_time = round(query_end_time - query_start_time, 2)

    if title == None:
        title = "Result"

    embed = format_leaderboard(rows, di)
    embed.title = title
    embed.set_footer(
        text=f"Based on Profile Stats • took {query_execution_time}s",
        icon_url="https://pek.li/maj7qa.png",
    )

    await ctx.reply(embed=embed)


async def check_tables(ctx, operation, table, di, embedtitle=None):
    base = f"select scores.user_id, {operation} as stat from {table} \
            inner join users2 on {table}.user_id = users2.user_id \
            inner join beatmaps on {table}.beatmap_id = beatmaps.beatmap_id"

    if (
        di.get("-pack")
        or di.get("-pack-min")
        or di.get("-pack-max")
        or di.get("-packs")
        or di.get("-apacks")
    ):
        base = (
            base
            + " inner join beatmap_packs on beatmaps.beatmap_id = beatmap_packs.beatmap_id"
        )

    if di.get("-leastssed") and di["-leastssed"] == "true":
        base = (
            base + " inner join ss_count on beatmaps.beatmap_id = ss_count.beatmap_id"
        )

    if (
        di.get("-o") == "missingscore"
        or di.get("-score")
        or di.get("-score-min")
        or di.get("-score-max")
        or di.get("-topscore")
        or di.get("-topscore-min")
        or di.get("-topscore-max")
        or di.get("-scorepersecond")
        or di.get("-scorepersecond-min")
        or di.get("-scorepersecond-max")
    ):
        base = (
            base
            + " inner join (select beatmap_id, top_score from top_score) top_score on beatmaps.beatmap_id = top_score.beatmap_id"
        )

    if (
        di.get("-o") == "missingnomodscore"
        or di.get("-topscorenomod")
        or di.get("-topscorenomod-min")
        or di.get("-topscorenomod-max")
        or di.get("-nomodscorepersecond")
        or di.get("-nomodscorepersecond-min")
        or di.get("-nomodscorepersecond-max")
    ):
        base = (
            base
            + " inner join (select beatmap_id, top_score_nomod from top_score_nomod) top_score_nomod on beatmaps.beatmap_id = top_score_nomod.beatmap_id"
        )

    if di.get("-o") and di["-o"] == "lazerscore":
        base = base + " inner join mods on scores.enabled_mods = mods.enum"

    if di.get("-rank"):
        base = (
            base
            + " inner join (select beatmap_id, user_id from top_score) firsts on beatmaps.beatmap_id = firsts.beatmap_id"
        )

    if di.get("-modded") and di["-modded"] == "true":
        base = (
            base + " inner join moddedsr on beatmaps.beatmap_id = moddedsr.beatmap_id"
        )

    if table in unique_tables:
        base = (
            base
            + f" inner join scores on {table}.beatmap_id = scores.beatmap_id and {table}.user_id = scores.user_id"
        )

    options = [
        "completion",
        "%",
        "length_completion",
        "length",
        "score",
        "scoer",
        "lazerscore",
        "lazerscore_nomod",
        "lazerscore_standard",
        "lazerscore_standard_nomod",
        "lazerscore_doublesliders",
        "totalpp",
        "pp",
        "weighed_pp",
        "100",
        "50",
        "miss",
        "x",
        "sets",
        "mapsets",
        "agedscore",
        "scorev0",
        "missingscore",
        "missingnomodscore",
    ]

    if not di.get("-loved"):
        di["-loved"] = "false"

    if not di.get("-o") or (di.get("-o") and di["-o"] in options):
        ndi = di.copy()
        ndi["-notscorestable"] = "true"
        mapsets = False
        if di.get("-o"):
            if di["-o"] == "sets" or di["-o"] == "mapsets":
                mapsets = True
            del ndi["-o"]
        beatmap_count = await check_beatmaps(ctx, ndi, None, mapsets)

    base = base + build_where_clause(di)
    base = base + " group by scores.user_id"
    if di.get("-o"):
        if di["-o"] not in options:
            groupby = ""
            columns = di["-o"].split("/")
            for c in columns:
                if ("scores." and "(" and ")") not in c:
                    groupby += f", {c}"

            if len(groupby) > 0:
                base = base + groupby
            if not di.get("-float"):
                di["-float"] = "true"
    if di.get("-groupby"):
        base = base + di["-groupby"]

    if di.get("-o") and di["-o"] == "scorev0":
        base = f"SELECT user_id, SUM(stat) as stat FROM ({base} ,beatmaps.set_id) best_scores GROUP BY best_scores.user_id"

    print("base: ", base)
    query = await build_leaderboard(ctx, base, di)
    print("query:", query)
    query_start_time = time.time()
    rows = await db.execute_query(query)
    query_end_time = time.time()
    query_execution_time = round(query_end_time - query_start_time, 2)

    if embedtitle == None:
        embedtitle = "Result"

    if "beatmap_count" in locals():
        print(beatmap_count)
        embedtitle = embedtitle + " | " + f"{beatmap_count:,}" + " beatmaps"
        if mapsets:
            embedtitle += "ets"

    embed = format_leaderboard(rows, di)
    embed.title = embedtitle
    embed.set_footer(
        text=f"Based on Scores in the database • took {query_execution_time}s",
        icon_url="https://pek.li/maj7qa.png",
    )

    await ctx.reply(embed=embed)


async def check_beatmaps(ctx, di, tables=None, sets=False):
    for key in di.copy().keys():
        if key in blacklist:
            if (key == "-user" or key == "-u") and "-unplayed" in di:
                continue
            del di[key]
    operation = "count(beatmaps.beatmap_id)"
    if "-modded" in di and di["-modded"] == "true":
        operation = "count(distinct beatmaps.beatmap_id)"

    if di.get("-o"):
        if di["-o"] == "length" or di["-o"] == "length_completion":
            operation = "sum(length)"
        if di["-o"] == "score":
            operation = "sum(top_score)"
        if di["-o"] == "nomodscore":
            operation = "sum(top_score_nomod)"
        if di["-o"] == "maxcombo":
            operation = "sum(maxcombo)"
    if not di.get("-mode"):
        di["-mode"] = 0
    if not di.get("-loved"):
        di["-loved"] = "false"

    if di.get("-unplayed") and not di.get("-user"):
        di["-user"] = await get_user_id(ctx, di)

    if sets:
        operation = "count(distinct set_id)"

    query = "select " + operation + " from beatmaps"

    if tables != None:
        for table in tables:
            query = query + " inner join " + table + " using (beatmap_id)"
    if (
        di.get("-pack")
        or di.get("-pack-min")
        or di.get("-pack-max")
        or di.get("-packs")
        or di.get("-apacks")
    ):
        query = (
            query
            + " inner join beatmap_packs on beatmaps.beatmap_id = beatmap_packs.beatmap_id"
        )
    if (
        di.get("-o")
        and di["-o"] == "nomodscore"
        or di.get("-nomodscorepersecond")
        or di.get("-nomodscorepersecond-min")
        or di.get("-nomodscorepersecond-max")
    ):
        query = (
            query
            + " inner join (select beatmap_id, top_score_nomod from top_score_nomod) top_score_nomod on beatmaps.beatmap_id = top_score_nomod.beatmap_id"
        )
    if (
        di.get("-o")
        and di["-o"] == "score"
        or di.get("-scorepersecond")
        or di.get("-scorepersecond-min")
        or di.get("-scorepersecond-max")
    ):
        query = (
            query
            + " inner join (select beatmap_id, top_score from top_score) top_score on beatmaps.beatmap_id = top_score.beatmap_id"
        )
    if (
        di.get("-modded")
        and di["-modded"] == "true"
        or (di.get("-mods") or di.get("-m"))
    ):
        query = (
            query + " inner join moddedsr on beatmaps.beatmap_id = moddedsr.beatmap_id"
        )
    if di.get("-topscore") or di.get("-topscore-min") or di.get("-topscore-max"):
        query = (
            query
            + " inner join (select beatmap_id, top_score from top_score) top_score on beatmaps.beatmap_id = top_score.beatmap_id"
        )
    if di.get("-topscorenomod") or di.get("-topscorenomod-max"):
        query = (
            query
            + " inner join (select beatmap_id, top_score_nomod from top_score_nomod) top_score_nomod on beatmaps.beatmap_id = top_score_nomod.beatmap_id"
        )
    query = query + build_where_clause(di)
    print(query)
    res = await db.execute_query(query)
    ans = res[0][0]
    print(ans)
    if operation == "sum(length)" and not "-noformat" in di:
        if ans == None:
            return "ZERO"
        days = ans // (3600 * 24)
        hours = (ans // 3600) % 24
        minutes = (ans // 60) % 60
        return "Length: " + str(days) + "d" + str(hours) + "h" + str(minutes) + "m"
    else:
        return ans


async def check_weighted_pp(ctx, operation, di, embedtitle=None):
    table = "select scores.user_id, scores.beatmap_id, scores.pp, scores.accuracy, ROW_NUMBER() OVER(partition by scores.user_id order by scores.pp desc) as pp_index from scores inner join users2 on scores.user_id = users2.user_id inner join beatmaps on scores.beatmap_id = beatmaps.beatmap_id"

    if di.get("-o") and di["-o"] == "ppv1":
        table = "select scores_top.user_id, scores_top.beatmap_id, scores_top.pp, scores_top.accuracy from scores_top inner join users2 on scores_top.user_id = users2.user_id inner join beatmaps on scores_top.beatmap_id = beatmaps.beatmap_id"

    if (
        di.get("-pack")
        or di.get("-pack-min")
        or di.get("-pack-max")
        or di.get("-packs")
        or di.get("-apacks")
    ):
        table = (
            table
            + " inner join beatmap_packs on beatmaps.beatmap_id = beatmap_packs.beatmap_id"
        )

    if (
        di.get("-score")
        or di.get("-score-min")
        or di.get("-score-max")
        or di.get("-topscore")
        or di.get("-topscore-min")
        or di.get("-topscore-max")
        or di.get("-scorepersecond")
        or di.get("-scorepersecond-min")
        or di.get("-scorepersecond-max")
    ):
        table = (
            table
            + " inner join (select beatmap_id, top_score from top_score) top_score on beatmaps.beatmap_id = top_score.beatmap_id"
        )

    if (
        di.get("-topscorenomod")
        or di.get("-topscorenomod-min")
        or di.get("-topscorenomod-max")
        or di.get("-nomodscorepersecond")
        or di.get("-nomodscorepersecond-min")
        or di.get("-nomodscorepersecond-max")
    ):
        table = (
            table
            + " inner join (select beatmap_id, top_score_nomod from top_score_nomod) top_score_nomod on beatmaps.beatmap_id = top_score_nomod.beatmap_id"
        )

    if di.get("-modded") and di["-modded"] == "true":
        table = (
            table + " inner join moddedsr on beatmaps.beatmap_id = moddedsr.beatmap_id"
        )

    if not di.get("-loved"):
        di["-loved"] = "false"

    table = table + build_where_clause(di)

    base = (
        "select a.user_id, "
        + str(operation)
        + " as stat from ("
        + str(table)
        + ") as a inner join users2 on a.user_id = users2.user_id inner join beatmaps on a.beatmap_id = beatmaps.beatmap_id group by a.user_id"
    )
    query = await build_leaderboard(ctx, base, di)

    print(query)

    query_start_time = time.time()
    rows = await db.execute_query(query)
    query_end_time = time.time()
    query_execution_time = round(query_end_time - query_start_time, 2)

    embed = format_leaderboard(rows, di)
    embed.title = embedtitle
    embed.set_footer(
        text=f"Based on Scores in the database • took {query_execution_time}s",
        icon_url="https://pek.li/maj7qa.png",
    )

    await ctx.reply(embed=embed)


async def check_weighted_score(ctx, operation, di, embedtitle=None):
    table = "select scores.user_id, scores.beatmap_id, scores.score, ROW_NUMBER() OVER(partition by scores.user_id order by score desc) as score_index from scores inner join beatmaps on scores.beatmap_id = beatmaps.beatmap_id inner join users2 on scores.user_id = users2.user_id"

    if (
        di.get("-score")
        or di.get("-score-min")
        or di.get("-score-max")
        or di.get("-topscore")
        or di.get("-topscore-min")
        or di.get("-topscore-max")
        or di.get("-scorepersecond")
        or di.get("-scorepersecond-min")
        or di.get("-scorepersecond-max")
    ):
        base = (
            base
            + " inner join (select beatmap_id, top_score from top_score) top_score on beatmaps.beatmap_id = top_score.beatmap_id"
        )

    if (
        di.get("-topscorenomod")
        or di.get("-topscorenomod-min")
        or di.get("-topscorenomod-max")
        or di.get("-nomodscorepersecond")
        or di.get("-nomodscorepersecond-min")
        or di.get("-nomodscorepersecond-max")
    ):
        base = (
            base
            + " inner join (select beatmap_id, top_score_nomod from top_score_nomod) top_score_nomod on beatmaps.beatmap_id = top_score_nomod.beatmap_id"
        )

    if not di.get("-loved"):
        di["-loved"] = "false"

    table = table + build_where_clause(di)

    base = (
        "select a.user_id, "
        + str(operation)
        + " as stat from ("
        + str(table)
        + ") as a inner join users2 on a.user_id = users2.user_id inner join beatmaps on a.beatmap_id = beatmaps.beatmap_id group by a.user_id"
    )
    query = await build_leaderboard(ctx, base, di)

    print(query)
    query_start_time = time.time()
    rows = await db.execute_query(query)
    query_end_time = time.time()
    query_execution_time = round(query_end_time - query_start_time, 2)

    embed = format_leaderboard(rows, di)
    embed.title = embedtitle
    embed.set_footer(
        text=f"Based on Scores in the database • took {query_execution_time}s",
        icon_url="https://pek.li/maj7qa.png",
    )

    await ctx.reply(embed=embed)


async def get_beatmap_list(
    ctx,
    di,
    tables=None,
    sets=False,
    bonusColumn=None,
    missingScore=False,
    returnCount=False,
):
    limit = 10
    page = 1
    order = "stars"
    direction = "asc"
    unique_table = None
    if di.get("-order"):
        if di["-order"] == "date":
            di["-order"] = "date_played"
        if di["-order"] == "approved_date":
            di["-order"] = "beatmaps.approved_date"
        if di["-order"] == "mods":
            di["-order"] = "enabled_mods"
        if di["-order"] == "agedscore":
            if not di.get("-direction") or di.get("-dir"):
                di["-direction"] = "desc"
            di[
                "-order"
            ] = "score * (DATE_PART('year', NOW() - approved_date) + DATE_PART('day', NOW() - approved_date) / 365.2425)"
        if di["-order"] == "lazerscore":
            if not di.get("-direction") or di.get("-dir"):
                di["-direction"] = "desc"
            standardised = "(((((50 * scores.count50 + 100 * scores.count100 + 300 * scores.count300) / (300 * scores.count50 + 300 * scores.count100 + 300 * scores.count300 + 300 * scores.countmiss)::float) * 300000) + ((scores.combo/beatmaps.maxcombo::float)*700000)) * mods.multiplier)"
            max_score = "1000000"
            totalHitObjects = (
                "(beatmaps.circles + beatmaps.spinners + beatmaps.sliders)"
            )
            di[
                "-order"
            ] = f"(POW((({standardised} / {max_score}) * {totalHitObjects}), 2) * 36)::int"
        if (
            di["-order"] == "score"
            or di["-order"] == "pp"
            or di["-order"] == "nomodscore"
            or di["-order"] == "top_score"
        ):
            if not di.get("-direction") or di.get("-dir"):
                di["-direction"] = "desc"
            if di["-order"] == "nomodscore":
                di["-order"] = "top_score_nomod"
                di["-o"] = "nomodscore"
        order = str(di["-order"])
        if bonusColumn == None:
            if order not in (
                "set_id",
                "beatmaps.beatmap_id",
                "beatmap_id",
                "artist",
                "title",
                "diffname",
                "stars",
            ):
                bonusColumn = str(di["-order"])
    if di.get("-direction") or di.get("-dir"):
        if di.get("-dir"):
            di["-direction"] = di["-dir"]
        direction = di["-direction"]
    if di.get("-l"):
        limit = di["-l"]
    if di.get("-p"):
        page = di["-p"]
    offset = int(limit) * (int(page) - 1)

    if not di.get("-mode"):
        di["-mode"] = "0"

    if not di.get("-loved"):
        di["-loved"] = "false"

    if not di.get("-notscorestable") == "true" or "-unplayed" in di:
        user_id = await get_user_id(ctx, di)
        di["-user"] = user_id
        di["-u"] = user_id

    count_query = "select count(beatmaps.beatmap_id)"
    if sets:
        count_query = "select count(distinct beatmaps.set_id)"
    elif returnCount and (di.get("-o") == "score" or di.get("-o") == "nomodscore"):
        count_query = "select sum(scores.score)"

    count_query = count_query + " from beatmaps"
    if tables != None:
        for table in tables:
            if table == "mods":
                count_query = (
                    count_query
                    + " inner join "
                    + table
                    + " on scores.enabled_mods = "
                    + table
                    + ".enum"
                )
            else:
                count_query = (
                    count_query + " inner join " + table + " using (beatmap_id)"
                )
            if table in unique_tables:
                count_query = (
                    count_query
                    + f" inner join scores on {table}.beatmap_id = scores.beatmap_id and {table}.user_id = scores.user_id"
                )
                unique_table = table

    if (
        di.get("-pack")
        or di.get("-pack-min")
        or di.get("-pack-max")
        or di.get("-packs")
        or di.get("-apacks")
    ):
        count_query = (
            count_query
            + " inner join beatmap_packs on beatmaps.beatmap_id = beatmap_packs.beatmap_id"
        )
    if di["-mode"] == "0":
        if tables == None:
            if (di.get("-o") and di["-o"] == "nomodscore") or (
                di.get("-topscorenomod") or di.get("-topscorenomod-max")
            ):
                count_query = (
                    count_query
                    + " inner join (select beatmap_id, top_score_nomod from top_score_nomod) top_score_nomod on beatmaps.beatmap_id = top_score_nomod.beatmap_id"
                )
            else:
                count_query = (
                    count_query
                    + " inner join (select beatmap_id, top_score from top_score) top_score on beatmaps.beatmap_id = top_score.beatmap_id"
                )
        elif not ("top_score" in tables or "top_score_nomod" in tables):
            if (di.get("-o") and di["-o"] == "nomodscore") or (
                di.get("-topscorenomod") or di.get("-topscorenomod-max")
            ):
                count_query = (
                    count_query
                    + " inner join (select beatmap_id, top_score_nomod from top_score_nomod) top_score_nomod on beatmaps.beatmap_id = top_score_nomod.beatmap_id"
                )
            else:
                count_query = (
                    count_query
                    + " inner join (select beatmap_id, top_score from top_score) top_score on beatmaps.beatmap_id = top_score.beatmap_id"
                )

    if di.get("-rank"):
        count_query = (
            count_query
            + " inner join (select beatmap_id, user_id from top_score) firsts on beatmaps.beatmap_id = firsts.beatmap_id"
        )

    if di.get("-modded") and di["-modded"] == "true":
        count_query = (
            count_query
            + " inner join moddedsr on beatmaps.beatmap_id = moddedsr.beatmap_id"
        )

    count_query = count_query + build_where_clause(di, unique_table)
    print("Count query: " + count_query)
    count_res = await db.execute_query(count_query)
    if len(count_res) > 0:
        count = count_res[0][0]
    if returnCount == True:
        return count

    query = "select set_id, beatmaps.beatmap_id, artist, title, diffname, stars"

    if di.get("-modded") and di["-modded"] == "true":
        query = "select set_id, beatmaps.beatmap_id, artist, title, diffname, moddedsr.star_rating::numeric as stars"

    if bonusColumn != None:
        query = query + ", " + bonusColumn
    if sets:
        query = "select set_id, max(beatmaps.beatmap_id) as beatmap_id, max(beatmaps.artist) as artist, max(beatmaps.title) as title, max(beatmaps.diffname) as diffname, max(beatmaps.stars) as stars"
        if bonusColumn != None:
            query = query + ", max(" + bonusColumn + ") as bonuscolumn"
    query = query + " from beatmaps"
    if tables != None:
        for table in tables:
            if table == "mods":
                query = (
                    query
                    + " inner join "
                    + table
                    + " on scores.enabled_mods = "
                    + table
                    + ".enum"
                )
            else:
                query = query + " inner join " + table + " using (beatmap_id)"
            if table in unique_tables:
                query = (
                    query
                    + f" inner join scores on {table}.beatmap_id = scores.beatmap_id and {table}.user_id = scores.user_id"
                )
    if (
        di.get("-pack")
        or di.get("-pack-min")
        or di.get("-pack-max")
        or di.get("-packs")
        or di.get("-apacks")
    ):
        query = (
            query
            + " inner join beatmap_packs on beatmaps.beatmap_id = beatmap_packs.beatmap_id"
        )
    if di["-mode"] == "0":
        if tables == None:
            if (di.get("-o") and di["-o"] == "nomodscore") or (
                di.get("-topscorenomod") or di.get("-topscorenomod-max")
            ):
                query = (
                    query
                    + " inner join (select beatmap_id, top_score_nomod from top_score_nomod) top_score_nomod on beatmaps.beatmap_id = top_score_nomod.beatmap_id"
                )
            else:
                query = (
                    query
                    + " inner join (select beatmap_id, top_score from top_score) top_score on beatmaps.beatmap_id = top_score.beatmap_id"
                )
        elif not ("top_score" in tables or "top_score_nomod" in tables):
            if (di.get("-o") and di["-o"] == "nomodscore") or (
                di.get("-topscorenomod") or di.get("-topscorenomod-max")
            ):
                query = (
                    query
                    + " inner join (select beatmap_id, top_score_nomod from top_score_nomod) top_score_nomod on beatmaps.beatmap_id = top_score_nomod.beatmap_id"
                )
            else:
                query = (
                    query
                    + " inner join (select beatmap_id, top_score from top_score) top_score on beatmaps.beatmap_id = top_score.beatmap_id"
                )
    if di.get("-rank"):
        query = (
            query
            + " inner join (select beatmap_id, user_id from top_score) firsts on beatmaps.beatmap_id = firsts.beatmap_id"
        )

    # if di.get("-modded") and di["-modded"] == "true":
    #     query = query + " inner join moddedsr on beatmaps.beatmap_id = moddedsr.beatmap_id and greatest(0, (case when is_dt = 'true' then 64 else 0 end + case when is_hr = 'true' then 16 else 0 end + case when is_ez = 'true' then 2 else 0 end + case when is_fl = 'true' then 1024 else 0 end)) = moddedsr.mods_enum"

    if di.get("-modded") and di["-modded"] == "true":
        query = (
            query + " inner join moddedsr on beatmaps.beatmap_id = moddedsr.beatmap_id"
        )

    query = query + build_where_clause(di, unique_table)
    if sets:
        query = query + " group by set_id"
    if missingScore:
        query = (
            query
            + " group by set_id, beatmaps.beatmap_id, artist, title, diffname, stars"
        )
        total_missing_query = query
    query = (
        query
        + " order by "
        + order
        + " "
        + direction
        + ", artist limit "
        + str(limit)
        + " offset "
        + str(offset)
    )
    print("Query: " + query)
    query_start_time = time.time()
    res = await db.execute_query(query)
    query_end_time = time.time()
    query_execution_time = round(query_end_time - query_start_time, 2)

    embed = discord.Embed(colour=discord.Colour(0xCC5288))
    total_missing_score = ""
    s = ""

    if bonusColumn == None:
        for b in res:
            s = (
                s
                + str(round(b[5], 2))
                + "★ | "
                + "["
                + b[2]
                + " - "
                + b[3]
                + " ["
                + b[4]
                + "]](https://osu.ppy.sh/beatmapsets/"
                + str(b[0])
                + "#osu/"
                + str(b[1])
                + ")\n"
            )
        embed.description = s
    elif missingScore:
        for b in res:
            s = (
                s
                + str(round(b[5], 2))
                + "★ | "
                + "{:,}".format(b[6])
                + " | "
                + "["
                + b[2]
                + " - "
                + b[3]
                + " ["
                + b[4]
                + "]](https://osu.ppy.sh/beatmapsets/"
                + str(b[0])
                + "#osu/"
                + str(b[1])
                + ")\n"
            )
        embed.description = s
    else:
        for b in res:
            if order == "date_played" or order == "beatmaps.approved_date":
                date = datetime.datetime.strptime(str(b[6]), "%Y-%m-%d %H:%M:%S")
                timestamp = date.replace(tzinfo=datetime.timezone.utc).timestamp()
                formatBonusColumn = f"<t:{int(timestamp)}:R>"
            elif order == "length":
                formatBonusColumn = str(datetime.timedelta(seconds=int(b[6])))
            elif order == "enabled_mods":
                formatBonusColumn = get_mods_string(b[6])
            elif (
                order
                == "score * (DATE_PART('year', NOW() - approved_date) + DATE_PART('day', NOW() - approved_date) / 365.2425)"
            ):
                formatBonusColumn = "{:,.0f}".format(b[6])
            elif not str(b[6]).isnumeric():
                formatBonusColumn = str(b[6])
            else:
                formatBonusColumn = "{:,}".format(b[6])
            s = (
                s
                + str(round(b[5], 2))
                + "★ | "
                + formatBonusColumn
                + " | "
                + "["
                + b[2]
                + " - "
                + b[3]
                + " ["
                + b[4]
                + "]](https://osu.ppy.sh/beatmapsets/"
                + str(b[0])
                + "#osu/"
                + str(b[1])
                + ")\n"
            )
        embed.description = s

    if missingScore:
        total_missing_query = (
            "select sum(missing_score) from ("
            + total_missing_query
            + ") as total_missing_score"
        )
        res = await db.execute_query(total_missing_query)
        score_sum = res[0][0]
        if score_sum != None:
            total_missing_score = " | Total missing score: " + "{:,}".format(score_sum)

    embed.title = "Amount: " + str(count) + total_missing_score
    embed.set_footer(
        text="Page "
        + str(page)
        + " of "
        + str(math.ceil(int(count) / int(limit)))
        + f" • took {query_execution_time}s",
        icon_url="https://pek.li/maj7qa.png",
    )

    await ctx.reply(embed=embed)


async def get_beatmap_ids(di, tables=None):
    if not di.get("-mode"):
        di["-mode"] = "0"
    if not di.get("-loved"):
        di["-loved"] = "false"

    query = "select beatmaps.beatmap_id from beatmaps"
    if tables != None:
        for table in tables:
            if table == "mods":
                query = (
                    query
                    + " inner join "
                    + table
                    + " on scores.enabled_mods = "
                    + table
                    + ".enum"
                )
            else:
                query = (
                    query
                    + " inner join "
                    + table
                    + " on beatmaps.beatmap_id = "
                    + table
                    + ".beatmap_id"
                )
    if di.get("-score") or di.get("-score-min") or di.get("-score-max"):
        query = (
            query
            + " inner join (select beatmap_id, top_score from top_score) top_score on beatmaps.beatmap_id = top_score.beatmap_id"
        )
    if (
        di.get("-pack")
        or di.get("-pack-min")
        or di.get("-pack-max")
        or di.get("-packs")
        or di.get("-apacks")
    ):
        query = (
            query
            + " inner join beatmap_packs on beatmaps.beatmap_id = beatmap_packs.beatmap_id"
        )
    query = query + build_where_clause(di)
    print(query)
    res = await db.execute_query(query)
    return res


async def get_completion(ctx, type, di):
    user_id = await get_user_id(ctx, di)
    username = await get_username(user_id)

    if user_id is None:
        raise ValueError(
            "Please specify a user using '-u'. If username doesn't work, try using the user_id instead."
        )

    # Parse args
    default_size = 1
    length = max(int(di.get("-l", 10)), 1)
    group_size = max(float(di.get("-g", default_size)), 0.01)
    page = max(int(di.get("-p", 1)), 1)
    di["-p"] = page
    if not "-g" in di and not "-l" in di:
        length += 1

    def round_rng(rng):
        rounded = round(rng, 2)
        rounded = (
            int(rounded)
            if ".0" in str(rounded)
            and (not "-g" in di and not "-l" in di)
            or (type == "combo" or type == "length")
            else rounded
        )
        return rounded

    # Calculate ranges
    ranges = []
    start = (page - 1) * length * group_size
    i = start
    while len(ranges) < length:
        ranges.append(f"{round_rng(i)}-{round_rng(i+group_size)}")
        i += group_size
    print("RANGES:", ranges)

    if type == "ar":
        title = "AR Completion"
        range_arg = "ar"
        prefix = "AR "
    elif type == "od":
        title = "OD Completion"
        range_arg = "od"
        prefix = "OD "
    elif type == "cs":
        title = "CS Completion"
        range_arg = "cs"
        prefix = "CS "
    elif type == "stars":
        if "-modded" in di:
            del di["-modded"]
        if not "-g" in di and not "-l" in di:
            ranges = [
                "0-1",
                "1-2",
                "2-3",
                "3-4",
                "4-5",
                "5-6",
                "6-7",
                "7-8",
                "8-9",
                "9-10",
                "10-20",
            ]
        title = "Stars Completion"
        range_arg = "stars"
        prefix = ""
    elif type == "combo":
        if "-modded" in di:
            del di["-modded"]
        if not "-g" in di and not "-l" in di:
            ranges = [
                "0-100",
                "100-200",
                "200-300",
                "300-400",
                "400-500",
                "500-600",
                "600-700",
                "700-800",
                "800-900",
                "900-1000",
                "1000-99999",
            ]
        title = "Combo Completion"
        range_arg = "maxcombo"
        prefix = ""
    elif type == "length":
        if "-modded" in di:
            del di["-modded"]
        if not "-g" in di and not "-l" in di:
            ranges = [
                "0-60",
                "60-120",
                "120-180",
                "180-240",
                "240-300",
                "300-360",
                "360-420",
                "420-480",
                "480-540",
                "540-600",
                "600-99999",
            ]
        title = "Length Completion"
        range_arg = "length"
        prefix = ""
    elif type == "grade":
        if "-modded" in di:
            del di["-modded"]
        ranges = ["XH", "SH", "X", "S", "A", "B", "C", "D"]
        title = "Grade Completion"
        range_arg = "-letters"
        prefix = ""
    elif type == "grade_breakdown":
        if "-modded" in di:
            del di["-modded"]
        beatmap_count = await get_beatmap_list(
            ctx, di, ["scores", "fc_count", "ss_count"], False, None, False, True
        )
        ranges = ["XH", "SH", "X", "S", "A", "B", "C", "D"]
        title = "Grade Breakdown"
        range_arg = "-letters"
        prefix = ""
    elif type == "yearly":
        ranges = range(2007, datetime.datetime.now().year + 1)
        title = "Yearly Completion"
        range_arg = "DATE_PART('year', approved_date)"
        prefix = ""
    elif type == "monthly":
        if "-y" in di:
            di["-year"] = di["-y"]
        if not "-year" in di:
            di["-year"] = datetime.datetime.now().year
        ranges = range(1, 13)
        title = "Monthly Completion"
        range_arg = "DATE_PART('month', approved_date)"
        prefix = ""
    elif type == "daily":
        now = datetime.datetime.now()
        if "-y" in di:
            di["-year"] = di["-y"]
        if not "-year" in di:
            di["-year"] = now.year
        if not "-month" in di:
            di["-month"] = now.month

        year = normalize_year(int(di["-year"]))
        month = int(di["-month"])

        last_day = (
            now.day
            if year == now.year and month == now.month
            else calendar.monthrange(year, month)[1]
        )
        ranges = range(1, last_day + 1)
        title = f"Daily Completion - {calendar.month_name[month]} {year}"
        range_arg = "DATE_PART('day', approved_date)"
        prefix = ""

    query_start_time = time.time()

    if type not in ("grade", "grade_breakdown"):
        beatmap_di = di.copy()
        for key in di.keys():
            if key in blacklist:
                del beatmap_di[key]

        query = f"""
        SELECT
            {type}_range,
        {"SUM(DISTINCT scores.score) AS scores_count," if di.get("-o") in ("score", "nomodscore") else "COUNT(DISTINCT scores.beatmap_id) AS scores_count,"}
        {"SUM(DISTINCT scores.top_score) AS beatmap_count" if di.get("-o") == "score" else ("SUM(DISTINCT scores.top_score_nomod) AS beatmap_count" if di.get("-o") == "nomodscore" else f"COUNT(DISTINCT {type}_ranges.beatmap_id) AS beatmap_count")}
        FROM (
            SELECT beatmaps.beatmap_id,
            CASE
        """

        range_conditions = []
        for rng in ranges:
            if type in ("yearly", "monthly", "daily"):
                range_conditions.append(f"WHEN {range_arg} = {rng} THEN '{rng}'")
            else:
                start, end = str(rng).split("-")
                range_conditions.append(
                    f"WHEN {range_arg} >= {decimal.Decimal(start) - decimal.Decimal('0.005') if type == 'stars' else start} AND {range_arg} < {decimal.Decimal(end) - decimal.Decimal('0.005') if type == 'stars' else end} THEN '{rng}'"
                )

        query += "\n".join(range_conditions)
        query += f"""
                END AS {type}_range
            FROM beatmaps
            WHERE mode = 0 AND approved IN (1, 2{', 4' if "-loved" in di and di["-loved"] == 'true' or di.get("-a") else ''})
            {f"AND DATE_PART('year', approved_date) = {normalize_year(int(di.get('-year')))}" if type == "monthly" else ""}
            ) AS {type}_ranges
        LEFT JOIN (
            SELECT beatmaps.beatmap_id, scores.score,
            {"top_score_nomod.top_score_nomod" if (di.get("-o") and di["-o"] == "nomodscore") or (di.get("-topscorenomod") or di.get("-topscorenomod-max")) else "top_score.top_score"}
            FROM beatmaps
            LEFT JOIN beatmap_packs ON beatmap_packs.beatmap_id = beatmaps.beatmap_id
            {"LEFT" if di.get("-o") in ("score", "nomodscore") else "INNER"} JOIN scores ON scores.beatmap_id = beatmaps.beatmap_id AND scores.user_id = {user_id}
            {"inner join (select beatmap_id, top_score_nomod from top_score_nomod) top_score_nomod on beatmaps.beatmap_id = top_score_nomod.beatmap_id" if (di.get("-o") and di["-o"] == "nomodscore") or (di.get("-topscorenomod") or di.get("-topscorenomod-max")) else " inner join (select beatmap_id, top_score from top_score) top_score on beatmaps.beatmap_id = top_score.beatmap_id"}
            {" inner join moddedsr on beatmaps.beatmap_id = moddedsr.beatmap_id" if di.get("-modded") == "true" else ""}
            {build_where_clause(di)}
        ) AS scores ON scores.beatmap_id = {type}_ranges.beatmap_id
        WHERE {type}_ranges.beatmap_id IN (
            SELECT DISTINCT beatmaps.beatmap_id
            FROM beatmaps
            {build_where_clause(beatmap_di)}
        )
        GROUP BY
            {type}_range
        ORDER BY
            {type}_range
        """
        print("QUERY:", query)
        range_rows = await db.execute_query(query)

        range_data = {}
        for row in range_rows:
            range_data[str(row[f"{type}_range"])] = {
                "scores_count": row["scores_count"],
                "beatmap_count": row["beatmap_count"],
            }
        print(range_data)

    description = "```pascal\n"
    for rng in ranges:
        completion = 100
        di[range_arg] = str(rng).lower()
        if type not in ("grade", "grade_breakdown"):
            beatmap_count = range_data.get(str(rng), {"beatmap_count": 0})[
                "beatmap_count"
            ]
            scores_count = range_data.get(str(rng), {"scores_count": 0})["scores_count"]
        else:
            if not type == "grade_breakdown":
                beatmap_count = await check_beatmaps(ctx, di.copy())
            di["-user"] = user_id
            scores_count = (
                await get_beatmap_list(
                    ctx,
                    di,
                    ["scores", "fc_count", "ss_count"],
                    False,
                    None,
                    False,
                    True,
                )
                or 0
            )
        print(scores_count)
        if int(beatmap_count) > 0:
            completion = int(scores_count) / int(beatmap_count) * 100

        if type == "length":
            start, end = map(int, rng.split("-"))
            start_minutes = (
                start // 60
                if not "-g" in di and not "-l" in di
                else round(start / 60, 2)
            )
            end_minutes = (
                end // 60 if not "-g" in di and not "-l" in di else round(end / 60, 2)
            )
            if rng == "600-99999":
                rng = "10 min+"
            else:
                rng = f"{start_minutes}-{end_minutes} min"
        elif not type == "stars" and rng == "10-11":
            rng = "10+"
        elif type == "stars":
            if rng == "10-20":
                rng = "10★+"
            else:
                start, end = rng.split("-")
                rng = f"{start}-{end}★"
        elif type == "combo":
            if rng == "1000-99999":
                rng = "1000x+"
            else:
                start, end = rng.split("-")
                rng = f"{start}-{end}x"
        elif type == "monthly":
            rng = calendar.month_abbr[rng]

        completion_percent = (
            f"{completion:06.3f}" if completion < 100 else f"{completion:,.2f}"
        )
        if di.get("-o") == "score" or di.get("-o") == "nomodscore":
            scores_count = f"{scores_count:,}"
            beatmap_count = f"{beatmap_count:,}"
        description += (
            f"{prefix}{rng} | {completion_percent}% | {scores_count}/{beatmap_count}\n"
        )
    description += "```"
    query_end_time = time.time()
    query_execution_time = round(query_end_time - query_start_time, 2)

    embed = discord.Embed(
        title=f"{title} for {username or user_id}", colour=discord.Colour(0xCC5288)
    )
    embed.description = description
    embed.set_footer(
        text=f"Based on Scores in the database • took {query_execution_time}s",
        icon_url="https://pek.li/maj7qa.png",
    )
    await ctx.reply(embed=embed)


async def get_pack_completion(ctx, di):
    user_id = await get_user_id(ctx, di)
    username = await get_username(user_id)
    di["-mode"] = "0"

    # Parse args
    approved = int(di.get("-approved", di.get("-a", 1))) == 2
    default_size = 2 if approved else 10
    length = max(int(di.get("-l", 10)), 1)
    group_size = max(int(di.get("-g", default_size)), 1)
    page = max(int(di.get("-p", 1)), 1)
    di["-p"] = page

    # Calculate pack ranges
    packs_ranges = []
    start = (page - 1) * length * group_size + 1
    i = start
    lowest_number = i
    highest_number = i
    while len(packs_ranges) < length:
        if group_size > 1:
            packs_ranges.append(f"{i:03}-{i+group_size-1:03}")
            highest_number = i + group_size - 1
        else:
            packs_ranges.append(f"{i:03}")
            highest_number = i
        i += group_size

    if approved:
        di["-apacks"] = f"{lowest_number:03}-{highest_number:03}"
    else:
        di["-packs"] = f"{lowest_number:03}-{highest_number:03}"

    beatmap_di = di.copy()
    for key in di.keys():
        if key in blacklist:
            del beatmap_di[key]

    print(f"{lowest_number:03}-{highest_number:03}")
    query_start_time = time.time()

    query = f"""
    SELECT
    pack_id,
    {"SUM(DISTINCT scores.score) AS scores_count," if di.get("-o") in ("score", "nomodscore") else "COUNT(DISTINCT scores.beatmap_id) AS scores_count,"}
    {"SUM(DISTINCT top_score.top_score) AS beatmap_count" if di.get("-o") == "score" else ("SUM(DISTINCT top_score_nomod.top_score_nomod) AS beatmap_count" if di.get("-o") == "nomodscore" else "COUNT(DISTINCT beatmaps.beatmap_id) AS beatmap_count")}
    FROM 
    beatmap_packs 
    LEFT JOIN beatmaps ON beatmaps.beatmap_id = beatmap_packs.beatmap_id
    LEFT JOIN (
        SELECT DISTINCT beatmaps.beatmap_id
        FROM beatmaps
        INNER JOIN beatmap_packs ON beatmap_packs.beatmap_id = beatmaps.beatmap_id
        {"LEFT" if di.get("-o") in ("score", "nomodscore") else "INNER"} JOIN scores ON scores.beatmap_id = beatmaps.beatmap_id AND scores.user_id = {user_id}
        {"inner join (select beatmap_id, top_score_nomod from top_score_nomod) top_score_nomod on beatmaps.beatmap_id = top_score_nomod.beatmap_id" if (di.get("-o") and di["-o"] == "nomodscore") or (di.get("-topscorenomod") or di.get("-topscorenomod-max")) else " inner join (select beatmap_id, top_score from top_score) top_score on beatmaps.beatmap_id = top_score.beatmap_id"}
        {" inner join moddedsr on beatmaps.beatmap_id = moddedsr.beatmap_id" if di.get("-modded") == "true" else ""}
        {build_where_clause(di)}
    ) as scores ON scores.beatmap_id = beatmaps.beatmap_id
        {build_where_clause(beatmap_di)}
    GROUP BY
        beatmap_packs.pack_id
    ORDER BY
        beatmap_packs.pack_id"""

    print("QUERY:", query)
    pack_rows = await db.execute_query(query)

    beatmap_packs = {}
    for row in pack_rows:
        beatmap_packs[row["pack_id"]] = {
            "scores_count": row["scores_count"],
            "beatmap_count": row["beatmap_count"],
        }

    description = "```pascal\n"
    for packs in packs_ranges:
        completion = 100
        beatmap_count = 0
        scores_count = 0
        if "-" in packs:
            pack_start, pack_end = map(int, packs.split("-"))
            for pack in range(pack_start, pack_end + 1):
                pack_id = f"SA{pack}" if approved else f"S{pack}"
                beatmap_count += beatmap_packs.get(pack_id, {"beatmap_count": 0})[
                    "beatmap_count"
                ]
                scores_count += beatmap_packs.get(pack_id, {"scores_count": 0})[
                    "scores_count"
                ]
        else:
            pack_id = f"SA{packs.lstrip('0')}" if approved else f"S{packs.lstrip('0')}"
            beatmap_count += beatmap_packs.get(pack_id, {"beatmap_count": 0})[
                "beatmap_count"
            ]
            scores_count += beatmap_packs.get(pack_id, {"scores_count": 0})[
                "scores_count"
            ]

        if int(beatmap_count) > 0:
            completion = int(scores_count) / int(beatmap_count) * 100

        completion_percent = (
            f"{completion:06.3f}" if completion < 100 else f"{completion:,.2f}"
        )
        if di.get("-o") == "score" or di.get("-o") == "nomodscore":
            scores_count = f"{scores_count:,}"
            beatmap_count = f"{beatmap_count:,}"
        description += (
            f"{packs} | {completion_percent}% | {scores_count}/{beatmap_count}\n"
        )
    description += "```"
    query_end_time = time.time()
    query_execution_time = round(query_end_time - query_start_time, 2)

    embed = discord.Embed(
        title=f"Pack Completion for {username or user_id}",
        colour=discord.Colour(0xCC5288),
    )
    embed.description = description
    embed.set_footer(
        text=f"Based on Scores in the database • took {query_execution_time}s",
        icon_url="https://pek.li/maj7qa.png",
    )
    await ctx.reply(embed=embed)


async def get_username(user_id):
    query = "SELECT username FROM users2 WHERE user_id = $1"
    res = await db.execute_query(query, user_id)
    if len(res) > 0:
        username = res[0][0]
        return username
    else:
        return None


async def get_user_id(ctx, args):
    if not args.get("-u"):
        query = "SELECT user_id FROM discorduser WHERE discord_id = $1"
        res = await db.execute_query(query, str(ctx.message.author.id))
        if len(res) > 0:
            user_id = res[0][0]
            return user_id
        else:
            return None

    if not str(args["-u"]).isnumeric():
        username = str(args["-u"]).replace("+", " ").lower()
        query = "SELECT user_id FROM users2 WHERE LOWER(username) = $1"
        res = await db.execute_query(query, str(username))
        if len(res) > 0:
            user_id = res[0][0]
            return user_id
        else:
            return None
    else:
        user_id = args["-u"]
        return user_id


async def build_leaderboard(ctx, base, di, user=None):
    limit = 10
    page = 1
    direction = "desc"

    if di.get("-direction") or di.get("-dir"):
        if di.get("-dir"):
            di["-direction"] = di["-dir"]
        direction = di["-direction"]
    if di.get("-l"):
        limit = di["-l"]
    if di.get("-p"):
        page = di["-p"]

    offset = int(limit) * (int(page) - 1)

    if di.get("-u") and not (di["-u"]).isnumeric():
        user = str(di["-u"]).replace("+", " ").lower()
    else:
        user_id = await get_user_id(ctx, di)
        if user_id is None:
            user = None
        else:
            query = "SELECT username FROM users2 WHERE user_id = $1"
            res = await db.execute_query(query, int(user_id))
            if len(res) > 0:
                user = str(res[0][0]).lower()

    rank = f"""
        SELECT user_id, stat, ROW_NUMBER() OVER(ORDER BY stat {direction}) as rank
        FROM ({base}) base
    """

    if user is not None:
        leaderboard_query = f"""
            WITH leaderboard AS (
                {rank}
            )
            SELECT rank, username, stat
            FROM leaderboard
            INNER JOIN users2 ON users2.user_id = leaderboard.user_id
            WHERE rank <= {int(limit) * int(page)}
                AND rank > {offset}
                OR LOWER(username) = '{user}'
            ORDER BY rank
            LIMIT {int(limit) + 1}
        """
    else:
        leaderboard_query = f"""
            WITH leaderboard AS (
                {rank}
            )
            SELECT rank, username, stat
            FROM leaderboard
            INNER JOIN users2 ON users2.user_id = leaderboard.user_id
            ORDER BY rank
            LIMIT {limit}
            OFFSET {offset}
        """

    return leaderboard_query
