# 🛰️ Orbit Wars — Live Competition Dashboard

> **Team:** cid007 (Chirag Desai) &nbsp;|&nbsp; **Deadline:** June 23, 2026 &nbsp;|&nbsp; **Total Teams:** ~3,676

---

## 🏅 Medal Tracker

```
Gold   ████░░░░░░░░░░░░░░░░░░░░░░░░  Top 1%  (~37 teams)   Need: ~1500+
Silver ████████████████████░░░░░░░░  Top 5%  (~184 teams)  Need: ~1226   ← 59 pts away
Bronze ████████████████████████████  Top 10% (~366 teams)  ✅ ACHIEVED    rank ~201
──────────────────────────────────
Us     ██████████████████░░░░░░░░░░  1167  (rank ~201)
```

| Medal | Threshold Score | Required Rank | Status |
|-------|----------------|---------------|--------|
| 🥇 Gold | ~1500+ | Top 37 | ❌ Far |
| 🥈 Silver | ~1226 | Top 184 | 🔄 59 pts away |
| 🥉 Bronze | ~1100 | Top 366 | ✅ **Achieved** |

---

## 📊 Current Leaderboard Position

| Metric | Value |
|--------|-------|
| **Best Active Score** | **1166.9** (v9_producer) |
| **Estimated Rank** | ~201 / 3,676 |
| **Percentile** | Top 5.4% |
| **Peak Score Ever** | 1197 (v9_producer_b, Jun 9) |
| **Competition Leader** | 1679 (Jake Will) |
| **Silver Border (rank 184)** | ~1226 |

---

## 🚀 Agent History

| # | Agent | Architecture | LB Score | Peak | Status | Key Change |
|---|-------|-------------|----------|------|--------|-----------|
| v1 | `v1_starter` | safar1 heuristic (3605 lines) | 991 | **1072** | Inactive | Baseline |
| v2 | `v2_roman` | romantamrazov (mission-based) | 980 | 980 | Inactive | Gang-up, elimination missions |
| v3 | `v3_pascal` | orbitbotnext (bugfixed) | 736 | 736 | Inactive | Had crash bug (_rear_prod_history) |
| v4 | `v4_momentum` | Fresh build (momentum+MC+MM) | — | — | Never submitted | Lost 0/10 vs v1 locally |
| v5 | `v5_hybrid` | v1 + MC eval + momentum + minimax | 948 | 948 | Inactive | All additions hurt |
| v6 | `v6_2p` | v1 + dynamic 2P mode | 1008 | 1008 | Inactive | 80% local win but LB regression |
| v7 | `v7_expand` | v1 + expand_k fix | 1000 | 1000 | Inactive | expand_k_mid 2→5 hurt production |
| v8 | `v8_realsim` | v1 + `ow.swept_pair_hit` eval | 990 | 990 | Inactive | No improvement over v1 ceiling |
| v9 | `v9_producer` | **orbit_lite PyTorch** (slawekbiel) | 1167 | **1197** | ✅ **Active** | +200 pts over v1 |
| v9b | `v9_producer_b` | Same as v9 (2nd slot) | 1139 | 1197 | ✅ Active | Doubles game volume |
| v10 | `v10_tuned` | orbit_lite, roi_threshold=1.2 | 1113 | 1113 | 🔄 Converging | 75% win rate vs v9 locally |

---

## 📈 Score Timeline

```
1200 ┤                                              ★ 1197 (peak)
1180 ┤                                        ╭───╮
1160 ┤                                  ╭─────╯   ╰──── 1167
1140 ┤                            ╭─────╯
1120 ┤                      ╭─────╯
1100 ┤                ╭─────╯
1080 ┤          ╭─────╯ 1072 ← v1 peak
1060 ┤    ╭─────╯
1040 ┤────╯
      Jun2  Jun3  Jun4  Jun5  Jun6  Jun7  Jun8  Jun9  Jun10
      v1    v3    v1pk  v6    v7    v8    v9A   v9B   v10
      base  pasc  1072        fail  fail  1167  1197  cnvg
```

---

## 🔬 What We Learned

### ❌ What Doesn't Work
| Approach | Why It Failed |
|----------|--------------|
| MC evaluation (2 rollouts) | Too noisy — variance worse than stable heuristic |
| 2P mode fixes | Benchmarked vs v1_starter only — LB field doesn't have same bug |
| Expansion parameter changes | Fragile, opponent-specific |
| From-scratch builds | 800 lines can't compete with 3600 lines of tuned heuristics |
| Real-sim eval on v1 | Accurate physics doesn't fix evaluation architecture limit |

### ✅ What Works
| Approach | Gain |
|----------|------|
| **orbit_lite PyTorch library** | **+200 pts** (980→1167+) |
| `roi_threshold` tuning (1.5→1.2) | **+?** (v10 converging, 75% local) |

### 💡 Key Insights
- **Local self-play benchmarks are unreliable** — v6 won 80% vs v1 but scored worse on LB
- **Same agent twice** accelerates Glicko convergence (more games = faster rating)
- **The orbit_lite library** uses vectorized PyTorch garrison flow-diff simulation vs our serial Python loops — fundamentally better architecture
- **Field evolves fast** — a 1224 score in April is ~980 today

---

## 🧠 Architecture Comparison

| | v1_starter | orbit_lite (v9/v10) |
|--|-----------|-------------------|
| **Core eval** | Linear forward projection | Vectorized garrison flow-diff |
| **Candidate scoring** | Serial Python loop | Batched PyTorch tensor ops |
| **Physics** | Approx circle check | `ow.swept_pair_hit` exact sweep |
| **Horizon** | 20 turns | 18 turns (configurable) |
| **Lines** | 3,605 | 369 (main) + 4,439 (library) |
| **LB ceiling** | ~1072 | 1197+ |

---

## 🎯 Next Steps

| Priority | Action | Expected Gain |
|----------|--------|--------------|
| 🔄 **Now** | Wait for v10_tuned (roi=1.2) to converge | +30–60 pts? |
| 📌 High | Try `horizon=22` (deeper planning) | +?? |
| 📌 High | Monitor shummingfang48 evolution (99 votes) | +?? |
| 📌 Medium | Find what jek1wantaufik's private model does (scored ~1300) | +?? |
| 📌 Low | Terminal phase tuning (aggressive last 40 turns) | +10–20 pts |

---

## 📦 Kernels

| Kernel | Agent | Slots |
|--------|-------|-------|
| [orbit-wars-v9-producer](https://www.kaggle.com/code/cid007/orbit-wars-v9-producer) | orbit_lite default | Active |
| [orbit-wars-v9-producer-b](https://www.kaggle.com/code/cid007/orbit-wars-v9-producer-b) | orbit_lite default | Active |
| [orbit-wars-v10-tuned](https://www.kaggle.com/code/cid007/orbit-wars-v10-tuned) | orbit_lite roi=1.2 | Active |
| [orbit-wars-v8-realsim](https://www.kaggle.com/code/cid007/orbit-wars-v8-realsim) | v1 + real-sim eval | Inactive |
| [orbit-wars-v1-starter](https://www.kaggle.com/code/cid007/orbit-wars-v1-starter) | safar1 heuristic | Inactive |

---

## 🔄 How to Update This Dashboard

When adding a new agent:
1. Add a row to **Agent History** table
2. Update **Current Leaderboard Position** block
3. Update **Score Timeline** ASCII chart
4. Update **Medal Tracker** progress bar
5. Move old active agents to Inactive

---

*Last updated: 2026-06-10 · v10_tuned converging · v9_producer active at 1167*
