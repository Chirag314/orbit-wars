# CLAUDE.md — Orbit Wars

## Competition Phase
Phase 1 — ACTIVE. Entry in progress. Deadline: June 23, 2026.
Starting from safar1/lb-score-1101 (~1101 rating). Bronze threshold: ~top 366 of 3,656 teams.

## Task Summary
Game AI competition. Submit a Python agent (`submission.py`) that plays Orbit Wars:
- 100×100 continuous 2D board, sun at center (50, 50, radius 10)
- Each player starts with one home planet
- Goal: maximize total ships (planets + fleets) after 500 turns
- 2-player or 4-player free-for-all
- Rating: Glicko-style skill score from win/loss outcomes

## Agent Interface
Agent receives an observation dict with:
- `player` — your player index
- `step` — current turn (0–499)
- `planets` — list of [id, owner, x, y, radius, ships, production]
- `fleets` — list of [id, owner, x, y, angle, from_planet_id, ships]
- `initial_planets` — planets at turn 0 (for orbital prediction)
- `angular_velocity` — planet orbit speed (radians/turn)
- `comet_planet_ids`, `comets` — comet mechanics
Agent returns: list of [from_planet_id, angle_radians, num_ships]

## Game Physics (Critical)
- Planet radius = 1 + ln(production); production 1–5
- Fleet speed: `1 + 5 * (log(ships)/log(1000))^1.5`; range [1.0, 6.0] units/turn
- Planets within orbital_radius < 50 orbit the sun; static beyond 50
- Fleets destroyed if path crosses sun (radius 10 + safety margin 1.5)
- Combat: attacker group vs defender — top minus second survivor, flips owner if survivor > garrison
- Neutral planets (owner=-1) don't produce; captured by first fleet with > garrison ships

## Score Scale and Medal Thresholds
As of June 2, 2026 (3,656 teams):
- Top score: ~1817 (Isaiah @ Tufa Labs)
- Gold: top ~37 teams (top 1%)
- Silver: top ~183 teams (top 5%)
- Bronze: top ~366 teams (top 10%) — estimated score ~1100–1150
- Starting baseline (safar1 v1101): ~1101 — at/near bronze floor

## Hard Rules
- Do not rescan the whole codebase unless asked
- Read only files needed for the current task
- One experiment at a time — test before suggesting next
- All agents must be private kernels on Kaggle
- Keep agents as single-file `submission.py` for Kaggle submission format
- Before editing, summarize current state + exact change
- Prefer minimal diffs over rewrites

## Current Agent Architecture (v1_starter — safar1 1101)
`agents/v1_starter/submission.py` — ~3,600 lines pure Python heuristic

Key systems:
| System | Description |
|---|---|
| `World` class | Parses observation, computes arrivals, orbital positions, mode |
| `forward_project()` | Simulate future planet states with arrival/combat resolution |
| `melis_evaluate()` | Multi-horizon score (ships + 5×planets + 8×production advantage) |
| HAMMER / MEGA_HAMMER | Concentrated attack on high-value targets when stockpile ≥ threshold |
| COALITION | Multi-source coordinated attack |
| `_detect_mode()` | patient/opportunistic/pressure based on enemy aggression |
| ANTI_SNIPE / COUNTER_SNIPE | Detect and block enemy intercepts |
| RACE detection | Don't send to neutrals enemy will win first |

Known parameter knobs (config block at top):
- `SO1_STATIC_BONUS_4P = 2.95474` — prefer static (non-orbiting) planets
- `VALUE_WEIGHT_2P = 4.86118` — ship-vs-position weight in 2P
- `HAMMER_PROD_SHARE_TRIGGER = 0.40` — when to use hammer
- `MELIS_SANITY_THETA = 3.0` — 2P: skip action if gain < this

## Experiment Queue
| # | Experiment | Expected Gain | Cost |
|---|---|---|---|
| 1 | Fork safar1 to private kernel; verify it runs and posts a score | baseline | Low |
| 2 | Diff ajayrao43/v12 (4869 lines) vs safar1 (3606 lines); cherry-pick improvements | +30–80 pts | Medium |
| 3 | Tune SO1/VALUE_WEIGHT/HAMMER params via local arena | +10–30 pts | Medium |
| 4 | Improve 2P mode (currently always returns "pressure") | unknown | Medium |
| 5 | Orbital aim improvement — precomputed path for comets | +?? | High |

## What We Know About the Top Agents
- AjayRao43 `oribt-war-12` (56 votes) — extended fork of safar1, ~4869 lines; likely scores 1200+
- vkhydras / penguin069 (55 votes) — independent implementation; worth studying for diversity
- Top agents (1600+) appear to use deeper search, better 2P handling, and possibly MCTS
- No public RL agents are competitive yet (too slow per turn)

## Default Workflow
1. Read only relevant files
2. Summarize current state in 5 bullets max
3. Identify biggest bottleneck
4. Propose 1–3 next actions
5. Edit only after approval

## Output Style
Always return:
- Summary of change
- Why it helps
- Exact files to edit
- Recommended next command/prompt
