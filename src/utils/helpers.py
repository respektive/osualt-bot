import datetime
from textwrap import wrap
import json
import requests
import dateutil.parser

def catbox_upload(file_name, file_path):
    catbox_api = "https://litterbox.catbox.moe/resources/internals/api.php"
    response = requests.post(catbox_api,
        data = {
            "reqtype" : "fileupload",
            "time": "1h"
        },
        files = {
            "fileToUpload" : (file_name, open(file_path, "rb"))
        }
    )
    return response.text

unique_tables = ["unique_ss", "unique_fc", "unique_dt_fc", "first_ss", "first_fc"]

mods_enum = {
    ''    : 0,
    'NF'  : 1,
    'EZ'  : 2,
    'TD'  : 4,
    'HD'  : 8,
    'HR'  : 16,
    'SD'  : 32,
    'DT'  : 64,
    'RX'  : 128,
    'HT'  : 256,
    'NC'  : 512,
    'FL'  : 1024,
    'AT'  : 2048,
    'SO'  : 4096,
    'AP'  : 8192,
    'PF'  : 16384,
    '4K'  : 32768,
    '5K'  : 65536,
    '6K'  : 131072,
    '7K'  : 262144,
    '8K'  : 524288,
    'FI'  : 1048576,
    'RD'  : 2097152,
    'LM'  : 4194304,
    '9K'  : 16777216,
    '10K' : 33554432,
    '1K'  : 67108864,
    '3K'  : 134217728,
    '2K'  : 268435456,
    'V2'  : 536870912
}

language_ids = {
    "any": 0,
    "unspecified": 1,
    "english": 2,
    "japanese": 3,
    "chinese": 4,
    "instrumental": 5,
    "korean": 6,
    "french": 7,
    "german": 8,
    "swedish": 9,
    "spanish": 10,
    "italian": 11,
    "russian": 12,
    "polish": 13,
    "other": 14
}

diff_mods = ["HR","EZ","DT","HT","FL","HD"]

def escape_string(s):
    """
    Escapes special characters for use in SQL queries
    """
    special_chars = {"'": "''", '\\': '\\\\', '\"': ''}
    for char, escaped in special_chars.items():
        s = s.replace(char, escaped)
    return s

def write_to_blacklist(di):
        blacklist = []
        path = "./blacklist"

        with open(path, "r") as f:
            blacklist = json.load(f)

        if di.get("-add"):
            with open(path, "w") as f:
                if "," in di["-add"]:
                    to_add = di["-add"].split(",")
                    blacklist = blacklist + to_add
                else:
                    blacklist.append(di["-add"])
                json.dump(blacklist, f)

        return blacklist

def check_date_string(date_string):
    # current UTC date and time
    now = datetime.datetime.utcnow()
    date_format = "%Y-%m-%d"
    if date_string.lower() == "today":
        return now.date().strftime(date_format)
    elif date_string.lower() == "yesterday":
        return (now - datetime.timedelta(days=1)).date().strftime(date_format)
    else:
        date = dateutil.parser.parse(date_string, yearfirst=True)
        return date.isoformat()

def get_mods_enum(mods, diff=False):
    mods = wrap(mods, 2)

    if diff:
        filtered_mods = []
        if "HD" in mods and not "FL" in mods:
            mods.remove("HD")
        for mod in mods:
            if mod in diff_mods:
                filtered_mods.append(mod)
        mods = filtered_mods

    if 'NC' in mods:
        if 'DT' not in mods:
            mods.append('DT')
    if 'PF' in mods:
        if 'SD' not in mods:
            mods.append('SD')
    return_value = 0
    for mod in mods:
        if mod.upper() in mods_enum:
            return_value |= mods_enum[mod.upper()]
    return return_value

# gives a list of the ranked mods given a peppy number lol
def get_mods_string(number):
    """This is the way pyttanko does it. 
    Just as an actual bitwise instead of list. 
    Deal with it."""
    number = int(number)
    mod_list = []

    if number == 0:     mod_list.append('NM')
    if number & 1<<0:   mod_list.append('NF')
    if number & 1<<1:   mod_list.append('EZ')
    if number & 1<<2:   mod_list.append('TD')
    if number & 1<<3:   mod_list.append('HD')
    if number & 1<<4:   mod_list.append('HR')
    if number & 1<<5:   mod_list.append('SD')
    if number & 1<<9:   mod_list.append('NC')
    elif number & 1<<6: mod_list.append('DT')
    if number & 1<<7:   mod_list.append('RX')
    if number & 1<<8:   mod_list.append('HT')
    if number & 1<<10:  mod_list.append('FL')
    if number & 1<<12:  mod_list.append('SO')
    if number & 1<<14:  mod_list.append('PF')
    if number & 1<<15:  mod_list.append('4 KEY')
    if number & 1<<16:  mod_list.append('5 KEY')
    if number & 1<<17:  mod_list.append('6 KEY')
    if number & 1<<18:  mod_list.append('7 KEY')
    if number & 1<<19:  mod_list.append('8 KEY')
    if number & 1<<20:  mod_list.append('FI')
    if number & 1<<24:  mod_list.append('9 KEY')
    if number & 1<<25:  mod_list.append('10 KEY')
    if number & 1<<26:  mod_list.append('1 KEY')
    if number & 1<<27:  mod_list.append('3 KEY')
    if number & 1<<28:  mod_list.append('2 KEY')

    return ''.join(mod_list)

def get_args(arg=None):
    args = []
    if arg != None:
        args = arg
    di = {}
    for i in range(0, len(args) - 1):
        if args[i].startswith("-"):
            key = args[i].lower()
            value = args[i+1].lower()
            if key == "-u":
                di[key] = escape_string(value)
            elif " " in value:
                raise ValueError("spaces are not allowed for argument " + key)
            else:
                di[key] = value
    
    # replace underscores on numbers
    for key, value in di.items():
        if value.isdigit() or (value.replace('_', '').isdigit() and '.' not in value):
            # value is a number with underscores as thousand separators
            di[key] = value.replace('_', '')  # remove the underscores
    
    return di

def build_where_clause(di, table=None):
    where = ""
    if di.get("-modded") and di["-modded"] == "true":
        if not (di.get("-notscorestable") and di["-notscorestable"] == "true"):
            where += " and moddedsr.mods_enum = (case when is_ht = 'true' then 256 else 0 end + case when is_dt = 'true' then 64 else 0 end + case when is_hr = 'true' then 16 else 0 end + case when is_ez = 'true' then 2 else 0 end + case when is_fl = 'true' then 1024 else 0 end + case when is_fl = 'true' and is_hd = 'true' then 8 else 0 end)"
    if di.get("-error"):
        where += " and this_will_error = " + str(di["-error"])
    if di.get("-registered") and str(di["-registered"]) == "true":
        where += " and scores.user_id in (select user_id from priorityuser)"
    if di.get("-min"):
        if di.get("-modded") and di["-modded"] == "true":
            where += " and ROUND(moddedsr.star_rating::numeric, 2) >= " + str(di["-min"])
        else:
            where += " and ROUND(stars, 2) >= " + str(di["-min"])
    if di.get("-max"):
        if di.get("-modded") and di["-modded"] == "true":
            where += " and ROUND(moddedsr.star_rating::numeric, 2) < " + str(di["-max"])
        else:
            where += " and ROUND(stars, 2) < " + str(di["-max"])
    if di.get("-range"):
        range = str(di["-range"]).split("-")
        if di.get("-modded") and di["-modded"] == "true":
            where += " and ROUND(moddedsr.star_rating::numeric, 2) >= " + range[0] + " and ROUND(moddedsr.star_rating::numeric, 2) < " + range[1]
        else:
            where += " and ROUND(stars, 2) >= " + range[0] + " and ROUND(stars, 2) < " + range[1]
    if di.get("-time"):
        where += " and days >= " + str(di["-time"])
    if di.get("-month") and not (di.get("-year") or di.get("-y")):
        day = 1
        year = datetime.datetime.now().year
        month = di["-month"]
        if int(month) < 12:
            next_month = int(month) + 1
            next_year = year
        else:
            next_month = 1
            next_year = int(year) + 1 
        
        di["-end"] = str(next_year) + "-" + str(next_month) + "-01 00:00:00"
        di["-start"] = str(year) + "-" + str(month) + "-" + str(day) + " 00:00:01"
    elif di.get("-month") and (di.get("-year") or di.get("-y")):
        if di.get("-y"):
            di["-year"] = di["-y"]
        day = 1
        year = di["-year"]
        month = di["-month"]
        if int(month) < 12:
            next_month = int(month) + 1
            next_year = year
        else:
            next_month = 1
            next_year = int(year) + 1 

        di["-end"] = str(next_year) + "-" + str(next_month) + "-01 00:00:00"
        di["-start"] = str(year) + "-" + str(month) + "-" + str(day) + " 00:00:01"
    elif di.get("-year") or di.get("-y"):
        if di.get("-y"):
            di["-year"] = di["-y"]
        where += " and beatmaps.approved_date >= '" + check_date_string(str(di["-year"]) + "-01-01 00:00:00") + "' and beatmaps.approved_date <= '" + check_date_string(str(di["-year"]) + "-12-31 23:59:59") + "'"
    if di.get("-start"):
        where += " and beatmaps.approved_date >= '" + check_date_string(str(di["-start"])) + "'"
    if di.get("-end"):
        where += " and beatmaps.approved_date < '" + check_date_string(str(di["-end"])) + "'"
    if di.get("-played-start"):
        where += " and date_played >= '" + check_date_string(str(di["-played-start"])) + "'"
    if di.get("-played-end"):
        where += " and date_played < '" + check_date_string(str(di["-played-end"])) + "'"
    if di.get("-played-date"):
        where += " and date_played >= '" + check_date_string(str(di["-played-date"]) + " 00:00:00") + "' and date_played <= '" + check_date_string(str(di["-played-date"]) + " 23:59:59") + "'"
    if di.get("-b"):
        where += " and beatmaps.beatmap_id in (" + str(di["-b"]) + ")"
    if di.get("-b-min"):
        where += " and beatmaps.beatmap_id >= " + str(di["-b-min"])
    if di.get("-b-max"):
        where += " and beatmaps.beatmap_id < " + str(di["-b-max"])
    if di.get("-b-range"):
        range = str(di["-b-range"]).split("-")
        where += " and beatmaps.beatmap_id > " + range[0] + " and beatmaps.beatmap_id < " + range[1]
    if di.get("-mode") or di.get("-mode") == 0:
        where += " and mode = " + str(di["-mode"])
    if di.get("-approved") or di.get("-a"):
        if di.get("-a"):
            di["-approved"] = di["-a"]
        if di["-approved"] == "4":
            where += " and approved = 4 and beatmaps.beatmap_id not in (184846,1265925,1355907,2562022,1510266,2571051)"
        else:
            where += " and approved = " + str(di["-approved"])
    elif di.get("-loved"):
        if di["-loved"] == "true":
            where += " and approved in (1,2,4) and beatmaps.beatmap_id not in (184846,1265925,1355907,2562022,1510266,2571051)"
        else:
            where += " and approved between 1 and 2"
    if di.get("-date"):
            where += " and beatmaps.approved_date >= '" + check_date_string(str(di["-date"])) + " 00:00:00' and beatmaps.approved_date <= '" + check_date_string(str(di["-date"])) + " 23:59:59'"
    if di.get("-is_fc"):
        if str(di["-is_fc"]).lower() == "true":
            where += " and (countmiss = 0 and (maxcombo - combo) <= scores.count100 or rank like '%X%')"
        if str(di["-is_fc"]).lower() == "false":
            where += " and (countmiss > 0 or (maxcombo - combo) > scores.count100) and rank not like '%X%'"
    if di.get("-is_ss"):
        if str(di["-is_ss"]).lower() == "true":
            where += " and rank like '%X%'"
        if str(di["-is_ss"]).lower() == "false":
            where += " and rank not like '%X%'"
    if di.get("-is_ht"):
        where += " and is_ht = " + di["-is_ht"]
    if di.get("-is_dt"):
        where += " and is_dt = " + di["-is_dt"]
    if di.get("-is_ez"):
        where += " and is_ez = " + di["-is_ez"]
    if di.get("-is_fl"):
        where += " and is_fl = " + di["-is_fl"]
    if di.get("-is_hd"):
        where += " and is_hd = " + di["-is_hd"]
    if di.get("-is_hr"):
        where += " and is_hr = " + di["-is_hr"]
    if di.get("-is_nf"):
        where += " and is_nf = " + di["-is_nf"]
    if di.get("-is_so"):
        where += " and is_so = " + di["-is_so"]
    if di.get("-is_nc"):
        where += " and is_nc = " + di["-is_nc"]
    if di.get("-is_sd"):
        where += " and is_sd = " + di["-is_sd"]
    if di.get("-is_pf"):
        where += " and is_pf = " + di["-is_pf"]
    if di.get("-is_td"):
        where += " and is_td = " + di["-is_td"]
    if di.get("-is_fullmod") and str(di["-is_fullmod"]).lower() == "true":
        where += " and is_hd = true and is_hr = true and is_dt = true and is_fl = true"
    if di.get("-is_nm") and str(di["-is_nm"]).lower() == "true":
        where += " and is_hd = false and is_hr = false and is_dt = false and is_fl = false and is_ez = false and is_ht = false"
    if di.get("-is_nm") and str(di["-is_nm"]).lower() == "false":
        where += " and enabled_mods not in ('0', '1', '4096', '32', '16416', '4097', '4128', '20512')"
    if di.get("-mods") or di.get("-m"):
        if di.get("-m"):
            di["-mods"] = di["-m"]
        if di.get("-notscorestable") and di["-notscorestable"] == "true":
            where += " and moddedsr.mods_enum = '" + str(get_mods_enum(di["-mods"].upper(), True)) + "'"
        else:
            where += " and enabled_mods = '" + str(get_mods_enum(di["-mods"].upper())) + "'"
    if di.get("-is"):
        mod_list = wrap(di["-is"], 2)
        for mod in mod_list:
            if mod == "ss":
                where += " and rank like '%X%'"
            elif mod == "fc":
                where += " and (countmiss = 0 and (maxcombo - combo) <= scores.count100 or rank like '%X%')"
            elif mod == "nm":
                where += " and is_hd = false and is_hr = false and is_dt = false and is_fl = false and is_ez = false and is_ht = false"
            elif mod == "fm":
                where += " and is_hd = true and is_hr = true and is_dt = true and is_fl = true"
            else:
                where += " and is_" + mod + " = true"
    if di.get("-isnot") or di.get("-not"):
        if di.get("-not"):
            di["-isnot"] = di["-not"]
        mod_list = wrap(di["-isnot"], 2)
        for mod in mod_list:
            if mod == "ss":
                where += " and rank not like '%X%'"
            elif mod == "fc":
                where += " and (countmiss > 0 or (maxcombo - combo) > scores.count100) and rank not like '%X%'"
            elif mod == "nm":
                where += " and enabled_mods not in ('0', '1', '4096', '32', '16416', '4097', '4128', '20512')"
            elif mod == "fm":
                where += " and enabled_mods not in ('1112', '1624', '1144', '17528', '1656', '18040')"
            else:
                where += " and is_" + mod + " = false"
    if di.get("-status"):
        if str(di["-status"]).lower() == "sliderbreak":
            where += " and rank like '%S%' and (countmiss > 0 or (maxcombo - combo) > scores.count100)"
        if str(di["-status"]).lower() == "fc":
            where += " and (countmiss = 0 and (maxcombo - combo) <= scores.count100 or rank like '%X%') and is_ht = FALSE and is_ez = FALSE"
        if str(di["-status"]).lower() == "miss":
            where += " and (countmiss > 0 or (maxcombo - combo) > scores.count100) and rank = 'A'"
    if di.get("-multiplier"):
        where += " and ROUND(multiplier, 2) = " + str(di["-multiplier"])
    if di.get("not-multiplier"):
        where += " and ROUND(multiplier, 2) != " + str(di["-multiplier"])
    if di.get("-rank"):
        if int(di["-rank"]) == 1:
            #where += " and beatmaps.beatmap_id in (select beatmap_id from top_score where user_id = " + str(di["-user"]) + ")"
            where += " and scores.user_id = firsts.user_id"
    if di.get("-letters") or di.get("-letter"):
        if di.get("-letter"):
            di["-letters"] = di["-letter"]
        letters = str(di["-letters"]).split(",")
        where += " and ("
        for letter in letters:
            where += "LOWER(rank) like '" + letter + "' or "
        where = where[:-3]
        where += ")"
    if di.get("-user") and not di.get("-unplayed"):
        if table:
            where += f" and {table}.user_id = '" + str(di["-user"]) + "'"
        elif di.get("-rank") or di.get("-nolist"):
            where += " and scores.user_id = '" + str(di["-user"]) + "'"
        else:
            where += " and user_id = '" + str(di["-user"]) + "'"
    if di.get("-country") or di.get("-c"):
        country_code = di.get("-country") or di.get("-c")
        where += f" and LOWER(country_code) = '{country_code.lower()}'"
    if di.get("-rankedscore"):
        where += " and ranked_score >= " + str(di["-rankedscore"])
    if di.get("-rankedscore-max"):
        where += " and ranked_score < " + str(di["-rankedscore-max"])
    if di.get("-totalscore"):
        where += " and total_score >= " + str(di["-totalscore"])
    if di.get("-totalscore-max"):
        where += " and total_score < " + str(di["-totalscore-max"])
    if di.get("-profile-pp") or di.get("-profile-pp-min"):
        if di.get("-profile-pp-min"):
            di["-profile-pp"] = di["-profile-pp-min"]
        where += " and users2.pp >= " + str(di["-profile-pp"])
    if di.get("-profile-pp-max"):
        where += " and users2.pp < " + str(di["-profile-pp-max"])
    if di.get("-playcount-min"):
        where += " and users2.playcount >= " + str(di["-playcount-min"])
    if di.get("-playcount-max"):
        where += " and users2.playcount < " + str(di["-playcount-max"])
    if di.get("-playcount-range"):
        range = str(di["-playcount-range"]).split("-")
        where += " and users2.playcount >= " + range[0] + " and users2.playcount < " + range[1]
    if di.get("-joined-start"):
        where += " and users2.join_date > '" + str(di["-joined-start"]) + " 00:00:00'"
    if di.get("-joined-end"):
        where += " and users2.join_date < '" + str(di["-joined-end"]) + " 00:00:00'"
    if di.get("-topscore") or di.get("-topscore-min"):
        if di.get("-topscore-min"):
            di["-topscore"] = di["-topscore-min"]
        where += " and top_score >= " + str(di["-topscore"])
    if di.get("-topscore-max"):
        where += " and top_score < " + str(di["-topscore-max"])
    if di.get("-topscorenomod"):
        where += " and top_score_nomod >= " + str(di["-topscorenomod"])
    if di.get("-topscorenomod-max"):
        where += " and top_score_nomod < " + str(di["-topscorenomod-max"])
    if di.get("-o") and di["-o"] == "score":
        if di.get("-score") or di.get("-score-min"):
            if di.get("-score-min"):
                di["-score"] = di["-score-min"]
            where += " and top_score >= " + str(di["-score"])
        if di.get("-score-max"):
            where += " and top_score < " + str(di["-score-max"])
    elif di.get("-o") and di["-o"] == "nomodscore":
        if di.get("-score") or di.get("-score-min"):
            if di.get("-score-min"):
                di["-score"] = di["-score-min"]
            where += " and top_score_nomod >= " + str(di["-score"])
        if di.get("-score-max"):
            where += " and top_score_nomod < " + str(di["-score-max"])
    elif di.get("-score") or di.get("-score-min"):
        if di.get("-score-min"):
            di["-score"] = di["-score-min"]
        where += " and score >= " + str(di["-score"])
        if di.get("-score-max"):
            where += " and score < " + str(di["-score-max"])
    elif di.get("-score-max"):
        where += " and score < " + str(di["-score-max"])
    if di.get("-missingscore"):
        if di.get("-unplayed"):
            if di.get("-o") and di["-o"] == "nomodscore":
                where += " and top_score_nomod >= " + str(di["-missingscore"])
            else:
                where += " and top_score >= " + str(di["-missingscore"])
        else:
            if di.get("-o") and di["-o"] == "nomodscore":
                where += " and (top_score_nomod - score) >= " + str(di["-missingscore"])
            else:
                where += " and (top_score - score) >= " + str(di["-missingscore"])
    if di.get("-scorepersecond") or di.get("-scorepersecond-min"):
        if di.get("-scorepersecond-min"):
            di["-scorepersecond"] = di["-scorepersecond-min"]
        where += " and (top_score.top_score / length) >= " + str(di["-scorepersecond"])
    if di.get("-scorepersecond-max"):
        where += " and (top_score.top_score / length) < " + str(di["-scorepersecond-max"])
    if di.get("-nomodscorepersecond") or di.get("-nomodscorepersecond-min"):
        if di.get("-nomodscorepersecond-min"):
            di["-nomodscorepersecond"] = di["-nomodscorepersecond-min"]
        where += " and (top_score_nomod.top_score_nomod / length) >= " + str(di["-nomodscorepersecond"])
    if di.get("-nomodscorepersecond-max"):
        where += " and (top_score_nomod.top_score_nomod / length) < " + str(di["-nomodscorepersecond-max"])
    if di.get("-acc-max"):
        where += " and scores.accuracy < " + str(di["-acc-max"])
    if di.get("-acc-min"):
        where += " and scores.accuracy >= " + str(di["-acc-min"])
    if di.get("-acc-range"):
        range = str(di["-acc-range"]).split("-")
        where += " and scores.accuracy >= " + range[0] + " and scores.accuracy < " + range[1]
    if di.get("-miss-max"):
        where += " and scores.countmiss < " + str(di["-miss-max"])
    if di.get("-miss-min"):
        where += " and scores.countmiss >= " + str(di["-miss-min"])
    if di.get("-miss-range"):
        range = str(di["-miss-range"]).split("-")
        where += " and scores.countmiss >= " + range[0] + " and scores.countmiss < " + range[1]
    if di.get("-300-max"):
        where += " and scores.count300 < " + str(di["-300-max"])
    if di.get("-300-min"):
        where += " and scores.count300 >= " + str(di["-300-min"])
    if di.get("-300-range"):
        range = str(di["-300-range"]).split("-")
        where += " and scores.count300 >= " + range[0] + " and scores.count300 < " + range[1]
    if di.get("-100-max"):
        where += " and scores.count100 < " + str(di["-100-max"])
    if di.get("-100-min"):
        where += " and scores.count100 >= " + str(di["-100-min"])
    if di.get("-100-range"):
        range = str(di["-100-range"]).split("-")
        where += " and scores.count100 >= " + range[0] + " and scores.count100 < " + range[1]
    if di.get("-50-max"):
        where += " and scores.count50 < " + str(di["-50-max"])
    if di.get("-50-min"):
        where += " and scores.count50 >= " + str(di["-50-min"])
    if di.get("-50-range"):
        range = str(di["-50-range"]).split("-")
        where += " and scores.count50 >= " + range[0] + " and scores.count50 < " + range[1]
    if di.get("-fc-max"):
        where += " and fc_count < " + str(di["-fc-max"])
    if di.get("-fc-min"):
        where += " and fc_count >= " + str(di["-fc-min"])
    if di.get("-fc-range"):
        range = str(di["-fc-range"]).split("-")
        where += " and fc_count >= " + range[0] + " and fc_count < " + range[1]
    if di.get("-ss-max"):
        if di.get("-leastssed") and di["-leastssed"] == "true":
            where += " and ss_count.ss_count < " + str(di["-ss-max"])
        else:
            where += " and ss_count + ssh_count < " + str(di["-ss-max"])
    if di.get("-ss-min"):
        if di.get("-leastssed") and di["-leastssed"] == "true":
            where += " and ss_count.ss_count >= " + str(di["-ss-min"])
        else:
            where += " and ss_count + ssh_count >= " + str(di["-ss-min"])
    if di.get("-ss-range"):
        range = str(di["-ss-range"]).split("-")
        if di.get("-leastssed") and di["-leastssed"] == "true":
            where += " and ss_count.ss_count >= " + + range[0] + " and ss_count.ss_count < " + range[1]
        else:
            where += " and ss_count + ssh_count >= " + range[0] + " and ss_count + ssh_count < " + range[1]
    if di.get("-s-max"):
        where += " and s_count + sh_count < " + str(di["-s-max"])
    if di.get("-s-min"):
        where += " and s_count + sh_count >= " + str(di["-s-min"])
    if di.get("-s-range"):
        range = str(di["-s-range"]).split("-")
        where += " and s_count + sh_count >= " + range[0] + " and s_count + sh_count < " + range[1]
    if di.get("-a-max"):
        where += " and a_count < " + str(di["-a-max"])
    if di.get("-a-min"):
        where += " and a_count >= " + str(di["-a-min"])
    if di.get("-a-range"):
        range = str(di["-a-range"]).split("-")
        where += " and a_count >= " + range[0] + " and a_count < " + range[1]
    if di.get("-clears-max"):
        where += " and s_count + sh_count + ss_count + ssh_count + a_count < " + str(di["-clears-max"])
    if di.get("-clears-min"):
        where += " and s_count + sh_count + ss_count + ssh_count + a_count >= " + str(di["-clears-min"])
    if di.get("-clears-range"):
        range = str(di["-clears-range"]).split("-")
        where += " and s_count + sh_count + ss_count + ssh_count + a_count >= " + range[0] + " and s_count + sh_count + ss_count + ssh_count + a_count < " + range[1]
    if di.get("-unplayed") and di["-unplayed"] == "true":
        where += " and beatmaps.beatmap_id not in (select beatmap_id from scores where user_id = " + str(di["-user"]) + ")"
    if di.get("-ssed-by"):
        users = str(di["-ssed-by"]).replace("+", " ")
        users = users.replace("'", "")

        if not users.replace(",", "").isnumeric():
            users = users.split(",")
            for i, user in enumerate(users):
                users[i] = f"'{user}'"
            users = ",".join(users)
            where += " and beatmaps.beatmap_id in (select beatmap_id from scores inner join users2 on scores.user_id = users2.user_id where LOWER(users2.username) in (" + users + ") and rank like '%X%')"
        else:
            where += " and beatmaps.beatmap_id in (select beatmap_id from scores where user_id in (" + users + ") and rank like '%X%')"
    if di.get("-cleared-by"):
        users = str(di["-cleared-by"]).replace("+", " ")
        users = users.replace("'", "")

        if not users.replace(",", "").isnumeric():
            users = users.split(",")
            for i, user in enumerate(users):
                users[i] = f"'{user}'"
            users = ",".join(users)
            where += " and beatmaps.beatmap_id in (select beatmap_id from scores inner join users2 on scores.user_id = users2.user_id where LOWER(users2.username) in (" + users + "))"
        else:
            where += " and beatmaps.beatmap_id in (select beatmap_id from scores where user_id in (" + users + "))"
    if di.get("-uncleared-by"):
        users = str(di["-uncleared-by"]).replace("+", " ")
        users = users.replace("'", "")

        if not users.replace(",", "").isnumeric():
            users = users.split(",")
            for i, user in enumerate(users):
                users[i] = f"'{user}'"
            users = ",".join(users)
            where += " and beatmaps.beatmap_id not in (select beatmap_id from scores inner join users2 on scores.user_id = users2.user_id where LOWER(users2.username) in (" + users + "))"
        else:
            where += " and beatmaps.beatmap_id not in (select beatmap_id from scores where user_id in (" + users + "))"
    if di.get("-ar"):
        where += " and ar = " + str(di["-ar"])
    if di.get("-ar-max"):
        where += " and ar < " + str(di["-ar-max"])
    if di.get("-ar-min"):
        where += " and ar >= " + str(di["-ar-min"])
    if di.get("-ar-range"):
        range = str(di["-ar-range"]).split("-")
        where += " and ar >= " + range[0] + " and ar < " + range[1]
    if di.get("-od"):
        where += " and od = " + str(di["-od"])
    if di.get("-od-max"):
        where += " and od < " + str(di["-od-max"])
    if di.get("-od-min"):
        where += " and od >= " + str(di["-od-min"])
    if di.get("-od-range"):
        range = str(di["-od-range"]).split("-")
        where += " and od >= " + range[0] + " and od < " + range[1]
    if di.get("-hp"):
        where += " and hp = " + str(di["-hp"])
    if di.get("-hp-max"):
        where += " and hp < " + str(di["-hp-max"])
    if di.get("-hp-min"):
        where += " and hp >= " + str(di["-hp-min"])
    if di.get("-hp-range"):
        range = str(di["-hp-range"]).split("-")
        where += " and hp >= " + range[0] + " and hp < " + range[1]
    if di.get("-cs"):
        where += " and cs = " + str(di["-cs"])
    if di.get("-cs-max"):
        where += " and cs < " + str(di["-cs-max"])
    if di.get("-cs-min"):
        where += " and cs >= " + str(di["-cs-min"])
    if di.get("-cs-range"):
        range = str(di["-cs-range"]).split("-")
        where += " and cs >= " + range[0] + " and cs < " + range[1]
    if di.get("-bpm"):
        where += " and bpm = " + str(di["-bpm"])
    if di.get("-bpm-max"):
        where += " and bpm < " + str(di["-bpm-max"])
    if di.get("-bpm-min"):
        where += " and bpm >= " + str(di["-bpm-min"])
    if di.get("-bpm-range"):
        range = str(di["-bpm-range"]).split("-")
        where += " and bpm >= " + range[0] + " and bpm < " + range[1]
    if di.get("-pp-max"):
        where += " and scores.pp < " + str(di["-pp-max"])
    if di.get("-pp-min"):
        where += " and scores.pp >= " + str(di["-pp-min"])
    if di.get("-pp-range"):
        range = str(di["-pp-range"]).split("-")
        where += " and scores.pp >= " + range[0] + " and scores.pp < " + range[1]
    if di.get("-length-max"):
        where += " and length < " + str(di["-length-max"])
    if di.get("-length-min"):
        where += " and length >= " + str(di["-length-min"])
    if di.get("-length-range"):
        range = str(di["-length-range"]).split("-")
        where += " and length >= " + range[0] + " and length < " + range[1]
    if di.get("-maxcombo"):
        where += " and maxcombo = " + str(di["-maxcombo"])
    if di.get("-maxcombo-max"):
        where += " and maxcombo < " + str(di["-maxcombo-max"])
    if di.get("-maxcombo-min"):
        where += " and maxcombo >= " + str(di["-maxcombo-min"])
    if di.get("-maxcombo-range"):
        range = str(di["-maxcombo-range"]).split("-")
        where += " and maxcombo >= " + range[0] + " and maxcombo < " + range[1]
    if di.get("-combo"):
        where += " and combo = " + str(di["-combo"])
    if di.get("-combo-max"):
        where += " and combo < " + str(di["-combo-max"])
    if di.get("-combo-min"):
        where += " and combo >= " + str(di["-combo-min"])
    if di.get("-combo-range"):
        range = str(di["-combo-range"]).split("-")
        where += " and combo >= " + range[0] + " and combo < " + range[1]
    if di.get("-circles"):
        where += " and circles = " + str(di["-circles"])
    if di.get("-circles-max"):
        where += " and circles < " + str(di["-circles-max"])
    if di.get("-circles-min"):
        where += " and circles >= " + str(di["-circles-min"])
    if di.get("-circles-range"):
        range = str(di["-circles-range"]).split("-")
        where += " and circles >= " + range[0] + " and circles < " + range[1]
    if di.get("-sliders"):
        where += " and sliders = " + str(di["-sliders"])
    if di.get("-sliders-max"):
        where += " and sliders < " + str(di["-sliders-max"])
    if di.get("-sliders-min"):
        where += " and sliders >= " + str(di["-sliders-min"])
    if di.get("-sliders-range"):
        range = str(di["-sliders-range"]).split("-")
        where += " and sliders >= " + range[0] + " and sliders < " + range[1]
    if di.get("-spinners"):
        where += " and spinners = " + str(di["-spinners"])
    if di.get("-spinners-max"):
        where += " and spinners < " + str(di["-spinners-max"])
    if di.get("-spinners-min"):
        where += " and spinners >= " + str(di["-spinners-min"])
    if di.get("-spinners-range"):
        range = str(di["-spinners-range"]).split("-")
        where += " and spinners >= " + range[0] + " and spinners < " + range[1]
    if di.get("-objects"):
        where += " and (spinners + sliders + circles) = " + str(di["-objects"])
    if di.get("-objects-max"):
        where += " and (spinners + sliders + circles) < " + str(di["-objects-max"])
    if di.get("-objects-min"):
        where += " and (spinners + sliders + circles) >= " + str(di["-objects-min"])
    if di.get("-objects-range"):
        range = str(di["-objects-range"]).split("-")
        where += " and (spinners + sliders + circles) >= " + range[0] + " and (spinners + sliders + circles) < " + range[1]
    if di.get("-tags"):
        where += " and LOWER(source || ' ' || tags || ' ' || artist || ' ' || beatmaps.title || ' ' || creator || ' ' || diffname) like '" + str(di["-tags"]).lower() + "'"
    if di.get("-genre"):
        where += " and genre = " + str(di["-genre"])
    if di.get("-language"):
        lang = str(di["-language"])
        if lang.isnumeric():
            where += " and language = " + lang
        elif lang in language_ids:
            where += " and language = " + str(language_ids[lang])
    if di.get("-artist"):
        where += " and LOWER(artist) like '" + str(di["-artist"]).lower() + "'"
    if di.get("-title"):
        where += " and LOWER(beatmaps.title) like '" + str(di["-title"]).lower() + "'"
    if di.get("-title-max"):
        where += " and LOWER(beatmaps.title) < '" + str(di["-title-max"]).lower() + "'"
    if di.get("-mapper"):
        where += " and LOWER(creator) like '" + str(di["-mapper"]).lower() + "'"
    if di.get("-diff"):
        where += " and LOWER(diffname) like '" + str(di["-diff"]).lower() + "'"
    if di.get("-replay"):
        if str(di["-replay"]).lower() == "true":
            where += " and replay_available = 1"
        else:
            where += " and replay_available = 0"
    if di.get("-pack"):
        if str(di["-pack"]).isnumeric():
            pack = "s" + str(di["-pack"])
        else:
            pack = str(di["-pack"])
        where += " and LOWER(pack_id) = '" + pack.lower() + "'"
    if di.get("-pack-min"):
        where += " and pack_id similar to 'S[0-9]%' and cast(substr(pack_id, 2, 10) as integer) >= '" + str(di["-pack-min"]).lower() + "'"
    if di.get("-pack-max"):
        where += " and pack_id similar to 'S[0-9]%' and cast(substr(pack_id, 2, 10) as integer) <= '" + str(di["-pack-max"]).lower() + "'"
    if di.get("-packs"):
        range = str(di["-packs"]).split("-")
        if len(range) == 1:
            range *= 2
        where += " and pack_id similar to 'S[0-9]%' and cast(substr(pack_id, 2, 10) as integer) >= " + range[0] + " and cast(substr(pack_id, 2, 10) as integer) <= " + range[1]
    if di.get("-apacks"):
        range = str(di["-apacks"]).split("-")
        if len(range) == 1:
            range *= 2
        where += " and pack_id similar to 'SA[0-9]%' and cast(substr(pack_id, 3, 10) as integer) >= " + range[0] + " and cast(substr(pack_id, 3, 10) as integer) <= " + range[1]
    if di.get("-tragedy"):
        if di["-tragedy"] == "100":
            where += " and (count100 = 1 and countmiss = 0 and count50 = 0)"
        if di["-tragedy"] == "50":
            where += " and (count100 = 0 and countmiss = 0 and count50 = 1)"
        if di["-tragedy"] == "miss":
            where += " and (count100 = 0 and countmiss = 1 and count50 = 0)"
        if di["-tragedy"] == "x":
            where += " and countmiss = 1"
    if di.get("-o"):
        if str(di["-o"]).lower() == "pp":
            where += " and scores.pp != 'NaN'"
        if di["-o"] == "nomodnumberones":
            where += " and beatmaps.beatmap_id in (select beatmap_id from top_score_nomod where user_id = " + str(di["-user"]) + ")"
        if di["-o"] == "hiddennumberones":
            where += " and beatmaps.beatmap_id in (select beatmap_id from top_score_nomod_hidden where user_id = " + str(di["-user"]) + ")"

    if where != "":
        where = " where " + where[4:]
    
    return where