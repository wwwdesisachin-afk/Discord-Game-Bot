
import os
import sys
import discord
from discord.ext import commands

sys.path.insert(0, os.path.dirname(__file__))

from game import GameState
from views import active_games, AcceptDeclineView
from embeds import build_playing_xi_embed
from data import SAMPLE_TEAMS

TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def get_user_team(user: discord.Member) -> dict | None:
    name = user.display_name
    for team_name, team_data in SAMPLE_TEAMS.items():
        if team_name.lower() in name.lower():
            return team_data
    return None


def assign_teams(challenger: discord.Member, opponent: discord.Member):
    team_names = list(SAMPLE_TEAMS.keys())
    import random
    random.shuffle(team_names)
    t1 = SAMPLE_TEAMS[team_names[0]]
    t2 = SAMPLE_TEAMS[team_names[1]]
    return t1, t2


@bot.event
async def on_ready():
    print(f"[CricketBot] Logged in as {bot.user} ({bot.user.id})")
    print(f"[CricketBot] Ready! Use !cs start @user <overs>")


@bot.group(name="cs", invoke_without_command=True)
async def cs(ctx: commands.Context):
    await ctx.send("Usage: `!cs start @user <overs>`")


@cs.command(name="start")
async def cs_start(ctx: commands.Context, opponent: discord.Member, overs: int = 20):
    if ctx.channel.id in active_games:
        await ctx.send("A match is already in progress in this channel!")
        return

    if opponent.bot:
        await ctx.send("You can't challenge a bot!")
        return

    if opponent.id == ctx.author.id:
        await ctx.send("You can't challenge yourself!")
        return

    if overs < 1 or overs > 50:
        await ctx.send("Overs must be between 1 and 50.")
        return

    game = GameState(ctx.author, opponent, overs)

    t1, t2 = assign_teams(ctx.author, opponent)
    game.teams[ctx.author.id] = t1
    game.teams[opponent.id] = t2

    active_games[ctx.channel.id] = game

    embed1 = build_playing_xi_embed(t1)
    embed2 = build_playing_xi_embed(t2)

    view = AcceptDeclineView(game, ctx.channel.id)
    msg = await ctx.send(
        content=(
            f"⚔️ **{ctx.author.mention}** challenges **{opponent.mention}** to a **{overs}-over** match!\n\n"
            f"🏏 **{t1['name']}** (OVR:{t1['ovr']}) vs **{t2['name']}** (OVR:{t2['ovr']})\n\n"
            f"{opponent.mention} — accept or decline?"
        ),
        embeds=[embed1, embed2],
        view=view,
    )
    game.game_message = msg


@cs.command(name="cancel")
async def cs_cancel(ctx: commands.Context):
    if ctx.channel.id not in active_games:
        await ctx.send("No active match in this channel.")
        return
    game = active_games[ctx.channel.id]
    if ctx.author.id not in (game.challenger.id, game.opponent.id):
        await ctx.send("Only match participants can cancel.")
        return
    active_games.pop(ctx.channel.id)
    await ctx.send(f"🚫 Match cancelled by **{ctx.author.display_name}**.")


@cs.command(name="score")
async def cs_score(ctx: commands.Context):
    if ctx.channel.id not in active_games:
        await ctx.send("No active match in this channel.")
        return
    from embeds import build_scoreboard_embed
    game = active_games[ctx.channel.id]
    embed = build_scoreboard_embed(game)
    await ctx.send(embed=embed)


@cs.command(name="xi")
async def cs_xi(ctx: commands.Context):
    if ctx.channel.id not in active_games:
        await ctx.send("No active match in this channel.")
        return
    game = active_games[ctx.channel.id]
    if ctx.author.id not in (game.challenger.id, game.opponent.id):
        await ctx.send("Only match participants can view XIs.")
        return
    team = game.teams.get(ctx.author.id)
    if team:
        embed = build_playing_xi_embed(team)
        await ctx.send(embed=embed, ephemeral=False)


@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument. Usage: `!cs start @user <overs>`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid arguments. Usage: `!cs start @user <overs>`")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(f"[ERROR] {error}")
        raise error


if __name__ == "__main__":
    if not TOKEN:
        print("[ERROR] DISCORD_BOT_TOKEN not set.")
        sys.exit(1)
    bot.run(TOKEN)
