GLOBAL_PARAMS = """```ahk
-l: specify how many results to output. Beware the 4000 character limit
-p: specify the resulting page to output
-u: specify a user (For a space in the username, use "+")  
```"""

BEATMAP_PARAMS = """```ahk
-ar-min, -od-max, -cs-min, -length-max, etc: map parameters
-tags: queue a subset of maps with given tags
-title: queue a subset of maps with a given title
-mapper: queue a subset of maps with a given mapper name
-artist: queue a subset of maps with a given artist name
-diff: queue a subset of maps with a given difficulty name
```"""

COMMON_PARAMS = """```ahk
-clears-min: minimal number of clears to include (inclusive)
-clears-max: minimal number of clears to include (exclusive)
-country: specify a country using the ISO 2 letter code
-direction: desc, asc
-playcount-min: minimal ranked score to include (inclusive)
-playcount-max: maximal ranked score to include (exclusive)
-profile-pp-min: minimal profile pp to include (inclusive)
-profile-pp-max: maximal profile pp to include (exclusive)
-rankedscore: minimal ranked score to include (inclusive)
-rankedscore-max: maximal ranked score to include (exclusive)
-totalscore-min: minimal ranked score to include (inclusive)
-totalscore-max: maximal ranked score to include (exclusive)
```"""

ADVANCED_PARAMS = """```ahk
-letter: X XH X% SH S S% A B C D 
-is_ss, -is_ht, -is_dt, etc. : true/false
-is: hd, hdhrdt, etc. short for -is_mod true
-isnot: hd, hdhrdt, etc. short for -is_mod false
-mods: ht, nfso, dthrfl, hd, ezhtnfhdfl, etc.
-replay: true/false
-order: score, length, approved_date, accuracy, ar, od etc.
-direction: desc, asc
-min/-max: min/max star rating of maps to include 
-acc-min/max: min/max acc to include 
-pp-min/max: min/max pp to include 
-playcount-min/max: min/max amount of playcount to include 
-played-start/end: earliest/latest date played maps to include
-start: earliest rank date of maps to include
-end: latest rank date of maps to include
-year: specify a year
-unplayed: true
-tragedy: 100, 50, x, miss
-score: minimum score to include
```"""

COMMAND_FLAGS = {
    "global": { "name": "Global Parameters", "value": GLOBAL_PARAMS },
    "common": { "name": "Parameters", "value": COMMON_PARAMS },
    "beatmap": { "name": "Beatmap Parameters", "value": BEATMAP_PARAMS },
    "advanced": { "name": "Optional Parameters", "value": ADVANCED_PARAMS },
}

COG_FLAGS = {
    "profile": ["global", "common"],
    "performance": ["global", "common"],
    "advanced": ["global", "advanced", "beatmap"],
    "beatmaps": ["global", "beatmap"],
    "score": ["global", "advanced", "beatmap"],
    "yearly": ["global", "advanced", "beatmap"],
    "completion": ["global", "advanced", "beatmap"],
}

EXTRA_COMMAND_FLAGS = {
    "generateosdb": ["global", "advanced", "beatmap"],
    "getfile": ["advanced", "beatmap"],
}

SPECIAL_COMMAND_PARAMS = {
    "tragedy": """```ahk
-o: 100, 50, miss, x
• 100: 1x100 only score for an SS
• 50: 1x50 only score for an SS
• miss: 1 miss only score for an SS
• x: 1 miss only score for an FC
```""",
    "register": """```ahk
your user_id. username won't work.
```""",
    "scorequeue": """```ahk
-b: Which beatmap id to check
-u: Which user id to check
```""",
    "pack_completion": """```ahk
-g: grouping size
-a: set to 2 for approved packs
```""",
    "getfile": """```ahk
-type: List to fetch. neverbeenssed, neverbeenfced, neverbeendted, scores, scoresimple, beatmaps, beatmapsimple, fc_count, top_score, top_score_nomod, top_score_hidden, registered, nomodnumberones, hiddennumberones, numberones
-u: specify a user
```""",
}