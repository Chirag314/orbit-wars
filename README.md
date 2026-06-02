# Orbit Wars — Kaggle Competition

**Competition**: https://www.kaggle.com/competitions/orbit-wars
**Deadline**: June 23, 2026 (23:59 UTC)
**Prize**: $50,000 USD (Featured)
**Teams**: 3,656 as of June 2, 2026

## What It Is
A game AI competition where agents compete in real-time spacecraft strategy:
- 500 turns, 2–4 players, 100×100 board with orbiting planets
- Maximize total ships (on planets + in transit) at game end
- Rated via Glicko-style skill rating (win/loss outcomes, not score margin)

## Repository Structure
```
orbit_wars/
├── CLAUDE.md              — Competition rules + Claude instructions
├── README.md              — This file
├── competition_memo.md    — Full analysis report
└── agents/
    ├── v1_starter/
    │   └── submission.py  — Baseline: safar1/lb-score-1101 (~1101 rating)
    └── v2_ajay_merge/     — (planned) Cherry-pick from ajayrao43/v12
```

## Medal Targets
| Medal | Rank | Teams | Score |
|---|---|---|---|
| Bronze | top 10% | top 366 | ~1100–1150 est. |
| Silver | top 5% | top 183 | ~1300–1400 est. |
| Gold | top 1% | top 37 | ~1600+ |

## Current Status
- **v1_starter** (safar1 fork): ~1101 — at bronze floor
- **Next step**: Submit v1_starter as private Kaggle kernel, verify it posts a score

## Submission
```bash
# From agents/v2/ folder:
kaggle competitions submit orbit-wars -f submission.py -m "v2 description"
```

Or create a notebook kernel that writes `submission.py` and set as submission output.
