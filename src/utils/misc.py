import datetime
import gzip
import os
import struct
import discord

from utils.helpers import build_where_clause, catbox_upload, get_mods_string
from sql.queries import get_user_id, get_username
from sql.db import Database

db = Database()

OA_S_PER_DAY = 8.64e4
OA_EPOC = datetime.datetime(1899, 12, 30, 0, 0, 0, tzinfo=datetime.timezone.utc)


def OADoubleNow():
    return (
        datetime.datetime.now(datetime.timezone.utc) - OA_EPOC
    ).total_seconds() / OA_S_PER_DAY


def uleb128encode(n):
    assert n >= 0
    arr = []
    while True:
        b = n & 0x7F
        n >>= 7
        if n == 0:
            arr.append(b)
            return bytearray(arr)
        arr.append(0x80 | b)


def format_str(s):
    s = bytes(s, "utf-8")
    return uleb128encode(len(s)) + s


async def generateosdb(ctx, di):
    if not di.get("-mode"):
        di["-mode"] = "0"

    if not di.get("-loved"):
        di["-loved"] = "false"

    user_id = await get_user_id(ctx, di)
    # if user_id is None:
    #     raise ValueError("Please specify a user using '-u'. If username doesn't work, try using the user_id instead.")

    if user_id == 647309 and not ctx.message.author.id == 131558221717438475:
        await ctx.reply("It's a secret. 🤫")
        return

    if di.get("-unplayed"):
        if not di.get("-o"):
            di["-o"] = "score"
        if user_id:
            di["-user"] = user_id
        else:
            raise ValueError(
                "Please specify a user using '-u'. If username doesn't work, try using the user_id instead."
            )

    if not di.get("-u"):
        if not di.get("-o"):
            di["-o"] = "score"

    if di.get("-u") or di.get("-missingscore"):
        if user_id:
            di["-user"] = user_id
        else:
            raise ValueError(
                "Please specify a user using '-u'. If username doesn't work, try using the user_id instead."
            )

    query = "select beatmaps.beatmap_id, set_id, artist, title, diffname, file_md5, mode, stars from beatmaps"
    count = "select count(*) from beatmaps"

    if not di.get("-unplayed"):
        if di.get("-u") or di.get("-missingscore"):
            query = (
                query + " inner join scores on scores.beatmap_id = beatmaps.beatmap_id"
            )
            count = (
                count + " inner join scores on scores.beatmap_id = beatmaps.beatmap_id"
            )
            if not di.get("-registered"):
                di["-registered"] = "true"

    if di.get("-o"):
        if di["-o"] == "neverbeenssed":
            query = (
                query
                + " inner join neverbeenssed on neverbeenssed.beatmap_id = beatmaps.beatmap_id"
            )
            count = (
                count
                + " inner join neverbeenssed on neverbeenssed.beatmap_id = beatmaps.beatmap_id"
            )
        if di["-o"] == "neverbeenfced":
            query = (
                query
                + " inner join neverbeenfced on neverbeenfced.beatmap_id = beatmaps.beatmap_id"
            )
            count = (
                count
                + " inner join neverbeenfced on neverbeenfced.beatmap_id = beatmaps.beatmap_id"
            )
        if di["-o"] == "neverbeendted":
            query = (
                query
                + " inner join neverbeendted on neverbeendted.beatmap_id = beatmaps.beatmap_id"
            )
            count = (
                count
                + " inner join neverbeendted on neverbeendted.beatmap_id = beatmaps.beatmap_id"
            )

    if di["-mode"] == "0":
        if di.get("-fc-min") or di.get("-fc-max") or di.get("-fc-range"):
            query = (
                query
                + " inner join fc_count on beatmaps.beatmap_id = fc_count.beatmap_id"
            )
            count = (
                count
                + " inner join fc_count on beatmaps.beatmap_id = fc_count.beatmap_id"
            )
        if (di.get("-ss-min") or di.get("-ss-max") or di.get("-ss-range")) and not (
            di.get("-u") and di.get("-missingscore")
        ):
            di["-leastssed"] = "true"
            query = (
                query
                + " inner join ss_count on beatmaps.beatmap_id = ss_count.beatmap_id"
            )
            count = (
                count
                + " inner join ss_count on beatmaps.beatmap_id = ss_count.beatmap_id"
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
            count = (
                count
                + " inner join beatmap_packs on beatmaps.beatmap_id = beatmap_packs.beatmap_id"
            )
        if (
            di.get("-o")
            and di["-o"] == "score"
            or (
                di.get("-scorepersecond")
                or di.get("-scorepersecond-min")
                or di.get("-scorepersecond-max")
            )
        ):
            query = (
                query
                + " inner join (select beatmap_id, top_score from top_score) top_score on beatmaps.beatmap_id = top_score.beatmap_id"
            )
            count = (
                count
                + " inner join (select beatmap_id, top_score from top_score) top_score on beatmaps.beatmap_id = top_score.beatmap_id"
            )
        elif (
            di.get("-o")
            and di["-o"] == "nomodscore"
            or (
                di.get("-nomodscorepersecond")
                or di.get("-nomodscorepersecond-min")
                or di.get("-nomodscorepersecond-max")
            )
        ):
            query = (
                query
                + " inner join (select beatmap_id, top_score_nomod from top_score_nomod) top_score_nomod on beatmaps.beatmap_id = top_score_nomod.beatmap_id"
            )
            count = (
                count
                + " inner join (select beatmap_id, top_score_nomod from top_score_nomod) top_score_nomod on beatmaps.beatmap_id = top_score_nomod.beatmap_id"
            )

        if di.get("-rank"):
            query = (
                query
                + " inner join (select beatmap_id, user_id from top_score) firsts on beatmaps.beatmap_id = firsts.beatmap_id"
            )
            count = (
                count
                + " inner join (select beatmap_id, user_id from top_score) firsts on beatmaps.beatmap_id = firsts.beatmap_id"
            )

    where = build_where_clause(di)
    query = query + where
    count = count + where

    print(count)
    count_res = await db.execute_query(count)
    count = count_res[0][0]
    rows = await db.execute_query(query)

    name = "GENERATED-COLLECTION"

    if di.get("-name"):
        name = str(di["-name"])

    temp_bytes = format_str("o!dm8")
    temp_bytes += struct.pack("d", OADoubleNow())
    temp_bytes += format_str("N/A")
    temp_bytes += struct.pack("i", 1)

    temp_bytes += format_str(name)
    temp_bytes += struct.pack("i", -1)  # online ID
    temp_bytes += struct.pack("i", count)  # amount of beatmaps

    for row in rows:
        beatmap_id = row[0]
        temp_bytes += struct.pack("i", beatmap_id)
        set_id = row[1]
        temp_bytes += struct.pack("i", set_id)
        artist = row[2]
        temp_bytes += format_str(artist)
        title = row[3]
        temp_bytes += format_str(title)
        diffname = row[4]
        temp_bytes += format_str(diffname)
        md5_hash = row[5]
        temp_bytes += format_str(md5_hash)
        temp_bytes += format_str("")
        mode = row[6]
        temp_bytes += struct.pack("b", mode)
        stars = row[7]
        temp_bytes += struct.pack("d", stars)

    temp_bytes += struct.pack("i", 0)
    temp_bytes += format_str("By Piotrekol")

    f = open("collection.osdb", "wb")
    f.write(format_str("o!dm8"))
    f.write(gzip.compress(temp_bytes))
    f.close()

    fw = open("collection.osdb", "rb")

    with open("collection.osdb", "rb") as file:
        await ctx.reply("Your file is:", file=discord.File(file, name + ".osdb"))


async def getfile(ctx, di):
    user_id = await get_user_id(ctx, di)
    username = await get_username(user_id)

    if user_id == 647309 and not ctx.message.author.id == 131558221717438475:
        await ctx.reply("It's a secret. 🤫")
        return

    if not di.get("-user") and di["-type"] != "beatmaps":
        di["-user"] = user_id

    if di["-type"] == "neverbeenssed":
        type = "select set_id, beatmaps.beatmap_id, artist, title, diffname, round(stars, 2) as stars from neverbeenssed inner join beatmaps on neverbeenssed.beatmap_id = beatmaps.beatmap_id order by stars, artist"
    elif di["-type"] == "neverbeenfced":
        type = "select set_id, beatmaps.beatmap_id, artist, title, diffname, round(stars, 2) as stars from neverbeenfced inner join beatmaps on neverbeenfced.beatmap_id = beatmaps.beatmap_id order by stars, artist"
    elif di["-type"] == "neverbeendted":
        type = "select set_id, beatmaps.beatmap_id, artist, title, diffname, round(stars, 2) as stars from neverbeendted inner join beatmaps on neverbeendted.beatmap_id = beatmaps.beatmap_id order by stars, artist"
    elif di["-type"] == "fc_count":
        type = "select set_id, beatmaps.beatmap_id, fc_count, artist, title, diffname, round(stars, 2) as stars from fc_count inner join beatmaps on fc_count.beatmap_id = beatmaps.beatmap_id order by stars, artist"
    elif di["-type"] == "top_score":
        type = "select set_id, beatmaps.beatmap_id, top_score.user_id, top_score, artist, title, diffname, round(stars, 2) as stars from top_score inner join beatmaps on top_score.beatmap_id = beatmaps.beatmap_id order by stars, artist"
    elif di["-type"] == "top_score_nomod":
        type = "select set_id, beatmaps.beatmap_id, top_score_nomod.user_id, top_score_nomod, artist, title, diffname, round(stars, 2) as stars from top_score_nomod inner join beatmaps on top_score_nomod.beatmap_id = beatmaps.beatmap_id order by stars, artist"
    elif di["-type"] == "top_score_hidden":
        type = "select set_id, beatmaps.beatmap_id, top_score_hidden.user_id, top_score_hidden, artist, title, diffname, round(stars, 2) as stars from top_score_hidden inner join beatmaps on top_score_hidden.beatmap_id = beatmaps.beatmap_id order by stars, artist"
    elif di["-type"] == "registered":
        type = "select * from priorityuser"
    elif di["-type"] == "scores":
        if int(user_id) > 0:
            where = build_where_clause(di)
            columns = "user_id,beatmaps.beatmap_id,score,count300,count100,count50,countmiss,combo,perfect,enabled_mods,date_played,rank,pp,replay_available,accuracy,approved,submit_date,beatmaps.approved_date,last_update,artist,set_id,bpm,creator,creator_id,stars,diff_aim,diff_speed,cs,od,ar,hp,drain,source,genre,language,title,length,diffname,file_md5,mode,tags,favorites,rating,playcount,passcount,circles,sliders,spinners,maxcombo,storyboard,video,download_unavailable,audio_unavailable,star_rating,aim_diff,speed_diff,fl_diff,slider_factor,speed_note_count,modded_od,modded_ar,modded_cs,modded_hp,pack_id"
            type = f"select {columns} from scores inner join beatmaps on scores.beatmap_id = beatmaps.beatmap_id left join moddedsr on beatmaps.beatmap_id = moddedsr.beatmap_id and moddedsr.mods_enum = (case when is_ht = 'true' then 256 else 0 end + case when is_dt = 'true' then 64 else 0 end + case when is_hr = 'true' then 16 else 0 end + case when is_ez = 'true' then 2 else 0 end + case when is_fl = 'true' then 1024 else 0 end)"
            type = (
                type
                + " inner join (select beatmap_id, STRING_AGG(pack_id, ',') as pack_id from beatmap_packs group by beatmap_id) bp on beatmaps.beatmap_id = bp.beatmap_id "
            )
            type = type + where
    elif di["-type"] == "scoresimple":
        if int(user_id) > 0:
            where = build_where_clause(di)
            type = f"select set_id, beatmaps.beatmap_id, approved_date, round(stars, 2) as stars, rank from scores inner join beatmaps on scores.beatmap_id = beatmaps.beatmap_id"
            if (
                di.get("-pack")
                or di.get("-pack-min")
                or di.get("-pack-max")
                or di.get("-packs")
                or di.get("-apacks")
            ):
                type = (
                    type
                    + " inner join beatmap_packs on beatmaps.beatmap_id = beatmap_packs.beatmap_id"
                )
            type = type + where
    elif di["-type"] == "beatmaps" or di["-type"] == "beatmapsimple":
        if not di.get("-mode"):
            di["-mode"] = "0"
        if not di.get("-loved"):
            di["-loved"] = "false"
        if di.get("-unplayed"):
            di["-user"] = user_id
        where = build_where_clause(di)
        if di["-type"] == "beatmapsimple":
            type = "select set_id, beatmaps.beatmap_id, approved_date, round(stars, 2) as stars, artist, title, diffname from beatmaps"
        else:
            type = f"select * from beatmaps"
        if (
            di.get("-pack")
            or di.get("-pack-min")
            or di.get("-pack-max")
            or di.get("-packs")
            or di.get("-apacks")
        ):
            type = (
                type
                + " inner join beatmap_packs on beatmaps.beatmap_id = beatmap_packs.beatmap_id"
            )
        type = type + where
    elif di["-type"] == "nomodnumberones":
        if int(user_id) > 0:
            type = f"select set_id, beatmaps.beatmap_id, artist, title, diffname, round(stars, 2) as stars from top_score_nomod inner join beatmaps on top_score_nomod.beatmap_id = beatmaps.beatmap_id where top_score_nomod.user_id = {user_id} order by stars, artist"
    elif di["-type"] == "hiddennumberones":
        if int(user_id) > 0:
            type = f"select set_id, beatmaps.beatmap_id, artist, title, diffname, round(stars, 2) as stars from top_score_hidden inner join beatmaps on top_score_hidden.beatmap_id = beatmaps.beatmap_id where top_score_hidden.user_id = {user_id} order by stars, artist"
    elif di["-type"] == "numberones":
        if int(user_id) > 0:
            type = f"select set_id, beatmaps.beatmap_id, artist, title, diffname, round(stars, 2) as stars from top_score inner join beatmaps on top_score.beatmap_id = beatmaps.beatmap_id where top_score.user_id = {user_id} order by stars, artist"
    else:
        await ctx.reply("Type not found.")
        return

    print(type)
    await db.export_to_csv(type, "tmp.txt")

    name = None
    if di.get("-name"):
        name = di["-name"]

    if name is not None:
        filename = name + ".csv"
    else:
        now = datetime.datetime.now()
        timestamp = now.strftime("_%Y-%m-%d_%H:%M:%S")
        filename = username + "_" + str(di["-type"]) + timestamp + ".csv"
        print(filename)

    with open("tmp.txt", "rb") as file:
        file_size = os.path.getsize("tmp.txt")
        if file_size >= 50000000:
            catbox_url = catbox_upload(filename, "tmp.txt")
            msg = "File is over 50MB, here's a 1h temp link: " + catbox_url
            await ctx.reply(msg)
        else:
            await ctx.reply("Your file is:", file=discord.File(file, filename))


async def updatelists(client):
    channel = client.get_channel(793570054008340511)
    li = await db.execute_query("select * from newfcs")
    if len(li) > 0:
        print(len(li), "new fcs")
        for entry in li:
            beatmap, user, date = entry[0], entry[1], entry[2]
            query = f"""select artist, title, diffname, beatmaps.approved_date, set_id, moddedsr.star_rating, length, maxcombo, 
            modded_cs, modded_ar, modded_od, modded_hp, score, accuracy, enabled_mods, pp from scores
            left join beatmaps on scores.beatmap_id = beatmaps.beatmap_id 
            left join moddedsr on scores.beatmap_id = moddedsr.beatmap_id where scores.beatmap_id = {str(beatmap)} and user_id = {str(user)}
            and moddedsr.mods_enum = (case when is_ht = 'true' then 256 else 0 end + case when is_dt = 'true' then 64 else 0 end + case when is_hr = 'true' then 16 else 0 end + case when is_ez = 'true' then 2 else 0 end + case when is_fl = 'true' then 1024 else 0 end + case when is_fl = 'true' and is_hd = 'true' then 8 else 0 end)"""
            rows = await db.execute_query(query)
            b = rows[0] if len(rows) > 0 else None
            if b is None:
                await db.execute_query(
                    "delete from newfcs where beatmap_id = " + str(beatmap)
                )
                continue
            approved_date = b[3]
            minutes = b[6] // 60
            seconds = b[6] % 60

            # differential = ((date.year * 365) + (date.month*31) + (date.day)) - ((approved_date.year * 365) + (approved_date.month*31) + (approved_date.day))
            differential = abs((date - approved_date).days)

            if differential >= 7:
                rows = await db.execute_query(
                    "select username, pp, global_rank from users2 where user_id = "
                    + str(user)
                )
                result = None
                if len(rows) > 0:
                    result = rows[0]
                username = user
                if result is not None:
                    username = result[0]
                    pp = result[1]
                    rank = result[2]

                embed = discord.Embed(
                    title="A map has been FCed for the first time after "
                    + str(differential)
                    + " days!",
                    colour=discord.Colour(0xE5E242),
                )
                author = {
                    "name": f"""{username + " - " + str(pp) + "pp #" + str(rank) if result is not None else str(username)}""",
                    "url": f"https://osu.ppy.sh/users/{user}",
                    "icon_url": f"https://a.ppy.sh/{user}",
                }
                embed.set_author(
                    name=author["name"], url=author["url"], icon_url=author["icon_url"]
                )

                score_pp = f"{b[15]:.2f}pp" if b[15] > 0 else "loved"
                embed.description = f"""
**[{b[0]} - {b[1]} [{b[2]}]](https://osu.ppy.sh/beatmapsets/{b[4]}#osu/{beatmap})**
**{get_mods_string(b[14])} • {b[12]:,} • {b[13]}% • {score_pp}**
**Time of play: ** <t:{date.replace(tzinfo=datetime.timezone.utc).timestamp():.0f}:R>
**Date ranked: ** <t:{approved_date.replace(tzinfo=datetime.timezone.utc).timestamp():.0f}:f>

**Beatmap information**
CS **{b[8]:.1f}** • AR **{b[9]:.1f}** • OD **{b[10]:.1f}** • HP **{b[11]:.1f}** • **{b[5]:.2f}★**
**{minutes}m{seconds}s** • **{b[7]} combo**
                """

                await channel.send(embed=embed)

            await db.execute_query(
                "delete from newfcs where beatmap_id = " + str(beatmap)
            )

    channel = client.get_channel(793594664262303814)

    li = await db.execute_query("select * from newSSs")
    if len(li) > 0:
        print(len(li), "new sss")
        for entry in li:
            beatmap, user, date = entry[0], entry[1], entry[2]
            query = f"""select artist, title, diffname, beatmaps.approved_date, set_id, moddedsr.star_rating, length, maxcombo, 
            modded_cs, modded_ar, modded_od, modded_hp, score, accuracy, enabled_mods, pp from scores
            left join beatmaps on scores.beatmap_id = beatmaps.beatmap_id 
            left join moddedsr on scores.beatmap_id = moddedsr.beatmap_id where scores.beatmap_id = {str(beatmap)} and user_id = {str(user)}
            and moddedsr.mods_enum = (case when is_ht = 'true' then 256 else 0 end + case when is_dt = 'true' then 64 else 0 end + case when is_hr = 'true' then 16 else 0 end + case when is_ez = 'true' then 2 else 0 end + case when is_fl = 'true' then 1024 else 0 end + case when is_fl = 'true' and is_hd = 'true' then 8 else 0 end)"""
            rows = await db.execute_query(query)
            b = rows[0] if len(rows) > 0 else None
            if b is None:
                await db.execute_query(
                    "delete from newSSs where beatmap_id = " + str(beatmap)
                )
                continue
            approved_date = b[3]
            minutes = b[6] // 60
            seconds = b[6] % 60

            # differential = ((date.year * 365) + (date.month*31) + (date.day)) - ((approved_date.year * 365) + (approved_date.month*31) + (approved_date.day))
            differential = abs((date - approved_date).days)

            if differential >= 30:
                rows = await db.execute_query(
                    "select username, pp, global_rank from users2 where user_id = "
                    + str(user)
                )
                result = None
                if len(rows) > 0:
                    result = rows[0]
                username = user
                if result is not None:
                    username = result[0]
                    pp = result[1]
                    rank = result[2]

                embed = discord.Embed(
                    title="A map has been SSed for the first time after "
                    + str(differential)
                    + " days!",
                    colour=discord.Colour(0xE5E242),
                )
                author = {
                    "name": f"""{username + " - " + str(pp) + "pp #" + str(rank) if result is not None else str(username)}""",
                    "url": f"https://osu.ppy.sh/users/{user}",
                    "icon_url": f"https://a.ppy.sh/{user}",
                }
                embed.set_author(
                    name=author["name"], url=author["url"], icon_url=author["icon_url"]
                )

                score_pp = f"{b[15]:.2f}pp" if b[15] > 0 else "loved"
                embed.description = f"""
**[{b[0]} - {b[1]} [{b[2]}]](https://osu.ppy.sh/beatmapsets/{b[4]}#osu/{beatmap})**
**{get_mods_string(b[14])} • {b[12]:,} • {b[13]}% • {score_pp}**
**Time of play: ** <t:{date.replace(tzinfo=datetime.timezone.utc).timestamp():.0f}:R>
**Date ranked: ** <t:{approved_date.replace(tzinfo=datetime.timezone.utc).timestamp():.0f}:f>

**Beatmap information**
CS **{b[8]:.1f}** • AR **{b[9]:.1f}** • OD **{b[10]:.1f}** • HP **{b[11]:.1f}** • **{b[5]:.2f}★**
**{minutes}m{seconds}s** • **{b[7]} combo**
                """

                await channel.send(embed=embed)

            await db.execute_query(
                "delete from newSSs where beatmap_id = " + str(beatmap)
            )

    channel = client.get_channel(942934179425943562)

    li = await db.execute_query("select * from newdtfcs")
    if len(li) > 0:
        print(len(li), "new dt fcs")
        for entry in li:
            beatmap, user, date = entry[0], entry[1], entry[2]
            query = f"""select artist, title, diffname, beatmaps.approved_date, set_id, moddedsr.star_rating, length, maxcombo, 
            modded_cs, modded_ar, modded_od, modded_hp, score, accuracy, enabled_mods, pp from scores
            left join beatmaps on scores.beatmap_id = beatmaps.beatmap_id 
            left join moddedsr on scores.beatmap_id = moddedsr.beatmap_id where scores.beatmap_id = {str(beatmap)} and user_id = {str(user)}
            and moddedsr.mods_enum = (case when is_ht = 'true' then 256 else 0 end + case when is_dt = 'true' then 64 else 0 end + case when is_hr = 'true' then 16 else 0 end + case when is_ez = 'true' then 2 else 0 end + case when is_fl = 'true' then 1024 else 0 end + case when is_fl = 'true' and is_hd = 'true' then 8 else 0 end)"""
            rows = await db.execute_query(query)
            b = rows[0] if len(rows) > 0 else None
            if b is None:
                await db.execute_query(
                    "delete from newdtfcs where beatmap_id = " + str(beatmap)
                )
                continue
            approved_date = b[3]
            minutes = b[6] // 60
            seconds = b[6] % 60

            # differential = ((date.year * 365) + (date.month*31) + (date.day)) - ((approved_date.year * 365) + (approved_date.month*31) + (approved_date.day))
            differential = abs((date - approved_date).days)

            if differential >= 7:
                rows = await db.execute_query(
                    "select username, pp, global_rank from users2 where user_id = "
                    + str(user)
                )
                result = None
                if len(rows) > 0:
                    result = rows[0]
                username = user
                if result is not None:
                    username = result[0]
                    pp = result[1]
                    rank = result[2]

                embed = discord.Embed(
                    title="A map has been FCed with DT for the first time after "
                    + str(differential)
                    + " days!",
                    colour=discord.Colour(0xE5E242),
                )
                author = {
                    "name": f"""{username + " - " + str(pp) + "pp #" + str(rank) if result is not None else str(username)}""",
                    "url": f"https://osu.ppy.sh/users/{user}",
                    "icon_url": f"https://a.ppy.sh/{user}",
                }
                embed.set_author(
                    name=author["name"], url=author["url"], icon_url=author["icon_url"]
                )

                score_pp = f"{b[15]:.2f}pp" if b[15] > 0 else "loved"
                embed.description = f"""
**[{b[0]} - {b[1]} [{b[2]}]](https://osu.ppy.sh/beatmapsets/{b[4]}#osu/{beatmap})**
**{get_mods_string(b[14])} • {b[12]:,} • {b[13]}% • {score_pp}**
**Time of play: ** <t:{date.replace(tzinfo=datetime.timezone.utc).timestamp():.0f}:R>
**Date ranked: ** <t:{approved_date.replace(tzinfo=datetime.timezone.utc).timestamp():.0f}:f>

**Beatmap information**
CS **{b[8]:.1f}** • AR **{b[9]:.1f}** • OD **{b[10]:.1f}** • HP **{b[11]:.1f}** • **{b[5]:.2f}★**
**{minutes}m{seconds}s** • **{b[7]} combo**
                """

                await channel.send(embed=embed)

            await db.execute_query(
                "delete from newdtfcs where beatmap_id = " + str(beatmap)
            )
