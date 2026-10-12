from services.flags import compute_flag


def test_low():
    assert compute_flag(11.2, 13.0, 17.0) == "low"


def test_high():
    assert compute_flag(142, 70, 100) == "high"


def test_lower_boundary_is_normal():
    assert compute_flag(150000, 150000, 410000) == "normal"


def test_upper_boundary_is_normal():
    assert compute_flag(100, 70, 100) == "normal"


def test_no_range_is_unknown():
    assert compute_flag(5, None, None) == "unknown"


def test_only_upper_limit():
    assert compute_flag(120, None, 100) == "high"
    assert compute_flag(80, None, 100) == "normal"


def test_missing_value_is_unknown():
    assert compute_flag(None, 1, 2) == "unknown"