# Orbit Wars — Competition Progress Report

**Competition:** [Orbit Wars](https://www.kaggle.com/competitions/orbit-wars)  
**Deadline:** June 23, 2026  
**Team:** cid007 (Chirag Desai)

---

## Current Best Score

| Agent | LB Score | Est. Rank | Medal Zone |
|---|---|---|---|
| **v9_producer (orbit_lite)** | **1191.6** | **~200 / 3676** | **Bronze ✓ — Silver edge** |

Bronze threshold: top 10% (~366 teams)  
Silver threshold: top 5% (~184 teams) — need ~1220+  
Gold threshold: top 1% (~37 teams)

---

## Score History

| Date | Agent | Score | Notes |
|---|---|---|---|
| Jun 2 | v1_starter | 600 → 1072 | Initial submission, converged to 1072 |
| Jun 3 | v3_pascal | 736 | romantamrazov fork, had crash bug |
| Jun 3 | v5_hybrid | 948 | v1 + MC eval + momentum + minimax — hurt performance |
| Jun 4 | v1_starter (peak) | **1072** | Best heuristic score |
| Jun 5 | v6_2p | 1008 | 2P mode fix — slight regression |
| Jun 6 | v7_expand | 1001 | Expansion param change — regression |
| Jun 7 | v8_realsim | 990 | Real-sim evaluator — no improvement |
| **Jun 9** | **v9_producer** | **1191.6** | **orbit_lite breakthrough** |

---

## Agents Directory

```
agents/
├── v1_starter/      # safar1 fork — 3605-line heuristic, ceiling ~1072
├── v2_roman/        # romantamrazov agent (~1224 LB in April, now ~980)
├── v3_pascal/       # orbitbotnext (pascal), had _rear_prod_history crash bug
├── v4_momentum/     # fresh-build with momentum/MC/minimax — lost 0/10 vs v1
├── v5_hybrid/       # v1 + momentum strike + MC eval + 2P minimax
├── v6_2p/           # v1 + dynamic 2P mode + counter-attack window
├── v7_expand/       # v6 + expand_k_mid fix — hurt production race
├── v8_realsim/      # v1 + ow.swept_pair_hit real simulation
├── v9_producer/     # slawekbiel orbit_lite — CURRENT BEST ★
├── slawekbiel/      # Reference: the-producer-agent (orbit_lite, 150 votes)
├── romantamrazov/   # Reference: original romantamrazov agent
├── romantamrazov_v2/ # Reference: i-m-stronger (same orbit_lite as slawek)
├── orbit_lite_pkg/  # The orbit_lite PyTorch library (4439 lines)
├── ajayrao43_v12/   # Reference: oribt-war-12 (v1_starter + docstrings only)
├── djenkivanov/     # Reference: 808-line independent impl using ow module
├── pascalledesma/   # Reference: orbitbotnext (has crash bug)
├── pascalledesma_v14/ # Reference: orbitwork-v14 (dead stub _eval_moves)
├── kuni05/          # Reference: lb-1240 torch-based agent
└── vkhydras/        # Reference: v1_starter copy (their real agent is private)
```

---

## What We Learned

### The Architecture Ceiling (~1072)
All v1_starter variants (safar1, v2_roman, v3_pascal, v5-v8) converge to
~980–1072. The ceiling is structural: the `melis_evaluate` linear projection
and Python-loop simulation are not accurate enough to consistently beat
mid-tier agents. Local win-rate benchmarks against v1_starter were misleading —
improving against one specific opponent doesn't translate to the broader field.

### The orbit_lite Breakthrough
The `orbit_lite` library (slawekbiel/producer-orbit-wars-utils) uses:
- **PyTorch vectorized garrison flow simulation** over an 18-turn horizon
- **`sparse_launch_flow_delta`**: "if I launch this fleet, how does every
  player's ship count change over 18 turns?" — exact competitive delta
- **Batched candidate scoring**: evaluates all (source, target) pairs in
  parallel via tensor ops, vs our serial Python loop
- **`swept_pair_hit`** for exact orbital collision detection

Result: 10/10 wins against v1_starter locally, 1191.6 on LB vs ~980 for v1.

### Competition Field Evolution
The field strengthened significantly over the competition:
- Jun 2: bronze ~1100, top score ~1817
- Jun 9: bronze ~1350+, top score ~1735

Agents that scored 1224 in April now score ~980. Staying current with the
field requires using the best available architectures.

### What Does NOT Help
- **MC evaluation with 2 rollouts**: too noisy, hurts action quality
- **Momentum strike on v1_starter**: correct idea but parameters hard to tune
- **2P mode fixes**: local benchmarks misleading — LB opponents don't have
  the same v1_starter "hardcoded pressure" bug
- **Expansion parameter changes**: fragile, field-dependent
- **Real-sim evaluation on v1_starter**: not enough improvement to overcome
  the fundamental evaluation function limit

---

## Current Active Kernels

| Kernel | Agent | Status |
|---|---|---|
| orbit-wars-v9-producer | orbit_lite (slawekbiel) | Active — 1191.6 |
| orbit-wars-v9-producer-b | orbit_lite (slawekbiel) | Running — accelerate convergence |

---

## Next Steps (ranked by expected impact)

1. **Wait for v9_producer to fully converge** — Glicko needs 50-100 games.
   If it reaches 1220+ we're in silver.

2. **Tune ProducerLiteConfig** — current config is slawekbiel's defaults.
   Key params to tune: `roi_threshold` (1.5), `horizon` (18), `max_waves_per_turn` (6).
   Lower `roi_threshold` → more aggressive; raise `horizon` → deeper planning.

3. **Check newer orbit_lite versions** — romantamrazov has been iterating
   ("i-m-stronger" → may have newer orbit_lite package).

4. **Study 1500+ agents** — top agents (Isaiah, 213tubo, TonyK) are using
   something beyond orbit_lite. Possible MCTS or deeper search.
