# 🛰️ ORBIT WARS — Competition Dashboard

<div align="center">

`cid007 · Chirag Desai` &nbsp;·&nbsp; **Deadline: Jun 23, 2026** &nbsp;·&nbsp; 3,676 teams &nbsp;·&nbsp; *Updated: 2026-06-10*

</div>

---

## ⚡ At a Glance

<div align="center">

| 🏆 Best Ever | 📍 Current | 🎯 Rank | 📊 Percentile | 🤖 Agents Built | 📅 Days Left |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **1,197** | **1,167** | **#201 / 3,676** | **Top 5.4%** | **10** | **13** |

</div>

> **The jump:** Eight heuristic variants (v1–v8) topped out at **1,072**. One architecture switch to orbit_lite pushed the ceiling to **1,197** — a **+125 pt** gain over the heuristic limit, and **+200 pts** over v1's initial score.

---

## 🏅 Medal Progress

```
   BRONZE  ████████████████████████  100%  ✅ ACHIEVED   threshold ~1,100  (+97 margin)
   SILVER  ██████████████████████░░   91%  🎯 next goal  threshold ~1,226  ( -59 pts  )
     GOLD  ██████████████░░░░░░░░░░   57%  🔭 long game  threshold ~1,500  (-303 pts  )
           └───────────────────────┘
           progression from start (600) to each threshold
```

| Medal | Threshold | Our Best | Current Gap | Est. Rank Needed |
|:---:|:---:|:---:|:---:|:---:|
| 🥇 Gold | ~1,500+ | 1,197 | −303 | Top 37 (top 1%) |
| 🥈 Silver | ~1,226 | 1,197 | **−29 at peak** | Top 184 (top 5%) |
| 🥉 Bronze | ~1,100 | 1,197 | **+97** | Top 366 (top 10%) |

> **Silver gap is only 29 pts at our best.** v10_tuned (roi=1.2) + a horizon sweep could close it before Jun 23.

---

## 📈 Score Journey

```
 Score
  1260 ┤─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ Silver ─ ─ ─ ─  1226
       │                                                    ★ 1197
  1200 ┤                                              ╭────────────── 1197 (v9b peak)
       │                                        ╭─────╯
  1150 ┤                                  ╭─────╯           ┄┄ 1167 (v9 settled)
       │                                  │         ┄┄┄┄┄┄┄┄╯  1113 (v10, converging)
  1100 ┤─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ Bronze ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  1100
       │          ╭────────────────────────╯  ← orbit_lite jump
  1050 ┤     ─────╯   heuristic ceiling
       │  ──╮                            ╰──────────────────── 1072 (v1 ceiling)
  1000 ┤    ╰───────────────────────────────────────── v6·v7·v8 variants (~990–1008)
       │
   950 ┤   v3 crash (736)   v5 overfit (948)
       │
   600 ┤●  start (Jun 2, Glicko provisional)
       └──────────────────────────────────────────────────────────────
        Jun2    Jun3    Jun4    Jun5    Jun6    Jun7    Jun8    Jun9   Jun10
        v1↑     v1 pk   v6      ─       v7      v8      ─       v9★   v10↑
```

**Heuristic plateau (Jun 2–8):** Every v1–v8 variant converged to a band of 980–1,072.
No parameter change, physics improvement, or evaluation fix escaped the ceiling.
**orbit_lite jump (Jun 9):** Architecture switch to vectorized PyTorch garrison simulation → immediate +125 pts above the heuristic ceiling.

---

## 🤖 Agent Arsenal

| # | Agent | Architecture | Best LB | Δ vs v1 | Status | Why It Matters |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| v1 | `v1_starter` | safar1 heuristic · 3,605 lines | 1,072 | — | 💤 | Baseline; melis_evaluate bottleneck |
| v2 | `v2_roman` | romantamrazov mission-based | 980 | −92 | 💤 | 1,224 in April → 980 in June (field evolved) |
| v3 | `v3_pascal` | orbitbotnext (pascal) | 736 | −336 | 💤 | Runtime NameError on `_rear_prod_history` |
| v4 | `v4_momentum` | fresh build: MC + minimax | — | — | ⛔ | Lost 0/10 locally; never submitted |
| v5 | `v5_hybrid` | v1 + MC eval + momentum | 948 | −124 | 💤 | 2-rollout MC noise > heuristic signal |
| v6 | `v6_2p` | v1 + dynamic 2P mode | 1,008 | −64 | 💤 | 80% local win → LB regression (overfitting) |
| v7 | `v7_expand` | v1 + expand_k fix | 1,001 | −71 | 💤 | travel_mid=22 cut reach to far neutrals |
| v8 | `v8_realsim` | v1 + `ow.swept_pair_hit` eval | 990 | −82 | 💤 | Exact physics ≠ better decisions |
| **v9** | **`v9_producer`** | **orbit_lite PyTorch** | **1,167** | **+95** | **✅** | **Core breakthrough · +200 pts over start** |
| v9b | `v9_producer_b` | orbit_lite (2nd slot) | 1,197 | +125 | ✅ | Extra slot = 2× Glicko game volume |
| v10 | `v10_tuned` | orbit_lite · roi_threshold=1.2 | 1,113 | +41 | 🔄 | 75% local win vs v9; converging |

---

## 🧬 Architecture Deep Dive

### Heuristic Era (v1–v8) · Ceiling: 1,072

The evaluation loop in `v1_starter`:

```python
for candidate in actions:
    future = forward_project(world, candidate, turns=20)   # linear approximation
    score  = ships + 5 * planets + 8 * production_lead      # melis_evaluate
top_action = max(candidates, key=score)
```

Every improvement attempt was blocked by this ceiling:

| Experiment | Change | Local Result | LB Δ | Root Cause of Failure |
|:---|:---|:---:|:---:|:---|
| v5 MC eval | 2-rollout Monte Carlo rescore | ↑ slight | −124 | Rollout variance dominates signal at 2 samples |
| v6 2P mode | Dynamic pressure/patient switching | **+80% win** | −64 | Overfit to v1_starter's exact bug; LB field differs |
| v7 expand fix | expand_k_mid: 2→5 | +67% win | −71 | travel_mid=22 cut reach to far neutrals |
| v8 real-sim | `ow.swept_pair_hit` exact collision | ≈ parity | −82 | Decision quality, not physics accuracy, was the limit |

> **Critical insight:** The bottleneck was `melis_evaluate` itself — linear weights can't capture
> the garrison dynamics that orbit_lite resolves exactly. No amount of parameter tuning escapes
> a structural ceiling.

---

### orbit_lite Era (v9+) · Ceiling: 1,197+

The `sparse_launch_flow_delta()` core from `garrison_launch.py`:

```python
# Evaluate ALL candidate launches in parallel via batched tensor ops
Δflow = sparse_launch_flow_delta(
    launches,            # [C × L] candidate fleet dispatches
    garrison_status,     # PlanetGarrisonStatus — exact future garrison [P × T]
    horizon=18,
)
# Δflow[C, players] = net ship delta per candidate per player
roi   = Δflow[:, us] / ships_spent     # return on investment
picks = greedy_select(roi, roi_threshold=1.5)
```

How orbit_lite differs from melis_evaluate:

| Dimension | v1_starter | orbit_lite | Impact |
|:---|:---|:---|:---:|
| Evaluation method | Linear projection | Exact garrison tracking (PyTorch) | High |
| Candidate scoring | Serial Python loop | Batched tensor ops (all candidates at once) | High |
| Combat model | Approx circle check | Top-minus-second with exact ETA resolution | Medium |
| Fleet aim | Static angle | `intercept_aim()` with orbital prediction | Medium |
| Planning horizon | 20 turns (fixed) | 18 turns (configurable) | Low |
| Regroup logic | None | `_plan_regroup()` consolidates backline ships | Medium |
| Code (main agent) | 3,605 lines | 369 lines + 4,439 library | — |
| **LB ceiling** | **~1,072** | **1,197+** | **+125 pts** |

---

### Parameter Sensitivity (orbit_lite)

The only tuning done so far: **roi_threshold** (min score-per-ship to execute a launch)

```
roi_threshold    Behavior                  Local win vs v9   LB (est.)
─────────────    ────────────────────────  ────────────────  ─────────
    1.0          Very aggressive           untested          unknown
    1.2 ← v10   More launches per turn    75%  (9/12)       converging
    1.5 ← v9   Default (slawekbiel)       50%  (baseline)   1,167
    2.0          Conservative             untested          unknown
```

> Lower threshold = more fleet dispatches per turn = more pressure, but also more overextension risk.
> The 75% win rate of roi=1.2 over roi=1.5 in 12 local games is promising but not conclusive.

---

## 📊 Field Analysis

The competition has ~3,676 teams. Approximate score distribution from leaderboard snapshots:

```
Score     Approx teams  Distribution
──────    ────────────  ──────────────────────────────────────────────
1600+          ~5        ▌                 elite tier (Isaiah, 213tubo)
1500–1599      ~32       ████              gold zone   ← 37 teams
1400–1499      ~43       █████
1300–1399      ~55       ███████
1226–1299      ~100      ████████████      silver zone ← 184 teams
─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  ─ ─ ─ ─ ─ ─ ─ ─ ─ OUR PEAK 1197 ─ ─ ─ ─
1167–1225      ~90       ███████████       ← WE ARE HERE
─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
1100–1166      ~90       ███████████       bronze zone ← 366 teams
1000–1099      ~200      ████████████████████████
 900–999       ~250      █████████████████████████████
 800–899       ~300      ████████████████████████████████████
 600–799       ~500      ████████████████████████████████████████████
```

We are sitting **59 pts below the silver border** and **29 pts below it at our peak**.
The top 5% boundary (rank 184) is currently around 1,226. That band holds ~90 teams
within a 60-point window — it's competitive but reachable.

**Top of field context:**
- Rank 1: Isaiah @ Tufa Labs — **1,679** (likely MCTS or deep rollout search)
- Rank ~37: **~1,500** (gold floor)
- Rank ~184: **~1,226** (silver floor) ← our target
- Rank ~201: **1,167** ← us (current)
- Gap to silver: **59 pts** / gap at peak: **29 pts**

---

## ⚔️ Head-to-Head Record

| Matchup | W | L | Win% | Note |
|:---|:---:|:---:|:---:|:---|
| v9_producer vs v1_starter | 10 | 0 | **100%** | orbit_lite completely dominates heuristic |
| v10_tuned vs v9_producer | 9 | 3 | **75%** | roi=1.2 more aggressive, wins more |
| v4_momentum vs v1_starter | 0 | 10 | **0%** | from-scratch 800 lines vs 3,600 tuned |
| shummingfang48 vs v9 | 4 | 8 | **33%** | shum loses: size_multiplier per-turn overhead |

---

## 💡 Key Learnings

<details>
<summary><b>Click to expand: What failed and why</b></summary>

| Approach | Why It Seemed Good | Why It Failed | Lesson |
|:---|:---|:---|:---|
| MC evaluation (2 rollouts) | Stochastic search > deterministic heuristic | Signal/noise < 1 at only 2 samples | Need 20+ rollouts for MC to be useful |
| 2P mode fix (v6) | 80% win rate in self-play | Overfit to v1_starter's hardcoded-pressure bug | Benchmark diversity matters more than win % |
| expand_k tuning (v7) | More expansion sources = faster neutrals | travel_mid=22 cut off 23-50 unit neutrals | Parameter changes have cross-dependencies |
| Real-sim eval (v8) | Exact physics = better decisions | Decision quality ≠ physics accuracy | The evaluation **architecture** was the bottleneck |
| From-scratch build (v4) | Clean design, no tech debt | 800 lines vs 3,600 lines of tuned heuristics | Existing agents have thousands of implicit edge-case fixes |
| romantamrazov fork (v2) | Scored 1,224 in April | Field evolved; same code scores 980 in June | Stale agents lose to field evolution, not opponents |

</details>

### What Actually Works

| What | Mechanism | Gain |
|:---|:---|:---:|
| **orbit_lite library** | Vectorized PyTorch garrison flow-diff simulation | **+200 pts** |
| **roi_threshold=1.2** | More fleet launches per turn, higher pressure | +?? (converging) |
| **Two submission slots** | Same agent, 2× game volume → 2× Glicko convergence speed | faster rating |

### The Meta-Lesson

> Local benchmarks against a single opponent are **unreliable proxies** for LB performance.
> A 75–80% local win rate can mean: (a) you found a real improvement, or (b) you overfit to
> one opponent's weakness. The only reliable signal is the leaderboard.

---

## 🗺️ Roadmap

```
  Priority   Action                                    Exp. Gain     Effort
  ─────────────────────────────────────────────────────────────────────────
  ► NOW      Wait: v10_tuned (roi=1.2) converges       +30–60 pts?   passive
  ► HIGH     Try: horizon=22 (deeper planning)          unknown       1 kernel
  ► HIGH     Monitor: shummingfang48 (99 votes)         observe       passive
  ► MED      Decode: jek1wantaufik model (~1300 LB)     high value    1 day
  ► LOW      Terminal aggression: last 40 turns push    +10–20 pts    1 kernel
  ─────────────────────────────────────────────────────────────────────────
  TARGET     Silver medal by Jun 23                     need ~1226    13 days
```

---

## 🎮 What Is Orbit Wars?

<details>
<summary><b>Competition overview (click to expand)</b></summary>

A 2-player or 4-player real-time strategy game running 500 turns per match on a 100×100 map:

- **Planets** orbit the central sun (radius 10) at configurable angular velocity
- **Ships** are produced by planets each turn (production rate 1–5)
- **Fleets** travel at speed `1 + 5 × (log(ships)/log(1000))^1.5` — range [1.0, 6.0] units/turn
- **Combat** resolves as: top group − second group = survivor; if survivor > garrison, planet flips
- **Goal:** maximize total ships (planets + fleets) after 500 turns
- **Complication:** fleets destroyed if path crosses the sun (radius 10 + 1.5 margin)
- **Rating:** Glicko-style skill score; converges over ~50–100 games from a 600 provisional

**Key game mechanic:** Planets within orbital radius < 50 orbit continuously, making aim prediction
essential. orbit_lite's `intercept_aim()` computes exact arrival angles accounting for orbital motion;
v1_starter's heuristic used a static-position approximation.

**What separates top agents (~1500+):** Likely deeper lookahead (MCTS or full rollout search),
better multi-target coordination, and possibly learning-based value functions. No public RL agent
is competitive yet due to per-turn time budgets.

</details>

---

## 🔗 Active Kernels

| Kernel | Agent | Score | Status |
|:---|:---|:---:|:---:|
| [orbit-wars-v10-tuned](https://www.kaggle.com/code/cid007/orbit-wars-v10-tuned) | orbit_lite · roi=1.2 | 1,113 | 🔄 Converging |
| [orbit-wars-v9-producer](https://www.kaggle.com/code/cid007/orbit-wars-v9-producer) | orbit_lite default | 1,167 | ✅ Active |
| [orbit-wars-v9-producer-b](https://www.kaggle.com/code/cid007/orbit-wars-v9-producer-b) | orbit_lite default | ~1,139 | ✅ Active |

---

## 🔄 How to Update

When a new score lands:
1. **At a Glance** — update Best/Current/Rank/Percentile
2. **Medal Progress** — recalculate bars: `blocks = round((score−600)/(threshold−600) × 24)`
3. **Score Journey** — extend the ASCII chart right edge
4. **Agent Arsenal** — add a row with architecture, best LB, status
5. **Roadmap** — reprioritize based on current gap

---

<div align="center">
<sub>
v9_producer active · v10_tuned converging · competition ends Jun 23 2026<br>
<a href="dashboard.py">dashboard.py</a> generates the visual PNG version of this dashboard
</sub>
</div>
