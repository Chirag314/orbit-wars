"""
Local arena: run N games between two agents and report win rate + timing.

Usage:
    python local_arena.py <agent_a_dir> <agent_b_dir> [--games N] [--players 2|4]

Examples:
    python local_arena.py agents/v15_terminal agents/v11_horizon22 --games 20
    python local_arena.py agents/v21_terminal_early agents/v15_terminal --games 10
"""

import argparse
import importlib.util
import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")

ORBIT_LITE_PATH = os.path.join(os.path.dirname(__file__), "agents", "orbit_lite_pkg")


def load_agent(agent_dir: str):
    agent_dir = os.path.abspath(agent_dir)
    spec = importlib.util.spec_from_file_location(
        "submission", os.path.join(agent_dir, "submission.py")
    )
    mod = importlib.util.module_from_spec(spec)
    _prev = sys.path[:]
    sys.path.insert(0, agent_dir)
    sys.path.insert(0, ORBIT_LITE_PATH)
    sys.modules[spec.name] = mod  # needed for @dataclass module lookup
    spec.loader.exec_module(mod)
    sys.path[:] = _prev
    return mod.agent


def run_arena(agent_a, agent_b, *, n_games: int = 20, n_players: int = 2):
    import kaggle_environments as ke

    wins_a = wins_b = draws = 0
    times = []

    agents = [agent_a, agent_b] if n_players == 2 else [agent_a, agent_b, agent_a, agent_b]

    for i in range(n_games):
        # Alternate who plays first to remove seat bias
        if i % 2 == 0:
            lineup = agents
            a_idx, b_idx = 0, 1
        else:
            lineup = [agent_b, agent_a] if n_players == 2 else [agent_b, agent_a, agent_b, agent_a]
            a_idx, b_idx = 1, 0

        env = ke.make("orbit_wars", debug=False)
        t0 = time.time()
        env.run(lineup)
        elapsed = time.time() - t0
        times.append(elapsed)

        r_a = env.steps[-1][a_idx].reward
        r_b = env.steps[-1][b_idx].reward

        if r_a > r_b:
            wins_a += 1
        elif r_b > r_a:
            wins_b += 1
        else:
            draws += 1

        print(
            f"  game {i+1:>3}/{n_games}  "
            f"a={'WIN ' if r_a>r_b else ('LOSS' if r_a<r_b else 'DRAW')}  "
            f"b={'WIN ' if r_b>r_a else ('LOSS' if r_b<r_a else 'DRAW')}  "
            f"{elapsed:.1f}s  "
            f"[A {wins_a}W {wins_b}L {draws}D]",
            flush=True,
        )

    total = wins_a + wins_b + draws
    print()
    print(f"Results over {total} games:")
    print(f"  Agent A:  {wins_a:>3} wins  ({100*wins_a/total:.1f}%)")
    print(f"  Agent B:  {wins_b:>3} wins  ({100*wins_b/total:.1f}%)")
    print(f"  Draws:    {draws:>3}")
    print(f"  Avg game time: {sum(times)/len(times):.2f}s  total: {sum(times):.1f}s")
    return wins_a, wins_b, draws


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("agent_a", help="Path to agent A directory (contains submission.py)")
    parser.add_argument("agent_b", help="Path to agent B directory (contains submission.py)")
    parser.add_argument("--games", type=int, default=20)
    parser.add_argument("--players", type=int, default=2, choices=[2, 4])
    args = parser.parse_args()

    print(f"Loading agents...")
    agent_a = load_agent(args.agent_a)
    agent_b = load_agent(args.agent_b)
    print(f"  A: {args.agent_a}")
    print(f"  B: {args.agent_b}")
    print(f"Running {args.games} games ({args.players}P)...\n")

    run_arena(agent_a, agent_b, n_games=args.games, n_players=args.players)


if __name__ == "__main__":
    main()
