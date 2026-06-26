# Orbit Wars — Experiment Log

Detailed record of every agent experiment, what changed, and what happened.

---

## v1_starter — Baseline
**Source:** public-baseline-kernel (public Kaggle kernel)  
**Lines:** 3605  
**LB Score:** 1072 (peak Jun 4), ~980 after field strengthened  
**Architecture:** Multi-horizon heuristic with HAMMER, COALITION, ANTI_SNIPE  

Key systems: `melis_evaluate` (forward projection), `search_step_action`,
`handle_hammer`, `handle_expand`, `handle_defense`, `handle_accumulator`

---

## v2_roman — mission-agent-kernel Fork
**Source:** mission-agent-kernel  
**Lines:** 3307  
**LB Score:** ~980 (April-vintage tuning doesn't survive field evolution)  
**What's different:** Mission-based planning (build_gang_up_missions,
build_elimination_missions, build_reinforce_missions), crash exploit  
**Lesson:** mission-agent-kernel's April score (1224) was vs weaker field.
Same code scores ~980 in June.

---

## v3_pascal — orbitbotnext (Fixed)
**Source:** orbit-next-kernel (Candidate 054)  
**Lines:** 3500  
**LB Score:** 736 (disappointing)  
**Bug found:** `_rear_prod_history` referenced but never defined → NameError
mid-game. Notebook ran fine but submission crashed during actual games.  
**Fix:** Removed the 23-line broken production-dominance history block.  
**Lesson:** Always test with `kaggle_environments.make()` before submitting —
syntax checks don't catch runtime NameErrors in game-state branches.

---

## v4_momentum — Fresh Build
**Architecture:** Built from scratch: momentum strike + MC evaluation +
2P minimax + multi-dispatch greedy expand  
**LB Score:** Never submitted (lost 0/12 vs v1_starter locally)  
**Why it failed:** 800 lines can't match 3600 lines of battle-tested
heuristics. The greedy expand only sent 1 fleet/turn in opening.
Minimax consumed time budget, blocking expansion.  
**Lesson:** Building from scratch to beat a well-tuned agent is very hard.
Graft ideas onto the existing base instead.

---

## v5_hybrid — v1_starter + 3 Ideas
**Changes from v1:**
- Momentum strike: `handle_momentum_strike()` in plan_moves
- MC evaluation: `mc_rescore_actions()` re-ranks top-5 candidates
- 2P minimax: `handle_minimax_2p()` for combat phase (step>80)

**LB Score:** 948 (WORSE than v1_starter)  
**Why:** MC with 2 rollouts too noisy — random variance worse than heuristic.
Momentum strike stole ships from HAMMER. Minimax added overhead.  
**Lesson:** Adding features to v1_starter hurts when each feature has noise
that overrides well-tuned baseline decisions.

---

## v6_2p — 2P Mode Fix
**Changes from v1:**
- `_detect_mode()`: dynamic 2P mode instead of hardcoded "pressure"
  (switch to "patient" only when prod_share < 42% AND step ≥ 60)
- Counter-attack: lower HAMMER threshold when enemy recently launched
- `MELIS_SANITY_THETA`: 3.0 → 1.5

**Local benchmark:** 80% win rate vs v1_starter (huge improvement!)  
**LB Score:** 1008 (WORSE than v1_starter)  
**Why:** Local benchmark against v1_starter was misleading. LB opponents at
~1000 rating don't have the same "hardcoded pressure" bug. MELIS_SANITY
lowering allowed bad moves. The 80% vs v1 was overfitting to one opponent.  
**Lesson:** Self-play benchmarks against one agent are unreliable. Need
diverse opponents to evaluate robustly.

---

## v7_expand — Expansion Fix Attempt
**Change from v6:** MODE_PARAMS_2P "pressure": expand_k_mid 2→5,
expand_max_travel_mid 52→22  
**Rationale:** "pressure" mode had expand_k_mid=2 (worst of all modes),
should expand more sources simultaneously.  
**Local benchmark:** 67% vs v1_starter, 50% production race wins  
**LB Score:** 1001 (WORSE)  
**Why:** travel_mid=22 cut reach too short — missed neutrals at 23-50 units.
The production race gains against v1 didn't help against LB field.  
**Lesson:** Parameter changes that improve against one specific opponent
(v1_starter) often hurt against the broader field.

---

## v8_realsim — Real Game Engine Evaluation
**Change from v1:** Replace `melis_evaluate` top-5 candidate re-scoring
with `real_evaluate()` using `ow.swept_pair_hit` for exact physics.  
**Bug fixed:** `p[2], p[3] = ppaths[p[0]]` stored (old,new) tuple pair
into planet x,y instead of unpacking new position → TypeError on step 2+.  
**Local benchmark:** 50% vs v1_starter (parity)  
**LB Score:** 990 (no improvement)  
**Why:** The evaluation function isn't the bottleneck at this rating level.
The real bottleneck is the architecture: heuristic HAMMER/expand vs
vectorized flow-diff simulation.  
**Lesson:** Accurate physics alone doesn't help if the decision-making
framework is the bottleneck.

---

## v9_producer — orbit_lite BREAKTHROUGH ★
**Source:** orbit_lite-producer-kernel + orbit_lite PyTorch library  
**Lines:** 369 (main.py) + 4439 (orbit_lite package)  
**LB Score:** **1191.6** (~rank 200/3676, top 5.4%)  
**Submitted as:** submission.tar.gz (main.py + orbit_lite/ directory)  

**Why it works:**
- `sparse_launch_flow_delta()`: vectorized PyTorch tensor computation of
  "if I send N ships from planet A to planet B, how does every player's
  ship count change over the next 18 turns?" — batched over all candidates
- `PlanetGarrisonStatus`: exact garrison simulation tracking all known
  arrivals over a future horizon (vs v1's approximate linear projection)
- `reachable_mask`: strict superset gate ensures fleets can actually reach
- `_plan_regroup`: consolidates ships from backline planets to frontline

**vs v1_starter locally:** 10/10 wins  
**vs v1_starter LB:** +200 points (1191 vs 980)

**Deployment note:** orbit_lite embedded directly in 16 notebook cells
(%%writefile orbit_lite/<module>.py) — no external dataset dependency.

---

## Key Benchmarking Lessons

1. **Local benchmark vs single opponent is unreliable** for predicting LB.
   v6 won 80% vs v1 but scored LOWER on LB.

2. **Check win rate against diverse opponents** — use random, v1, v3, v9
   together to get a more representative sample.

3. **Always test with `kaggle_environments.make()`** before submitting —
   catches runtime errors that syntax checks miss.

4. **The Glicko system needs 50-100 games to converge** — don't panic at
   the initial 600 provisional score.

5. **The field strengthens over time** — an agent scoring 1224 in April
   scores ~980 in June as better agents join.
