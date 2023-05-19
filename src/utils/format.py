import datetime
import discord

def format_td(seconds, digits=3):
    isec, fsec = divmod(round(seconds*10**digits), 10**digits)
    return f'{datetime.timedelta(seconds=isec)}.{fsec:0{digits}.0f}'

def format_leaderboard(rows, di=""):
    embed = discord.Embed(colour=discord.Colour(0xcc5288))
    s = "```pascal\n"
    for row in rows:
        fixed_user = "{0:<15}".format(str(row[1]))
        fixed_rank = "{0:<3}".format(str(row[0]))
        if row[2] == None:
            fixed_number = "0"
        elif isinstance(row[2], datetime.datetime):
            fixed_number = str(row[2])
        elif di.__contains__("-o") and (di["-o"] == "completion" or di["-o"] == "%" or di["-o"] == "length_completion"):
            fixed_number = str(row[2]) + "%"
        elif di.__contains__("-o") and ("length" in di["-o"] and "score" not in di["-o"]):
            # days = int(row[2])//(3600*24)
            # hours = (int(row[2]) // 3600) % 24
            # minutes = (int(row[2]) // 60) % 60
            # fixed_number = str(days) + "d" + str(hours) + "h" + str(minutes) + "m"
            fixed_number = format_td(row[2], 3)
            split_number = fixed_number.split(".")
            if int(split_number[1]) == 0:
                fixed_number = split_number[0]
        elif di.__contains__("-formattime") and di["-formattime"] == "true":
            hours = int(row[2] / 3600)
            minutes = int(row[2] / 60) % 60
            seconds = int(row[2]) % 60
            fixed_number = str(hours) + "h " + str(minutes) + "m " + str(seconds) + "s"
        elif di.__contains__("-float") and di["-float"] == "true":
            if di.__contains__("-precision"):
                precision = 5 if not di["-precision"].isnumeric() else int(di["-precision"])
                fixed_number = f'{float(row[2]):,.{precision}f}'
            else:
                fixed_number = f'{float(row[2]):,.2f}'
        elif di.__contains__("-float") and di["-float"] == "false":
            fixed_number = f'{int(row[2]):,}'
        elif di.__contains__("-o") and "." in str(row[2]):
            fixed_number = f'{float(row[2]):,.2f}'
        else:
            fixed_number = f'{int(row[2]):,}'

        if di.__contains__("-percentage") and di["-percentage"] == "true" and not (di.__contains__("-o") and (di["-o"] == "completion" or di["-o"] == "%")):
            fixed_number += "%"

        s = s + "#" + fixed_rank + " | " + fixed_user + " | " + fixed_number + '\n'

    if s == "```pascal\n":
        s += "No result\n"
    embed.description = s + "```"

    return embed