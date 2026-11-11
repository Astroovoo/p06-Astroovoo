from io import BytesIO

from PIL import Image, ImageDraw

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine


def _sticker_gif():
    # Palette GIF: index 0 is the transparent background, index 1 is blue.
    src = Image.new("P", (100, 100), 0)
    src.putpalette([0, 0, 0, 0, 0, 255] + [0, 0, 0] * 254)
    ImageDraw.Draw(src).ellipse((10, 10, 90, 90), fill=1)
    buf = BytesIO()
    src.save(buf, "GIF", transparency=0)
    return buf.getvalue()


def test_resized_gif_keeps_transparency_with_indexed_preserve():
    cfg = Config(
        SECURITY_KEY="ACME-SEC",
        ENGINE="thumbor.engines.pil",
        PILLOW_PRESERVE_INDEXED_MODE=True,
    )
    engine = Engine(Context(config=cfg))
    engine.load(_sticker_gif(), ".gif")
    assert engine.original_mode == "P"

    engine.resize(240, 160)
    img = Image.open(BytesIO(engine.read(".gif")))

    assert img.info.get("transparency") is not None

    alpha = img.convert("RGBA").getchannel("A")
    transparent_pixels = sum(1 for value in alpha.getdata() if value == 0)
    assert transparent_pixels > 0
