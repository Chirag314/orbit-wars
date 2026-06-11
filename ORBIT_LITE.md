# orbit_lite — Architecture Notes

The `orbit_lite` library (orbit_lite-producer-kernel) is the
foundation of the top mid-tier agents (orbit_lite-author, mission-agent-v2).

## Package Structure

```
orbit_lite/
├── __init__.py
├── constants.py        # Game constants (CENTER, SUN_RADIUS, etc.)
├── geometry.py         # fleet_speed(), vectorized (torch tensors)
├── obs.py              # parse_obs() — converts dict/object obs to tensors
├── adapter.py          # single_obs_to_tensor(), sparse_action_row_to_moves()
├── movement.py         # PlanetMovement, PlanetGarrisonStatus (core!) — 1962 lines
├── movement_step.py    # LaunchEntries, apply_private_planned_launches
├── movement_aiming.py  # Fleet surface offsets
├── intercept_aim.py    # intercept_angle() — orbital aim with ow.swept_pair_hit
├── aiming.py           # Simple angle helpers
├── distance_cache.py   # build_distance_cache(), min_distance_to_targets()
├── garrison_launch.py  # GarrisonFlowDiff, sparse_launch_flow_delta() (key!)
└── planner_core.py     # build_target_shortlist, score_candidates, _greedy_select
```

## Core Innovation: sparse_launch_flow_delta()

Located in `garrison_launch.py`. This is the key function that beats v1_starter.

**What it does:** Given a set of hypothetical launches (source_planet, target_planet,
ships, ETA), compute for each launch: "how does every player's net ship flow
change over the next horizon turns?"

**Why it's better than melis_evaluate:**
- v1_starter: projects one action at a time, uses linear weights (5×planets + 8×prod)
- orbit_lite: projects ALL candidate launches simultaneously via batched tensor ops,
  computes exact garrison evolution accounting for all known inbound fleets

**Computational approach:**
```
LaunchSet[C, L] → sparse_launch_flow_delta → Δ(net_ship_flow)[C, players]
```
- C = candidate launches
- L = individual fleet dispatches in a candidate
- Evaluates all candidates in parallel with PyTorch matrix ops

## PlanetGarrisonStatus

Located in `movement.py`. Tracks exact garrison over a future horizon for
all planets simultaneously:

- Maintains `owner[P, T]` and `ships[P, T]` tensors (P planets, T timesteps)
- Accounts for all known in-flight fleets and their arrival ETAs
- Handles combat resolution exactly (top-minus-second engine rule)
- Used as baseline for flow-diff computation

## ProducerLiteConfig Parameters

```python
horizon: int = 18              # planning window
max_sources_per_lane: int = 12 # source planets per target
max_offensive_targets: int = 12 # targets to score
max_defensive_targets: int = 4  
max_waves_per_turn: int = 6    # max fleet dispatches per turn
roi_threshold: float = 1.5     # min score to execute action
min_ships_to_launch: float = 4.0
enable_regroup: bool = True    # consolidate backline ships
max_regroup_time: float = 7.0
```

## Submission Format

orbit_lite requires PyTorch. Submitted as `submission.tar.gz` containing:
```
main.py          # 369-line ProducerLite agent
orbit_lite/      # entire package directory
```

The `main.py` uses `sys.path.insert(0, _HERE)` so orbit_lite is found
next to it when extracted from the archive.

## Tuning Opportunities

The current agent uses the library author's default ProducerLiteConfig. Potential
improvements:
- `roi_threshold`: lower (1.0?) = more aggressive, more fleet dispatches
- `horizon`: increase (24?) = deeper planning but slower per turn
- `max_waves_per_turn`: increase (8?) = more simultaneous fleet groups
- `enable_regroup`: can disable if ship consolidation hurts tempo
- `regroup_pressure_delta_min`: tune for more/less aggressive consolidation
