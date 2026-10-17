"""Input and validation module."""
import re

PROBLEMS = {
    "capacity": {"param": "days", "min_len": 1},
    "speed": {"param": "hours", "min_len": 1},
    "spacing": {"param": "stops", "min_len": 2},
}
MAX_ITEMS = 10_000
MAX_VALUE = 10**9


def parse_numbers(raw):
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, str):
        items = [x for x in re.split(r"[,\s]+", raw.strip()) if x != ""]
    else:
        raise ValueError("Values must be a list or comma-separated text.")
    out = []
    for x in items:
        try:
            if isinstance(x, bool) or (isinstance(x, float) and not x.is_integer()):
                raise ValueError
            out.append(int(x))
        except (ValueError, TypeError):
            raise ValueError(f"'{x}' is not a whole number.")
    return out


def validate(data):
    """Return (clean, errors). clean = (problem, values, param)."""
    errors = []
    if not isinstance(data, dict):
        return None, ["Request body must be JSON."]
    problem = data.get("problem")
    if problem not in PROBLEMS:
        return None, [f"Problem must be one of: {', '.join(PROBLEMS)}."]
    spec = PROBLEMS[problem]

    values = []
    try:
        values = parse_numbers(data.get("values", ""))
    except ValueError as e:
        errors.append(str(e))
    try:
        param = parse_numbers([data.get("param")])[0]
    except (ValueError, IndexError):
        param = None
        errors.append(f"Please enter a whole number for {spec['param']}.")
    if errors:
        return None, errors

    if len(values) < spec["min_len"]:
        errors.append(f"Enter at least {spec['min_len']} value(s).")
    if len(values) > MAX_ITEMS:
        errors.append(f"At most {MAX_ITEMS} values are allowed.")
    if any(v <= 0 for v in values):
        errors.append("All values must be positive (greater than 0).")
    if any(v > MAX_VALUE for v in values):
        errors.append(f"Values must not exceed {MAX_VALUE}.")
    if param is not None and param < 1:
        errors.append(f"{spec['param'].capitalize()} must be at least 1.")
    if errors:
        return None, errors

    if problem == "capacity" and param > len(values):
        errors.append("Days cannot exceed the number of packages.")
    if problem == "speed" and param < len(values):
        errors.append("Hours must be at least the number of tasks (each takes >= 1 hour).")
    if problem == "spacing":
        if param < 2 or param > len(values):
            errors.append("Stops must be between 2 and the number of positions.")
        if len(set(values)) != len(values):
            errors.append("Positions must be distinct.")
    if errors:
        return None, errors
    return (problem, values, param), []
