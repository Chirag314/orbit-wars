# Orbit Wars — Full Competition Analysis
*Generated: 2026-06-02*

---

## 1. Competition Overview

**Slug**: `orbit-wars`
**Kaggle URL**: https://www.kaggle.com/competitions/orbit-wars
**Category**: Featured | **Prize**: $50,000 USD | **Teams**: 3,656
**Submission deadline**: June 23, 2026 23:59 UTC
**Final evaluation**: June 24 – July 8, 2026 (games continue running to convergence)

### Medal Thresholds (3,656 teams)
| Medal | Rank Cutoff | Score Est. (June 2) |
|---|---|---|
| Gold | Top 37 (~1%) | 1600+ |
| Silver | Top 183 (~5%) | ~1400 |
| Bronze | Top 366 (~10%) | ~1100–1150 |

---

## 2. Game Mechanics (Complete Reference)

### Board
- 100×100 continuous coordinate plane
- Sun at (50, 50), radius = 10 units
- Fleets destroyed if travel path crosses sun (radius 10 + safety margin 1.5)
- Boundary: fleets lost if they exit [0, 100]²

### Planets
- Each planet has: `id, owner, x, y, radius, ships, production`
- `radius = 1 + ln(production)` where production ∈ {1, 2, 3, 4, 5}
- Planets with `orbital_radius + planet_radius < 50` orbit the sun with `angular_velocity` (radians/turn)
- Planets with `orbital_radius + planet_radius >= 50` are static
- Owned planets: produce `production` ships/turn
- Neutral planets (`owner = -1`): don't produce, captured by first fleet with > garrison

### Fleets
- `[fleet_id, owner, x, y, angle, from_planet_id, ships]`
- Speed: `1.0 + 5.0 * (log(ships)/log(1000))^1.5` — range [1.0, 6.0] units/turn
  - 1 ship = 1.0 u/t | 10 ships ≈ 1.5 | 100 ships ≈ 2.8 | 1000 ships = 6.0
- Launch format: `[from_planet_id, angle_radians, num_ships]`
- Fleet fires straight line from planet surface

### Combat
- Multiple fleets arriving same turn: all combat resolved simultaneously
- Rule: sort by count descending — top group minus second group = survivor
- If tie (two largest equal): all eliminated (survivor = 0)
- Survivor reinforces if same owner as defender, or flips ownership if > garrison

### Comets
- Special "wandering planets" with precomputed trajectory paths
- Ignore for v1 — too complex, low priority

### Scoring & Rating
- Win = more total ships at turn 500 than all opponents
- Rating: Glicko-like system — not margin-sensitive, just win/loss/tie
- Each submission plays ~500+ episodes; newer submissions get more games for faster convergence
- Final score stabilizes over the June 24–July 8 evaluation window

---

## 3. Leaderboard Analysis (June 2, 2026)

### Top 20 Scores (Jun 2, 2026 snapshot — names redacted)
```
 1.  [Competitor 01]   1816.9
 2.  [Competitor 02]   1683.0
 3.  [Competitor 03]   1639.0
 4.  [Competitor 04]   1610.5
 5.  [Competitor 05]   1609.0
 6.  [Competitor 06]   1602.6
 7.  [Competitor 07]   1592.1
 8.  [Competitor 08]   1576.6
 9.  [Competitor 09]   1560.4
10.  [Competitor 10]   1549.8
11.  [Competitor 11]   1529.6
12.  [Competitor 12]   1518.4
13.  [Competitor 13]   1512.2
14.  [Competitor 14]   1507.2
15.  [Competitor 15]   1505.8
16.  [Competitor 16]   1502.6
17.  [Competitor 17]   1490.9
18.  [Competitor 18]   1478.1
19.  [Competitor 19]   1476.2
20.  [Competitor 20]   1471.9
```

### Key Observations
- Top-1 gap to Top-20: 345 points — significant, but scores are compressing mid-field
- Field is still improving; expect scores to rise ~10% by deadline
- Bronze floor estimated ~1100–1150 based on field size and score distribution
- **Our baseline (public-baseline-kernel)** is right at estimated bronze — need +50–100 pts to be safely in

### Score Distribution Estimate
Based on the top-20 range (1471–1817) and a typical Glicko distribution:
- 1400–1817: top ~50 teams (Gold zone)
- 1200–1400: top ~150 teams (Silver zone)
- 1000–1200: top ~400 teams (Bronze zone, rough)
- <1000: bottom 3,256 teams

---

## 4. Public Agent Analysis

### public-baseline-kernel (our v1 baseline)
- ~3,606 lines of pure Python heuristic
- **Confirmed rating: ~1101** (at/near bronze floor)
- Architecture: `World` state parser → `forward_project()` → `melis_evaluate()` → tactical systems
- Version markers suggest ~v128 internal iteration
- Key parameters (tunable at top of file):
  ```python
  SO1_STATIC_BONUS_4P = 2.95474    # prefer static planets
  VALUE_WEIGHT_2P = 4.86118        # ship-vs-position weight
  HAMMER_PROD_SHARE_TRIGGER = 0.40 # when to hammer
  MELIS_SANITY_THETA = 3.0         # 2P sanity gate
  ```

### extended-heuristic-kernel (best public kernel, 56 votes)
- ~4,869 lines — 1,263 lines added over public-baseline
- Appears to be a direct extension of public-baseline codebase
- Contains more inline comments; added features unknown without deeper diff
- Likely scores 1150–1250 based on vote count and recency

### independent-impl-kernel (55 votes)
- Independent implementation
- May offer genuine architectural diversity
- Worth studying for alternative approaches (not just param tweaks)

### exp-agent-kernel (multiple exp28–31, 18–35 votes each)
- Active iterating competitor
- Kernel iterations are near-identical (testing small changes) — similar to our BirdCLEF approach
- Good proxy for mid-field competition velocity

---

## 5. Agent Architecture Deep Dive (public-baseline v1101)

### Core Loop (per turn)
```
observation → World() → tactical systems → list of [planet, angle, ships]
```

### World Class
Computes on init:
- `arrivals_by_planet`: which fleets hit which planets and when (via `fleet_target_planet()`)
- `owner_strength`, `owner_production`, `my_prod_share`
- `mode`: patient / opportunistic / pressure
- Multiple `stop_expand_*` flags controlling expansion behavior
- `enemy_race_eta`: earliest turn enemy can take each neutral

### forward_project(horizon=20)
- Simulates planet production + fleet arrivals for H turns
- Returns `{planet_id: (owner, ships)}` at horizon
- Optional `project_opponent_moves`: enemy planets emit 40% of surplus toward closest non-friendly every 4 turns
- Used in `melis_evaluate()` to score hypothetical actions

### melis_evaluate(action=None)
- Aggregated score across multiple time horizons (4, 8, 14, 20 turns)
- Score = `(my_ships - leader_ships) + 5*(my_planets - leader_planets) + 8*(my_prod - leader_prod)`
- Called for every candidate action; picks highest-gain action
- 2P: decays score by `0.97^arrival_turn` to prefer fast captures

### Tactical Systems (in priority order)
1. **HAMMER** (turn ~40+): Concentrated attack from multiple planets on single high-production target
2. **MEGA_HAMMER** (4P only): When 300+ ships available, all-in on fortified target
3. **COALITION**: Multi-source coordinated attack
4. **ANTI_SNIPE**: Block enemy intercepts of our fleets
5. **COUNTER_SNIPE**: Intercept enemy fleets
6. **CHEAP_PICKUP** (4P only): Low-risk neutral grabs
7. **expand** (search_step_action): Normal expansion via MELIS evaluation

### 2P-Specific Logic
- `is_2p = True` whenever only 2 players exist
- 2P mode always returns "pressure" from `_detect_mode()` (known simplification)
- 2P patient escalation: after 20 turns of no prod-share gain → force pressure mode
- `STOP_EXPAND_2P_ENABLED`: when prod_share ≥ 0.65, stop expanding, focus combat

---

## 6. Improvement Roadmap

### Tier 1: Quick Wins (Days 1–5, estimated +30–100 pts)
1. **Submit v1_starter**: Get a live score as baseline. Validate we understand submission format.
2. **Diff extended-heuristic-kernel vs public-baseline**: ~1,263 added lines. Cherry-pick meaningful new logic.
   - Focus: new tactical systems, 2P improvements, any new HAMMER variants
3. **Fix 2P mode detection**: `_detect_mode()` always returns "pressure" in 2P — this is a stub that may hurt. Study what "patience" would look like in 2P.

### Tier 2: Targeted Improvements (Days 5–14, estimated +50–150 pts)
4. **Local arena testing**: Download `local-arena-dataset` dataset, run agents against each other locally to test changes without Kaggle submissions.
5. **Parameter sweep on MELIS weights**: score = ships + 5×planets + 8×prod. Try different weights for 2P vs 4P.
6. **Orbital aim accuracy**: Current `aim_at_target()` iterates 6 times but converges by distance, not angle error. Potential aim miss on fast orbital planets.

### Tier 3: Research (Days 14–21, +100–300 pts if successful)
7. **Deeper look at top-1817 agent** (competition leader): Private — can only observe via LB position. Check if they have public notebooks or forum posts.
8. **Time-limited MCTS**: 1-step lookahead is current depth. Adding even 2-step with pruning could matter for 2P endgame.
9. **Better endgame**: Late-game (turn 450+) flush logic is basic. Production-weighted optimal redistribution matters.

---

## 7. Submission Workflow

### Option A: Direct file submission (fast)
```bash
cd /data/orbit_wars/agents/v2/
kaggle competitions submit orbit-wars -f submission.py -m "v2: ajay merge"
```

### Option B: Notebook kernel submission (preferred)
Create a Kaggle notebook that:
1. Writes `submission.py` to `/kaggle/working/`
2. Set as a competition submission output

This matches the public-baseline pattern (kernel output is `submission.py`).

### Submission Limits
- 5 submissions per day
- Last 2 submissions are tracked for final ratings
- Episode games continue after June 23 through July 8

---

## 8. Key Risks

| Risk | Probability | Mitigation |
|---|---|---|
| Score degrades after ajay merge | Medium | Test locally first, compare agent vs agent |
| Bronze floor rises above 1150 before June 23 | Medium | Submit early; 21 days of field improvement |
| Top agents are private and well-defended | High | Focus on steady improvement, not catching top-1 |
| Kaggle episode randomness causes rating variance | High | Submit multiple versions, track average trend |

---

## 9. Resources

- Competition rules: https://www.kaggle.com/competitions/orbit-wars/rules
- Local arena dataset: `kaggle datasets download local-arena-dataset`
- Public baseline kernel: `/data/orbit_wars/agents/v1_starter/submission.py`
- extended-heuristic-kernel v12: `kaggle kernels output extended-heuristic-kernel` (already at `/tmp/orbit_ajay/submission.py`)
- Local arena kernel: `kaggle kernels output [independent-impl-kernel]`
