
import random

MATCHUP_MATRIX = {
    ("Fast",        "Drive"):        {"bat": 1.2, "wkt": 0.9},
    ("Fast",        "Pull"):         {"bat": 0.8, "wkt": 1.3},
    ("Fast",        "Cut"):          {"bat": 1.0, "wkt": 1.0},
    ("Fast",        "Sweep"):        {"bat": 0.5, "wkt": 1.6},
    ("Fast",        "Lofted"):       {"bat": 1.3, "wkt": 1.4},
    ("Fast",        "Flick"):        {"bat": 1.1, "wkt": 0.9},
    ("Fast",        "Defend"):       {"bat": 0.3, "wkt": 0.5},
    ("Fast",        "Reverse-Sweep"):{"bat": 0.7, "wkt": 1.6},

    ("Swing",       "Drive"):        {"bat": 0.7, "wkt": 1.6},
    ("Swing",       "Pull"):         {"bat": 0.7, "wkt": 1.3},
    ("Swing",       "Cut"):          {"bat": 0.8, "wkt": 1.4},
    ("Swing",       "Sweep"):        {"bat": 0.6, "wkt": 1.4},
    ("Swing",       "Lofted"):       {"bat": 0.9, "wkt": 1.8},
    ("Swing",       "Flick"):        {"bat": 1.2, "wkt": 0.8},
    ("Swing",       "Defend"):       {"bat": 0.4, "wkt": 0.6},
    ("Swing",       "Reverse-Sweep"):{"bat": 0.5, "wkt": 1.8},

    ("Yorker",      "Drive"):        {"bat": 0.5, "wkt": 2.0},
    ("Yorker",      "Pull"):         {"bat": 0.3, "wkt": 2.5},
    ("Yorker",      "Cut"):          {"bat": 0.4, "wkt": 2.0},
    ("Yorker",      "Sweep"):        {"bat": 0.4, "wkt": 1.8},
    ("Yorker",      "Lofted"):       {"bat": 0.3, "wkt": 2.5},
    ("Yorker",      "Flick"):        {"bat": 0.9, "wkt": 1.2},
    ("Yorker",      "Defend"):       {"bat": 0.6, "wkt": 0.7},
    ("Yorker",      "Reverse-Sweep"):{"bat": 0.5, "wkt": 2.0},

    ("Bouncer",     "Drive"):        {"bat": 0.3, "wkt": 2.5},
    ("Bouncer",     "Pull"):         {"bat": 1.9, "wkt": 0.6},
    ("Bouncer",     "Cut"):          {"bat": 1.2, "wkt": 0.8},
    ("Bouncer",     "Sweep"):        {"bat": 0.4, "wkt": 2.0},
    ("Bouncer",     "Lofted"):       {"bat": 0.7, "wkt": 1.6},
    ("Bouncer",     "Flick"):        {"bat": 0.4, "wkt": 2.0},
    ("Bouncer",     "Defend"):       {"bat": 0.2, "wkt": 1.2},
    ("Bouncer",     "Reverse-Sweep"):{"bat": 0.3, "wkt": 2.5},

    ("Good Length", "Drive"):        {"bat": 1.0, "wkt": 1.0},
    ("Good Length", "Pull"):         {"bat": 0.7, "wkt": 1.2},
    ("Good Length", "Cut"):          {"bat": 0.8, "wkt": 1.1},
    ("Good Length", "Sweep"):        {"bat": 0.7, "wkt": 1.2},
    ("Good Length", "Lofted"):       {"bat": 1.2, "wkt": 1.3},
    ("Good Length", "Flick"):        {"bat": 0.9, "wkt": 1.0},
    ("Good Length", "Defend"):       {"bat": 0.4, "wkt": 0.5},
    ("Good Length", "Reverse-Sweep"):{"bat": 0.6, "wkt": 1.5},

    ("Full",        "Drive"):        {"bat": 1.9, "wkt": 0.5},
    ("Full",        "Pull"):         {"bat": 0.6, "wkt": 1.4},
    ("Full",        "Cut"):          {"bat": 0.8, "wkt": 1.1},
    ("Full",        "Sweep"):        {"bat": 0.8, "wkt": 1.1},
    ("Full",        "Lofted"):       {"bat": 1.8, "wkt": 1.0},
    ("Full",        "Flick"):        {"bat": 1.7, "wkt": 0.6},
    ("Full",        "Defend"):       {"bat": 0.3, "wkt": 0.4},
    ("Full",        "Reverse-Sweep"):{"bat": 0.5, "wkt": 1.6},

    ("Off Break",   "Drive"):        {"bat": 0.8, "wkt": 1.4},
    ("Off Break",   "Pull"):         {"bat": 0.6, "wkt": 1.4},
    ("Off Break",   "Cut"):          {"bat": 0.7, "wkt": 1.3},
    ("Off Break",   "Sweep"):        {"bat": 1.7, "wkt": 0.5},
    ("Off Break",   "Lofted"):       {"bat": 1.3, "wkt": 1.2},
    ("Off Break",   "Flick"):        {"bat": 1.1, "wkt": 0.9},
    ("Off Break",   "Defend"):       {"bat": 0.4, "wkt": 0.6},
    ("Off Break",   "Reverse-Sweep"):{"bat": 1.4, "wkt": 0.7},

    ("Doosra",      "Drive"):        {"bat": 0.7, "wkt": 1.5},
    ("Doosra",      "Pull"):         {"bat": 0.6, "wkt": 1.5},
    ("Doosra",      "Cut"):          {"bat": 0.7, "wkt": 1.4},
    ("Doosra",      "Sweep"):        {"bat": 0.5, "wkt": 2.0},
    ("Doosra",      "Lofted"):       {"bat": 1.0, "wkt": 1.4},
    ("Doosra",      "Flick"):        {"bat": 0.8, "wkt": 1.3},
    ("Doosra",      "Defend"):       {"bat": 0.5, "wkt": 0.8},
    ("Doosra",      "Reverse-Sweep"):{"bat": 1.5, "wkt": 0.8},

    ("Carrom Ball", "Drive"):        {"bat": 0.8, "wkt": 1.3},
    ("Carrom Ball", "Pull"):         {"bat": 0.7, "wkt": 1.3},
    ("Carrom Ball", "Cut"):          {"bat": 0.9, "wkt": 1.2},
    ("Carrom Ball", "Sweep"):        {"bat": 0.9, "wkt": 1.3},
    ("Carrom Ball", "Lofted"):       {"bat": 1.1, "wkt": 1.3},
    ("Carrom Ball", "Flick"):        {"bat": 1.0, "wkt": 1.0},
    ("Carrom Ball", "Defend"):       {"bat": 0.4, "wkt": 0.7},
    ("Carrom Ball", "Reverse-Sweep"):{"bat": 1.1, "wkt": 1.2},

    ("Arm Ball",    "Drive"):        {"bat": 1.2, "wkt": 0.9},
    ("Arm Ball",    "Pull"):         {"bat": 0.7, "wkt": 1.3},
    ("Arm Ball",    "Cut"):          {"bat": 0.8, "wkt": 1.2},
    ("Arm Ball",    "Sweep"):        {"bat": 0.6, "wkt": 1.5},
    ("Arm Ball",    "Lofted"):       {"bat": 1.2, "wkt": 1.2},
    ("Arm Ball",    "Flick"):        {"bat": 1.1, "wkt": 0.9},
    ("Arm Ball",    "Defend"):       {"bat": 0.4, "wkt": 0.6},
    ("Arm Ball",    "Reverse-Sweep"):{"bat": 0.7, "wkt": 1.5},

    ("Top Spin",    "Drive"):        {"bat": 0.7, "wkt": 1.4},
    ("Top Spin",    "Pull"):         {"bat": 0.7, "wkt": 1.3},
    ("Top Spin",    "Cut"):          {"bat": 0.7, "wkt": 1.3},
    ("Top Spin",    "Sweep"):        {"bat": 0.8, "wkt": 1.3},
    ("Top Spin",    "Lofted"):       {"bat": 0.9, "wkt": 1.5},
    ("Top Spin",    "Flick"):        {"bat": 0.9, "wkt": 1.1},
    ("Top Spin",    "Defend"):       {"bat": 0.5, "wkt": 0.7},
    ("Top Spin",    "Reverse-Sweep"):{"bat": 1.0, "wkt": 1.3},

    ("Drift Ball",  "Drive"):        {"bat": 0.9, "wkt": 1.1},
    ("Drift Ball",  "Pull"):         {"bat": 0.7, "wkt": 1.2},
    ("Drift Ball",  "Cut"):          {"bat": 0.8, "wkt": 1.2},
    ("Drift Ball",  "Sweep"):        {"bat": 1.2, "wkt": 0.9},
    ("Drift Ball",  "Lofted"):       {"bat": 1.0, "wkt": 1.2},
    ("Drift Ball",  "Flick"):        {"bat": 1.1, "wkt": 0.9},
    ("Drift Ball",  "Defend"):       {"bat": 0.4, "wkt": 0.7},
    ("Drift Ball",  "Reverse-Sweep"):{"bat": 0.8, "wkt": 1.4},

    ("Leg Break",   "Drive"):        {"bat": 0.7, "wkt": 1.4},
    ("Leg Break",   "Pull"):         {"bat": 0.6, "wkt": 1.4},
    ("Leg Break",   "Cut"):          {"bat": 1.4, "wkt": 0.7},
    ("Leg Break",   "Sweep"):        {"bat": 0.7, "wkt": 1.4},
    ("Leg Break",   "Lofted"):       {"bat": 1.1, "wkt": 1.3},
    ("Leg Break",   "Flick"):        {"bat": 0.8, "wkt": 1.2},
    ("Leg Break",   "Defend"):       {"bat": 0.4, "wkt": 0.7},
    ("Leg Break",   "Reverse-Sweep"):{"bat": 0.8, "wkt": 1.5},

    ("Googly",      "Drive"):        {"bat": 0.6, "wkt": 1.8},
    ("Googly",      "Pull"):         {"bat": 0.6, "wkt": 1.6},
    ("Googly",      "Cut"):          {"bat": 0.7, "wkt": 1.5},
    ("Googly",      "Sweep"):        {"bat": 0.5, "wkt": 2.1},
    ("Googly",      "Lofted"):       {"bat": 0.9, "wkt": 1.6},
    ("Googly",      "Flick"):        {"bat": 0.7, "wkt": 1.5},
    ("Googly",      "Defend"):       {"bat": 0.5, "wkt": 0.8},
    ("Googly",      "Reverse-Sweep"):{"bat": 1.7, "wkt": 0.6},

    ("Flipper",     "Drive"):        {"bat": 0.7, "wkt": 1.6},
    ("Flipper",     "Pull"):         {"bat": 0.5, "wkt": 1.8},
    ("Flipper",     "Cut"):          {"bat": 0.6, "wkt": 1.5},
    ("Flipper",     "Sweep"):        {"bat": 0.5, "wkt": 2.0},
    ("Flipper",     "Lofted"):       {"bat": 0.6, "wkt": 1.8},
    ("Flipper",     "Flick"):        {"bat": 0.7, "wkt": 1.4},
    ("Flipper",     "Defend"):       {"bat": 0.5, "wkt": 0.9},
    ("Flipper",     "Reverse-Sweep"):{"bat": 0.7, "wkt": 1.7},

    ("Top Spinner", "Drive"):        {"bat": 0.7, "wkt": 1.5},
    ("Top Spinner", "Pull"):         {"bat": 0.7, "wkt": 1.4},
    ("Top Spinner", "Cut"):          {"bat": 0.8, "wkt": 1.3},
    ("Top Spinner", "Sweep"):        {"bat": 0.8, "wkt": 1.4},
    ("Top Spinner", "Lofted"):       {"bat": 0.9, "wkt": 1.5},
    ("Top Spinner", "Flick"):        {"bat": 0.9, "wkt": 1.2},
    ("Top Spinner", "Defend"):       {"bat": 0.5, "wkt": 0.8},
    ("Top Spinner", "Reverse-Sweep"):{"bat": 1.0, "wkt": 1.4},

    ("Slider",      "Drive"):        {"bat": 0.9, "wkt": 1.2},
    ("Slider",      "Pull"):         {"bat": 0.7, "wkt": 1.3},
    ("Slider",      "Cut"):          {"bat": 0.8, "wkt": 1.2},
    ("Slider",      "Sweep"):        {"bat": 1.4, "wkt": 0.7},
    ("Slider",      "Lofted"):       {"bat": 1.0, "wkt": 1.2},
    ("Slider",      "Flick"):        {"bat": 1.1, "wkt": 0.9},
    ("Slider",      "Defend"):       {"bat": 0.4, "wkt": 0.7},
    ("Slider",      "Reverse-Sweep"):{"bat": 0.9, "wkt": 1.3},
}

BASE_WEIGHTS = {
    "0":  35,
    "1":  22,
    "2":  10,
    "3":   3,
    "4":  11,
    "6":   5,
    "W":   8,
    "Wd":  4,
    "NB":  2,
}


def calculate_outcome(delivery: str, shot: str, bowler_ovr: int, batsman_ovr: int):
    m = MATCHUP_MATRIX.get((delivery, shot), {"bat": 1.0, "wkt": 1.0})
    bat_m = m["bat"]
    wkt_m = m["wkt"]

    ovr_diff = bowler_ovr - batsman_ovr
    ovr_factor = ovr_diff / 100.0

    w = dict(BASE_WEIGHTS)
    for k in ("1", "2", "3", "4", "6"):
        w[k] = max(0.5, w[k] * bat_m * (1 - ovr_factor * 0.25))
    w["W"] = max(0.5, w["W"] * wkt_m * (1 + ovr_factor * 0.5))
    w["0"] = max(1, w["0"] * (1 + ovr_factor * 0.2))

    outcomes = list(w.keys())
    probs = [w[k] for k in outcomes]
    total = sum(probs)
    probs = [p / total for p in probs]

    outcome = random.choices(outcomes, weights=probs, k=1)[0]
    is_extra = outcome in ("Wd", "NB")
    return outcome, is_extra
