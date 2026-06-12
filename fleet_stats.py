"""
Fleet stats: run one game and log fleets-per-tick, aiming precision, and
late-game aggression for a given agent.

Usage:
    python fleet_stats.py <agent_dir> [--opponent <agent_dir>] [--games N]
"""

import argparse
import importlib.util
import os
import sys
import time
import warnings
from collections import defaultdict

warnings.filterwarnings("ignore")

ORBIT_LITE_PATH = os.path.join(os.path.dirname(__file__), "agents", "orbit_lite_pkg")


def load_agent(agent_dir: str):
    agent_dir = os.path.abspath(agent_dir)
    spec = importlib.util.spec_from_file_location(
        f"sub_{os.path.basename(agent_dir)}",
        os.path.join(agent_dir, "submission.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    _prev = sys.path[:]
    sys.path.insert(0, agent_dir)
    sys.path.insert(0, ORBIT_LITE_PATH)
    sys.modules[spec.name] = mod  # needed for @dataclass module lookup
    spec.loader.exec_module(mod)
    sys.path[:] = _prev
    return mod.agent


def instrument_agent(raw_agent, player_id: int, stats: dict):
    """Wrap agent to count fleets launched per step."""

    def wrapped(obs, *args, **kwargs):
        actions = raw_agent(obs, *args, **kwargs)
        step = obs.step if hasattr(obs, "step") else obs.get("step", -1)
        n_fleets = len(actions) if actions else 0
        stats["fleets_per_step"][step] = n_fleets
        stats["total_launches"] += n_fleets
        stats["steps_played"] += 1
        return actions

    return wrapped


def run_fleet_stats(agent_dir: str, opponent_dir: str, n_games: int = 5):
    import kaggle_environments as ke

    all_stats = []

    for game_i in range(n_games):
        stats = {"fleets_per_step": {}, "total_launches": 0, "steps_played": 0}

        raw_agent = load_agent(agent_dir)
        opp_agent = load_agent(opponent_dir)
        tracked = instrument_agent(raw_agent, 0, stats)

        env = ke.make("orbit_wars", debug=False)
        env.run([tracked, opp_agent])

        reward = env.steps[-1][0].reward
        all_stats.append((stats, reward))

        fps = stats["fleets_per_step"]
        avg_all   = sum(fps.values()) / max(len(fps), 1)
        late_fps  = {k: v for k, v in fps.items() if k > 400}
        mid_fps   = {k: v for k, v in fps.items() if 200 < k <= 400}
        early_fps = {k: v for k, v in fps.items() if k <= 200}
        avg_late  = sum(late_fps.values())  / max(len(late_fps), 1)
        avg_mid   = sum(mid_fps.values())   / max(len(mid_fps), 1)
        avg_early = sum(early_fps.values()) / max(len(early_fps), 1)

        outcome = "WIN" if reward > 0 else ("LOSS" if reward < 0 else "DRAW")
        print(f"Game {game_i+1}: {outcome}  launches: {stats['total_launches']:>5}  "
              f"fleets/tick  early={avg_early:.2f}  mid={avg_mid:.2f}  late={avg_late:.2f}")

    print()
    print("=" * 60)
    # Aggregate across games
    combined_fps = defaultdict(list)
    for stats, _ in all_stats:
        for step, n in stats["fleets_per_step"].items():
            combined_fps[step].append(n)

    avg_by_step = {k: sum(v) / len(v) for k, v in combined_fps.items()}

    # Bucket into 50-step windows
    print("Avg fleets/tick by game phase:")
    for lo in range(0, 500, 50):
        hi = lo + 50
        bucket = [v for k, v in avg_by_step.items() if lo <= k < hi]
        avg = sum(bucket) / max(len(bucket), 1)
        bar = "#" * int(avg * 10)
        print(f"  step {lo:>3}-{hi:<3}: {avg:.3f}  {bar}")

    outcomes = [r for _, r in all_stats]
    wins = sum(1 for r in outcomes if r > 0)
    print(f"\nWin rate: {wins}/{n_games} ({100*wins/n_games:.0f}%)")
    print(f"Target late-game fleets/tick (winners): 3.75")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("agent_dir")
    parser.add_argument("--opponent", default=None,
                        help="Opponent agent dir (default: same agent)")
    parser.add_argument("--games", type=int, default=5)
    args = parser.parse_args()

    opponent = args.opponent or args.agent_dir
    print(f"Agent:    {args.agent_dir}")
    print(f"Opponent: {opponent}")
    print(f"Games:    {args.games}\n")
    run_fleet_stats(args.agent_dir, opponent, n_games=args.games)


if __name__ == "__main__":
    main()
