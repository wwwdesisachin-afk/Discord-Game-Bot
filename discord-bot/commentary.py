
import random

BOUNDARY_4 = [
    "{dist} METRES! THE FIELDER DOESN'T EVEN BOTHER RUNNING!",
    "CRACKED THROUGH THE COVERS! NOBODY STOPPING THAT!",
    "DRIVEN HARD AND TRUE! FOUR ALL THE WAY!",
    "WHAT A SHOT! RIGHT TO THE BOUNDARY!",
    "TIMING IS EVERYTHING — PERFECTLY PLACED FOR FOUR!",
    "TOO SHORT, TOO WIDE — PUNISHED FOR FOUR!",
    "SMASHED THROUGH MID-WICKET! BEAUTIFUL STROKE!",
    "FLASHED HARD AND IT RACES TO THE ROPES!",
    "PERFECT PLACEMENT! FOUR RUNS!",
    "HE'S MAKING THE BOWLER PAY DEARLY! FOUR!",
]

BOUNDARY_6 = [
    "{dist} METRES! THAT'S GONE INTO ORBIT!",
    "ABSOLUTELY DEMOLISHED! STRAIGHT OVER THE BOWLER'S HEAD!",
    "SIX! AND THE CROWD IS ON THEIR FEET!",
    "HE'S HIT THAT INTO THE NEXT POSTCODE!",
    "WHAT A MASSIVE HIT! EFFORTLESS POWER!",
    "RIGHT OUT OF THE PARK! NOTHING LESS THAN SIX!",
    "CLEARED THE ROPES BY A MILE! MAXIMUM!",
    "THE BALL HAS LEFT THE STADIUM! SIX RUNS!",
    "CLEAN HIT! NOT A CHANCE FOR THE FIELDER!",
    "SENSATIONAL! THE CROWD GOES WILD!",
]

WICKET_COMMENTARY = [
    "🎉 BOWLED HIM! THE STUMPS ARE ALL OVER THE PLACE!",
    "🎉 CAUGHT IN THE OUTFIELD! WHAT A CATCH!",
    "🎉 LBW! PLUMB IN FRONT! THE FINGER GOES UP!",
    "🎉 CAUGHT BEHIND! THE KEEPER TAKES A SHARP ONE!",
    "🎉 CLEANED UP! THAT'S A JAFFA!",
    "🎉 BOWLED THROUGH THE GATE! BRILLIANT DELIVERY!",
    "🎉 CAUGHT AT SLIP! THE BATSMAN REGRETS THAT SHOT!",
    "🎉 HE'S GONE! THE BOWLER IS PUMPED!",
]

DOT_COMMENTARY = [
    "Dot ball. Good pressure from the bowler.",
    "Beaten! That delivery was too good.",
    "Defended solidly. Dot ball.",
    "Outside the off stump — left alone.",
    "Good shape from the bowler. No run.",
    "Tight line and length. Dot.",
]

SINGLES_COMMENTARY = [
    "Pushed into the gap — quick single taken.",
    "Worked off the hips for one.",
    "Punched through covers, they cross for one.",
    "Dabbed fine for a single.",
    "Good running between the wickets — one run.",
]

def get_boundary_4_text():
    dist = random.randint(62, 78)
    line = random.choice(BOUNDARY_4).replace("{dist}", str(dist))
    return line

def get_boundary_6_text():
    dist = random.randint(82, 108)
    line = random.choice(BOUNDARY_6).replace("{dist}", str(dist))
    return line

def get_wicket_text():
    return random.choice(WICKET_COMMENTARY)

def get_dot_text():
    return random.choice(DOT_COMMENTARY)

def get_single_text():
    return random.choice(SINGLES_COMMENTARY)

def build_ball_commentary(bowler_name: str, bowler_ovr: int, delivery: str, speed: int,
                          batsman_name: str, shot: str, outcome: str) -> str:
    from data import BALL_DESCRIPTIONS, SHOT_DESCRIPTIONS
    ball_desc = BALL_DESCRIPTIONS.get(delivery, delivery.lower())
    shot_desc = SHOT_DESCRIPTIONS.get(shot, shot.lower())

    lines = []

    if outcome == "4":
        lines.append(f"**{get_boundary_4_text()}**")
    elif outcome == "6":
        lines.append(f"**{get_boundary_6_text()}**")
    elif outcome == "W":
        lines.append(f"**{get_wicket_text()}**")

    lines.append(f"> **{bowler_name}** ({bowler_ovr}) comes into the attack")
    lines.append(f"> **{bowler_name}**: {delivery} at **{speed} kmph**")

    if outcome == "0":
        lines.append(f"> **{batsman_name}** {shot_desc} the {ball_desc} — *dot ball*")
    elif outcome == "Wd":
        lines.append(f"> **Wide!** — ball drifts down the leg side. *Extra run awarded.*")
    elif outcome == "NB":
        lines.append(f"> **No Ball!** — overstepped. *Free hit on the next delivery!*")
    elif outcome == "NB+1":
        lines.append(f"> **No Ball!** — {batsman_name} {shot_desc} for 1. *Two runs total.*")
    elif outcome == "W":
        lines.append(f"> **{batsman_name}** {shot_desc} the {ball_desc} — **WICKET!**")
    else:
        lines.append(f"> **{batsman_name}** {shot_desc} the {ball_desc} for **{outcome}**")

    return "\n".join(lines)
