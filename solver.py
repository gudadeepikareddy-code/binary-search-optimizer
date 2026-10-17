"""Binary Search algorithm module + optimization / result calculation module.

All three problems share one idea: the answer lies in a numeric range and the
feasibility check is monotonic, so we can binary search on the answer.

  capacity : minimum truck capacity to deliver all packages (in order) in D days
  speed    : minimum speed to finish all tasks within H hours
  spacing  : maximum possible minimum distance when placing K stops
"""
import math
import time

MAX_BASELINE_WORK = 5_000_000  # skip the linear baseline if (range x items) is too big


# ---------- feasibility checks ----------
def days_needed(weights, cap):
    days, load = 1, 0
    for w in weights:
        if load + w > cap:
            days += 1
            load = 0
        load += w
    return days


def hours_needed(piles, speed):
    return sum(math.ceil(p / speed) for p in piles)


def stops_placed(positions, dist):
    count, last = 1, positions[0]
    for p in positions[1:]:
        if p - last >= dist:
            count += 1
            last = p
    return count


# ---------- generic binary search ----------
def binary_search(lo, hi, ok, maximize=False):
    """Smallest x in [lo, hi] with ok(x) (or largest if maximize=True).
    ok must be monotonic. Returns (answer, steps)."""
    steps = []
    ans = None
    while lo <= hi:
        mid = (lo + hi) // 2
        good = ok(mid)
        steps.append({"low": lo, "high": hi, "mid": mid, "feasible": good})
        if good:
            ans = mid
            if maximize:
                lo = mid + 1
            else:
                hi = mid - 1
        else:
            if maximize:
                hi = mid - 1
            else:
                lo = mid + 1
    return ans, steps


def linear_search(lo, hi, ok, maximize=False):
    """Baseline: try every value one by one. Returns (answer, checks)."""
    rng = range(hi, lo - 1, -1) if maximize else range(lo, hi + 1)
    checks = 0
    for x in rng:
        checks += 1
        if ok(x):
            return x, checks
    return None, checks


# ---------- problem definitions ----------
def build_problem(problem, values, param):
    """Return (lo, hi, ok, maximize, details) for the chosen problem."""
    if problem == "capacity":
        lo, hi = max(values), sum(values)
        ok = lambda c: days_needed(values, c) <= param
        details = lambda a: {"days_used": days_needed(values, a), "days_allowed": param}
        return lo, hi, ok, False, details, "Minimum capacity per day"
    if problem == "speed":
        lo, hi = 1, max(values)
        ok = lambda s: hours_needed(values, s) <= param
        details = lambda a: {"hours_used": hours_needed(values, a), "hours_allowed": param}
        return lo, hi, ok, False, details, "Minimum speed"
    if problem == "spacing":
        pos = sorted(values)
        values[:] = pos
        lo, hi = 1, max(1, (pos[-1] - pos[0]) // (param - 1))
        ok = lambda d: stops_placed(pos, d) >= param
        details = lambda a: {"stops_placed": stops_placed(pos, a), "stops_required": param}
        return lo, hi, ok, True, details, "Maximum minimum-distance"
    raise ValueError("unknown problem")


def solve(problem, values, param):
    values = list(values)
    lo, hi, ok, maximize, details, label = build_problem(problem, values, param)

    t0 = time.perf_counter()
    answer, steps = binary_search(lo, hi, ok, maximize)
    bs_time = time.perf_counter() - t0

    baseline = {"skipped": True, "reason": "search range too large for linear scan"}
    if (hi - lo + 1) * len(values) <= MAX_BASELINE_WORK:
        t0 = time.perf_counter()
        lin_answer, checks = linear_search(lo, hi, ok, maximize)
        lin_time = time.perf_counter() - t0
        baseline = {
            "skipped": False,
            "answer": lin_answer,
            "checks": checks,
            "time_ms": round(lin_time * 1000, 4),
            "matches": lin_answer == answer,
        }

    return {
        "problem": problem,
        "label": label,
        "answer": answer,
        "search_range": [lo, hi],
        "details": details(answer) if answer is not None else {},
        "binary_search": {
            "checks": len(steps),
            "time_ms": round(bs_time * 1000, 4),
            "steps": steps,
        },
        "baseline": baseline,
    }
