from __future__ import annotations

import pytest

from modules.scale_calibration import canvas_to_real, compute_scale, real_to_canvas


def test_compute_scale_uses_real_over_canvas_distance() -> None:
    assert compute_scale((0, 0), (3, 4), 250.0) == 50.0


def test_compute_scale_rejects_invalid_distances() -> None:
    with pytest.raises(ValueError):
        compute_scale((1, 1), (1, 1), 100.0)
    with pytest.raises(ValueError):
        compute_scale((0, 0), (10, 0), 0.0)


def test_canvas_to_real_applies_origin_and_scale() -> None:
    assert canvas_to_real(12.0, 24.0, 50.0, (10.0, 20.0)) == (100.0, 200.0)


def test_real_to_canvas_is_inverse_of_canvas_to_real() -> None:
    canvas = (123.5, -42.25)
    scale = 25.4
    origin = (10.0, 20.0)

    real = canvas_to_real(*canvas, scale, origin)
    restored = real_to_canvas(*real, scale, origin)

    assert restored == pytest.approx(canvas)


def test_coordinate_conversion_rejects_invalid_scale() -> None:
    with pytest.raises(ValueError):
        canvas_to_real(0, 0, 0, (0, 0))
    with pytest.raises(ValueError):
        real_to_canvas(0, 0, -1, (0, 0))
