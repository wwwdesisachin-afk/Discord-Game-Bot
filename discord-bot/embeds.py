
import discord
from game import GameState
from data import COUNTRY_FLAGS, TIMELINE_EMOJIS


def player_flag(player: dict) -> str:
    return COUNTRY_FLAGS.get(player["country"], "🏳")


def _ball_icon(player: dict) -> str:
    bt = player.get("bowling_type")
    if bt == "Fast":
        return "🔥"
    if bt in ("Off Spin", "Leg Spin"):
        return "🌀"
    return "🏏"


def _role_bonus(chem: int, role: str) -> int:
    extras = {"Batter": 0, "WK": 1, "All-Rounder": 0, "Bowler": -1}
    return max(1, (chem // 20) + extras.get(role, 0))


def _overs_display(legal_balls: int, total_overs: int) -> str:
    return f"{legal_balls // 6}.{legal_balls % 6}/{total_overs}.0"


# ---------------------------------------------------------------------------
# Playing XI
# ---------------------------------------------------------------------------

def build_playing_xi_embed(team: dict) -> discord.Embed:
    chem = team.get("chem", 70)
    embed = discord.Embed(
        title=team["name"],
        description=f"OVR:**{team['ovr']}** • CHEM:**{chem}**",
        color=discord.Color.blue(),
    )
    embed.add_field(
        name="\u200b",
        value="`Card | Player             | OVR | BAT | BOWL | Country`",
        inline=False,
    )

    role_cfg = [
        ("Batter",      "Batters 🏏"),
        ("WK",          "WK 🧤"),
        ("All-Rounder", "All-Rounders ⚡"),
        ("Bowler",      "Bowlers 🎯"),
    ]

    for role, label in role_cfg:
        players = [p for p in team["players"] if p["role"] == role]
        if not players:
            continue
        bonus = _role_bonus(chem, role)
        lines = []
        for p in players:
            flag = player_flag(p)
            card = p.get("card", "🥈")
            ball = _ball_icon(p)
            bowl_val = str(p["bowl"]) if p.get("bowling_type") else " —"
            name = f"{p['name'][:16]:<16}"
            lines.append(
                f"{card} | `{name}` | {p['ovr']} | {p['bat']} | {bowl_val:>3} | {ball} | {flag}"
            )
        embed.add_field(name=f"{label}  +{bonus}", value="\n".join(lines), inline=False)

    embed.set_footer(text=f"{team['name']} • Playing XI")
    return embed


# ---------------------------------------------------------------------------
# Scoreboard
# ---------------------------------------------------------------------------

def build_scoreboard_embed(game: GameState) -> discord.Embed:
    bat_team = game.get_batting_team()
    bowl_team = game.get_bowling_team()

    # ── Two-line team header ──────────────────────────────────────────────
    if game.innings == 1:
        ov = _overs_display(game.current_legal_balls, game.overs)
        line1 = f"**{bat_team['name']}**  {game.current_runs}/{game.current_wickets}  ({ov})"
        line2 = f"**{bowl_team['name']}**  Yet to Bat"
    else:
        inn1_name = bowl_team["name"]   # after swap, bowling_user batted first
        ov = _overs_display(game.current_legal_balls, game.overs)
        line1 = f"**{inn1_name}**  {game.runs[0]}/{game.wickets[0]}"
        line2 = f"**{bat_team['name']}**  {game.current_runs}/{game.current_wickets}  ({ov})"

    color = discord.Color.green() if game.innings == 1 else discord.Color.orange()
    embed = discord.Embed(description=f"{line1}\n{line2}", color=color)

    # ── Batters ──────────────────────────────────────────────────────────
    rows = ["**BATTERS**\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000R\u3000B\u3000SR"]
    for player, striker in [(game.striker, True), (game.non_striker, False)]:
        if player:
            s = game.batsman_stats.get(player["name"], {"runs": 0, "balls": 0})
            sr = game.sr(player["name"])
            mark = "🔴" if striker else "⬜"
            rows.append(f"{mark} **{player['name']}**\u3000\u3000{s['runs']}\u3000{s['balls']}\u3000{sr}")
    embed.add_field(name="\u200b", value="\n".join(rows), inline=False)

    # ── P'Ship / CRR / RRR or Proj ───────────────────────────────────────
    crr = game.crr()
    meta = f"P'Ship: **{game.partnership_runs}**({game.partnership_balls})  CRR: **{crr}**"
    if game.innings == 2:
        meta += f"  RRR: **{game.rrr()}**"
    else:
        proj = int(crr * game.overs) if game.current_legal_balls > 0 else 0
        meta += f"  Proj: **{proj}**"
    embed.add_field(name="\u200b", value=meta, inline=False)

    # ── Bowler ───────────────────────────────────────────────────────────
    if game.current_bowler:
        b = game.current_bowler
        bs = game.bowler_stats.get(b["name"], {"balls": 0, "runs": 0, "wickets": 0})
        ov = game.bowler_overs_str(b["name"])
        bowl_header = "**BOWLER**\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000O\u3000R\u3000W"
        bowl_row = f"**{b['name']}**\u3000\u3000{ov}\u3000{bs['runs']}\u3000{bs['wickets']}"
        embed.add_field(name="\u200b", value=f"{bowl_header}\n{bowl_row}", inline=False)

    # ── Timeline ─────────────────────────────────────────────────────────
    tl = "  ".join(game.timeline[-12:]) if game.timeline else "—"
    embed.add_field(name="Timeline", value=tl, inline=False)

    # ── Footer ───────────────────────────────────────────────────────────
    if game.innings == 2:
        target = game.target()
        balls_left = game.overs * 6 - game.current_legal_balls
        runs_needed = target - game.current_runs
        if runs_needed > 0 and balls_left > 0:
            embed.set_footer(
                text=f"{bat_team['name']} need {runs_needed} run{'s' if runs_needed != 1 else ''} "
                     f"to win in {balls_left} ball{'s' if balls_left != 1 else ''}"
            )
        elif runs_needed <= 0:
            embed.set_footer(text=f"🏆 {bat_team['name']} have won!")
        else:
            embed.set_footer(text=f"Target: {target}")
    else:
        embed.set_footer(text=f"{bat_team['name']} chose to bat first")

    return embed


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

def build_result_embed(game: GameState) -> discord.Embed:
    result_text = game.match_result()
    # In innings 2: bowling_user batted first; batting_user is chasing
    inn1_team = game.teams[game.bowling_user_id]
    inn2_team = game.teams[game.batting_user_id]

    embed = discord.Embed(
        title="🏏 MATCH RESULT",
        description=result_text,
        color=discord.Color.gold(),
    )
    embed.add_field(
        name=inn1_team["name"],
        value=f"**{game.runs[0]}/{game.wickets[0]}**  ({game.overs}.0 ov)",
        inline=True,
    )
    embed.add_field(
        name=inn2_team["name"],
        value=f"**{game.runs[1]}/{game.wickets[1]}**",
        inline=True,
    )
    return embed
