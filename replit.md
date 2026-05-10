# Cricket Strike Bot

A feature-complete Discord cricket game bot built in Python. Two users play a full T20-style match ball-by-ball using Discord buttons and dropdowns.

## Run & Operate

- **Discord Bot**: `cd discord-bot && python3 main.py` (runs via "Discord Cricket Bot" workflow)
- Required env: `DISCORD_BOT_TOKEN` — Discord bot token (already set in secrets)

## Stack

- Python 3.11 + discord.py 2.x
- In-memory game state (per channel)
- pnpm workspaces (Node.js API server also available)

## Where things live

- `discord-bot/main.py` — Bot entry point, command handlers (`!cs start`, `!cs cancel`, `!cs score`, `!cs xi`)
- `discord-bot/game.py` — `GameState` class (full match state)
- `discord-bot/views.py` — All Discord UI: buttons, dropdowns, game flow logic
- `discord-bot/logic.py` — Delivery outcome calculation (ball type × shot type matrix + OVR modifiers)
- `discord-bot/embeds.py` — Scoreboard, Playing XI, and result embeds
- `discord-bot/commentary.py` — Dynamic commentary text for each outcome
- `discord-bot/data.py` — Constants: custom emojis, sample teams (India & Australia), ball speeds, matchup data

## Commands

| Command | Description |
|---|---|
| `!cs start @user <overs>` | Challenge a user to a match (default 20 overs) |
| `!cs cancel` | Cancel the current match |
| `!cs score` | Show current scoreboard |
| `!cs xi` | Show your Playing XI |

## Game Flow

`Challenge → Accept/Decline → Toss (Head/Tail) → Bat/Bowl choice → Select Striker + Non-Striker → Select Bowler → Ball-by-ball play (Bowling buttons → Batting buttons) → Wicket/Over events → 2nd Innings → Result`

## Architecture decisions

- Game state is keyed by `channel_id` — one match per channel at a time
- Bowling buttons dynamically change based on bowler type (Fast / Off Spin / Leg Spin)
- Outcome uses a (delivery × shot) probability matrix with OVR difference modifier
- Wides/No-balls don't count as legal deliveries; strike rotates on 1 or 3 runs and at over end
- Max 1/5th of total overs per bowler; no consecutive overs

## Customising Teams

Edit `discord-bot/data.py` → `SAMPLE_TEAMS` to add your own players with custom OVR/BAT/BOWL stats, roles, bowling types, and card icons.

## User preferences

- Custom Discord emoji IDs baked into timeline and toss buttons
- Command prefix: `!cs`

## Gotchas

- One active match allowed per channel
- Bot needs `Message Content Intent` enabled in Discord Developer Portal
- Bot needs `Send Messages`, `Embed Links`, `Read Message History` permissions in your server
