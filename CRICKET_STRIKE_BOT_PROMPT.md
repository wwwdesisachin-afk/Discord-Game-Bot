# Cricket Strike Bot — Complete Recreation Prompt

Build a fully-featured Discord cricket game bot in Python called **Cricket Strike Bot** (command prefix `!cs`). Two human players play a full T20-style match ball-by-ball using Discord buttons and dropdowns. Every phase of the game sends a **new Discord message** in the channel — never edit the main game message. The bot is named FootQuiz#4031 but the code is generic.

---

## 1. File Structure

```
discord-bot/
├── main.py          # Bot entry point, commands
├── game.py          # GameState class
├── views.py         # All Discord UI (buttons, dropdowns, game flow)
├── logic.py         # Delivery × shot outcome probability matrix
├── embeds.py        # Scoreboard, Playing XI, Result embeds
├── commentary.py    # Ball-by-ball commentary builder
├── data.py          # Constants: emojis, teams, speeds, deliveries, shots
└── emoji_sync.py    # Download & register custom Application Emojis on startup
```

Run command: `cd discord-bot && python3 main.py`
Required env var: `DISCORD_BOT_TOKEN`
Dependencies: `discord.py>=2.0`, `aiohttp`

---

## 2. `data.py` — All Constants

```python
TOSS_HEAD_EMOJI = "<:emoji_:1482453280679264319>"
TOSS_TAIL_EMOJI = "<:emoji_:1482453206205464658>"

TIMELINE_EMOJIS = {
    "0":    "<:emoji_49:1483444731383119965>",
    "1":    "<:emoji_46:1483442692192075957>",
    "2":    "<:emoji_46:1483442723599155240>",
    "3":    "<:emoji_47:1483442748802728178>",
    "4":    "<a:aemoji_:1480816551996162048>",
    "6":    "<a:emoji_16:1480816170067165274>",
    "W":    "<:emoji_20:1480816418982330491>",
    "NB":   "<:emoji_49:1483444755613614341>",
    "NB+1": "<:emoji_56:1484027767774380102>",
    "Wd":   "⬜",
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
    "Drive":         "drives",
    "Pull":          "pulls",
    "Cut":           "cuts",
    "Sweep":         "sweeps",
    "Lofted":        "lofts",
    "Flick":         "flicks",
    "Defend":        "defends",
    "Reverse-Sweep": "reverse-sweeps",
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
    "India":        "🇮🇳",
    "Australia":    "🇦🇺",
    "England":      "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Pakistan":     "🇵🇰",
    "South Africa": "🇿🇦",
    "New Zealand":  "🇳🇿",
    "West Indies":  "🌴",
    "Bangladesh":   "🇧🇩",
    "Sri Lanka":    "🇱🇰",
    "Afghanistan":  "🇦🇫",
    "Zimbabwe":     "🇿🇼",
    "Ireland":      "🇮🇪",
}

SAMPLE_TEAMS = {
    "India": {
        "name": "India",
        "ovr": 90,
        "chem": 94,
        "players": [
            {"name": "Rohit Sharma",     "country": "India", "ovr": 92, "bat": 95, "bowl": 45, "bowling_type": "Fast",     "role": "Batter",      "card": "🥇"},
            {"name": "Virat Kohli",      "country": "India", "ovr": 94, "bat": 97, "bowl": 40, "bowling_type": None,       "role": "Batter",      "card": "🥇"},
            {"name": "Shubman Gill",     "country": "India", "ovr": 88, "bat": 90, "bowl": 28, "bowling_type": None,       "role": "Batter",      "card": "🥈"},
            {"name": "Suryakumar Yadav", "country": "India", "ovr": 91, "bat": 93, "bowl": 22, "bowling_type": None,       "role": "Batter",      "card": "🥇"},
            {"name": "Rishabh Pant",     "country": "India", "ovr": 88, "bat": 90, "bowl": 15, "bowling_type": None,       "role": "WK",          "card": "🥇"},
            {"name": "Hardik Pandya",    "country": "India", "ovr": 87, "bat": 82, "bowl": 84, "bowling_type": "Fast",     "role": "All-Rounder", "card": "🥇"},
            {"name": "Ravindra Jadeja",  "country": "India", "ovr": 89, "bat": 78, "bowl": 88, "bowling_type": "Off Spin", "role": "All-Rounder", "card": "🥇"},
            {"name": "Kuldeep Yadav",    "country": "India", "ovr": 83, "bat": 38, "bowl": 87, "bowling_type": "Leg Spin", "role": "Bowler",      "card": "🥈"},
            {"name": "Jasprit Bumrah",   "country": "India", "ovr": 92, "bat": 28, "bowl": 96, "bowling_type": "Fast",     "role": "Bowler",      "card": "🥇"},
            {"name": "Mohammed Siraj",   "country": "India", "ovr": 84, "bat": 25, "bowl": 85, "bowling_type": "Fast",     "role": "Bowler",      "card": "🥈"},
            {"name": "Yuzvendra Chahal", "country": "India", "ovr": 82, "bat": 22, "bowl": 84, "bowling_type": "Leg Spin", "role": "Bowler",      "card": "🥈"},
        ],
    },
    "Australia": {
        "name": "Australia",
        "ovr": 89,
        "chem": 91,
        "players": [
            {"name": "David Warner",   "country": "Australia", "ovr": 91, "bat": 93, "bowl": 42, "bowling_type": None,       "role": "Batter",      "card": "🥇"},
            {"name": "Travis Head",    "country": "Australia", "ovr": 89, "bat": 91, "bowl": 50, "bowling_type": "Off Spin", "role": "Batter",      "card": "🥇"},
            {"name": "Steve Smith",    "country": "Australia", "ovr": 92, "bat": 94, "bowl": 55, "bowling_type": "Leg Spin", "role": "Batter",      "card": "🥇"},
            {"name": "Glenn Maxwell",  "country": "Australia", "ovr": 88, "bat": 86, "bowl": 80, "bowling_type": "Off Spin", "role": "All-Rounder", "card": "🥇"},
            {"name": "Matthew Wade",   "country": "Australia", "ovr": 82, "bat": 80, "bowl": 15, "bowling_type": None,       "role": "WK",          "card": "🥈"},
            {"name": "Cameron Green",  "country": "Australia", "ovr": 84, "bat": 80, "bowl": 82, "bowling_type": "Fast",     "role": "All-Rounder", "card": "🥈"},
            {"name": "Pat Cummins",    "country": "Australia", "ovr": 90, "bat": 60, "bowl": 93, "bowling_type": "Fast",     "role": "Bowler",      "card": "🥇"},
            {"name": "Mitchell Starc", "country": "Australia", "ovr": 89, "bat": 42, "bowl": 91, "bowling_type": "Fast",     "role": "Bowler",      "card": "🥇"},
            {"name": "Adam Zampa",     "country": "Australia", "ovr": 84, "bat": 28, "bowl": 85, "bowling_type": "Leg Spin", "role": "Bowler",      "card": "🥈"},
            {"name": "Josh Hazlewood", "country": "Australia", "ovr": 87, "bat": 22, "bowl": 88, "bowling_type": "Fast",     "role": "Bowler",      "card": "🥇"},
            {"name": "Nathan Lyon",    "country": "Australia", "ovr": 84, "bat": 35, "bowl": 85, "bowling_type": "Off Spin", "role": "Bowler",      "card": "🥈"},
        ],
    },
}
```

---

## 3. `emoji_sync.py` — Application Emoji Registration

On `on_ready`, call `sync_emojis(bot)`. This:
1. Fetches the bot's existing Application Emojis via `bot.fetch_application_emojis()`
2. For each emoji not yet registered, downloads the image from Discord CDN:
   `https://cdn.discordapp.com/emojis/{original_id}.{png|gif}`
3. Uploads it via `bot.create_application_emoji(name=name, image=bytes)`
4. Patches `data.TIMELINE_EMOJIS`, `data.TOSS_HEAD_EMOJI`, `data.TOSS_TAIL_EMOJI` at runtime so every module gets live `<:name:id>` strings

Source emoji mapping (key → app_name, original_discord_id, animated):
```
toss_head    → cs_head,    1482453280679264319, False
toss_tail    → cs_tail,    1482453206205464658, False
timeline_0   → cs_dot,     1483444731383119965, False
timeline_1   → cs_1run,    1483442692192075957, False
timeline_2   → cs_2run,    1483442723599155240, False
timeline_3   → cs_3run,    1483442748802728178, False
timeline_4   → cs_4run,    1480816551996162048, True  (animated)
timeline_6   → cs_6run,    1480816170067165274, True  (animated)
timeline_W   → cs_wicket,  1480816418982330491, False
timeline_NB  → cs_noball,  1483444755613614341, False
timeline_NB1 → cs_noball1, 1484027767774380102, False
```

---

## 4. `game.py` — GameState Class

All match state is stored per channel (`channel_id → GameState`). One active match per channel.

**Constructor** takes `(challenger: discord.Member, opponent: discord.Member, overs: int)`.

**Fields:**
```
challenger, opponent          — discord.Member
overs                         — int (default 20, range 1-50)
teams: dict[int, dict]        — user_id → team dict
toss_winner_id                — int | None
batting_user_id               — int | None
bowling_user_id               — int | None
striker, non_striker          — player dict | None
current_bowler                — player dict | None
innings                       — 1 or 2
runs: [0, 0]                  — [inn1_runs, inn2_runs]
wickets: [0, 0]
legal_balls: [0, 0]
batsman_stats: dict[name, {runs, balls}]
bowler_stats:  dict[name, {balls, runs, wickets}]
dismissed: list[str]          — player names out this innings
bowler_ball_count: dict[name, int]
last_over_bowler: str | None  — no consecutive overs
partnership_runs, partnership_balls — reset on wicket
timeline: list[str]           — emoji per delivery, reset on innings 2
pending_delivery: str | None
current_over_balls: int       — resets each over (legal only)
current_over_runs: int
phase: str                    — "pending" | "toss" | "bat_or_bowl" | "select_striker" |
                                "select_bowler" | "bowl_select" | "bat_select" |
                                "wicket_fallen" | "over_end"
game_message: discord.Message | None
```

**Key methods:**

`add_runs(runs)` — add to innings score, batsman stat, bowler stat, partnership, current_over_runs.

`add_legal_ball()` — increment legal_balls, current_over_balls, partnership_balls, batsman balls, bowler balls+ball_count.

`add_wicket()` — increment wickets, bowler wickets, append dismissed, reset partnership.

`rotate_strike()` — swap striker ↔ non_striker.

`end_over()` — rotate_strike(), set last_over_bowler, reset current_over_balls/runs, set current_bowler=None.

`overs_str()` → `"X.Y"` — completed overs dot balls in current over.

`bowler_overs_str(name)` → `"X.Y"`.

`sr(name)` → `"XX.X"` — strike rate.

`crr()` → float — current run rate = (runs / legal_balls) * 6.

`rrr()` → float — required run rate in innings 2 only = (needed / balls_left) * 6.

`target()` → `runs[0] + 1` in innings 2, else None.

`is_innings_over()` → True if wickets >= 10, or legal_balls >= overs*6, or (innings==2 and runs[1] >= runs[0]+1).

`max_bowler_balls()` → `max(1, overs // 5) * 6` — max balls per bowler (1/5th of total overs).

`get_available_bowlers()` — players with a bowling_type, under ball cap, not last_over_bowler.

`get_available_batsmen()` — players not dismissed, not currently batting.

`start_second_innings()` — swap batting/bowling user IDs, reset striker/non_striker/bowler/dismissed/ball_counts/last_over_bowler/partnership/timeline/current_over, set innings=2, phase="select_striker".

`match_result()` → string — "🏆 X wins by Y wickets (Z balls remaining)!" or "🏆 X wins by Y runs!" or "🤝 Match tied!".

**Properties:** `batting_user`, `bowling_user` (discord.Member), `current_runs`, `current_wickets`, `current_legal_balls`.

---

## 5. `logic.py` — Outcome Calculation

### Base weights (before modifiers)
```
"0": 35, "1": 22, "2": 10, "3": 3, "4": 11, "6": 5, "W": 8, "Wd": 4, "NB": 2
```
Note: `"NB+1"` (no-ball with a run) is not in base weights — it is produced by promoting some NB weight in calculation (the actual implementation keeps NB+1 separate; in the matrix it stays as NB=2 and the outcome string "NB+1" comes from random logic in commentary; here keep NB=2 and occasionally return "NB+1" as a variant, or simply keep both outcomes).

### Delivery × Shot MATCHUP_MATRIX

Each entry: `(delivery, shot) → {"bat": float, "wkt": float}`

`bat` multiplier scales run-scoring outcomes. `wkt` multiplier scales wicket probability.
`bat > 1` = batsman-favoured. `wkt > 1` = bowler-favoured.

Full matrix (all 17 deliveries × 8 shots = 136 entries):

**Fast deliveries:**
```
(Fast,        Drive)         bat=1.2  wkt=0.9
(Fast,        Pull)          bat=0.8  wkt=1.3
(Fast,        Cut)           bat=1.0  wkt=1.0
(Fast,        Sweep)         bat=0.5  wkt=1.6
(Fast,        Lofted)        bat=1.3  wkt=1.4
(Fast,        Flick)         bat=1.1  wkt=0.9
(Fast,        Defend)        bat=0.3  wkt=0.5
(Fast,        Reverse-Sweep) bat=0.7  wkt=1.6

(Swing,       Drive)         bat=0.7  wkt=1.6
(Swing,       Pull)          bat=0.7  wkt=1.3
(Swing,       Cut)           bat=0.8  wkt=1.4
(Swing,       Sweep)         bat=0.6  wkt=1.4
(Swing,       Lofted)        bat=0.9  wkt=1.8
(Swing,       Flick)         bat=1.2  wkt=0.8
(Swing,       Defend)        bat=0.4  wkt=0.6
(Swing,       Reverse-Sweep) bat=0.5  wkt=1.8

(Yorker,      Drive)         bat=0.5  wkt=2.0
(Yorker,      Pull)          bat=0.3  wkt=2.5
(Yorker,      Cut)           bat=0.4  wkt=2.0
(Yorker,      Sweep)         bat=0.4  wkt=1.8
(Yorker,      Lofted)        bat=0.3  wkt=2.5
(Yorker,      Flick)         bat=0.9  wkt=1.2
(Yorker,      Defend)        bat=0.6  wkt=0.7
(Yorker,      Reverse-Sweep) bat=0.5  wkt=2.0

(Bouncer,     Drive)         bat=0.3  wkt=2.5
(Bouncer,     Pull)          bat=1.9  wkt=0.6
(Bouncer,     Cut)           bat=1.2  wkt=0.8
(Bouncer,     Sweep)         bat=0.4  wkt=2.0
(Bouncer,     Lofted)        bat=0.7  wkt=1.6
(Bouncer,     Flick)         bat=0.4  wkt=2.0
(Bouncer,     Defend)        bat=0.2  wkt=1.2
(Bouncer,     Reverse-Sweep) bat=0.3  wkt=2.5

(Good Length, Drive)         bat=1.0  wkt=1.0
(Good Length, Pull)          bat=0.7  wkt=1.2
(Good Length, Cut)           bat=0.8  wkt=1.1
(Good Length, Sweep)         bat=0.7  wkt=1.2
(Good Length, Lofted)        bat=1.2  wkt=1.3
(Good Length, Flick)         bat=0.9  wkt=1.0
(Good Length, Defend)        bat=0.4  wkt=0.5
(Good Length, Reverse-Sweep) bat=0.6  wkt=1.5

(Full,        Drive)         bat=1.9  wkt=0.5
(Full,        Pull)          bat=0.6  wkt=1.4
(Full,        Cut)           bat=0.8  wkt=1.1
(Full,        Sweep)         bat=0.8  wkt=1.1
(Full,        Lofted)        bat=1.8  wkt=1.0
(Full,        Flick)         bat=1.7  wkt=0.6
(Full,        Defend)        bat=0.3  wkt=0.4
(Full,        Reverse-Sweep) bat=0.5  wkt=1.6
```

**Off Spin deliveries:**
```
(Off Break,   Drive)         bat=0.8  wkt=1.4
(Off Break,   Pull)          bat=0.6  wkt=1.4
(Off Break,   Cut)           bat=0.7  wkt=1.3
(Off Break,   Sweep)         bat=1.7  wkt=0.5
(Off Break,   Lofted)        bat=1.3  wkt=1.2
(Off Break,   Flick)         bat=1.1  wkt=0.9
(Off Break,   Defend)        bat=0.4  wkt=0.6
(Off Break,   Reverse-Sweep) bat=1.4  wkt=0.7

(Doosra,      Drive)         bat=0.7  wkt=1.5
(Doosra,      Pull)          bat=0.6  wkt=1.5
(Doosra,      Cut)           bat=0.7  wkt=1.4
(Doosra,      Sweep)         bat=0.5  wkt=2.0
(Doosra,      Lofted)        bat=1.0  wkt=1.4
(Doosra,      Flick)         bat=0.8  wkt=1.3
(Doosra,      Defend)        bat=0.5  wkt=0.8
(Doosra,      Reverse-Sweep) bat=1.5  wkt=0.8

(Carrom Ball, Drive)         bat=0.8  wkt=1.3
(Carrom Ball, Pull)          bat=0.7  wkt=1.3
(Carrom Ball, Cut)           bat=0.9  wkt=1.2
(Carrom Ball, Sweep)         bat=0.9  wkt=1.3
(Carrom Ball, Lofted)        bat=1.1  wkt=1.3
(Carrom Ball, Flick)         bat=1.0  wkt=1.0
(Carrom Ball, Defend)        bat=0.4  wkt=0.7
(Carrom Ball, Reverse-Sweep) bat=1.1  wkt=1.2

(Arm Ball,    Drive)         bat=1.2  wkt=0.9
(Arm Ball,    Pull)          bat=0.7  wkt=1.3
(Arm Ball,    Cut)           bat=0.8  wkt=1.2
(Arm Ball,    Sweep)         bat=0.6  wkt=1.5
(Arm Ball,    Lofted)        bat=1.2  wkt=1.2
(Arm Ball,    Flick)         bat=1.1  wkt=0.9
(Arm Ball,    Defend)        bat=0.4  wkt=0.6
(Arm Ball,    Reverse-Sweep) bat=0.7  wkt=1.5

(Top Spin,    Drive)         bat=0.7  wkt=1.4
(Top Spin,    Pull)          bat=0.7  wkt=1.3
(Top Spin,    Cut)           bat=0.7  wkt=1.3
(Top Spin,    Sweep)         bat=0.8  wkt=1.3
(Top Spin,    Lofted)        bat=0.9  wkt=1.5
(Top Spin,    Flick)         bat=0.9  wkt=1.1
(Top Spin,    Defend)        bat=0.5  wkt=0.7
(Top Spin,    Reverse-Sweep) bat=1.0  wkt=1.3
```

**Leg Spin deliveries:**
```
(Drift Ball,  Drive)         bat=0.9  wkt=1.1
(Drift Ball,  Pull)          bat=0.7  wkt=1.2
(Drift Ball,  Cut)           bat=0.8  wkt=1.2
(Drift Ball,  Sweep)         bat=1.2  wkt=0.9
(Drift Ball,  Lofted)        bat=1.0  wkt=1.2
(Drift Ball,  Flick)         bat=1.1  wkt=0.9
(Drift Ball,  Defend)        bat=0.4  wkt=0.7
(Drift Ball,  Reverse-Sweep) bat=0.8  wkt=1.4

(Leg Break,   Drive)         bat=0.7  wkt=1.4
(Leg Break,   Pull)          bat=0.6  wkt=1.4
(Leg Break,   Cut)           bat=1.4  wkt=0.7
(Leg Break,   Sweep)         bat=0.7  wkt=1.4
(Leg Break,   Lofted)        bat=1.1  wkt=1.3
(Leg Break,   Flick)         bat=0.8  wkt=1.2
(Leg Break,   Defend)        bat=0.4  wkt=0.7
(Leg Break,   Reverse-Sweep) bat=0.8  wkt=1.5

(Googly,      Drive)         bat=0.6  wkt=1.8
(Googly,      Pull)          bat=0.6  wkt=1.6
(Googly,      Cut)           bat=0.7  wkt=1.5
(Googly,      Sweep)         bat=0.5  wkt=2.1
(Googly,      Lofted)        bat=0.9  wkt=1.6
(Googly,      Flick)         bat=0.7  wkt=1.5
(Googly,      Defend)        bat=0.5  wkt=0.8
(Googly,      Reverse-Sweep) bat=1.7  wkt=0.6

(Flipper,     Drive)         bat=0.7  wkt=1.6
(Flipper,     Pull)          bat=0.5  wkt=1.8
(Flipper,     Cut)           bat=0.6  wkt=1.5
(Flipper,     Sweep)         bat=0.5  wkt=2.0
(Flipper,     Lofted)        bat=0.6  wkt=1.8
(Flipper,     Flick)         bat=0.7  wkt=1.4
(Flipper,     Defend)        bat=0.5  wkt=0.9
(Flipper,     Reverse-Sweep) bat=0.7  wkt=1.7

(Top Spinner, Drive)         bat=0.7  wkt=1.5
(Top Spinner, Pull)          bat=0.7  wkt=1.4
(Top Spinner, Cut)           bat=0.8  wkt=1.3
(Top Spinner, Sweep)         bat=0.8  wkt=1.4
(Top Spinner, Lofted)        bat=0.9  wkt=1.5
(Top Spinner, Flick)         bat=0.9  wkt=1.2
(Top Spinner, Defend)        bat=0.5  wkt=0.8
(Top Spinner, Reverse-Sweep) bat=1.0  wkt=1.4

(Slider,      Drive)         bat=0.9  wkt=1.2
(Slider,      Pull)          bat=0.7  wkt=1.3
(Slider,      Cut)           bat=0.8  wkt=1.2
(Slider,      Sweep)         bat=1.4  wkt=0.7
(Slider,      Lofted)        bat=1.0  wkt=1.2
(Slider,      Flick)         bat=1.1  wkt=0.9
(Slider,      Defend)        bat=0.4  wkt=0.7
(Slider,      Reverse-Sweep) bat=0.9  wkt=1.3
```

### `calculate_outcome(delivery, shot, bowler_ovr, batsman_ovr)`

```python
m = MATCHUP_MATRIX.get((delivery, shot), {"bat": 1.0, "wkt": 1.0})
ovr_diff = bowler_ovr - batsman_ovr
ovr_factor = ovr_diff / 100.0

# Copy base weights
w = dict(BASE_WEIGHTS)
for k in ("1", "2", "3", "4", "6"):
    w[k] = max(0.5, w[k] * m["bat"] * (1 - ovr_factor * 0.25))
w["W"] = max(0.5, w["W"] * m["wkt"] * (1 + ovr_factor * 0.5))
w["0"] = max(1, w["0"] * (1 + ovr_factor * 0.2))

# Weighted random choice
outcome = random.choices(list(w.keys()), weights=list(w.values()), k=1)[0]
is_extra = outcome in ("Wd", "NB")
return outcome, is_extra
```

Outcome strings: `"0"`, `"1"`, `"2"`, `"3"`, `"4"`, `"6"`, `"W"`, `"Wd"`, `"NB"`.

---

## 6. `commentary.py` — Ball Commentary

### Wicket texts by delivery type (pick random from list):
```
Fast:         "What a delivery! Nips off the seam and crashes into the stumps!"
              "Brilliant seam movement! The stumps are shattered!"
              "Thunderbolt! Too quick to handle!"
Swing:        "The ball swings late and clips the off stump! Magnificently bowled!"
              "Swings back in sharply — trapped plumb in front! LBW!"
              "Reverse swing at its finest! He had no idea!"
Yorker:       "PERFECT YORKER! Slides under the bat and uproots the stumps!"
              "Nailed it! The full delivery crashes into the base of middle stump!"
              "That is absolutely unplayable. Batsman had no answer to that yorker!"
Bouncer:      "Fended it straight to leg gully! What a catch!"
              "Gloved it through to the keeper! Brilliant bumper plan executed!"
              "Top-edged the pull! Skied to the fielder at deep square!"
Good Length:  "Nips back off the pitch and traps him plumb LBW!"
              "Good length and some late movement — caught at slip!"
              "Straightened enough to beat the bat and clip the off stump!"
Full:         "Overpitched but wicket-to-wicket — LBW! Umpire has no hesitation!"
              "Driven hard straight back — caught and bowled!"
Leg Break:    "What a beauty! Leg-spin spins sharply and sends the stumps flying!"
              "Pitched on leg, hit the top of off stump — unplayable!"
              "Ripped through the gate! The batsman had no clue!"
Googly:       "Deceived by the googly! Completely bamboozled! Beaten on the inside edge!"
              "The googly did the damage! He had no idea which way it would turn!"
              "Sensational! Googly beats the outside edge — bowled him!"
Flipper:      "The flipper skids on low and the batsman is LBW! Trapped!"
              "Low and fast — the flipper crashes into the stumps!"
Off Break:    "Turned sharply and clipped the off stump — beautiful!"
              "Big off-break and it's through the gate! What a delivery!"
              "Spun past the outside edge and shattered the stumps!"
Doosra:       "The doosra went the other way! He had absolutely no clue!"
              "Doosra magic! Went through the gate and hit the top of off stump!"
Carrom Ball:  "Carrom ball turns sharply! Catches the outside edge to slip!"
              "Flicked off the fingers — goes the wrong way and bowls him!"
Arm Ball:     "Arm ball — doesn't turn and crashes into the stumps! LBW!"
              "Went straight on! Completely deceived him — caught at short leg!"
Top Spin:     "Extra bounce from the top-spinner and he gloves it to the keeper!"
              "Dips on him late and he miscues to mid-on!"
Drift Ball:   "Drifted in and spun the other way — trapped plumb!"
              "Big drift then spin — edge to slip!"
Top Spinner:  "Skids through low and fast — LBW! Struck right in front!"
              "Deceived by the extra pace — straight back into the stumps!"
Slider:       "Doesn't turn — slides through and clips the off stump!"
              "Deceived in flight — the slider does the job!"

Generic fallback: "He's gone! Brilliant delivery beats the bat!"
                  "OUT! The bowler is absolutely pumped!"
                  "What a catch! He has to walk back!"
                  "BOWLED! Stumps all over the place!"
                  "LBW! Plumb in front! The umpire has no hesitation!"
```

### Four boundary texts (pick random):
```
"CRACKED THROUGH THE COVERS! NOBODY STOPPING THAT! FOUR!"
"DRIVEN HARD AND TRUE! FOUR ALL THE WAY!"
"PERFECTLY PLACED THROUGH MID-WICKET! FOUR!"
"TOO SHORT, TOO WIDE — PUNISHED HARD FOR FOUR!"
"RACES TO THE ROPES! BEAUTIFUL TIMING! FOUR!"
"CUT HARD AND SQUARE — SCREAMS TO THE BOUNDARY! FOUR!"
"HE'S FLICKED THAT OFF HIS HIPS! FOUR RUNS!"
```

### Delivery modifier enrichment:
- Fast bowlers (45% chance): prefix with one of `["Outswinging ", "Inswinging ", "Quick ", "Reverse swing "]` then lowercase the delivery name.
- Spin bowlers (30% chance): prefix with one of `["Dipping ", "Flighted ", "Sharp "]` then lowercase.

### `build_ball_commentary(bowler_name, bowler_ovr, delivery, speed, batsman_name, shot, outcome, bowling_type=None)`

`speed` is a **float** generated via `random.uniform(*speed_range)`.

Output format (lines joined with `\n`):
```
[If outcome=="6"]  **1️⃣0️⃣0️⃣ METRES, ROW Z, MEET THE CRICKET BALL!**   ← distance random 82-108 in number emojis
**BowlerName** : [enriched delivery] at **XX.X kmph**
**BatsmanName** [shot_verb] the [ball_description]
[If "4"]  **CRACKED THROUGH THE COVERS! NOBODY STOPPING THAT! FOUR!**
[If "W"]  **[delivery-specific wicket text]**
          **BatsmanName IS OUT** ☝️
[If "Wd"] **Wide!** The ball drifts past the batsman. Extra run awarded.
[If "NB"] **No Ball!** Overstepped! Free hit coming up!
[If "NB+1"] **No Ball!** Overstepped — and the batsman picks up a run too. Two extras!
```

Number emoji helper — convert integer to digit emojis: 0️⃣1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣

---

## 7. `embeds.py` — Discord Embeds

### Playing XI embed (`build_playing_xi_embed(team)`)

Title: team name. Description: `OVR:**90** • CHEM:**94**`

Column header field (zero-width space name):
```
`Card | Player             | OVR | BAT | BOWL | Country`
```

Role groups in order: Batters 🏏, WK 🧤, All-Rounders ⚡, Bowlers 🎯.
Each group shown only if it has players.

Chemistry bonus per role:
```python
def _role_bonus(chem, role):
    extras = {"Batter": 0, "WK": 1, "All-Rounder": 0, "Bowler": -1}
    return max(1, (chem // 20) + extras.get(role, 0))
```

Group label: `"Batters 🏏  +3"` (with bonus).

Each player row:
```
{card} | `{name:<16}` | {ovr} | {bat} | {bowl_or_dash:>3} | {ball_icon} | {flag}
```
- `card`: player's card emoji (🥇 or 🥈)
- Name padded to 16 chars in code block
- `bowl`: the numeric value, or ` —` if bowling_type is None
- `ball_icon`: 🔥 for Fast, 🌀 for spin, 🏏 if no bowling_type
- `flag`: COUNTRY_FLAGS lookup

Footer: `"{team_name} • Playing XI"`

### Scoreboard embed (`build_scoreboard_embed(game)`)

**Color:** green in innings 1, orange in innings 2.

**Two-line team header (embed description):**
- Innings 1: `**BattingTeam**  R/W  (X.Y/N.0)` on line 1, `**BowlingTeam**  Yet to Bat` on line 2.
- Innings 2: `**Inn1Team**  R1/W1` on line 1 (no overs, already done), `**ChasingTeam**  R2/W2  (X.Y/N.0)` on line 2. Note: after `start_second_innings()`, `bowling_user_id` = team that batted first.

Overs format: `legal_balls // 6 . legal_balls % 6 / total_overs .0`  e.g. `"4.3/20.0"`

**Batters field:**
```
BATTERS         [lots of U+3000 spaces]        R  B  SR
🔴 **StrikerName**  [U+3000 spaces]  runs  balls  sr
⬜ **NonStrikerName**  ...
```
(Use `\u3000` ideographic space for alignment in Discord monospace.)

**Partnership / rate field:**
```
P'Ship: **X**(Y)  CRR: **Z.ZZ**  Proj: **PPP**   ← innings 1
P'Ship: **X**(Y)  CRR: **Z.ZZ**  RRR: **R.RR**   ← innings 2
```

**Bowler field** (if current_bowler exists):
```
BOWLER          [spaces]           O  R  W
**BowlerName**  [spaces]  overs  runs  wickets
```

**Timeline field:** last 12 emoji joined with `  ` (two spaces), or `—` if empty.

**Footer:**
- Innings 2, runs needed > 0 and balls left > 0: `"{team} need X run(s) to win in Y ball(s)"`
- Innings 2, already won: `"🏆 {team} have won!"`
- Innings 2, other: `"Target: {target}"`
- Innings 1: `"{batting_team} chose to bat first"`

### Result embed (`build_result_embed(game)`)

Title: `"🏏 MATCH RESULT"`. Color: gold.
Description: `game.match_result()` string.
Two inline fields: inn1_team name + `"**R/W**  (N.0 ov)"`, inn2_team name + `"**R/W**"`.

**Result string logic:**
- `t2 > t1` → batting_user in innings 2 won by `(10 - wickets[1])` wickets, `(overs*6 - legal_balls[1])` balls remaining.
- `t1 > t2` → team batting first won by `(t1 - t2)` runs.
- Tie → `"🤝 Match tied! What a game!"`

---

## 8. `views.py` — Full UI Flow

`active_games: dict[int, GameState] = {}` — keyed by channel_id.

**Rule: every game phase sends a NEW message. Never edit the main scoreboard. Buttons remove themselves by calling `interaction.response.edit_message(view=None)` on the clicked message, then `interaction.followup.send(...)` for the next phase.**

### Helper: `_timeline_emoji(outcome)` → looks up TIMELINE_EMOJIS, fallback `"•"`.

### Helper: `_send_bowling_prompt(channel, game)` → sends scoreboard embed + BowlingView as new message.

### Helper: `_process_delivery(interaction, game, shot)` — core delivery handler:

```
1. Get delivery = game.pending_delivery, bowler = game.current_bowler, striker = game.striker
2. outcome, is_extra = calculate_outcome(delivery, shot, bowler["ovr"], striker["ovr"])
3. speed = random.uniform(*BALL_SPEEDS.get(delivery, (100, 130)))
4. commentary = build_ball_commentary(..., bowling_type=bowler.get("bowling_type"))
5. Update game state:
   - "W" → add_legal_ball(), add_wicket(), timeline.append(W emoji)
   - "Wd" → runs[inn-1] += 1, bowler_stats[runs] += 1, timeline.append(Wd emoji)
   - "NB" → runs[inn-1] += 1, bowler_stats[runs] += 1, timeline.append(NB emoji)
   - "NB+1" → runs += 2, bowler_stats[runs] += 2, timeline.append(NB+1 emoji)
   - else → add_legal_ball(), add_runs(int(outcome)), timeline.append(emoji)
             if runs in (1, 3): rotate_strike()
6. interaction.response.edit_message(view=None)  # remove batting buttons
7. embed = build_scoreboard_embed(game)
8. Check if innings over → _do_innings_break or result
9. Check if wicket → NextBatsmanView
10. Check if over end (not extra and current_over_balls >= 6) → NextBowlerView
11. Else → send commentary+embed, then _send_bowling_prompt
```

### Helper: `_do_innings_break(channel, game, commentary, embed)`:
```
1. game.start_second_innings()
2. bat_team = game.get_batting_team()
3. target = game.target()
4. balls_in_match = game.overs * 6
5. rrr_val = round((target / balls_in_match) * 6, 1)
6. Send commentary + embed (end of 1st innings scoreboard)
7. Send bold banner: "**⏸ Innings Break!\nTEAM REQUIRE X RUNS OFF Y BALLS (RRR: Z.Z)**"
8. Send OpenerSelectView with batting team's XI embed
```

---

### UI Classes:

**AcceptDeclineView**
- Opponent clicks Accept → edit original message (remove view), send TossView as new message.
- Opponent clicks Decline → edit message to declined, remove from active_games.

**TossView**
- Challenger clicks Head or Tail button (with custom emoji).
- Coin flip: `random.choice(["Head", "Tail"])`.
- Edit message to show result emoji + winner, send BatBowlView as new message.

**BatBowlView**
- Toss winner clicks 🏏 Bat or 🎯 Bowl.
- Sets batting_user_id / bowling_user_id.
- Edit message to confirm choice, send OpenerSelectView with batting team's XI embed.

**OpenerSelectView**
- Batting user selects exactly 2 players from dropdown (min_values=2, max_values=2).
- Edit message to "Player1 & Player2 selected — who takes strike?", replace view with StrikerDesignateView.

**StrikerDesignateView**
- Two buttons, one per opener.
- Batting user clicks the striker.
- Sets game.striker, game.non_striker, inits both batsman_stats.
- Edit message to "🔴 **Striker** on strike · **NonStriker** at non-striker end", view=None.
- Send announcement: `"**Striker** (OVR) and **NonStriker** (OVR) are opening the batting"`
- Send BowlerSelectView with bowling team's XI embed.

**BowlerSelectView**
- Bowling user selects from dropdown (bowlers with bowling_type).
- Sets game.current_bowler, inits bowler_stats.
- Edit message to "🎯 **BowlerName** will bowl.", view=None.
- Send announcement: `"**BowlerName** (OVR) comes into the attack"`
- Send scoreboard embed + BowlingView.

**BowlingView**
- Delivery buttons dynamically generated from bowler's bowling_type:
  - Fast → 6 buttons (Fast, Swing, Yorker, Bouncer, Good Length, Full)
  - Off Spin → 5 buttons (Off Break, Doosra, Carrom Ball, Arm Ball, Top Spin)
  - Leg Spin → 6 buttons (Drift Ball, Leg Break, Googly, Flipper, Top Spinner, Slider)
- Bowling user clicks a delivery.
- Sets game.pending_delivery, game.phase = "bat_select".
- Edit message to: `"**BowlerName** : **Delivery**"`, view=None.
- Send BattingView: `"🏏 @batting_user — **StrikerName**, play your shot:"`

**BattingView**
- 8 shot buttons with styles: Drive (green), Pull (green), Cut (green), Sweep (secondary), Lofted (danger), Flick (green), Defend (secondary), Reverse-Sweep (danger).
- Batting user clicks a shot → `_process_delivery(interaction, game, shot)`.

**NextBatsmanView** (wicket fallen)
- Batting user selects next batsman from `game.get_available_batsmen()`.
- Sets game.striker, inits batsman_stats.
- Edit message to "🏏 **Name** selected.", view=None.
- Send announcement: `"**Name** (OVR) comes to the crease"`
- If current_over_balls >= 6: end_over(), show NextBowlerView.
- Else: `_send_bowling_prompt`.

**NextBowlerView** (end of over)
- Bowling user selects from `game.get_available_bowlers()`.
- Dropdown shows `name (BOWL:X)` label, `bowling_type | X.Y ov bowled` description.
- Sets game.current_bowler, inits bowler_stats.
- Edit message to "🎯 **Name** starts a new over.", view=None.
- Send announcement: `"**Name** (OVR) comes into the attack"`
- `_send_bowling_prompt`.

---

## 9. `main.py` — Commands

**Command group:** `!cs` (prefix `!`)

| Command | Description |
|---|---|
| `!cs start @user [overs]` | Challenge @user (default 20 overs, range 1-50). Cannot challenge bots or self. One match per channel. Creates GameState, assigns two teams randomly from SAMPLE_TEAMS, sends both XI embeds + AcceptDeclineView. |
| `!cs cancel` | Either participant can cancel. Removes from active_games. |
| `!cs score` | Sends current scoreboard embed (any time during match). |
| `!cs xi` | Sends the caller's Playing XI embed. |

`on_ready`: print login info, call `await sync_emojis(bot)`.

Bot requires: `Message Content Intent` enabled, `Send Messages`, `Embed Links`, `Read Message History` permissions.

Team assignment: `random.shuffle(list(SAMPLE_TEAMS.keys()))` and assign the first two shuffled teams.

---

## 10. Cricket Rules Implemented

- **Strike rotation:** striker and non-striker swap on 1 or 3 runs scored; also swap at end of every over.
- **Wides / No-balls:** do NOT count as legal deliveries; runs added directly (wide = +1, NB = +1, NB+1 = +2).
- **Bowler limits:** max 1/5th of total overs per bowler (`max(1, overs//5)`), no consecutive overs.
- **Innings end conditions:** 10 wickets, or overs complete, or target reached (innings 2 only).
- **Target:** first innings runs + 1.
- **All-out:** if 10 wickets fall before overs are complete, innings ends.
- **Tie:** if both teams score equal runs, result is a tie.
- **Toss:** challenger calls (Head/Tail), winner chooses Bat or Bowl.
- **Phase tracking:** bot tracks the game phase as a string so stale button clicks can be rejected gracefully (check `interaction.user.id` before every action).

---

## 11. Discord Bot Requirements

- Python 3.11+
- `discord.py >= 2.0` (for `discord.ui.View`, Application Emojis, `fetch_application_emojis`, `create_application_emoji`)
- `aiohttp` (for CDN image download in emoji_sync)
- Bot token in env var `DISCORD_BOT_TOKEN`
- Intents: `default()` + `message_content = True`
- All views have `timeout=120` (2 minutes per interaction)
- Ephemeral error messages for wrong-user interactions (e.g. "Only the batting team selects!")
- `sys.path.insert(0, os.path.dirname(__file__))` so modules import cleanly

---

## 12. Announcement Messages Summary (new message in channel)

| Trigger | Message |
|---|---|
| Striker designated | `**Striker** (OVR) and **NonStriker** (OVR) are opening the batting` |
| Bowler selected (BowlerSelectView or NextBowlerView) | `**BowlerName** (OVR) comes into the attack` |
| New batsman after wicket | `**BatsmanName** (OVR) comes to the crease` |
| Innings break | `**⏸ Innings Break!\nTEAM REQUIRE X RUNS OFF Y BALLS (RRR: Z.Z)**` |

---

## 13. Full Game Flow Summary

```
!cs start @opponent [overs]
  → Both XI embeds + AcceptDeclineView

Opponent accepts
  → TossView (Head/Tail buttons with custom emojis)

Challenger calls toss
  → BatBowlView (Bat / Bowl) for toss winner

Toss winner chooses
  → OpenerSelectView (multi-select dropdown, min=2 max=2) + batting XI embed

Batting user picks 2 openers
  → StrikerDesignateView (2 buttons: which player faces first)

Batting user designates striker
  → Announcement "X and Y are opening the batting"
  → BowlerSelectView + bowling XI embed

Bowling user selects bowler
  → Announcement "Bowler comes into the attack"
  → Scoreboard embed + BowlingView (delivery buttons)

Bowling user picks delivery
  → Edit to "BowlerName : Delivery", send BattingView

Batting user plays shot
  → _process_delivery: calculate outcome, build commentary, update state
  → Send commentary + scoreboard embed

  ┌── Wicket? → NextBatsmanView; after selection → "X comes to the crease"
  │                └── Over also ended? → NextBowlerView
  │
  ├── Over end? → NextBowlerView; after selection → "X comes into the attack"
  │
  └── Continue → BowlingView (next delivery)

Innings 1 ends (10 wickets or overs complete)
  → _do_innings_break:
      Send final scoreboard
      Send "⏸ Innings Break! TEAM REQUIRE X RUNS OFF Y BALLS (RRR: Z.Z)"
      Send OpenerSelectView for chasing team

Innings 2 plays out the same way

Innings 2 ends (target reached, 10 wickets, or overs)
  → build_result_embed, remove from active_games
```

---

This prompt contains every rule, every data value, every embed format, every commentary line, every UI class and flow. Implement all 7 files exactly as described and the bot will be fully functional and identical to the original.
