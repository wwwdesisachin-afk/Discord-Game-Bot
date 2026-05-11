
import random


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _num_emoji(n: int) -> str:
    digits = {
        "0": "0️⃣", "1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣",
        "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣",
    }
    return "".join(digits[d] for d in str(n))


# ---------------------------------------------------------------------------
# Wicket text by delivery type
# ---------------------------------------------------------------------------

_WICKET_BY_DELIVERY = {
    "Fast":        [
        "What a delivery! Nips off the seam and crashes into the stumps!",
        "Brilliant seam movement! The stumps are shattered!",
        "Thunderbolt! Too quick to handle!",
    ],
    "Swing":       [
        "The ball swings late and clips the off stump! Magnificently bowled!",
        "Swings back in sharply — trapped plumb in front! LBW!",
        "Reverse swing at its finest! He had no idea!",
    ],
    "Yorker":      [
        "PERFECT YORKER! Slides under the bat and uproots the stumps!",
        "Nailed it! The full delivery crashes into the base of middle stump!",
        "That is absolutely unplayable. Batsman had no answer to that yorker!",
    ],
    "Bouncer":     [
        "Fended it straight to leg gully! What a catch!",
        "Gloved it through to the keeper! Brilliant bumper plan executed!",
        "Top-edged the pull! Skied to the fielder at deep square!",
    ],
    "Good Length": [
        "Nips back off the pitch and traps him plumb LBW!",
        "Good length and some late movement — caught at slip!",
        "Straightened enough to beat the bat and clip the off stump!",
    ],
    "Full":        [
        "Overpitched but wicket-to-wicket — LBW! Umpire has no hesitation!",
        "Driven hard straight back — caught and bowled!",
    ],
    "Leg Break":   [
        "What a beauty! Leg-spin spins sharply and sends the stumps flying!",
        "Pitched on leg, hit the top of off stump — unplayable!",
        "Ripped through the gate! The batsman had no clue!",
    ],
    "Googly":      [
        "Deceived by the googly! Completely bamboozled! Beaten on the inside edge!",
        "The googly did the damage! He had no idea which way it would turn!",
        "Sensational! Googly beats the outside edge — bowled him!",
    ],
    "Flipper":     [
        "The flipper skids on low and the batsman is LBW! Trapped!",
        "Low and fast — the flipper crashes into the stumps!",
    ],
    "Off Break":   [
        "Turned sharply and clipped the off stump — beautiful!",
        "Big off-break and it's through the gate! What a delivery!",
        "Spun past the outside edge and shattered the stumps!",
    ],
    "Doosra":      [
        "The doosra went the other way! He had absolutely no clue!",
        "Doosra magic! Went through the gate and hit the top of off stump!",
    ],
    "Carrom Ball": [
        "Carrom ball turns sharply! Catches the outside edge to slip!",
        "Flicked off the fingers — goes the wrong way and bowls him!",
    ],
    "Arm Ball":    [
        "Arm ball — doesn't turn and crashes into the stumps! LBW!",
        "Went straight on! Completely deceived him — caught at short leg!",
    ],
    "Top Spin":    [
        "Extra bounce from the top-spinner and he gloves it to the keeper!",
        "Dips on him late and he miscues to mid-on!",
    ],
    "Drift Ball":  [
        "Drifted in and spun the other way — trapped plumb!",
        "Big drift then spin — edge to slip!",
    ],
    "Top Spinner": [
        "Skids through low and fast — LBW! Struck right in front!",
        "Deceived by the extra pace — straight back into the stumps!",
    ],
    "Slider":      [
        "Doesn't turn — slides through and clips the off stump!",
        "Deceived in flight — the slider does the job!",
    ],
}

_GENERIC_WICKET = [
    "He's gone! Brilliant delivery beats the bat!",
    "OUT! The bowler is absolutely pumped!",
    "What a catch! He has to walk back!",
    "BOWLED! Stumps all over the place!",
    "LBW! Plumb in front! The umpire has no hesitation!",
]

_BOUNDARY_4 = [
    "CRACKED THROUGH THE COVERS! NOBODY STOPPING THAT! FOUR!",
    "DRIVEN HARD AND TRUE! FOUR ALL THE WAY!",
    "PERFECTLY PLACED THROUGH MID-WICKET! FOUR!",
    "TOO SHORT, TOO WIDE — PUNISHED HARD FOR FOUR!",
    "RACES TO THE ROPES! BEAUTIFUL TIMING! FOUR!",
    "CUT HARD AND SQUARE — SCREAMS TO THE BOUNDARY! FOUR!",
    "HE'S FLICKED THAT OFF HIS HIPS! FOUR RUNS!",
]

# Delivery modifiers to enrich commentary
_FAST_MODS = ["", "Outswinging ", "Inswinging ", "Quick ", "Reverse swing "]
_SPIN_MODS = ["", "Dipping ", "Flighted ", "Sharp ", ""]


def _wicket_text(delivery: str) -> str:
    options = _WICKET_BY_DELIVERY.get(delivery, _GENERIC_WICKET)
    return random.choice(options)


def _enrich_delivery(delivery: str, bowling_type: str | None) -> str:
    if bowling_type == "Fast" and random.random() < 0.45:
        mod = random.choice(_FAST_MODS[1:])
        return mod + delivery.lower()
    if bowling_type in ("Off Spin", "Leg Spin") and random.random() < 0.3:
        mod = random.choice(_SPIN_MODS[1:])
        if mod:
            return mod + delivery.lower()
    return delivery


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_ball_commentary(
    bowler_name: str, bowler_ovr: int,
    delivery: str, speed: float,
    batsman_name: str, shot: str,
    outcome: str,
    bowling_type: str | None = None,
) -> str:
    from data import BALL_DESCRIPTIONS, SHOT_DESCRIPTIONS

    ball_desc = BALL_DESCRIPTIONS.get(delivery, delivery.lower())
    shot_desc = SHOT_DESCRIPTIONS.get(shot, shot.lower())
    enriched = _enrich_delivery(delivery, bowling_type)

    delivery_line = f"**{bowler_name}** : {enriched} at **{speed:.1f} kmph**"
    shot_line = f"**{batsman_name}** {shot_desc} the {ball_desc}"

    lines = []

    # Six: big text BEFORE the delivery info
    if outcome == "6":
        dist = random.randint(82, 108)
        lines.append(f"**{_num_emoji(dist)} METRES, ROW Z, MEET THE CRICKET BALL!**")

    lines.append(delivery_line)
    lines.append(shot_line)

    # Four / Wicket / extras after the shot line
    if outcome == "4":
        lines.append(f"**{random.choice(_BOUNDARY_4)}**")
    elif outcome == "W":
        lines.append(f"**{_wicket_text(delivery)}**")
        lines.append(f"**{batsman_name} IS OUT** ☝️")
    elif outcome == "Wd":
        lines.append("**Wide!** The ball drifts past the batsman. Extra run awarded.")
    elif outcome == "NB":
        lines.append("**No Ball!** Overstepped! Free hit coming up!")
    elif outcome == "NB+1":
        lines.append("**No Ball!** Overstepped — and the batsman picks up a run too. Two extras!")

    return "\n".join(lines)
