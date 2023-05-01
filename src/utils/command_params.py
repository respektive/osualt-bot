GLOBAL_PARAMS = """```ahk
-l: specify how many results to output. Beware the 4000 character limit
-p: specify the resulting page to output
-u: specify a user (For a space in the username, use "+" or quotes)
-direction: desc, asc
```"""

BEATMAP_PARAMS = """```ahk
-ar-min, -od-max, -cs-min, -length-max, etc: map parameters
-maxcombo-min/max: min/max combo of the beatmap
-min/max: min/max star rating
-range: range of star rating
-tags: specify tags
-title: specify a title
-mapper: specify a mapper name
-artist: specify an artist name
-diff: specify a difficulty name
-genre: specficy a genre id
-language: specify a language id
-start: earliest rank date of maps to include
-end: latest rank date of maps to include
-year: specify a year
-month: specify a month (1-12)
-date: specify a date 
-pack: specifiy a pack id
-packs: specify a range of packs
-apacks: specify a range of approved packs
-approved: approved status (1 = ranked, 2 = approved, 4 = loved)
-loved: true, to include loved maps
-b: specify a beatmap id
-b-min/max/range: min/max/range of beatmap ids
```"""

PROFILE_PARAMS = """```ahk
-playcount-min/max/range: min/max/range of playcount to include 
-clears-min/max/range: min/max/range of clears to include
-country: specify a country using the ISO 2 letter code
-profile-pp-min/max: min/max profile pp to include
-rankedscore-min/max: min/max ranked score to include
-totalscore-min/max: min/max ranked score to include
-joined-start/end: earliest/latest date joined to include
-ss-min/max/range: min/max/range of SS ranks to include
-s-min/max/range: min/max/range of S ranks to include
-a-min/max/range: min/max/range of A ranks to include
```"""

ADVANCED_PARAMS = """```ahk
-letters: X XH S SH A B C D or comma separated list of letters
-is_ss, -is_ht, -is_dt, etc. : true/false
-is: hd, hdhrdt, etc. short for -is_mod true
-isnot: hd, hdhrdt, etc. short for -is_mod false
-mods: ht, nfso, dthrfl, hd, ezhtnfhdfl, etc.
-modded: true, to use the modded star rating
-score-min/max: min/max score amount
-topscore-min/max: min/max #1 score amount
-topscorenomod-min/max: min/max #1 nomod score amount
-replay: true/false
-order: score, length, approved_date, accuracy, ar, od etc.
-acc-min/max/range: min/max/range acc to include
-pp-min/max/range: min/max/range pp to include
-combo-min/max/range: min/max/range combo to include
-miss-min/max/range: min/max/range amount of misses to include
-300-min/max/range: min/max/range amount of 300s to include
-100-min/max/range: min/max/range amount of 100s to include
-50-min/max/range: min/max/range amount of 50s to include
-tragedy: 100, 50, x, miss
-unplayed: true
```"""

COMMAND_FLAGS = {
    "global": { "name": "Global Parameters", "value": GLOBAL_PARAMS },
    "profile": { "name": "Profile Parameters", "value": PROFILE_PARAMS },
    "advanced": { "name": "Advanced Parameters", "value": ADVANCED_PARAMS },
    "beatmap": { "name": "Beatmap Parameters", "value": BEATMAP_PARAMS },
}

COG_FLAGS = {
    "profile": ["global", "profile"],
    "performance": ["global", "profile"],
    "advanced": ["global", "profile", "advanced", "beatmap"],
    "beatmaps": ["global", "beatmap"],
    "score": ["global", "profile", "advanced", "beatmap"],
    "yearly": ["global", "profile", "advanced", "beatmap"],
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
-o: score, nomodscore for score completion
```""",
    "ar_completion": """```ahk
-g: grouping size
-o: score, nomodscore for score completion
```""",
    "od_completion": """```ahk
-g: grouping size
-o: score, nomodscore for score completion
```""",
    "cs_completion": """```ahk
-g: grouping size
-o: score, nomodscore for score completion
```""",
    "stars_completion": """```ahk
-g: grouping size
-o: score, nomodscore for score completion
```""",
    "length_completion": """```ahk
-g: grouping size
-o: score, nomodscore for score completion
```""",
    "combo_completion": """```ahk
-g: grouping size
-o: score, nomodscore for score completion
```""",
    "yearly_completion": """```ahk
-o: score, nomodscore for score completion
```""",
    "getfile": """```ahk
-type: List to fetch. neverbeenssed, neverbeenfced, neverbeendted, scores, scoresimple, beatmaps, beatmapsimple, fc_count, top_score, top_score_nomod, top_score_hidden, registered, nomodnumberones, hiddennumberones, numberones
-u: specify a user
```""",
}