from modules.elevation_input import validate_node_z_input


def test_blank_is_valid_and_uses_default():
    assert validate_node_z_input("") == (None, "")


def test_positive_value_is_valid():
    assert validate_node_z_input("1500") == (1500.0, "")


def test_non_numeric_value_returns_error():
    value, error = validate_node_z_input("abc")
    assert value is None
    assert error


def test_value_below_minimum_returns_range_error():
    value, error = validate_node_z_input("-99999")
    assert value is None
    assert "-50000" in error
    assert "200000" in error


def test_value_above_maximum_returns_range_error():
    value, error = validate_node_z_input("200001")
    assert value is None
    assert "-50000" in error
    assert "200000" in error


def test_zero_is_valid():
    assert validate_node_z_input("0") == (0.0, "")
