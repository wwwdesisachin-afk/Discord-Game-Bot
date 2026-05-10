
import discord
from game import GameState
from data import COUNTRY_FLAGS, BOWLING_TYPE_ICON, TIMELINE_EMOJIS


def player_flag(player: dict) -> str:
    return COUNTRY_FLAGS.get(player["country"], "🏳")


def player_bowling_icon(player: dict) -> str:
    if player["bowling_type"] is None:
        return "—"
    return BOWLING_TYPE_ICON.get(player["bowling_type"], "🎯")


def build_playing_xi_embed(team: dict) -> discord.Embed:
    embed = discord.Embed(
        title=team["name"],
        description=f"OVR:**{team['ovr']}** • CHEM:**{team['chem']}**",
        color=discord.Color.blue(),
    )

    header = "`Card | Player               | OVR | BAT | BOWL | Type`"
    embed.add_field(name="\u200b", value=header, inline=False)

    roles_order = ["Batter", "WK", "All-Rounder", "Bowler"]
    role_labels = {
        "Batter":      "Batters 🏏",
        "WK":          "WK 🧤",
        "All-Rounder": "All-Rounders 🏏",
        "Bowler":      "Bowlers 🔴",
    }

    for role in roles_order:
        players = [p for p in team["players"] if p["role"] == role]
        if not players:
            continue
        lines = []
        for p in players:
            flag = player_flag(p)
            icon = player_bowling_icon(p)
            card = p.get("card", "🥈")
            name = p["name"].ljust(20)[:20]
            lines.append(
                f"{card} {flag} `{name}` **{p['ovr']}** | {p['bat']} | {p['bowl']} | {icon}"
            )
        embed.add_field(name=role_labels[role], value="\n".join(lines), inline=False)

    return embed


def build_scoreboard_embed(game: GameState) -> discord.Embed:
    bat_team = game.get_batting_team()
    bowl_team = game.get_bowling_team()

    total_overs_str = f"{game.overs}"
    title = (
        f"🏏 {bat_team['name']}  "
        f"**{game.current_runs}/{game.current_wickets}**  "
        f"({game.overs_str()}/{total_overs_str})"
    )

    color = discord.Color.green() if game.innings == 1 else discord.Color.orange()
    embed = discord.Embed(title=title, color=color)

    def bat_line(player: dict | None, striker: bool) -> str:
        if player is None:
            return ""
        s = game.batsman_stats.get(player["name"], {"runs": 0, "balls": 0})
        marker = "🔴" if striker else "  "
        sr = game.sr(player["name"])
        name = player["name"][:16].ljust(16)
        return f"{marker} `{name}` **{s['runs']}** ({s['balls']}) SR:{sr}"

    bat_lines = []
    if game.striker:
        bat_lines.append(bat_line(game.striker, True))
    if game.non_striker:
        bat_lines.append(bat_line(game.non_striker, False))

    embed.add_field(
        name="BATTERS",
        value="\n".join(bat_lines) if bat_lines else "*Awaiting selection*",
        inline=False,
    )

    crr = game.crr()
    rrr = game.rrr()
    pship = f"P'Ship: **{game.partnership_runs}**({game.partnership_balls})"
    crr_str = f"CRR: **{crr}**"
    rrr_str = f"RRR: **{rrr}**" if game.innings == 2 else ""
    meta_parts = [pship, crr_str]
    if rrr_str:
        meta_parts.append(rrr_str)
    embed.add_field(name="\u200b", value="  ".join(meta_parts), inline=False)

    if game.current_bowler:
        b = game.current_bowler
        bs = game.bowler_stats.get(b["name"], {"balls": 0, "runs": 0, "wickets": 0})
        ov = game.bowler_overs_str(b["name"])
        name = b["name"][:16].ljust(16)
        bowl_line = f"`{name}` {ov}ov  {bs['runs']}r  {bs['wickets']}w"
        embed.add_field(name="BOWLER", value=bowl_line, inline=False)

    if game.timeline:
        tl = "  ".join(game.timeline[-10:])
        embed.add_field(name="Timeline", value=tl, inline=False)

    if game.innings == 2:
        target = game.target()
        balls_left = game.overs * 6 - game.current_legal_balls
        runs_needed = target - game.current_runs
        if runs_needed > 0 and balls_left > 0:
            chaser = bat_team["name"]
            footer = f"{chaser} need **{runs_needed}** runs in **{balls_left}** ball{'s' if balls_left != 1 else ''}"
            embed.set_footer(text=footer)
        elif runs_needed <= 0:
            embed.set_footer(text=f"🏆 {bat_team['name']} have chased down the target!")
        else:
            embed.set_footer(text=f"Target was {target}")

    return embed


def build_result_embed(game: GameState) -> discord.Embed:
    result_text = game.match_result()
    embed = discord.Embed(
        title="🏏 MATCH RESULT",
        description=result_text,
        color=discord.Color.gold(),
    )
    embed.add_field(
        name=game.teams[game.challenger.id]["name"],
        value=f"**{game.runs[0]}/{game.wickets[0]}** ({game.overs_str() if game.innings == 1 else f'{game.overs}.0'}ov)",
        inline=True,
    )
    embed.add_field(
        name=game.teams[game.opponent.id]["name"],
        value=f"**{game.runs[1]}/{game.wickets[1]}** ov",
        inline=True,
    )
    return embed
