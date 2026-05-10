
from __future__ import annotations
import discord


class GameState:
    def __init__(self, challenger: discord.Member, opponent: discord.Member, overs: int):
        self.challenger = challenger
        self.opponent = opponent
        self.overs = overs

        self.teams: dict[int, dict] = {}

        self.toss_winner_id: int | None = None
        self.batting_user_id: int | None = None
        self.bowling_user_id: int | None = None

        self.striker: dict | None = None
        self.non_striker: dict | None = None
        self.current_bowler: dict | None = None

        self.innings = 1
        self.runs = [0, 0]
        self.wickets = [0, 0]
        self.legal_balls = [0, 0]

        self.batsman_stats: dict[str, dict] = {}
        self.bowler_stats: dict[str, dict] = {}
        self.dismissed: list[str] = []
        self.bowler_ball_count: dict[str, int] = {}
        self.last_over_bowler: str | None = None

        self.partnership_runs = 0
        self.partnership_balls = 0

        self.timeline: list[str] = []
        self.pending_delivery: str | None = None

        self.current_over_balls = 0
        self.current_over_runs = 0

        self.phase = "pending"
        self.game_message: discord.Message | None = None

    @property
    def batting_user(self) -> discord.Member:
        return self.challenger if self.batting_user_id == self.challenger.id else self.opponent

    @property
    def bowling_user(self) -> discord.Member:
        return self.challenger if self.bowling_user_id == self.challenger.id else self.opponent

    @property
    def current_runs(self) -> int:
        return self.runs[self.innings - 1]

    @property
    def current_wickets(self) -> int:
        return self.wickets[self.innings - 1]

    @property
    def current_legal_balls(self) -> int:
        return self.legal_balls[self.innings - 1]

    def get_batting_team(self) -> dict:
        return self.teams[self.batting_user_id]

    def get_bowling_team(self) -> dict:
        return self.teams[self.bowling_user_id]

    def init_batsman_stats(self, player: dict):
        if player["name"] not in self.batsman_stats:
            self.batsman_stats[player["name"]] = {"runs": 0, "balls": 0}

    def init_bowler_stats(self, player: dict):
        if player["name"] not in self.bowler_stats:
            self.bowler_stats[player["name"]] = {"balls": 0, "runs": 0, "wickets": 0}

    def add_runs(self, runs: int):
        self.runs[self.innings - 1] += runs
        if self.striker:
            self.batsman_stats[self.striker["name"]]["runs"] += runs
        if self.current_bowler:
            self.bowler_stats[self.current_bowler["name"]]["runs"] += runs
        self.partnership_runs += runs
        self.current_over_runs += runs

    def add_legal_ball(self):
        self.legal_balls[self.innings - 1] += 1
        self.current_over_balls += 1
        self.partnership_balls += 1
        if self.striker:
            self.batsman_stats[self.striker["name"]]["balls"] += 1
        if self.current_bowler:
            name = self.current_bowler["name"]
            self.bowler_stats[name]["balls"] += 1
            self.bowler_ball_count[name] = self.bowler_ball_count.get(name, 0) + 1

    def add_wicket(self):
        self.wickets[self.innings - 1] += 1
        if self.current_bowler:
            self.bowler_stats[self.current_bowler["name"]]["wickets"] += 1
        if self.striker:
            self.dismissed.append(self.striker["name"])
        self.partnership_runs = 0
        self.partnership_balls = 0

    def rotate_strike(self):
        self.striker, self.non_striker = self.non_striker, self.striker

    def end_over(self):
        self.rotate_strike()
        self.last_over_bowler = self.current_bowler["name"] if self.current_bowler else None
        self.current_over_balls = 0
        self.current_over_runs = 0
        self.current_bowler = None

    def overs_str(self) -> str:
        inn = self.innings - 1
        completed = self.legal_balls[inn] // 6
        balls_in_over = self.legal_balls[inn] % 6
        return f"{completed}.{balls_in_over}"

    def bowler_overs_str(self, player_name: str) -> str:
        balls = self.bowler_ball_count.get(player_name, 0)
        return f"{balls // 6}.{balls % 6}"

    def sr(self, player_name: str) -> str:
        s = self.batsman_stats.get(player_name, {"runs": 0, "balls": 0})
        if s["balls"] == 0:
            return "0.00"
        return f"{(s['runs'] / s['balls']) * 100:.1f}"

    def crr(self) -> float:
        b = self.current_legal_balls
        if b == 0:
            return 0.0
        return round((self.runs[self.innings - 1] / b) * 6, 2)

    def rrr(self) -> float:
        if self.innings == 1:
            return 0.0
        target = self.runs[0] + 1
        needed = target - self.runs[1]
        balls_left = self.overs * 6 - self.current_legal_balls
        if balls_left <= 0 or needed <= 0:
            return 0.0
        return round((needed / balls_left) * 6, 2)

    def target(self) -> int | None:
        return self.runs[0] + 1 if self.innings == 2 else None

    def is_innings_over(self) -> bool:
        if self.current_wickets >= 10:
            return True
        if self.current_legal_balls >= self.overs * 6:
            return True
        if self.innings == 2 and self.runs[1] >= self.runs[0] + 1:
            return True
        return False

    def max_bowler_balls(self) -> int:
        max_overs = max(1, self.overs // 5)
        return max_overs * 6

    def get_available_bowlers(self) -> list[dict]:
        bowling_team = self.get_bowling_team()
        max_balls = self.max_bowler_balls()
        available = []
        for p in bowling_team["players"]:
            if p["bowling_type"] is None:
                continue
            if self.bowler_ball_count.get(p["name"], 0) >= max_balls:
                continue
            if p["name"] == self.last_over_bowler:
                continue
            available.append(p)
        return available

    def get_available_batsmen(self) -> list[dict]:
        batting_team = self.get_batting_team()
        current = set()
        if self.striker:
            current.add(self.striker["name"])
        if self.non_striker:
            current.add(self.non_striker["name"])
        return [
            p for p in batting_team["players"]
            if p["name"] not in self.dismissed and p["name"] not in current
        ]

    def start_second_innings(self):
        self.innings = 2
        self.batting_user_id, self.bowling_user_id = self.bowling_user_id, self.batting_user_id
        self.striker = None
        self.non_striker = None
        self.current_bowler = None
        self.dismissed = []
        self.bowler_ball_count = {}
        self.last_over_bowler = None
        self.partnership_runs = 0
        self.partnership_balls = 0
        self.timeline = []
        self.current_over_balls = 0
        self.current_over_runs = 0
        self.phase = "select_striker"

    def match_result(self) -> str:
        t1 = self.runs[0]
        t2 = self.runs[1]
        w_rem = 10 - self.wickets[1]
        b_rem = self.overs * 6 - self.legal_balls[1]

        if t2 > t1:
            winner = self.batting_user.display_name if self.innings == 2 else self.bowling_user.display_name
            return f"🏆 **{winner}** wins by **{w_rem} wicket{'s' if w_rem != 1 else ''}** ({b_rem} ball{'s' if b_rem != 1 else ''} remaining)!"
        elif t1 > t2:
            loser_user = self.batting_user if self.innings == 2 else self.bowling_user
            first_innings_runs = t1
            second_innings_runs = t2
            margin = first_innings_runs - second_innings_runs
            batting_first_user = self.bowling_user if self.innings == 2 else self.batting_user
            winner = batting_first_user.display_name
            return f"🏆 **{winner}** wins by **{margin} run{'s' if margin != 1 else ''}**!"
        else:
            return "🤝 **Match tied!** What a game!"
