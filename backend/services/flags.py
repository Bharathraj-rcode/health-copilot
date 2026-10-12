# High / Low / Normal is decided here in code, never by the AI.
# A value exactly on a boundary counts as normal.

# Generic adult reference ranges, used ONLY when the report prints none.
# Tests that depend on sex or age (hemoglobin, creatinine...) are left out on purpose.
_FALLBACK = {
    "fasting glucose": (70, 100),
    "fasting blood sugar": (70, 100),
    "hba1c": (4.0, 5.6),
    "total cholesterol": (None, 200),
    "ldl cholesterol": (None, 100),
    "ldl": (None, 100),
    "hdl cholesterol": (40, None),
    "hdl": (40, None),
    "triglycerides": (None, 150),
    "tsh": (0.4, 4.0),
}


def fallback_range(test_name):
    if not test_name:
        return None
    return _FALLBACK.get(str(test_name).strip().lower())


def compute_flag(value, low, high):
    if value is None:
        return "unknown"
    if low is None and high is None:
        return "unknown"
    if low is not None and value < low:
        return "low"
    if high is not None and value > high:
        return "high"
    return "normal"