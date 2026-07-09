# Orbit Wars Competition — Final Results & Lessons Learned

**Competition ended:** June 23, 2026  
**Result at Jun 26 read:** #841 / 1820 teams | Score: 1037.6 | No medal (Bronze: 1172.8)

---

## 🏁 TRUE FINAL RESULT (locked Jul 8, 2026 — private score revealed)

**Rank #648 / 4,730 teams | Score: 1064.9 | No medal** (Bronze cutoff: rank 473, score 1089.5)

Missed bronze by **175 ranks / 24.6 points**. The score peaked around ~1101 on Jul 6
morning after a win streak, but a sustained losing stretch (~39% win rate over the
last 18 tracked episodes, including several 4P losses) pulled it down to 1064.9 by
lock time — see the Jul 5-8 conversation log for the episode-by-episode tracking.
10,295 registrations, 5,196 participants, 4,729 teams, 9,047 submissions, 121 countries
(per Kaggle's official recap).

---

## 📡 Post-Deadline Update (Jul 5, 2026)

The Jun 26 numbers above were **not actually final** — Kaggle's episode-processing
backlog was still draining. Live leaderboard as of Jul 5:

| Metric | Jun 26 read | Jul 5 read (live) | Δ |
|---|---|---|---|
| Score | 1037.6 | **1087.2** | +49.6 |
| Rank | 841 / 1820 | **508 / 4730** | |
| Percentile | top 46.2% | **top 10.7%** | |

**Episode volume (best submission, `v36_submission.tar.gz`, id 53965498):** 302 total
episodes (1 validation + 301 real games), running since 2026-06-23 03:31, most recent
2026-07-06 04:48 — **~23 games/day**, roughly one game/hour. At that pace, expect
~40-50 more episodes before the Final Evaluation Period closes. Check anytime with:
```
kaggle competitions episodes 53965498
```

**Why the field size nearly tripled (1,820 → 4,730 teams):** the Jun 26 leaderboard
only included teams whose episodes had already finished processing. Thousands more
teams' games cleared the queue over the following ~12 days, adding ~2,900 newly-scored
teams to the leaderboard. That reshuffles percentile-based medal cutoffs even when an
individual agent's own score barely moves.

**Current bronze math:** top 10% of 4,730 teams = rank ≤ 473. Team count (4,730) is now
fixed — no more teams are being added, so only scores (via remaining episodes) can
still shift the ranking from here. The old bronze score cutoff (1172.8) was computed
against the stale 1,820-team field — ignore it.

**Score trend has reversed (Jul 6-7 update):** peaked around ~1101 on Jul 6 morning
after a 3-win streak, but a sustained losing patch pulled it back down —
**7 wins / 11 losses over the last 18 episodes (~39% win rate)**.
Verified match-by-match via `kaggle competitions replay <episode_id>` — decode with:
```python
import json
d = json.load(open('episode-<id>-replay.json'))
names = d['info']['TeamNames']; rewards = d['rewards']
# rank 1 (highest reward) = win
```

**Ground-truth leaderboard pull (Jul 7, via `kaggle competitions leaderboard orbit-wars -d`):**
this downloads the *entire* public leaderboard as a CSV — exact rank/score per team,
no more estimating. Current numbers:
- **Our rank: 495/4730**, score **1084.3**
- **Bronze cutoff (rank 473): score 1088.8** — up from 1087.6 a day earlier (the bronze
  line itself is drifting too, not just our score)
- **Gap: 22 ranks / 4.5 points**
- The 1087-1090 score band is extremely dense (dozens of teams within ~2 pts of each
  other), so rank position is volatile even on small score moves — don't over-read
  single-point rank swings

**Timeline:** per the competition rules, there's an official Final Evaluation Period
from Jun 24 to ~Jul 8, during which Kaggle keeps running games against frozen
submissions until the leaderboard converges. ~2-3 days left. This section will be
updated again once that window closes.

---

## Final Leaderboard (Top 20)

| Rank | Team | Score | Notes |
|------|------|-------|-------|
| 1 | Isaiah @ Tufa Labs | 1630.2 | +600 from competition start |
| 2 | Jake Will | 1571.4 | |
| 3 | TonyK | 1529.1 | New entrant, strong finish |
| 4 | Felix M Neumann | 1522.6 | Consistent top 5 |
| 5 | Hober Malloc | 1518.7 | |
| ... | ... | ... | |
| 841 | **Chirag Desai (Us)** | **1037.6** | Stale Jun 26 read — see TRUE FINAL RESULT above |

**Stale Jun 26 cutoffs (1,820-team field, since superseded):**
Gold 1414.6 | Silver 1248.9 | Bronze 1172.8

**True final cutoffs (4,730-team field, locked Jul 8):**
Gold (rank 47) 1349.0 | Silver (rank 236) 1136.0 | **Bronze (rank 473) 1089.5**

---

## Our Journey

### Early Phase (Jun 2-11): Baseline → v15
- **v1_starter** (public-baseline): 1072.7
- **v9_producer** (orbit_lite library): 1164–1167 ✓ Breakthrough
- **v15_terminal** (tuned, terminal phase): 1160.8

### Critical Bug Discovery (Jun 16-20)
**Packaging error:** API submissions used `submission.py` instead of `main.py`, and lacked `orbit_lite/` library. Agents crashed silently → scored ~970.

Discovered Jun 20 via replay analysis. Lost 10 days to this bug.

### Late Phase (Jun 21-23): Hybrid Agent
- **v34_hybrid** (Pilkwang + Alyce features): 1183 (lucky 5 games) → **1037.6 (true score, 100 games)**
- **v35_tuned** (added min_ships=12, drain_frac=0.65): 911 ✗ HURT performance
- **v36_closer** (close-out acceleration): 1035.7 (similar to v34)

---

## What Worked: v34 Hybrid Features

### From Pilkwang's ProducerLite
- **Size multipliers:** Evaluate 0.5x and 1.0x fleet sizes per (src, tgt) pair
- **Terminal phase:** Last 40 turns: roi=1.0, max_waves=8, disable regroup
- **Horizon=18** vs 22: Better 2P performance
- **Params.json loading:** Dynamic config overrides

### From Alyce's Intruder Agent
- **Dynamic ROI adjustment:** ratio-based ramp when behind; quadratic deficit formula
- **Late-game suppression:** Penalize attacks arriving after game ends, depreciate neutral captures
- **3P/4P configs:** Separate tuning per player count

### From All Top Kernels
- **Reinforcement risk β=2.2:** Don't attack planets enemies will reinforce mid-flight
- **Regroup with enemy pressure:** Move ships toward stressed planets
- **Multi-wave greedy selection:** Fire best scoring waves up to max per turn

---

## What Failed / Hurt

| Agent | Issue | Score | Lesson |
|-------|-------|-------|--------|
| v32_h18 | Broken packaging | 600 | Verify entry point immediately |
| v35_tuned | min_ships=12, drain_frac=0.65 | 911 | v34's default (min_ships=3) was better; β already blocked waste |
| v33_hammer | Multi-source pile-on | 732 | Complexity without evidence |
| v15 resubmit | Late resubmit, weaker field | 926 | Field strengthens mid-June; early scores inflated |
| Horizon > 18 | Over-commitment | 600–971 | h=22, 24, 26 all performed worse |
| ROI < 1.4 or > 1.5 | Poor decision threshold | 729–1114 | Sweet spot: 1.4–1.5 |

---

## Top Public Approaches (Post-Deadline Kernels)

Newly published high-voted kernels (likely from top teams):
- **Amged Alfaqih** (124 votes, Jun 21): "Apex Hybrid – Dynamic Ring Control & Border Defense"
- **olasadek** (119 votes, Jun 22): "i, the orbit"  
- **slawekbiel** (259 votes, Jun 12): "The Producer V2" (what we used as base)
- **pilkwang** (121 votes, Jun 15): "ProducerLite: Regroup-Limited Logistics" (what we used as base)

**Common theme:** All top agents combine:
1. PyTorch tensor-based simulation (orbit_lite framework)
2. Multi-horizon lookahead (15–22 turns)
3. Reinforcement-aware capture sizing (β = 1.0–2.2)
4. Dynamic ROI based on game state
5. Regroup mechanics for defense

**What's missing from public implementations:** Top teams (1500+) likely use:
- Deeper MCTS or policy-gradient search
- Learned value functions (RL pre-training)
- Game-state clustering for adaptive play

---

## 🔬 Post-Competition Solution Writeups (read Jul 8, after final lock)

Official recap: 10,295 registrations, 5,196 participants, 4,729 teams, 9,047 submissions,
121 countries. Read the actual top-placing writeups from the discussion forum
(`kaggle competitions topics list/show orbit-wars`) — here's what they did and how it
maps to what we did or missed.

### #1 place — Isaiah @ Tufa Labs — "Scaling Reinforcement Learning to the Stars"
Pure self-play PPO, 200M-parameter transformer, **15 billion training steps**, 8×B200
GPUs (~2,400 B200-hours total, multi-node). Entity-based observation (planets/fleets/
comets as tokens), simple action space (launch y/n + target + continuous fleet size).
4-bit quantized to fit the 100MiB submission cap. **Not replicable at our scale** — this
confirms our CLAUDE.md assumption "no public RL agent is competitive yet" was **wrong**;
RL wasn't just competitive, it dominated 1st place. Notable finding: **matchmaking ratio
flipped from 2P-heavy to 4P-heavy right after the submission deadline** — he over-tuned
for 2P assuming it'd stay 2P-dominant and got caught out, same shift we saw in our own
late losses (several of our post-deadline losses were 4P).

### #2 place — simjeg — RL + IL, much smaller scale
Started with hand-crafted heuristics (top 50), switched to **imitation learning on
replay data** (→ top 10), then **RL fine-tuning** (→ top 5), then **from-scratch
self-play RL** in the final days (→ 2nd). Only a 4.3M-parameter model (1D-CNN + small
ModernBERT transformer) — far smaller than #1, proving competitive RL doesn't strictly
require massive compute. Key point: **the path from heuristic → IL → RL was incremental
and each step was a leaderboard improvement** — this was a viable path we never explored
at all (we stayed 100% heuristic the entire competition).

### Top 2% (#72) — Gerardo Del Toro — "GPU Poor, PPO Rich"
Budget self-play PPO in JAX: local RTX 3070 Ti + **~$25 of rented Vast.ai GPU time**,
reaching ~750M steps. Simplified all-in/no-op action space, projected 23-step future
timeline per planet (conceptually identical to our own `forward_project()`/orbit_lite
garrison simulation). **This is the most damning comparison for us**: a ~$25, single-
person RL side-project beat our final rank (#72 vs our #648) with less domain-specific
tuning effort than we put into v1-v36. RL was accessible, not just for well-funded teams.

### Silver medal — sam_the_rice_cake — heuristic improvement of "The Producer V2"
**Same base agent family we used** (Producer/ProducerLite lineage), and stayed 100%
non-RL/deterministic — proof our overall architecture choice wasn't wrong, our tuning
and feature depth just didn't go far enough. Concrete things they added that we didn't:
- **Production-aware source selection**: rank candidate sources by `ships + w·production·horizon`,
  not just current ship count — lets high-production planets stay active launch sources
  even when temporarily low on garrison. We never weighted by production this way.
- **Focus fire / multi-source pooled attacks**: for targets no single source can crack,
  greedily sum the smallest prefix of sources (by size, up to 4) that clears the capture
  floor. Explicitly called "probably one of the most important practical improvements."
  **We had the same idea** (HAMMER/COALITION, `v33_hammer` "multi-source pile-on") **but
  ours scored 732 — badly broken** — right concept, bad execution (no principled
  prefix-sum/threshold selection like theirs).
- **Hard late-game arrival cutoff**: filter out any candidate launch whose arrival time
  is ≥ remaining game steps, scored `-inf`. We had a "terminal phase" (last 40 turns,
  roi=1.0) but not this explicit per-candidate ETA-vs-remaining-steps filter.
- **More aggressive, validated retuning**: raised `roi_threshold` 1.5→1.751,
  `min_ships_to_launch` 4.0→7.764, `reinforce_size_beta` 2.2→3.623 (more selective/
  conservative) — validated via their own local Rust arena with OpenSkill matchmaking
  simulation. **We tried the same direction** (`v35_tuned`: min_ships=12,
  drain_frac=0.65) **and it hurt us** (scored 911) — likely because we didn't have as
  rigorous a local evaluation loop to find the right values, and moved further/faster
  than the data supported.

### The core takeaway
Our architecture (deterministic projection/heuristic, Producer-lineage) was validated —
it's exactly what won Silver. What separated us from medal position wasn't the paradigm,
it was **execution rigor**: a better local arena for validating parameter changes before
submitting, more careful multi-source attack logic, and an explicit late-game cutoff.
Separately, RL was a completely untried, viable path this entire competition — from a
$25 budget solution beating our final rank to two of the top 3 places using it, "RL
isn't competitive yet" was a bad premise to have carried through the whole entry.

---

## Critical Mistakes & Lessons

### 1. Packaging Bug (Cost: 10 days)
**Problem:** Entry point must be `main.py`, not `submission.py`. Missing `orbit_lite/` library → silent crash → ~970 score.

**How we lost:** We submitted from Jun 11–16 with broken packaging. Discovered Jun 20 — only 3 days left.

**Lesson:** On day 1, submit simplest possible agent, verify it scores non-default, download a working kernel's tar.gz structure, match exactly. **Do NOT assume you know the format.**

### 2. Glicko Score Variance (Cost: Wrong decisions)
**Problem:** Early scores (< 50 games) are unreliable. v34 showed 1183 with 5 games, converged to 1037 with 100 games.

**Lesson:** Need 50+ games for stable score. Don't pivot strategy on new agents' first week. Check episode count when evaluating.

### 3. 5 Submission/Day Limit (Cost: Iteration lost)
**Problem:** Daily reset at midnight. Accidental double-submit (v35 dirty+clean) burned a critical day. Only had 5 total submissions to go from broken v32/v33 to final v36.

**Lesson:** Be extremely deliberate. Always plan the intended pair before submitting. Don't iterate frantically near deadline with limited budget.

### 4. Field Strengthening (Cost: Score compression)
**Problem:** Agents scoring 1160 early June scored ~926 by late June. The field nearly doubled in strength. Our v15 "converged" to 926 against a much tougher field.

**Lesson:** Early Glicko scores are inflated. If a score doesn't converge within 48h, it's likely provisional. Expect the actual score to be 50–100 pts lower vs. final field.

---

## What We'd Do Differently

1. **Day 1:** Verify packaging with the simplest agent. Download 3 public kernel outputs and study their exact structure.

2. **Week 1:** Don't chase early high scores. Aim for 1050+ with a robust agent, not 1200+ that might be lucky.

3. **Iteration:** Use public kernels as starting points, not remixes. Pilkwang + Alyce was the right move, but needed earlier.

4. **Late-game:** With 3 days left and limited submissions, stick to proven agents. v35's changes sounded good but hurt — we should have known from v34's success and the fact that β already blocks waste.

5. **Glicko management:** Once an agent scores decently (900+), let it play 100+ games. Don't keep resubmitting — converge one agent per 2-day window.

---

## Takeaways for Future Competitions

- **Packaging is not documentation.** Test day 1.
- **Glicko variance is real.** >50 games required for signal.
- **Daily submission limits are hard constraints.** Plan submissions like a budget.
- **Public kernels reveal meta.** Study top-voted ones; that's where the ideas are.
- **Field strengthens.** Early scores are inflated. Expect 50–100 pt drop vs. final field.
- **Simplicity wins.** Hybrid of 2–3 good ideas > novel complex ideas.

---

## Final Stats

| Metric | Value |
|--------|-------|
| Weeks of competition | 3.5 |
| Submissions sent | 18 |
| Agents built | 36 variants |
| Rank | #841 / 1820 |
| Score | 1037.6 |
| Medal earned | None (missed bronze by 135) |
| Cost of packaging bug | 10 days, ~100 points |
| Cost of v35 overfitting | 70–130 points |
