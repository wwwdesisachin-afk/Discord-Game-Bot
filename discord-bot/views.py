
from __future__ import annotations
import random
import discord

from game import GameState
from logic import calculate_outcome
from embeds import build_scoreboard_embed, build_result_embed, build_playing_xi_embed
from commentary import build_ball_commentary
from data import (
    TOSS_HEAD_EMOJI, TOSS_TAIL_EMOJI, TIMELINE_EMOJIS,
    BALL_SPEEDS, BATTING_SHOTS, BOWLING_DELIVERIES,
)

active_games: dict[int, GameState] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _timeline_emoji(outcome: str) -> str:
    return TIMELINE_EMOJIS.get(outcome, "•")


async def _process_delivery(interaction: discord.Interaction, game: GameState, shot: str):
    delivery = game.pending_delivery
    bowler = game.current_bowler
    striker = game.striker

    outcome, is_extra = calculate_outcome(
        delivery, shot,
        bowler["ovr"], striker["ovr"],
    )

    speed_range = BALL_SPEEDS.get(delivery, (100, 130))
    speed = random.randint(*speed_range)

    commentary = build_ball_commentary(
        bowler["name"], bowler["ovr"],
        delivery, speed,
        striker["name"], shot,
        outcome,
    )

    if outcome == "W":
        game.add_legal_ball()
        game.add_wicket()
        game.timeline.append(_timeline_emoji("W"))
    elif outcome == "Wd":
        game.runs[game.innings - 1] += 1
        game.bowler_stats[bowler["name"]]["runs"] += 1
        game.timeline.append(_timeline_emoji("Wd"))
    elif outcome == "NB":
        game.runs[game.innings - 1] += 1
        game.bowler_stats[bowler["name"]]["runs"] += 1
        game.timeline.append(_timeline_emoji("NB"))
    elif outcome == "NB+1":
        game.runs[game.innings - 1] += 2
        game.bowler_stats[bowler["name"]]["runs"] += 2
        game.timeline.append(_timeline_emoji("NB+1"))
    else:
        game.add_legal_ball()
        runs = int(outcome)
        game.add_runs(runs)
        game.timeline.append(_timeline_emoji(outcome))
        if runs in (1, 3):
            game.rotate_strike()

    embed = build_scoreboard_embed(game)

    if game.is_innings_over():
        if game.innings == 1:
            await _start_second_innings(interaction, game, commentary, embed)
            return
        else:
            result_embed = build_result_embed(game)
            active_games.pop(interaction.channel_id, None)
            await interaction.response.edit_message(content=commentary, embed=result_embed, view=None)
            return

    if outcome == "W":
        available = game.get_available_batsmen()
        if not available:
            if game.innings == 1:
                await _start_second_innings(interaction, game, commentary, embed)
            else:
                result_embed = build_result_embed(game)
                active_games.pop(interaction.channel_id, None)
                await interaction.response.edit_message(content=commentary, embed=result_embed, view=None)
            return
        game.phase = "wicket_fallen"
        view = NextBatsmanView(game, interaction.channel_id)
        await interaction.response.edit_message(content=commentary, embed=embed, view=view)
        return

    if not is_extra and game.current_over_balls >= 6:
        game.end_over()
        if game.current_legal_balls >= game.overs * 6:
            if game.innings == 1:
                await _start_second_innings(interaction, game, commentary, embed)
            else:
                result_embed = build_result_embed(game)
                active_games.pop(interaction.channel_id, None)
                await interaction.response.edit_message(content=commentary, embed=result_embed, view=None)
            return
        game.phase = "over_end"
        available = game.get_available_bowlers()
        view = NextBowlerView(game, interaction.channel_id, available)
        over_num = game.current_legal_balls // 6
        await interaction.response.edit_message(
            content=commentary + f"\n\n**End of over {over_num}.** {game.bowling_user.mention} — select your next bowler.",
            embed=embed,
            view=view,
        )
        return

    game.phase = "bowl_select"
    view = BowlingView(game, interaction.channel_id)
    prompt = f"{game.bowling_user.mention} — choose your delivery:"
    await interaction.response.edit_message(content=commentary + f"\n\n{prompt}", embed=embed, view=view)


async def _start_second_innings(
    interaction: discord.Interaction, game: GameState, commentary: str, embed: discord.Embed
):
    game.start_second_innings()
    bat_team = game.get_batting_team()
    target = game.target()
    msg = (
        commentary
        + f"\n\n**End of 1st Innings!** {bat_team['name']} chasing **{target}** in {game.overs} overs.\n"
        + f"{game.batting_user.mention} — select your opening pair."
    )
    xi_embed = build_playing_xi_embed(bat_team)
    view = StrikerSelectView(game, interaction.channel_id)
    await interaction.response.edit_message(content=msg, embed=xi_embed, view=view)


# ---------------------------------------------------------------------------
# Accept / Decline
# ---------------------------------------------------------------------------

class AcceptDeclineView(discord.ui.View):
    def __init__(self, game: GameState, channel_id: int):
        super().__init__(timeout=120)
        self.game = game
        self.channel_id = channel_id

    @discord.ui.button(label="Accept ✅", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.game.opponent.id:
            await interaction.response.send_message("This challenge isn't for you!", ephemeral=True)
            return
        self.game.phase = "toss"
        view = TossView(self.game, self.channel_id)
        await interaction.response.edit_message(
            content=(
                f"✅ **{self.game.opponent.display_name}** accepted the challenge!\n\n"
                f"**Toss time!** {self.game.challenger.mention} — call it:"
            ),
            view=view,
        )

    @discord.ui.button(label="Decline ❌", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.game.opponent.id:
            await interaction.response.send_message("This challenge isn't for you!", ephemeral=True)
            return
        active_games.pop(self.channel_id, None)
        await interaction.response.edit_message(
            content=f"❌ **{self.game.opponent.display_name}** declined the match.", view=None
        )


# ---------------------------------------------------------------------------
# Toss
# ---------------------------------------------------------------------------

class TossView(discord.ui.View):
    def __init__(self, game: GameState, channel_id: int):
        super().__init__(timeout=120)
        self.game = game
        self.channel_id = channel_id

    @discord.ui.button(label="Head", style=discord.ButtonStyle.primary, emoji=TOSS_HEAD_EMOJI)
    async def head(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._do_toss(interaction, "Head")

    @discord.ui.button(label="Tail", style=discord.ButtonStyle.primary, emoji=TOSS_TAIL_EMOJI)
    async def tail(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._do_toss(interaction, "Tail")

    async def _do_toss(self, interaction: discord.Interaction, call: str):
        if interaction.user.id != self.game.challenger.id:
            await interaction.response.send_message("Wait for your turn to toss!", ephemeral=True)
            return
        result = random.choice(["Head", "Tail"])
        won = (call == result)
        winner = self.game.challenger if won else self.game.opponent
        self.game.toss_winner_id = winner.id
        self.game.phase = "bat_or_bowl"
        view = BatBowlView(self.game, self.channel_id)
        await interaction.response.edit_message(
            content=(
                f"{TOSS_HEAD_EMOJI if result == 'Head' else TOSS_TAIL_EMOJI} "
                f"**{result}!** — {winner.mention} wins the toss!\n\n"
                f"{winner.mention} — do you want to **Bat** or **Bowl**?"
            ),
            view=view,
        )


# ---------------------------------------------------------------------------
# Bat or Bowl
# ---------------------------------------------------------------------------

class BatBowlView(discord.ui.View):
    def __init__(self, game: GameState, channel_id: int):
        super().__init__(timeout=120)
        self.game = game
        self.channel_id = channel_id

    @discord.ui.button(label="🏏 Bat", style=discord.ButtonStyle.green)
    async def bat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._choose(interaction, bat_first=True)

    @discord.ui.button(label="🎯 Bowl", style=discord.ButtonStyle.red)
    async def bowl(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._choose(interaction, bat_first=False)

    async def _choose(self, interaction: discord.Interaction, bat_first: bool):
        if interaction.user.id != self.game.toss_winner_id:
            await interaction.response.send_message("It's not your decision!", ephemeral=True)
            return
        winner_id = self.game.toss_winner_id
        loser_id = self.game.opponent.id if winner_id == self.game.challenger.id else self.game.challenger.id
        if bat_first:
            self.game.batting_user_id = winner_id
            self.game.bowling_user_id = loser_id
        else:
            self.game.bowling_user_id = winner_id
            self.game.batting_user_id = loser_id

        bat_team = self.game.get_batting_team()
        choice_txt = "bat" if bat_first else "bowl"
        xi_embed = build_playing_xi_embed(bat_team)
        self.game.phase = "select_striker"
        view = StrikerSelectView(self.game, self.channel_id)
        await interaction.response.edit_message(
            content=(
                f"**{interaction.user.display_name}** chose to **{choice_txt}**!\n\n"
                f"{self.game.batting_user.mention} — select your **Striker** (Opening Batsman):"
            ),
            embed=xi_embed,
            view=view,
        )


# ---------------------------------------------------------------------------
# Opener Selection
# ---------------------------------------------------------------------------

class StrikerSelectView(discord.ui.View):
    def __init__(self, game: GameState, channel_id: int):
        super().__init__(timeout=120)
        self.game = game
        self.channel_id = channel_id

        options = [
            discord.SelectOption(
                label=f"{p['name']} (BAT:{p['bat']})",
                value=p["name"],
                description=f"{p['country']} | OVR:{p['ovr']}",
            )
            for p in game.get_batting_team()["players"]
            if p["name"] not in game.dismissed
        ]
        select = discord.ui.Select(
            placeholder="Select Striker…",
            options=options,
            custom_id="striker_select",
        )
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.game.batting_user_id:
            await interaction.response.send_message("Only the batting team selects!", ephemeral=True)
            return
        chosen_name = interaction.data["values"][0]
        player = next(p for p in self.game.get_batting_team()["players"] if p["name"] == chosen_name)
        self.game.striker = player
        self.game.init_batsman_stats(player)
        self.game.phase = "select_non_striker"
        view = NonStrikerSelectView(self.game, self.channel_id)
        await interaction.response.edit_message(
            content=(
                f"✅ **{player['name']}** set as Striker.\n"
                f"{self.game.batting_user.mention} — now select your **Non-Striker**:"
            ),
            view=view,
        )


class NonStrikerSelectView(discord.ui.View):
    def __init__(self, game: GameState, channel_id: int):
        super().__init__(timeout=120)
        self.game = game
        self.channel_id = channel_id

        options = [
            discord.SelectOption(
                label=f"{p['name']} (BAT:{p['bat']})",
                value=p["name"],
                description=f"{p['country']} | OVR:{p['ovr']}",
            )
            for p in game.get_batting_team()["players"]
            if p["name"] not in game.dismissed
            and (game.striker is None or p["name"] != game.striker["name"])
        ]
        select = discord.ui.Select(
            placeholder="Select Non-Striker…",
            options=options,
            custom_id="non_striker_select",
        )
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.game.batting_user_id:
            await interaction.response.send_message("Only the batting team selects!", ephemeral=True)
            return
        chosen_name = interaction.data["values"][0]
        player = next(p for p in self.game.get_batting_team()["players"] if p["name"] == chosen_name)
        self.game.non_striker = player
        self.game.init_batsman_stats(player)

        bowl_team = self.game.get_bowling_team()
        xi_embed = build_playing_xi_embed(bowl_team)
        self.game.phase = "select_bowler"
        view = BowlerSelectView(self.game, self.channel_id, self.game.get_available_bowlers())
        await interaction.response.edit_message(
            content=(
                f"✅ **{player['name']}** set as Non-Striker.\n"
                f"{self.game.bowling_user.mention} — select your **Opening Bowler**:"
            ),
            embed=xi_embed,
            view=view,
        )


# ---------------------------------------------------------------------------
# Bowler Selection
# ---------------------------------------------------------------------------

class BowlerSelectView(discord.ui.View):
    def __init__(self, game: GameState, channel_id: int, available: list[dict]):
        super().__init__(timeout=120)
        self.game = game
        self.channel_id = channel_id

        options = [
            discord.SelectOption(
                label=f"{p['name']} (BOWL:{p['bowl']})",
                value=p["name"],
                description=f"{p['country']} | OVR:{p['ovr']} | {p['bowling_type']}",
            )
            for p in available
        ]
        if not options:
            options = [discord.SelectOption(label="No bowlers available", value="none")]

        select = discord.ui.Select(
            placeholder="Select Bowler…",
            options=options,
            custom_id="bowler_select",
        )
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.game.bowling_user_id:
            await interaction.response.send_message("Only the bowling team selects!", ephemeral=True)
            return
        chosen_name = interaction.data["values"][0]
        if chosen_name == "none":
            await interaction.response.send_message("No bowlers available!", ephemeral=True)
            return
        player = next(p for p in self.game.get_bowling_team()["players"] if p["name"] == chosen_name)
        self.game.current_bowler = player
        self.game.init_bowler_stats(player)
        self.game.phase = "bowl_select"
        embed = build_scoreboard_embed(self.game)
        view = BowlingView(self.game, self.channel_id)
        await interaction.response.edit_message(
            content=(
                f"🎯 **{player['name']}** will bowl.\n"
                f"{self.game.bowling_user.mention} — choose your delivery:"
            ),
            embed=embed,
            view=view,
        )


# ---------------------------------------------------------------------------
# Bowling Buttons
# ---------------------------------------------------------------------------

class BowlingView(discord.ui.View):
    def __init__(self, game: GameState, channel_id: int):
        super().__init__(timeout=120)
        self.game = game
        self.channel_id = channel_id

        bowling_type = game.current_bowler["bowling_type"] if game.current_bowler else "Fast"
        deliveries = BOWLING_DELIVERIES.get(bowling_type, BOWLING_DELIVERIES["Fast"])

        for delivery in deliveries:
            btn = discord.ui.Button(
                label=delivery,
                style=discord.ButtonStyle.primary,
                custom_id=f"bowl_{delivery.replace(' ', '_')}",
            )
            btn.callback = self._make_cb(delivery)
            self.add_item(btn)

    def _make_cb(self, delivery: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.game.bowling_user_id:
                await interaction.response.send_message("It's not your turn to bowl!", ephemeral=True)
                return
            self.game.pending_delivery = delivery
            self.game.phase = "bat_select"
            embed = build_scoreboard_embed(self.game)
            view = BattingView(self.game, self.channel_id)
            await interaction.response.edit_message(
                content=(
                    f"🎯 **{self.game.current_bowler['name']}** bowls a **{delivery}**!\n"
                    f"{self.game.batting_user.mention} — play your shot:"
                ),
                embed=embed,
                view=view,
            )
        return callback


# ---------------------------------------------------------------------------
# Batting Buttons
# ---------------------------------------------------------------------------

class BattingView(discord.ui.View):
    def __init__(self, game: GameState, channel_id: int):
        super().__init__(timeout=120)
        self.game = game
        self.channel_id = channel_id

        styles = [
            discord.ButtonStyle.success,
            discord.ButtonStyle.success,
            discord.ButtonStyle.success,
            discord.ButtonStyle.secondary,
            discord.ButtonStyle.danger,
            discord.ButtonStyle.success,
            discord.ButtonStyle.secondary,
            discord.ButtonStyle.danger,
        ]
        for shot, style in zip(BATTING_SHOTS, styles):
            btn = discord.ui.Button(
                label=shot,
                style=style,
                custom_id=f"shot_{shot.replace(' ', '_').replace('-', '_')}",
            )
            btn.callback = self._make_cb(shot)
            self.add_item(btn)

    def _make_cb(self, shot: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.game.batting_user_id:
                await interaction.response.send_message("It's not your turn to bat!", ephemeral=True)
                return
            await _process_delivery(interaction, self.game, shot)
        return callback


# ---------------------------------------------------------------------------
# Next Batsman after Wicket
# ---------------------------------------------------------------------------

class NextBatsmanView(discord.ui.View):
    def __init__(self, game: GameState, channel_id: int):
        super().__init__(timeout=120)
        self.game = game
        self.channel_id = channel_id

        available = game.get_available_batsmen()
        options = [
            discord.SelectOption(
                label=f"{p['name']} (BAT:{p['bat']})",
                value=p["name"],
                description=f"{p['country']} | OVR:{p['ovr']}",
            )
            for p in available
        ]
        select = discord.ui.Select(
            placeholder="Select next Batsman…",
            options=options,
            custom_id="next_bat_select",
        )
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.game.batting_user_id:
            await interaction.response.send_message("Only the batting team selects!", ephemeral=True)
            return
        chosen_name = interaction.data["values"][0]
        player = next(p for p in self.game.get_batting_team()["players"] if p["name"] == chosen_name)
        self.game.striker = player
        self.game.init_batsman_stats(player)
        self.game.phase = "bowl_select"

        if self.game.current_over_balls >= 6:
            self.game.end_over()
            available_bowlers = self.game.get_available_bowlers()
            bowl_view = NextBowlerView(self.game, self.channel_id, available_bowlers)
            embed = build_scoreboard_embed(self.game)
            await interaction.response.edit_message(
                content=(
                    f"✅ **{player['name']}** comes in to bat.\n"
                    f"**End of over.** {self.game.bowling_user.mention} — select your next bowler:"
                ),
                embed=embed,
                view=bowl_view,
            )
        else:
            embed = build_scoreboard_embed(self.game)
            view = BowlingView(self.game, self.channel_id)
            await interaction.response.edit_message(
                content=(
                    f"✅ **{player['name']}** comes in at #{self.game.current_wickets + 1}.\n"
                    f"{self.game.bowling_user.mention} — choose your delivery:"
                ),
                embed=embed,
                view=view,
            )


# ---------------------------------------------------------------------------
# Next Bowler after Over
# ---------------------------------------------------------------------------

class NextBowlerView(discord.ui.View):
    def __init__(self, game: GameState, channel_id: int, available: list[dict]):
        super().__init__(timeout=120)
        self.game = game
        self.channel_id = channel_id

        options = [
            discord.SelectOption(
                label=f"{p['name']} (BOWL:{p['bowl']})",
                value=p["name"],
                description=f"{p['bowling_type']} | {self.game.bowler_overs_str(p['name'])} ov bowled",
            )
            for p in available
        ]
        if not options:
            options = [discord.SelectOption(label="No eligible bowlers", value="none")]

        select = discord.ui.Select(
            placeholder="Select next Bowler…",
            options=options,
            custom_id="next_bowl_select",
        )
        select.callback = self.on_select
        self.add_item(select)

    def bowler_overs_str(self, name: str) -> str:
        balls = self.game.bowler_ball_count.get(name, 0)
        return f"{balls // 6}.{balls % 6}"

    async def on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.game.bowling_user_id:
            await interaction.response.send_message("Only the bowling team selects!", ephemeral=True)
            return
        chosen_name = interaction.data["values"][0]
        if chosen_name == "none":
            await interaction.response.send_message("No eligible bowlers!", ephemeral=True)
            return
        player = next(p for p in self.game.get_bowling_team()["players"] if p["name"] == chosen_name)
        self.game.current_bowler = player
        self.game.init_bowler_stats(player)
        self.game.phase = "bowl_select"
        embed = build_scoreboard_embed(self.game)
        view = BowlingView(self.game, self.channel_id)
        await interaction.response.edit_message(
            content=(
                f"🎯 **{player['name']}** starts a new over.\n"
                f"{self.game.bowling_user.mention} — choose your delivery:"
            ),
            embed=embed,
            view=view,
        )
