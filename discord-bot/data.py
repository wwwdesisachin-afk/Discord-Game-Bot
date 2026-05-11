
TOSS_HEAD_EMOJI = "<:emoji_:1482453280679264319>"
TOSS_TAIL_EMOJI = "<:emoji_:1482453206205464658>"

TIMELINE_EMOJIS = {
    "0":    "⚫",   # dot ball
    "1":    "🟤",   # 1 run
    "2":    "🟢",   # 2 runs
    "3":    "🟡",   # 3 runs
    "4":    "🔵",   # 4 (boundary)
    "6":    "🔴",   # 6 (six)
    "W":    "❌",   # wicket
    "NB":   "🟠",   # no ball
    "NB+1": "🟠",   # no ball + run
    "Wd":   "⬜",   # wide
}

BOWLING_TYPE_ICON = {
    "Fast":     "⚡",
    "Off Spin": "🌀",
    "Leg Spin": "🔄",
}

BALL_SPEEDS = {
    "Fast":        (135, 150),
    "Swing":       (120, 135),
    "Yorker":      (138, 148),
    "Bouncer":     (135, 150),
    "Good Length": (125, 140),
    "Full":        (126, 138),
    "Off Break":   (85, 98),
    "Doosra":      (88, 100),
    "Carrom Ball": (85, 96),
    "Arm Ball":    (88, 98),
    "Top Spin":    (85, 96),
    "Drift Ball":  (82, 95),
    "Leg Break":   (82, 95),
    "Googly":      (82, 92),
    "Flipper":     (88, 98),
    "Top Spinner": (83, 96),
    "Slider":      (83, 95),
}

BALL_DESCRIPTIONS = {
    "Fast":        "fast delivery",
    "Swing":       "swinging delivery",
    "Yorker":      "toe-crushing yorker",
    "Bouncer":     "throat-high bouncer",
    "Good Length": "good length delivery",
    "Full":        "full-pitched delivery",
    "Off Break":   "off-break",
    "Doosra":      "doosra",
    "Carrom Ball": "carrom ball",
    "Arm Ball":    "arm ball",
    "Top Spin":    "top-spinner",
    "Drift Ball":  "drifting delivery",
    "Leg Break":   "leg-break",
    "Googly":      "googly",
    "Flipper":     "flipper",
    "Top Spinner": "top-spinner",
    "Slider":      "slider",
}

SHOT_DESCRIPTIONS = {
    "Drive":        "drives",
    "Pull":         "pulls",
    "Cut":          "cuts",
    "Sweep":        "sweeps",
    "Lofted":       "lofts",
    "Flick":        "flicks",
    "Defend":       "defends",
    "Reverse-Sweep":"reverse-sweeps",
}

FAST_DELIVERIES     = ["Fast", "Swing", "Yorker", "Bouncer", "Good Length", "Full"]
OFF_SPIN_DELIVERIES = ["Off Break", "Doosra", "Carrom Ball", "Arm Ball", "Top Spin"]
LEG_SPIN_DELIVERIES = ["Drift Ball", "Leg Break", "Googly", "Flipper", "Top Spinner", "Slider"]

BOWLING_DELIVERIES = {
    "Fast":     FAST_DELIVERIES,
    "Off Spin": OFF_SPIN_DELIVERIES,
    "Leg Spin": LEG_SPIN_DELIVERIES,
}

BATTING_SHOTS = ["Drive", "Pull", "Cut", "Sweep", "Lofted", "Flick", "Defend", "Reverse-Sweep"]

COUNTRY_FLAGS = {
    "India":       "🇮🇳",
    "Australia":   "🇦🇺",
    "England":     "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Pakistan":    "🇵🇰",
    "South Africa":"🇿🇦",
    "New Zealand": "🇳🇿",
    "West Indies": "🌴",
    "Bangladesh":  "🇧🇩",
    "Sri Lanka":   "🇱🇰",
    "Afghanistan": "🇦🇫",
    "Zimbabwe":    "🇿🇼",
    "Ireland":     "🇮🇪",
}

SAMPLE_TEAMS = {
    "India": {
        "name": "India",
        "ovr": 90,
        "chem": 94,
        "players": [
            {"name": "Rohit Sharma",     "country": "India", "ovr": 92, "bat": 95, "bowl": 45, "bowling_type": "Fast",    "role": "Batter",      "card": "🥇"},
            {"name": "Virat Kohli",      "country": "India", "ovr": 94, "bat": 97, "bowl": 40, "bowling_type": None,      "role": "Batter",      "card": "🥇"},
            {"name": "Shubman Gill",     "country": "India", "ovr": 88, "bat": 90, "bowl": 28, "bowling_type": None,      "role": "Batter",      "card": "🥈"},
            {"name": "Suryakumar Yadav", "country": "India", "ovr": 91, "bat": 93, "bowl": 22, "bowling_type": None,      "role": "Batter",      "card": "🥇"},
            {"name": "Rishabh Pant",     "country": "India", "ovr": 88, "bat": 90, "bowl": 15, "bowling_type": None,      "role": "WK",          "card": "🥇"},
            {"name": "Hardik Pandya",    "country": "India", "ovr": 87, "bat": 82, "bowl": 84, "bowling_type": "Fast",    "role": "All-Rounder", "card": "🥇"},
            {"name": "Ravindra Jadeja",  "country": "India", "ovr": 89, "bat": 78, "bowl": 88, "bowling_type": "Off Spin","role": "All-Rounder", "card": "🥇"},
            {"name": "Kuldeep Yadav",    "country": "India", "ovr": 83, "bat": 38, "bowl": 87, "bowling_type": "Leg Spin","role": "Bowler",      "card": "🥈"},
            {"name": "Jasprit Bumrah",   "country": "India", "ovr": 92, "bat": 28, "bowl": 96, "bowling_type": "Fast",    "role": "Bowler",      "card": "🥇"},
            {"name": "Mohammed Siraj",   "country": "India", "ovr": 84, "bat": 25, "bowl": 85, "bowling_type": "Fast",    "role": "Bowler",      "card": "🥈"},
            {"name": "Yuzvendra Chahal", "country": "India", "ovr": 82, "bat": 22, "bowl": 84, "bowling_type": "Leg Spin","role": "Bowler",      "card": "🥈"},
        ],
    },
    "Australia": {
        "name": "Australia",
        "ovr": 89,
        "chem": 91,
        "players": [
            {"name": "David Warner",   "country": "Australia", "ovr": 91, "bat": 93, "bowl": 42, "bowling_type": None,      "role": "Batter",      "card": "🥇"},
            {"name": "Travis Head",    "country": "Australia", "ovr": 89, "bat": 91, "bowl": 50, "bowling_type": "Off Spin","role": "Batter",      "card": "🥇"},
            {"name": "Steve Smith",    "country": "Australia", "ovr": 92, "bat": 94, "bowl": 55, "bowling_type": "Leg Spin","role": "Batter",      "card": "🥇"},
            {"name": "Glenn Maxwell",  "country": "Australia", "ovr": 88, "bat": 86, "bowl": 80, "bowling_type": "Off Spin","role": "All-Rounder", "card": "🥇"},
            {"name": "Matthew Wade",   "country": "Australia", "ovr": 82, "bat": 80, "bowl": 15, "bowling_type": None,      "role": "WK",          "card": "🥈"},
            {"name": "Cameron Green",  "country": "Australia", "ovr": 84, "bat": 80, "bowl": 82, "bowling_type": "Fast",    "role": "All-Rounder", "card": "🥈"},
            {"name": "Pat Cummins",    "country": "Australia", "ovr": 90, "bat": 60, "bowl": 93, "bowling_type": "Fast",    "role": "Bowler",      "card": "🥇"},
            {"name": "Mitchell Starc", "country": "Australia", "ovr": 89, "bat": 42, "bowl": 91, "bowling_type": "Fast",    "role": "Bowler",      "card": "🥇"},
            {"name": "Adam Zampa",     "country": "Australia", "ovr": 84, "bat": 28, "bowl": 85, "bowling_type": "Leg Spin","role": "Bowler",      "card": "🥈"},
            {"name": "Josh Hazlewood", "country": "Australia", "ovr": 87, "bat": 22, "bowl": 88, "bowling_type": "Fast",    "role": "Bowler",      "card": "🥇"},
            {"name": "Nathan Lyon",    "country": "Australia", "ovr": 84, "bat": 35, "bowl": 85, "bowling_type": "Off Spin","role": "Bowler",      "card": "🥈"},
        ],
    },
}
