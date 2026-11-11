from thumbor.ext.filters import _round_corner


def test_transparent_round_corner_edge_is_partly_transparent():
    width, height, radius = 60, 60, 20
    buf = b"\xff" * (width * height * 4)
    out = _round_corner.apply(
        1, "RGBA", radius, radius, 255, 255, 255, width, height, buf, 1
    )
    alphas = out[3::4]
    assert any(0 < a < 255 for a in alphas), (
        "no edge pixel of the curve has partial alpha"
    )
