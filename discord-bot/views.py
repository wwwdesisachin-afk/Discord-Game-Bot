
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


async def _send_bowling_prompt(channel: discord.TextChannel, game: GameState):
    """Send a new message with bowling buttons."""
    embed = build_scoreboard_embed(game)
    view = BowlingView(game, channel.id)
    await channel.send(
        content=f"🎯 {game.bowling_user.mention} — choose your delivery:",
        embed=embed,
        view=view,
    )


async def _process_delivery(interaction: discord.Interaction, game: GameState, shot: str):
    delivery = game.pending_delivery
    bowler = game.current_bowler
    striker = game.striker

    outcome, is_extra = calculate_outcome(
        delivery, shot,
        bowler["ovr"], striker["ovr"],
    )

    speed_range = BALL_SPEEDS.get(delivery, (100, 130))
    speed = random.uniform(*speed_range)

    commentary = build_ball_commentary(
        bowler["name"], bowler["ovr"],
        delivery, speed,
        striker["name"], shot,
        outcome,
        bowling_type=bowler.get("bowling_type"),
    )

    # Update game state
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

    # Remove batting buttons from the clicked message
    await interaction.response.edit_message(view=None)

    channel = interaction.channel
    embed = build_scoreboard_embed(game)

    # ── Match / innings over ──────────────────────────────────────────────
    if game.is_innings_over():
        if game.innings == 1:
            await _do_innings_break(channel, game, commentary, embed)
            return
        else:
            active_games.pop(interaction.channel_id, None)
            result_embed = build_result_embed(game)
            await channel.send(content=commentary, embed=result_embed)
            return

    # ── Wicket ────────────────────────────────────────────────────────────
    if outcome == "W":
        available = game.get_available_batsmen()
        if not available:
            if game.innings == 1:
                await _do_innings_break(channel, game, commentary, embed)
            else:
                active_games.pop(interaction.channel_id, None)
                result_embed = build_result_embed(game)
                await channel.send(content=commentary, embed=result_embed)
            return
        game.phase = "wicket_fallen"
        view = NextBatsmanView(game, channel.id)
        await channel.send(
            content=commentary + f"\n\n🪦 **Wicket!** {game.batting_user.mention} — select your next batsman:",
            embed=embed,
            view=view,
        )
        return

    # ── Over end ──────────────────────────────────────────────────────────
    if not is_extra and game.current_over_balls >= 6:
        over_num = game.current_legal_balls // 6
        game.end_over()

        if game.is_innings_over():
            if game.innings == 1:
                await _do_innings_break(channel, game, commentary, embed)
            else:
                active_games.pop(interaction.channel_id, None)
                result_embed = build_result_embed(game)
                await channel.send(content=commentary, embed=result_embed)
            return

        game.phase = "over_end"
        available = game.get_available_bowlers()
        view = NextBowlerView(game, channel.id, available)
        await channel.send(
            content=commentary + f"\n\n**🔄 End of over {over_num}!** {game.bowling_user.mention} — select your next bowler:",
            embed=embed,
            view=view,
        )
        return

    # ── Continue: send new bowling prompt ─────────────────────────────────
    await channel.send(content=commentary, embed=embed)
    game.phase = "bowl_select"
    await _send_bowling_prompt(channel, game)


async def _do_innings_break(
    channel: discord.TextChannel, game: GameState, commentary: str, embed: discord.Embed
):
    game.start_second_innings()
    bat_team = game.get_batting_team()
    target = game.target()
    balls_in_match = game.overs * 6
    rrr_val = round((target / balls_in_match) * 6, 1) if balls_in_match > 0 else 0.0

    # End of innings scoreboard
    await channel.send(content=commentary, embed=embed)

    # Bold announcement banner
    await channel.send(
        content=(
            f"**⏸ Innings Break!**\n"
            f"**{bat_team['name'].upper()} REQUIRE {target} RUNS OFF {balls_in_match} BALLS (RRR: {rrr_val})**"
        )
    )

    xi_embed = build_playing_xi_embed(bat_team)
    view = OpenerSelectView(game, channel.id)
    await channel.send(
        content=f"{game.batting_user.mention} — select your **Opening Pair** (pick 2):",
        embed=xi_embed,
        view=view,
    )


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
        await interaction.response.edit_message(view=None)
        view = TossView(self.game, self.channel_id)
        await interaction.followup.send(
            content=(
                f"✅ **{self.game.opponent.display_name}** accepted the challenge!\n\n"
                f"🪙 **Toss time!** {self.game.challenger.mention} — call it:"
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
        await interaction.response.edit_message(
            content=(
                f"{TOSS_HEAD_EMOJI if result == 'Head' else TOSS_TAIL_EMOJI} "
                f"**{result}!** — **{winner.display_name}** wins the toss!"
            ),
            view=None,
        )
        view = BatBowlView(self.game, self.channel_id)
        await interaction.followup.send(
            content=f"{winner.mention} — do you want to **Bat** or **Bowl**?",
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

        choice_txt = "bat" if bat_first else "bowl"
        bat_team = self.game.get_batting_team()

        await interaction.response.edit_message(
            content=f"**{interaction.user.display_name}** elected to **{choice_txt}** first!",
            view=None,
        )
        xi_embed = build_playing_xi_embed(bat_team)
        self.game.phase = "select_striker"
        view = OpenerSelectView(self.game, self.channel_id)
        await interaction.followup.send(
            content=f"{self.game.batting_user.mention} — select your **Opening Pair** (pick 2):",
            embed=xi_embed,
            view=view,
        )


# ---------------------------------------------------------------------------
# Opener Selection  (single multi-pick → striker designate)
# ---------------------------------------------------------------------------

class OpenerSelectView(discord.ui.View):
    """Pick both openers in one dropdown (exactly 2 selections required)."""

    def __init__(self, game: GameState, channel_id: int):
        super().__init__(timeout=120)
        self.game = game
        self.channel_id = channel_id

        eligible = [
            p for p in game.get_batting_team()["players"]
            if p["name"] not in game.dismissed
        ]
        options = [
            discord.SelectOption(
                label=f"{p['name']} (BAT:{p['bat']})",
                value=p["name"],
                description=f"{p['country']} | OVR:{p['ovr']}",
            )
            for p in eligible
        ]
        select = discord.ui.Select(
            placeholder="Pick your 2 openers…",
            min_values=2,
            max_values=2,
            options=options,
        )
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.game.batting_user_id:
            await interaction.response.send_message("Only the batting team selects!", ephemeral=True)
            return
        names = interaction.data["values"]  # exactly 2
        players = [
            next(p for p in self.game.get_batting_team()["players"] if p["name"] == n)
            for n in names
        ]
        # Store both; user will now pick which is Striker
        self.game._pending_openers = players

        await interaction.response.edit_message(
            content=f"✅ **{players[0]['name']}** & **{players[1]['name']}** selected — who takes strike?",
            embed=None,
            view=StrikerDesignateView(self.game, self.channel_id, players),
        )


class StrikerDesignateView(discord.ui.View):
    """Two buttons: tap the player who will face the first ball."""

    def __init__(self, game: GameState, channel_id: int, players: list[dict]):
        super().__init__(timeout=120)
        self.game = game
        self.channel_id = channel_id

        for p in players:
            btn = discord.ui.Button(
                label=f"🔴 {p['name']}",
                style=discord.ButtonStyle.primary,
                custom_id=f"striker_{p['name']}",
            )
            btn.callback = self._make_cb(p, players)
            self.add_item(btn)

    def _make_cb(self, striker: dict, players: list[dict]):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.game.batting_user_id:
                await interaction.response.send_message("Only the batting team selects!", ephemeral=True)
                return
            non_striker = next(p for p in players if p["name"] != striker["name"])
            self.game.striker = striker
            self.game.non_striker = non_striker
            self.game.init_batsman_stats(striker)
            self.game.init_batsman_stats(non_striker)
            self.game.phase = "select_bowler"

            await interaction.response.edit_message(
                content=(
                    f"🔴 **{striker['name']}** on strike  ·  "
                    f"**{non_striker['name']}** at non-striker end"
                ),
                view=None,
            )
            # Opening pair announcement
            await interaction.followup.send(
                content=(
                    f"**{striker['name']}** ({striker['ovr']}) and "
                    f"**{non_striker['name']}** ({non_striker['ovr']}) are opening the batting"
                )
            )
            bowl_team = self.game.get_bowling_team()
            xi_embed = build_playing_xi_embed(bowl_team)
            view = BowlerSelectView(self.game, self.channel_id, self.game.get_available_bowlers())
            await interaction.followup.send(
                content=f"{self.game.bowling_user.mention} — select your **Opening Bowler**:",
                embed=xi_embed,
                view=view,
            )
        return callback


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
        ] or [discord.SelectOption(label="No eligible bowlers", value="none")]

        select = discord.ui.Select(placeholder="Select Bowler…", options=options)
        select.callback = self.on_select
        self.add_item(select)

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
        await interaction.response.edit_message(
            content=f"🎯 **{player['name']}** will bowl.",
            embed=None,
            view=None,
        )
        # "Comes into the attack" announcement
        await interaction.followup.send(
            content=f"**{player['name']}** ({player['ovr']}) comes into the attack"
        )
        embed = build_scoreboard_embed(self.game)
        view = BowlingView(self.game, self.channel_id)
        await interaction.followup.send(
            content=f"{self.game.bowling_user.mention} — choose your delivery:",
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

            # Remove bowling buttons, confirm delivery chosen
            await interaction.response.edit_message(
                content=f"**{self.game.current_bowler['name']}** : **{delivery}**",
                embed=None,
                view=None,
            )
            # Send batting prompt as new message
            view = BattingView(self.game, self.channel_id)
            await interaction.followup.send(
                content=f"🏏 {self.game.batting_user.mention} — **{self.game.striker['name']}**, play your shot:",
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

        options = [
            discord.SelectOption(
                label=f"{p['name']} (BAT:{p['bat']})",
                value=p["name"],
                description=f"{p['country']} | OVR:{p['ovr']}",
            )
            for p in game.get_available_batsmen()
        ]
        select = discord.ui.Select(placeholder="Select next Batsman…", options=options)
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

        await interaction.response.edit_message(
            content=f"🏏 **{player['name']}** selected.",
            embed=None,
            view=None,
        )
        # "Comes to the crease" announcement
        await interaction.followup.send(
            content=f"**{player['name']}** ({player['ovr']}) comes to the crease"
        )

        channel = interaction.channel
        if self.game.current_over_balls >= 6:
            self.game.end_over()
            available = self.game.get_available_bowlers()
            view = NextBowlerView(self.game, self.channel_id, available)
            embed = build_scoreboard_embed(self.game)
            await channel.send(
                content=f"**🔄 End of over!** {self.game.bowling_user.mention} — select your next bowler:",
                embed=embed,
                view=view,
            )
        else:
            await _send_bowling_prompt(channel, self.game)


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
                description=f"{p['bowling_type']} | {self._ov(p['name'])} ov bowled",
            )
            for p in available
        ] or [discord.SelectOption(label="No eligible bowlers", value="none")]

        select = discord.ui.Select(placeholder="Select next Bowler…", options=options)
        select.callback = self.on_select
        self.add_item(select)

    def _ov(self, name: str) -> str:
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

        await interaction.response.edit_message(
            content=f"🎯 **{player['name']}** starts a new over.",
            embed=None,
            view=None,
        )
        await interaction.followup.send(
            content=f"**{player['name']}** ({player['ovr']}) comes into the attack"
        )
        await _send_bowling_prompt(interaction.channel, self.game)
