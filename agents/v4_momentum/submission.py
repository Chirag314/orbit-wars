"""
v4_momentum — Orbit Wars agent
Three original ideas:
  1. Momentum Strike: exploit fleet-speed scaling — fat fleets arrive faster,
     leave a surplus that chain-captures nearby planets.
  2. Monte Carlo rollout evaluator: score actions by simulating forward
     N turns with a fast greedy policy, not a hand-tuned linear formula.
  3. 2P Minimax: alpha-beta search (depth 2) for 1v1 games.
"""
import math
import time
from collections import defaultdict
from typing import List, Optional, Tuple

# ── constants ────────────────────────────────────────────────────────────────
BOARD         = 100.0
CENTER_X      = 50.0
CENTER_Y      = 50.0
SUN_R         = 10.0
SUN_SAFETY    = 1.5
ROTATION_LIMIT= 50.0
MAX_SPEED     = 6.0
TOTAL_STEPS   = 500

SOFT_DEADLINE_FRAC = 0.82
MIN_DISPATCH       = 8

# Idea 1 – Momentum Strike
MOM_CLUSTER_RADIUS    = 22.0   # planets within this radius form a cluster
MOM_MIN_CLUSTER_PROD  = 3      # cluster worth hitting (total production)
MOM_MIN_LEFTOVER_FRAC = 0.8    # leftover / cluster_garrison ratio to trigger
MOM_MAX_SOURCE_DIST   = 38.0   # how far a source planet can be
MOM_KEEP_FRAC         = 0.15   # fraction to keep at source for defense
MOM_MIN_SHIPS         = 30     # minimum fleet to call it a momentum strike

# Idea 2 – Monte Carlo
MC_N_ROLLOUTS   = 3    # rollouts per candidate action
MC_HORIZON      = 20   # turns per rollout
MC_GREEDY_FRAC  = 0.55 # fraction of ships the greedy policy emits
MC_MAX_ACTIONS  = 12   # cap candidate actions evaluated

# Idea 3 – Minimax (2P)
MM_DEPTH        = 2
MM_BRANCH       = 6    # top-k actions per node


# ── physics helpers ──────────────────────────────────────────────────────────
from collections import namedtuple
Planet = namedtuple("Planet", ["id","owner","x","y","radius","ships","production"])
Fleet  = namedtuple("Fleet",  ["id","owner","x","y","angle","from_planet_id","ships"])

def dist(ax, ay, bx, by):
    return math.hypot(ax - bx, ay - by)

def fleet_speed(ships: int) -> float:
    if ships <= 1:
        return 1.0
    r = math.log(ships) / math.log(1000.0)
    r = max(0.0, min(1.0, r))
    return 1.0 + (MAX_SPEED - 1.0) * (r ** 1.5)

def is_static(p: Planet) -> bool:
    return dist(p.x, p.y, CENTER_X, CENTER_Y) + p.radius >= ROTATION_LIMIT

def _seg_sun_dist(x1, y1, x2, y2) -> float:
    dx, dy = x2 - x1, y2 - y1
    seg_sq = dx * dx + dy * dy
    if seg_sq <= 1e-9:
        return dist(CENTER_X, CENTER_Y, x1, y1)
    t = max(0.0, min(1.0, ((CENTER_X - x1) * dx + (CENTER_Y - y1) * dy) / seg_sq))
    return dist(CENTER_X, CENTER_Y, x1 + t * dx, y1 + t * dy)

def safe_angle(sx, sy, sr, tx, ty) -> Optional[float]:
    angle = math.atan2(ty - sy, tx - sx)
    lx = sx + math.cos(angle) * (sr + 0.1)
    ly = sy + math.sin(angle) * (sr + 0.1)
    if _seg_sun_dist(lx, ly, tx, ty) < SUN_R + SUN_SAFETY:
        return None
    return angle

def predict_pos(p: Planet, initial_by_id, ang_vel, turns) -> Tuple[float, float]:
    init = initial_by_id.get(p.id)
    if init is None:
        return p.x, p.y
    r = dist(init.x, init.y, CENTER_X, CENTER_Y)
    if r + init.radius >= ROTATION_LIMIT:
        return p.x, p.y
    cur = math.atan2(p.y - CENTER_Y, p.x - CENTER_X)
    new = cur + ang_vel * turns
    return CENTER_X + r * math.cos(new), CENTER_Y + r * math.sin(new)

def travel_turns(sx, sy, sr, tx, ty, ships) -> Optional[int]:
    angle = safe_angle(sx, sy, sr, tx, ty)
    if angle is None:
        return None
    d = max(0.0, dist(sx, sy, tx, ty) - sr - 0.1)
    return max(1, math.ceil(d / fleet_speed(max(1, ships))))

def aim(src: Planet, tgt: Planet, ships, initial_by_id, ang_vel) -> Optional[Tuple[float, int]]:
    """Iterative orbital aim; returns (angle, turns) or None."""
    tx, ty = tgt.x, tgt.y
    for _ in range(6):
        t = travel_turns(src.x, src.y, src.radius, tx, ty, ships)
        if t is None:
            return None
        ntx, nty = predict_pos(tgt, initial_by_id, ang_vel, t)
        ang = safe_angle(src.x, src.y, src.radius, ntx, nty)
        if ang is None:
            return None
        if abs(ntx - tx) < 0.5 and abs(nty - ty) < 0.5:
            return ang, t
        tx, ty = ntx, nty
    return None

def _read(obs, key, default=None):
    if isinstance(obs, dict):
        return obs.get(key, default)
    return getattr(obs, key, default)


# ── World ────────────────────────────────────────────────────────────────────
class World:
    def __init__(self, obs):
        self.player  = _read(obs, "player", 0)
        self.step    = _read(obs, "step", 0) or 0
        self.ang_vel = _read(obs, "angular_velocity", 0.0) or 0.0

        raw_planets = _read(obs, "planets", []) or []
        raw_fleets  = _read(obs, "fleets",  []) or []
        raw_init    = _read(obs, "initial_planets", []) or []

        self.planets        = [Planet(*p) for p in raw_planets]
        self.fleets         = [Fleet(*f)  for f in raw_fleets]
        self.initial_by_id  = {Planet(*p).id: Planet(*p) for p in raw_init}
        self.planet_by_id   = {p.id: p for p in self.planets}

        self.my_planets      = [p for p in self.planets if p.owner == self.player]
        self.enemy_planets   = [p for p in self.planets if p.owner not in (-1, self.player)]
        self.neutral_planets = [p for p in self.planets if p.owner == -1]

        # owner stats
        self.strength   = defaultdict(int)
        self.production = defaultdict(int)
        for p in self.planets:
            if p.owner != -1:
                self.strength[p.owner]   += int(p.ships)
                self.production[p.owner] += int(p.production)
        for f in self.fleets:
            self.strength[f.owner] += int(f.ships)

        # arrivals
        self.arrivals = defaultdict(list)   # planet_id → [(eta, owner, ships)]
        for f in self.fleets:
            best_p, best_t = None, 1e9
            spd = fleet_speed(f.ships)
            dx  = math.cos(f.angle)
            dy  = math.sin(f.angle)
            for p in self.planets:
                px, py = predict_pos(p, self.initial_by_id, self.ang_vel, 0)
                proj = (px - f.x) * dx + (py - f.y) * dy
                if proj < 0:
                    continue
                perp_sq = (px - f.x)**2 + (py - f.y)**2 - proj**2
                if perp_sq >= p.radius**2:
                    continue
                hit_d = max(0.0, proj - math.sqrt(max(0.0, p.radius**2 - perp_sq)))
                t = max(1, math.ceil(hit_d / spd))
                if t < best_t:
                    best_t, best_p = t, p
            if best_p is not None:
                self.arrivals[best_p.id].append((best_t, int(f.owner), int(f.ships)))

        # 2-player detection
        owners = set(p.owner for p in self.planets if p.owner != -1)
        owners |= set(f.owner for f in self.fleets)
        self.is_2p = len(owners) <= 2

        self.remaining = max(1, TOTAL_STEPS - self.step)

    def garrison_at(self, planet_id, turns) -> int:
        p = self.planet_by_id[planet_id]
        if p.owner == -1:
            return int(p.ships)
        return int(p.ships) + int(p.production) * turns

    def effective_garrison(self, planet_id, turns) -> Tuple[int, int]:
        """Returns (effective_owner, effective_ships) accounting for inbound fleets."""
        p = self.planet_by_id[planet_id]
        owner = int(p.owner)
        ships = int(p.ships)
        prod  = max(0, int(p.production))
        events = sorted(
            (eta, o, s) for eta, o, s in self.arrivals.get(planet_id, [])
            if 1 <= eta <= turns
        )
        last_t = 0
        for eta, evt_owner, evt_ships in events:
            if owner != -1:
                ships += prod * (eta - last_t)
            if evt_owner == owner:
                ships += evt_ships
            else:
                if evt_ships > ships:
                    owner = evt_owner
                    ships = evt_ships - ships
                elif evt_ships < ships:
                    ships -= evt_ships
                else:
                    ships = 0
            last_t = eta
        if owner != -1:
            ships += prod * (turns - last_t)
        return owner, max(0, ships)

    def available(self, pid, reserve_frac=0.10) -> int:
        p = self.planet_by_id[pid]
        if p.owner != self.player:
            return 0
        # keep a small reserve; always respect confirmed hostile inbound
        hostile_inbound = sum(
            s for eta, o, s in self.arrivals.get(pid, [])
            if o != self.player and o != -1 and eta <= 8
        )
        keep = max(int(p.ships * reserve_frac),
                   min(hostile_inbound + 2, int(p.ships)))
        return max(0, int(p.ships) - keep)


# ── Idea 1: Momentum Strike ──────────────────────────────────────────────────

def _cluster_value(world: World, seed: Planet, radius=MOM_CLUSTER_RADIUS):
    """Return (cluster_planets, total_prod, total_garrison) for planets near seed."""
    cluster, prod, garrison = [], 0, 0
    for p in world.planets:
        if p.owner == world.player:
            continue
        if dist(p.x, p.y, seed.x, seed.y) > radius:
            continue
        cluster.append(p)
        if p.owner != -1:
            prod += int(p.production)
        garrison += int(p.ships)
    return cluster, prod, garrison

def _optimal_fleet_size(world: World, src: Planet, tgt: Planet,
                        max_send: int) -> Tuple[Optional[float], int, int]:
    """
    Find the fleet size N in [MIN_DISPATCH, max_send] that maximises
    leftover ships after capturing tgt (leftover = N - garrison_at_arrival).
    Returns (angle, N, leftover) or (None, 0, 0).
    """
    best_angle, best_n, best_left = None, 0, -999

    # We try a handful of candidate sizes: min-needed, half, full, and quarter-steps
    candidates = sorted(set([
        MIN_DISPATCH,
        max_send // 4,
        max_send // 2,
        max_send * 3 // 4,
        max_send,
    ]))

    for n in candidates:
        if n < MIN_DISPATCH or n > max_send:
            continue
        a_info = aim(src, tgt, n, world.initial_by_id, world.ang_vel)
        if a_info is None:
            continue
        angle, turns = a_info
        _, garrison = world.effective_garrison(tgt.id, turns)
        needed = int(garrison) + 1
        if n < needed:
            continue
        leftover = n - needed
        if leftover > best_left:
            best_left  = leftover
            best_n     = n
            best_angle = angle

    return best_angle, best_n, best_left

def plan_momentum(world: World, spent: dict) -> List:
    """
    Idea 1 – Momentum Strike.

    For each capturable target that anchors a cluster of ≥2 productive
    planets, compute how many leftover ships a fat fleet would have after
    capture.  If leftover ≥ MOM_MIN_LEFTOVER_FRAC × cluster_garrison,
    the fat fleet can chain-capture the cluster.  Execute the single best
    such opportunity each turn.
    """
    if not world.my_planets:
        return []

    best_score  = -1e9
    best_moves  = []

    targets = world.enemy_planets + world.neutral_planets

    for tgt in targets:
        cluster, c_prod, c_garrison = _cluster_value(world, tgt)
        if c_prod < MOM_MIN_CLUSTER_PROD or len(cluster) < 2:
            continue

        for src in world.my_planets:
            d = dist(src.x, src.y, tgt.x, tgt.y)
            if d > MOM_MAX_SOURCE_DIST:
                continue
            avail = min(
                world.available(src.id) - spent.get(src.id, 0),
                int(src.ships) - int(src.ships * MOM_KEEP_FRAC),
            )
            if avail < MOM_MIN_SHIPS:
                continue

            angle, n, leftover = _optimal_fleet_size(world, src, tgt, avail)
            if angle is None or n < MIN_DISPATCH:
                continue

            # Score: leftover relative to what's still needed in the cluster
            remaining_garrison = max(0, c_garrison - int(tgt.ships))
            ratio = leftover / max(1, remaining_garrison)
            speed = fleet_speed(n)
            # Bonus for higher speed (faster arrival → less defender growth)
            score = ratio * speed + c_prod * 2.0

            if score > best_score and ratio >= MOM_MIN_LEFTOVER_FRAC:
                best_score = score
                best_moves = [[src.id, angle, n]]

    return best_moves


# ── Idea 2: Monte Carlo rollout evaluator ────────────────────────────────────

def _make_sim_state(world: World) -> dict:
    """Lightweight copy of world state for simulation."""
    owners, ships_map, prod_map = {}, {}, {}
    xy = {}
    for p in world.planets:
        owners[p.id]   = int(p.owner)
        ships_map[p.id]= float(p.ships)
        prod_map[p.id] = int(p.production)
        xy[p.id]       = (float(p.x), float(p.y))
    # in-flight fleets: [owner, x, y, angle, ships]
    fleets = [[int(f.owner), float(f.x), float(f.y), float(f.angle), int(f.ships)]
              for f in world.fleets]
    return {
        "owners": owners, "ships": ships_map, "prod": prod_map,
        "xy": xy, "fleets": fleets,
        "player": world.player,
        "pids": list(owners.keys()),
    }

def _sim_inject(state: dict, src_id: int, angle: float, n_ships: int) -> bool:
    if state["ships"].get(src_id, 0) < n_ships:
        return False
    state["ships"][src_id] -= n_ships
    sx, sy = state["xy"][src_id]
    # find radius from planet list (store once)
    state["fleets"].append([
        state["owners"][src_id], sx, sy, angle, n_ships
    ])
    return True

def _sim_step(state: dict):
    arrivals = defaultdict(list)
    surviving = []
    pids   = state["pids"]
    owners = state["owners"]
    ships_m= state["ships"]
    xy     = state["xy"]

    # production
    for pid in pids:
        if owners[pid] != -1:
            ships_m[pid] += state["prod"][pid]

    # move fleets
    for fl in state["fleets"]:
        o, fx, fy, ang, fs = fl
        if fs <= 0:
            continue
        spd = fleet_speed(fs)
        nx  = fx + math.cos(ang) * spd
        ny  = fy + math.sin(ang) * spd
        fl[1], fl[2] = nx, ny
        # sun check (simplified: centre distance)
        if _seg_sun_dist(fx, fy, nx, ny) < SUN_R:
            continue
        # hit check
        hit = None
        for pid in pids:
            px, py = xy[pid]
            if (nx - px)**2 + (ny - py)**2 < 4.0:   # radius² approx
                hit = pid
                break
        if hit is not None:
            arrivals[hit].append((o, fs))
        elif 0 <= nx <= BOARD and 0 <= ny <= BOARD:
            surviving.append(fl)
    state["fleets"] = surviving

    # resolve combat
    for pid, arr in arrivals.items():
        by_owner = defaultdict(int)
        for o, s in arr:
            by_owner[o] += s
        sorted_o = sorted(by_owner.items(), key=lambda kv: -kv[1])
        top_o, top_s = sorted_o[0]
        second_s = sorted_o[1][1] if len(sorted_o) > 1 else 0
        surv_s = top_s - second_s
        if surv_s <= 0:
            continue
        surv_o = top_o
        cur_owner = owners[pid]
        if cur_owner == surv_o:
            ships_m[pid] += surv_s
        else:
            ships_m[pid] -= surv_s
            if ships_m[pid] < 0:
                owners[pid] = surv_o
                ships_m[pid] = -ships_m[pid]

def _sim_score(state: dict, player: int, n_players: int) -> float:
    """Forward score: (my_ships + 5*my_planets + 8*my_prod) - best enemy equivalent."""
    my_s, my_p, my_r = 0, 0, 0
    others = defaultdict(lambda: [0, 0, 0])
    for pid in state["pids"]:
        o = state["owners"][pid]
        s = state["ships"][pid]
        r = state["prod"][pid]
        if o == player:
            my_s += s; my_p += 1; my_r += r
        elif o != -1:
            others[o][0] += s
            others[o][1] += 1
            others[o][2] += r
    for fl in state["fleets"]:
        o, _, _, _, fs = fl
        if o == player:
            my_s += fs
        elif o != -1:
            others[o][0] += fs
    if not others:
        return my_s + 5 * my_p + 8 * my_r
    best_enemy = max(v[0] + 5*v[1] + 8*v[2] for v in others.values())
    return (my_s + 5 * my_p + 8 * my_r) - best_enemy

def _greedy_launch(state: dict, player: int) -> None:
    """Fast greedy: each owned planet sends MC_GREEDY_FRAC ships at nearest non-friendly."""
    owners = state["owners"]
    ships_m= state["ships"]
    xy     = state["xy"]
    pids   = state["pids"]
    for pid in pids:
        if owners[pid] != player:
            continue
        if ships_m[pid] < MIN_DISPATCH:
            continue
        send = int(ships_m[pid] * MC_GREEDY_FRAC)
        if send < MIN_DISPATCH:
            continue
        sx, sy = xy[pid]
        # nearest non-friendly
        best_d, best_ang = 1e9, None
        for opid in pids:
            if owners[opid] == player:
                continue
            ox, oy = xy[opid]
            d = dist(sx, sy, ox, oy)
            if d < best_d:
                ang = math.atan2(oy - sy, ox - sx)
                # skip sun-blocking (cheap check)
                if _seg_sun_dist(sx, sy, ox, oy) >= SUN_R + SUN_SAFETY:
                    best_d  = d
                    best_ang = ang
        if best_ang is not None:
            ships_m[pid] -= send
            state["fleets"].append([player, sx, sy, best_ang, send])

def mc_score(world: World, src_id: int, angle: float, ships: int,
             n_rollouts=MC_N_ROLLOUTS, horizon=MC_HORIZON) -> float:
    """
    Idea 2 – MC rollout evaluator.
    Simulate horizon turns after injecting our action, average the score.
    """
    import copy
    total = 0.0
    base  = _make_sim_state(world)
    n_players = 4 if not world.is_2p else 2

    for _ in range(n_rollouts):
        state = copy.deepcopy(base)
        _sim_inject(state, src_id, angle, ships)
        for t in range(horizon):
            # all non-player owners use greedy launch every 3 turns
            if t % 3 == 0:
                for o in set(state["owners"].values()):
                    if o != -1 and o != world.player:
                        _greedy_launch(state, o)
            _sim_step(state)
        total += _sim_score(state, world.player, n_players)
    return total / max(1, n_rollouts)


# ── Idea 3: 2P Minimax ───────────────────────────────────────────────────────

def _gen_actions_for(world: World, state: dict, player: int, k=MM_BRANCH):
    """Generate top-k candidate single-planet actions for a player in sim-state."""
    actions = []
    owners = state["owners"]
    ships_m= state["ships"]
    xy     = state["xy"]

    my_pids = [pid for pid in state["pids"] if owners[pid] == player]
    tgt_pids= [pid for pid in state["pids"] if owners[pid] != player]

    for src_pid in my_pids:
        avail = int(ships_m[src_pid]) - MIN_DISPATCH
        if avail < MIN_DISPATCH:
            continue
        sx, sy = xy[src_pid]
        for tgt_pid in tgt_pids:
            tx, ty = xy[tgt_pid]
            ang = math.atan2(ty - sy, tx - sx)
            if _seg_sun_dist(sx, sy, tx, ty) < SUN_R + SUN_SAFETY:
                continue
            d = dist(sx, sy, tx, ty)
            # value heuristic for ranking
            tgt_prod = state["prod"][tgt_pid]
            val = tgt_prod * 3.0 - d * 0.1
            actions.append((val, src_pid, ang, avail))

    actions.sort(key=lambda x: -x[0])
    # also include pass (no action)
    result = [(None, None, None, 0)]
    for val, sp, ang, av in actions[:k]:
        result.append((sp, ang, av, val))
    return result

def _minimax(state: dict, world: World, depth: int,
             alpha: float, beta: float, maximising: bool,
             deadline: float) -> float:
    if time.perf_counter() > deadline or depth == 0:
        return _sim_score(state, world.player, 2)

    import copy
    player = world.player if maximising else _other_player(world)
    actions = _gen_actions_for(world, state, player)

    if maximising:
        val = -1e9
        for sp, ang, av, _ in actions:
            s2 = copy.deepcopy(state)
            if sp is not None:
                _sim_inject(s2, sp, ang, av)
            _sim_step(s2)
            val = max(val, _minimax(s2, world, depth - 1,
                                    alpha, beta, False, deadline))
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return val
    else:
        val = 1e9
        for sp, ang, av, _ in actions:
            s2 = copy.deepcopy(state)
            if sp is not None:
                _sim_inject(s2, sp, ang, av)
            _sim_step(s2)
            val = min(val, _minimax(s2, world, depth - 1,
                                    alpha, beta, True, deadline))
            beta = min(beta, val)
            if beta <= alpha:
                break
        return val

def _other_player(world: World) -> int:
    for p in world.planets:
        if p.owner not in (-1, world.player):
            return p.owner
    for f in world.fleets:
        if f.owner != world.player:
            return f.owner
    return 1 - world.player

def minimax_moves(world: World, deadline: float) -> List:
    """
    Idea 3 – 2P Minimax.
    Find the best single action via alpha-beta search; supplement with
    greedy expand for remaining planets.
    """
    import copy
    base = _make_sim_state(world)
    best_val  = -1e9
    best_move = None

    mm_deadline = time.perf_counter() + (deadline - time.perf_counter()) * 0.7

    for src in world.my_planets:
        avail = world.available(src.id)
        if avail < MIN_DISPATCH:
            continue
        for tgt in world.planets:
            if tgt.owner == world.player:
                continue
            a_info = aim(src, tgt, avail, world.initial_by_id, world.ang_vel)
            if a_info is None:
                continue
            angle, turns = a_info
            if time.perf_counter() > mm_deadline:
                break

            state = copy.deepcopy(base)
            _sim_inject(state, src.id, angle, avail)
            _sim_step(state)
            val = _minimax(state, world, MM_DEPTH - 1,
                           -1e9, 1e9, False, mm_deadline)
            if val > best_val:
                best_val  = val
                best_move = [src.id, angle, avail]

    moves = []
    if best_move:
        moves.append(best_move)

    # Fill remaining planets with greedy expand
    used = {best_move[0]} if best_move else set()
    moves += greedy_expand(world, exclude_srcs=used, deadline=deadline)
    return moves


# ── Greedy fallback ──────────────────────────────────────────────────────────

def greedy_expand(world: World, exclude_srcs=None,
                  exclude_tgts=None, deadline=None) -> List:
    """
    Greedy expand: each source attacks its best unclaimed target.
    Crucially allows MULTIPLE dispatches per source planet (split ships)
    so one home planet can capture several neutrals in the same turn.
    """
    if exclude_srcs is None:
        exclude_srcs = set()
    if exclude_tgts is None:
        exclude_tgts = set()

    moves = []
    spent = defaultdict(int)
    claimed_tgts = set(exclude_tgts)

    targets = sorted(
        world.enemy_planets + world.neutral_planets,
        key=lambda p: -(int(p.production) * 3 - int(p.ships) * 0.5)
    )

    # Multi-pass: keep dispatching until no budget left
    for _ in range(6):   # up to 6 fleets per source per turn
        dispatched_this_pass = 0
        for src in sorted(world.my_planets, key=lambda p: -int(p.ships)):
            if src.id in exclude_srcs:
                continue
            if deadline and time.perf_counter() > deadline:
                return moves
            avail = world.available(src.id) - spent[src.id]
            if avail < MIN_DISPATCH:
                continue
            for tgt in targets:
                if tgt.id in claimed_tgts:
                    continue
                a_info = aim(src, tgt, avail, world.initial_by_id, world.ang_vel)
                if a_info is None:
                    continue
                angle, turns = a_info
                _, garrison = world.effective_garrison(tgt.id, turns)
                needed = int(garrison) + 1
                if avail < needed:
                    continue
                # send a bit more than needed to leave ships for chain-capture
                send = min(avail, max(needed, int(needed * 1.3)))
                moves.append([src.id, angle, send])
                spent[src.id] += send
                claimed_tgts.add(tgt.id)
                dispatched_this_pass += 1
                break
        if dispatched_this_pass == 0:
            break   # nothing more to dispatch

    return moves


def mc_expand(world: World, exclude_srcs=None,
              exclude_tgts=None, deadline=None) -> List:
    """
    Idea 2 – MC-guided expansion.
    Generate candidates, score each with rollouts, pick the best ones.
    """
    if exclude_srcs is None:
        exclude_srcs = set()
    if exclude_tgts is None:
        exclude_tgts = set()

    # Generate candidate (src, tgt, angle, ships) tuples
    candidates = []
    targets = world.enemy_planets + world.neutral_planets

    for src in world.my_planets:
        if src.id in exclude_srcs:
            continue
        avail = world.available(src.id)
        if avail < MIN_DISPATCH:
            continue
        for tgt in targets:
            if tgt.id in exclude_tgts:
                continue
            a_info = aim(src, tgt, avail, world.initial_by_id, world.ang_vel)
            if a_info is None:
                continue
            angle, turns = a_info
            _, garrison = world.effective_garrison(tgt.id, turns)
            needed = int(garrison) + 1
            if avail < needed:
                continue
            # quick heuristic pre-score for pruning
            pre = int(tgt.production) * 3.0 - dist(src.x, src.y, tgt.x, tgt.y) * 0.1
            candidates.append((pre, src.id, tgt.id, angle, needed))

    candidates.sort(key=lambda x: -x[0])
    candidates = candidates[:MC_MAX_ACTIONS]

    if not candidates:
        return []

    # Score each with MC rollouts
    scored = []
    for pre, src_id, tgt_id, angle, ships in candidates:
        if deadline and time.perf_counter() > deadline - 0.1:
            break
        score = mc_score(world, src_id, angle, ships)
        scored.append((score, src_id, tgt_id, angle, ships))

    scored.sort(key=lambda x: -x[0])

    # Pick non-conflicting moves
    moves    = []
    used_src = set(exclude_srcs)
    used_tgt = set(exclude_tgts)
    spent    = defaultdict(int)

    for score, src_id, tgt_id, angle, ships in scored:
        if src_id in used_src or tgt_id in used_tgt:
            continue
        avail = world.available(src_id) - spent[src_id]
        if avail < ships:
            continue
        moves.append([src_id, angle, ships])
        used_src.add(src_id)
        used_tgt.add(tgt_id)
        spent[src_id] += ships

    return moves


# ── Defense ──────────────────────────────────────────────────────────────────

def plan_defense(world: World, spent: dict) -> List:
    """Reinforce planets under imminent threat from nearby friendlies."""
    moves = []
    for tgt in world.my_planets:
        inbound_hostile = sum(
            s for eta, o, s in world.arrivals.get(tgt.id, [])
            if o != world.player and o != -1 and eta <= 8
        )
        if inbound_hostile <= int(tgt.ships):
            continue
        deficit = inbound_hostile - int(tgt.ships) + 2
        # find nearest friendly with surplus
        helpers = sorted(
            [p for p in world.my_planets if p.id != tgt.id],
            key=lambda p: dist(p.x, p.y, tgt.x, tgt.y)
        )
        for helper in helpers:
            avail = world.available(helper.id) - spent.get(helper.id, 0)
            if avail < MIN_DISPATCH:
                continue
            ang = safe_angle(helper.x, helper.y, helper.radius, tgt.x, tgt.y)
            if ang is None:
                continue
            send = min(avail, deficit)
            if send < MIN_DISPATCH:
                continue
            moves.append([helper.id, ang, send])
            spent[helper.id] = spent.get(helper.id, 0) + send
            deficit -= send
            if deficit <= 0:
                break
    return moves


# ── Main planner ─────────────────────────────────────────────────────────────

def plan_moves(world: World, deadline: float) -> List:
    moves = []
    spent = defaultdict(int)

    # 0. Defense (always first)
    def_moves = plan_defense(world, spent)
    moves.extend(def_moves)

    # 1. 2P Minimax — only in late game when expansion is done (step > 100)
    if world.is_2p and world.step > 100 and (deadline - time.perf_counter()) > 0.35:
        mm = minimax_moves(world, deadline)
        return moves + mm

    # 2. Momentum Strike — fat fleet cluster attack
    mom_moves = plan_momentum(world, spent)
    if mom_moves:
        moves.extend(mom_moves)
        mom_srcs = {m[0] for m in mom_moves}
        # fill remaining with MC-guided expand
        mc = mc_expand(world,
                       exclude_srcs=mom_srcs,
                       deadline=deadline)
        moves.extend(mc)
        return moves

    # 3. MC-guided expand for all planets
    mc = mc_expand(world, deadline=deadline)
    if mc:
        moves.extend(mc)
        return moves

    # 4. Greedy fallback
    moves.extend(greedy_expand(world, deadline=deadline))
    return moves


# ── Agent entry point ─────────────────────────────────────────────────────────

_step = 0

def agent(obs, config=None):
    global _step
    obs_step = _read(obs, "step", 0) or 0
    if obs_step == 0:
        _step = 0
    _step += 1

    start = time.perf_counter()
    world = World(obs)
    if not world.my_planets:
        return []

    act_timeout = 1.0
    if config is not None:
        try:
            act_timeout = float(_read(config, "actTimeout", 1.0))
        except (TypeError, ValueError):
            pass
    deadline = start + max(0.4, act_timeout * SOFT_DEADLINE_FRAC)

    return plan_moves(world, deadline)


__all__ = ["agent"]
