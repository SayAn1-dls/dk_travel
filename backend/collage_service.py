"""Pillow-based Pinterest-aesthetic collage composer for Wanderly Vibe Lab.

Renders 1080x1920 (portrait, Insta-story ratio) collages across 6 templates:
    polaroid_scrapbook | magazine | postcard | filmstrip | moodboard | film_photo
"""

from __future__ import annotations

import base64
import io
import logging
import math
import os
import random
from datetime import datetime
from pathlib import Path
from typing import List, Sequence, Tuple

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

log = logging.getLogger(__name__)

# ---------- palette ----------
CREAM = (250, 243, 231)         # #FAF3E7
SAND = (232, 213, 183)          # #E8D5B7
TERRACOTTA = (198, 93, 58)      # #C65D3A
SAGE = (168, 184, 154)          # #A8B89A
INK = (44, 36, 22)              # #2C2416
PAPER = (247, 240, 226)         # subtle paper

CANVAS_W, CANVAS_H = 1080, 1920

# ---------- fonts ----------
FONT_DIR = Path(__file__).parent / "fonts"

VALID_TEMPLATES = {"polaroid_scrapbook", "magazine", "postcard", "filmstrip", "moodboard", "film_photo"}


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONT_DIR / name
    if not path.exists():
        # Fallback to any TTF we have
        candidates = list(FONT_DIR.glob("*.ttf")) + list(FONT_DIR.glob("*.otf"))
        if candidates:
            path = candidates[0]
        else:
            return ImageFont.load_default()
    return ImageFont.truetype(str(path), size)


def font_serif(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return _font("PlayfairDisplay-Bold.ttf" if bold else "PlayfairDisplay-Regular.ttf", size)


def font_display(size: int) -> ImageFont.FreeTypeFont:
    return _font("DMSerifDisplay-Regular.ttf", size)


def font_hand(size: int) -> ImageFont.FreeTypeFont:
    return _font("Caveat-Regular.ttf", size)


def font_sans(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return _font("Inter-Bold.ttf" if bold else "Inter-Regular.ttf", size)


# ---------- helpers ----------

def _decode_image(data: bytes) -> Image.Image:
    im = Image.open(io.BytesIO(data))
    im.load()
    if getattr(im, "is_animated", False):
        im.seek(0)
    return ImageOps.exif_transpose(im).convert("RGB")


def _fit_cover(img: Image.Image, w: int, h: int) -> Image.Image:
    """Crop-cover an image into an exact w x h box."""
    src_w, src_h = img.size
    scale = max(w / src_w, h / src_h)
    new_w, new_h = int(math.ceil(src_w * scale)), int(math.ceil(src_h * scale))
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    return resized.crop((left, top, left + w, top + h))


def _rounded_mask(size: Tuple[int, int], radius: int) -> Image.Image:
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return m


def _drop_shadow(size: Tuple[int, int], radius: int, offset: Tuple[int, int], blur: int,
                 opacity: int = 90) -> Image.Image:
    w, h = size
    pad = blur * 2 + max(abs(offset[0]), abs(offset[1])) + 8
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle(
        (pad + offset[0], pad + offset[1], pad + offset[0] + w - 1, pad + offset[1] + h - 1),
        radius=radius,
        fill=(0, 0, 0, opacity),
    )
    return canvas.filter(ImageFilter.GaussianBlur(blur))


def _paste_with_shadow(base: Image.Image, patch: Image.Image, pos: Tuple[int, int],
                       radius: int = 0, shadow_offset: Tuple[int, int] = (0, 12),
                       shadow_blur: int = 22, shadow_opacity: int = 90) -> None:
    """Paste `patch` on `base` at pos (top-left of the patch) with a soft drop shadow."""
    w, h = patch.size
    shadow = _drop_shadow((w, h), radius, shadow_offset, shadow_blur, shadow_opacity)
    sx = pos[0] - shadow_blur * 2 - 8 + max(0, -shadow_offset[0])
    sy = pos[1] - shadow_blur * 2 - 8 + max(0, -shadow_offset[1])
    base.alpha_composite(shadow, dest=(sx, sy))
    base.alpha_composite(patch, dest=pos)


def _rotate_rgba(img: Image.Image, angle: float) -> Image.Image:
    return img.rotate(angle, resample=Image.BICUBIC, expand=True)


def _paper_texture(size: Tuple[int, int], seed: int = 7) -> Image.Image:
    """A warm paper-like background with subtle noise."""
    w, h = size
    base = Image.new("RGB", (w, h), CREAM)
    # subtle vignette + noise
    noise = Image.effect_noise((w, h), 12).convert("L")
    noise = noise.filter(ImageFilter.GaussianBlur(0.6))
    tinted = Image.merge("RGB", (
        noise.point(lambda p: 250 - (255 - p) // 4),
        noise.point(lambda p: 243 - (255 - p) // 4),
        noise.point(lambda p: 231 - (255 - p) // 4),
    ))
    base = Image.blend(base, tinted, 0.35)

    # gentle warm vignette
    vignette = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vignette)
    for i, alpha in enumerate([10, 20, 30]):
        vd.rectangle((i * 30, i * 30, w - i * 30, h - i * 30), outline=alpha)
    vignette = vignette.filter(ImageFilter.GaussianBlur(120))
    overlay = Image.new("RGB", (w, h), (150, 110, 60))
    base = Image.composite(overlay, base, vignette).convert("RGB")
    base = Image.blend(Image.new("RGB", (w, h), CREAM), base, 0.35)
    return base


def _film_grain(size: Tuple[int, int], strength: int = 18) -> Image.Image:
    grain = Image.effect_noise(size, strength).convert("L")
    return grain.filter(ImageFilter.GaussianBlur(0.4))


def _apply_grain(img: Image.Image, opacity: float = 0.18) -> Image.Image:
    grain = _film_grain(img.size, strength=22).convert("RGB")
    return Image.blend(img, grain, opacity)


def _vintage_grade(img: Image.Image) -> Image.Image:
    """Warm, faded, mildly desaturated color grade."""
    im = ImageEnhance.Color(img).enhance(0.75)
    im = ImageEnhance.Contrast(im).enhance(0.92)
    warm = Image.new("RGB", im.size, (255, 175, 110))
    im = Image.blend(im, warm, 0.10)
    im = ImageEnhance.Brightness(im).enhance(1.02)
    return im


def _tape_strip(size: Tuple[int, int], angle: float = 0.0) -> Image.Image:
    """A translucent washi-tape strip."""
    w, h = size
    tape = Image.new("RGBA", (w, h), (255, 232, 170, 175))
    d = ImageDraw.Draw(tape)
    for x in range(0, w, 6):
        d.line((x, 0, x, h), fill=(255, 220, 150, 30))
    # torn edges
    mask = Image.new("L", (w, h), 255)
    md = ImageDraw.Draw(mask)
    for x in range(0, w, 3):
        md.line((x, 0, x, random.randint(0, 3)), fill=0)
        md.line((x, h - random.randint(1, 4), x, h), fill=0)
    tape.putalpha(mask)
    return _rotate_rgba(tape, angle)


def _text_wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    cur: List[str] = []
    for w in words:
        trial = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def _draw_wrapped(draw: ImageDraw.ImageDraw, xy: Tuple[int, int], text: str,
                  font: ImageFont.FreeTypeFont, fill, max_width: int, line_gap: int = 6,
                  align: str = "left") -> int:
    lines = _text_wrap(draw, text, font, max_width)
    x, y = xy
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        if align == "center":
            draw.text((x + (max_width - lw) // 2, y), line, font=font, fill=fill)
        elif align == "right":
            draw.text((x + max_width - lw, y), line, font=font, fill=fill)
        else:
            draw.text((x, y), line, font=font, fill=fill)
        y += lh + line_gap
    return y


# ---------- brand mark ----------

def _brand_mark(draw: ImageDraw.ImageDraw, x: int, y: int, color=INK) -> None:
    draw.text((x, y), "Wanderly", font=font_serif(30, bold=True), fill=color)
    draw.text((x, y + 42), "Where every trip becomes a story.", font=font_sans(15), fill=color)


# ==================================================================================
# TEMPLATES
# ==================================================================================

def _tpl_polaroid_scrapbook(photos: List[Image.Image], caption: str, quote: str) -> Image.Image:
    """Tilted polaroids on paper with washi-tape and handwritten caption."""
    canvas = _paper_texture((CANVAS_W, CANVAS_H)).convert("RGBA")

    # Header
    draw = ImageDraw.Draw(canvas)
    header = "The Trip"
    draw.text((80, 90), header.upper(), font=font_sans(18, bold=True), fill=INK + (255,))
    draw.line((80, 132, 260, 132), fill=TERRACOTTA + (255,), width=3)
    draw.text((80, 148), "A little scrapbook of moments.", font=font_serif(34), fill=INK + (255,))

    # Layout polaroids
    n = len(photos)
    positions: Sequence[Tuple[int, int, int, float]] = []  # (x, y, w, angle)
    if n == 3:
        positions = [
            (120, 290, 500, -5.5),
            (480, 560, 500, 4.8),
            (140, 860, 500, -3.2),
        ]
    elif n == 4:
        positions = [
            (90, 290, 440, -6.5),
            (540, 360, 420, 5.2),
            (110, 730, 420, 4.5),
            (520, 830, 440, -4.8),
        ]
    else:  # 5
        positions = [
            (60, 290, 400, -7.5),
            (560, 310, 400, 5.5),
            (140, 680, 400, 4.0),
            (540, 730, 380, -6.0),
            (240, 1070, 440, 2.5),
        ]

    rng = random.Random(hash(caption) & 0xFFFF)
    for photo, (x, y, w, angle) in zip(photos, positions):
        pw = w
        ph = int(w * 1.05)  # photo area
        polaroid_w = pw + 30
        polaroid_h = ph + 90  # bottom caption strip
        polaroid = Image.new("RGBA", (polaroid_w, polaroid_h), (253, 250, 240, 255))
        # photo inset
        inner = _fit_cover(photo, pw, ph)
        inner = _apply_grain(inner, 0.08)
        polaroid.paste(inner, (15, 15))
        # thin border
        pd = ImageDraw.Draw(polaroid)
        pd.rectangle((15, 15, 15 + pw - 1, 15 + ph - 1), outline=(220, 210, 190, 255), width=2)
        # handwritten mini-caption
        hand_bits = ["hi.", "sunday.", "us.", "golden.", "the crew.", "morning.", "hello.",
                     "postcard.", "later.", "sky.", "beach day.", "hills.", "gold.", "adieu."]
        pd.text((30, ph + 24), rng.choice(hand_bits), font=font_hand(38), fill=INK + (255,))

        rotated = _rotate_rgba(polaroid, angle)
        _paste_with_shadow(canvas, rotated, (x, y), radius=0,
                           shadow_offset=(0, 14), shadow_blur=22, shadow_opacity=110)

        # washi tape
        tape = _tape_strip((160, 40), angle=angle + rng.uniform(-6, 6))
        tx = x + rotated.size[0] // 2 - tape.size[0] // 2 + rng.randint(-20, 20)
        ty = y - 10
        canvas.alpha_composite(tape, dest=(tx, ty))

    # Big handwritten caption
    caption_y = CANVAS_H - 380
    draw.text((80, caption_y - 20), '"', font=font_serif(120), fill=TERRACOTTA + (255,))
    cap_end_y = _draw_wrapped(draw, (150, caption_y + 10), caption, font_hand(66),
                              fill=INK + (255,), max_width=CANVAS_W - 260, line_gap=2)

    # quote — placed below caption with clear spacing
    quote_y = max(cap_end_y + 22, CANVAS_H - 190)
    _draw_wrapped(draw, (80, quote_y), quote, font_serif(24),
                  fill=SAGE + (255,), max_width=CANVAS_W - 420, line_gap=6)

    # brand mark
    _brand_mark(draw, CANVAS_W - 340, CANVAS_H - 100)

    return canvas.convert("RGB")


def _tpl_magazine(photos: List[Image.Image], caption: str, quote: str) -> Image.Image:
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), CREAM + (255,))
    draw = ImageDraw.Draw(canvas)

    # Editorial masthead
    draw.text((80, 90), "ISSUE N°26  ·  FEB 2026", font=font_sans(18, bold=True), fill=INK + (255,))
    draw.line((80, 128, CANVAS_W - 80, 128), fill=INK + (255,), width=2)
    draw.text((80, 148), "WANDERLY", font=font_display(96), fill=TERRACOTTA + (255,))
    draw.text((80, 258), "A visual essay in five frames.", font=font_serif(30), fill=INK + (255,))

    # Hero photo
    hero = _fit_cover(photos[0], 920, 720)
    hero = _apply_grain(hero, 0.08)
    hero_rgba = hero.convert("RGBA")
    _paste_with_shadow(canvas, hero_rgba, (80, 340), radius=0,
                       shadow_offset=(0, 20), shadow_blur=30, shadow_opacity=90)

    # Overlay caption card on hero
    card = Image.new("RGBA", (500, 130), CREAM + (240,))
    cd = ImageDraw.Draw(card)
    cd.text((22, 20), "CHAPTER 01", font=font_sans(14, bold=True), fill=TERRACOTTA + (255,))
    _draw_wrapped(cd, (22, 46), caption, font_serif(30, bold=True), INK + (255,), max_width=460, line_gap=4)
    canvas.alpha_composite(card, dest=(120, 940))

    # Side photos
    side_positions = [(80, 1130), (395, 1130), (710, 1130)]
    side_size = (290, 380)
    for i, pos in enumerate(side_positions):
        if 1 + i >= len(photos):
            break
        p = _fit_cover(photos[1 + i], *side_size)
        p = _apply_grain(p, 0.06).convert("RGBA")
        _paste_with_shadow(canvas, p, pos, radius=0, shadow_offset=(0, 14), shadow_blur=22, shadow_opacity=90)

    # Pull quote
    draw.text((80, 1560), '"', font=font_display(150), fill=TERRACOTTA + (255,))
    _draw_wrapped(draw, (190, 1590), quote, font_serif(38, bold=False), INK + (255,), max_width=800, line_gap=6)

    # Footer
    draw.line((80, 1790, CANVAS_W - 80, 1790), fill=INK + (255,), width=1)
    draw.text((80, 1810), "WANDERLY", font=font_serif(28, bold=True), fill=TERRACOTTA + (255,))
    draw.text((80, 1852), "Where every trip becomes a story.", font=font_sans(16), fill=INK + (255,))
    draw.text((CANVAS_W - 200, 1810), "N°26", font=font_display(56), fill=INK + (255,))

    return canvas.convert("RGB")


def _tpl_postcard(photos: List[Image.Image], caption: str, quote: str) -> Image.Image:
    canvas = _paper_texture((CANVAS_W, CANVAS_H)).convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    # Card panel
    card_w, card_h = 900, 1300
    card_x = (CANVAS_W - card_w) // 2
    card_y = 260
    card = Image.new("RGBA", (card_w, card_h), (255, 251, 240, 255))
    _paste_with_shadow(canvas, card, (card_x, card_y), radius=6,
                       shadow_offset=(0, 24), shadow_blur=34, shadow_opacity=110)

    # Photo with thick white border (postcard photo)
    photo = _fit_cover(photos[0], 780, 900)
    photo = _apply_grain(photo, 0.09)
    frame = Image.new("RGB", (photo.size[0] + 40, photo.size[1] + 40), (255, 250, 240))
    frame.paste(photo, (20, 20))
    frame_rgba = frame.convert("RGBA")
    canvas.alpha_composite(frame_rgba, dest=(card_x + 40, card_y + 60))

    # "Wish you were here" stamp corner
    stamp_x = card_x + card_w - 200
    stamp_y = card_y + 50
    stamp = Image.new("RGBA", (160, 190), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rectangle((0, 0, 159, 189), outline=TERRACOTTA + (255,), width=3)
    for i in range(0, 160, 12):  # perforation dots
        sd.ellipse((i - 3, -3, i + 3, 3), fill=CREAM + (255,))
        sd.ellipse((i - 3, 186, i + 3, 192), fill=CREAM + (255,))
    for i in range(0, 190, 12):
        sd.ellipse((-3, i - 3, 3, i + 3), fill=CREAM + (255,))
        sd.ellipse((156, i - 3, 162, i + 3), fill=CREAM + (255,))
    sd.text((18, 30), "WISH", font=font_display(30), fill=TERRACOTTA + (255,))
    sd.text((18, 65), "YOU", font=font_display(30), fill=TERRACOTTA + (255,))
    sd.text((18, 100), "WERE", font=font_display(30), fill=TERRACOTTA + (255,))
    sd.text((18, 135), "HERE", font=font_display(30), fill=TERRACOTTA + (255,))
    stamp = _rotate_rgba(stamp, -6)
    canvas.alpha_composite(stamp, dest=(stamp_x, stamp_y))

    # Handwritten caption inside the postcard — wrapped, avoids clipping
    cap_top = card_y + 990
    cap_end = _draw_wrapped(draw, (card_x + 60, cap_top), caption, font_hand(56),
                            fill=INK + (255,), max_width=card_w - 120, line_gap=6)
    line_y = cap_end + 20
    draw.line((card_x + 60, line_y, card_x + card_w - 60, line_y), fill=SAND + (255,), width=2)
    _draw_wrapped(draw, (card_x + 60, line_y + 18), quote, font_serif(22),
                  fill=SAGE + (255,), max_width=card_w - 120, line_gap=4)

    # Top label + brand at bottom
    draw.text((card_x, 190), "POSTCARD FROM SOMEWHERE", font=font_sans(18, bold=True), fill=TERRACOTTA + (255,))
    _brand_mark(draw, card_x, card_y + card_h + 30)

    return canvas.convert("RGB")


def _tpl_filmstrip(photos: List[Image.Image], caption: str, quote: str) -> Image.Image:
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), INK + (255,))
    draw = ImageDraw.Draw(canvas)

    # Film strip — frame height scales to fit inside canvas
    strip_w = 720
    strip_x = (CANVAS_W - strip_w) // 2
    strip_top = 220
    bottom_reserve = 360  # space for caption + quote + brand below the strip
    max_strip_h = CANVAS_H - strip_top - bottom_reserve
    gap = 20
    n = min(len(photos), 5)
    frame_h = max(160, (max_strip_h - (n + 1) * gap - 80) // n)
    strip_h = n * frame_h + (n + 1) * gap + 80
    strip = Image.new("RGBA", (strip_w, strip_h), (20, 15, 10, 255))
    sd = ImageDraw.Draw(strip)

    # Sprocket holes — evenly spaced
    hole_w, hole_h = 44, 60
    for row in range(n * 2 + 2):
        y = int(row * (strip_h - 60) / (n * 2 + 1)) + 30
        sd.rounded_rectangle((28, y, 28 + hole_w, y + hole_h), radius=8, fill=(0, 0, 0, 255))
        sd.rounded_rectangle((strip_w - 28 - hole_w, y, strip_w - 28, y + hole_h), radius=8, fill=(0, 0, 0, 255))

    # Frames
    inner_x = 110
    inner_w = strip_w - 220
    for i in range(n):
        p = _fit_cover(photos[i], inner_w, frame_h)
        p = _apply_grain(p, 0.10)
        py = gap + i * (frame_h + gap) + 40
        strip.paste(p, (inner_x, py))
        # frame label
        sd.text((inner_x, py + frame_h + 2), f"FRAME 0{i + 1}", font=font_sans(12, bold=True), fill=(230, 220, 200, 255))

    _paste_with_shadow(canvas, strip, (strip_x, strip_top), radius=6,
                       shadow_offset=(0, 22), shadow_blur=30, shadow_opacity=140)

    # Header
    draw.text((80, 90), "35MM · A ROLL OF MEMORIES", font=font_sans(18, bold=True), fill=SAND + (255,))
    draw.line((80, 128, 640, 128), fill=TERRACOTTA + (255,), width=2)
    draw.text((80, 148), "Kodak of a kind.", font=font_display(46), fill=CREAM + (255,))

    # Bottom caption/quote
    below = strip_top + strip_h + 30
    end_y = _draw_wrapped(draw, (80, below), caption, font_serif(32, bold=True),
                          CREAM + (255,), max_width=CANVAS_W - 160, line_gap=4)
    _draw_wrapped(draw, (80, end_y + 16), quote, font_serif(20),
                  SAND + (255,), max_width=CANVAS_W - 200, line_gap=4)

    # brand
    _brand_mark(draw, 80, CANVAS_H - 100, color=CREAM)

    return canvas.convert("RGB")


def _tpl_moodboard(photos: List[Image.Image], caption: str, quote: str) -> Image.Image:
    canvas = _paper_texture((CANVAS_W, CANVAS_H)).convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    # Header
    draw.text((80, 100), "MOODBOARD", font=font_sans(18, bold=True), fill=TERRACOTTA + (255,))
    draw.text((80, 130), "The vibe, board-ified.", font=font_serif(40), fill=INK + (255,))

    # Photo tiles — irregular Pinterest grid
    tiles = []
    if len(photos) == 3:
        tiles = [(80, 260, 560, 620), (680, 260, 320, 380), (680, 700, 320, 460), (80, 900, 560, 260)]
    if len(photos) == 4:
        tiles = [(80, 260, 460, 620), (580, 260, 420, 300), (580, 600, 420, 380), (80, 900, 460, 320)]
    if len(photos) == 5:
        tiles = [(80, 260, 440, 520), (560, 260, 440, 340), (560, 640, 440, 420), (80, 800, 300, 420),
                 (420, 1240, 580, 300)]
    if not tiles:
        tiles = [(80, 260, 460, 520)] * len(photos)

    used = min(len(photos), len(tiles))
    for i in range(used):
        x, y, w, h = tiles[i]
        img = _fit_cover(photos[i], w, h)
        img = _apply_grain(img, 0.06)
        # rounded corners
        mask = _rounded_mask((w, h), 22)
        rgba = img.convert("RGBA")
        rgba.putalpha(mask)
        _paste_with_shadow(canvas, rgba, (x, y), radius=22, shadow_offset=(0, 16), shadow_blur=24, shadow_opacity=90)

    # Color chips row
    chips_y = CANVAS_H - 500
    for i, col in enumerate([TERRACOTTA, SAND, SAGE]):
        cx = 80 + i * 120
        chip = Image.new("RGBA", (100, 100), col + (255,))
        chip.putalpha(_rounded_mask((100, 100), 18))
        _paste_with_shadow(canvas, chip, (cx, chips_y), radius=18, shadow_offset=(0, 10), shadow_blur=16, shadow_opacity=70)

    # Big serif quote overlay
    quote_x, quote_y = 80, CANVAS_H - 380
    q_end = _draw_wrapped(draw, (quote_x, quote_y), f"\u201c{quote}\u201d", font_serif(38, bold=True),
                          fill=INK + (255,), max_width=CANVAS_W - 160, line_gap=6)

    # Handwritten caption — wrapped so it never runs off canvas
    _draw_wrapped(draw, (80, q_end + 24), caption, font_hand(52),
                  fill=TERRACOTTA + (255,), max_width=CANVAS_W - 380, line_gap=-2)

    _brand_mark(draw, CANVAS_W - 340, CANVAS_H - 100)

    return canvas.convert("RGB")


def _tpl_film_photo(photos: List[Image.Image], caption: str, quote: str) -> Image.Image:
    """Single hero photo, film grain, date stamp corner, vintage color grade."""
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (18, 14, 10, 255))
    draw = ImageDraw.Draw(canvas)

    # Hero photo with vintage grade
    photo = _fit_cover(photos[0], 900, 1200)
    photo = _vintage_grade(photo)
    photo = _apply_grain(photo, 0.20)

    # cream border (photo print border)
    border_w, border_h = photo.size[0] + 60, photo.size[1] + 60
    frame = Image.new("RGB", (border_w, border_h), CREAM)
    frame.paste(photo, (30, 30))
    frame_rgba = frame.convert("RGBA")

    fx = (CANVAS_W - border_w) // 2
    fy = 200
    _paste_with_shadow(canvas, frame_rgba, (fx, fy), radius=0,
                       shadow_offset=(0, 30), shadow_blur=40, shadow_opacity=180)

    # Date stamp corner (LED orange)
    date_str = datetime.now().strftime("%d.%m.%Y").replace(".", " . ")
    stamp = Image.new("RGBA", (280, 60), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.text((0, 0), date_str, font=font_sans(38, bold=True), fill=(230, 90, 40, 255))
    # slight glow
    glow = stamp.filter(ImageFilter.GaussianBlur(3))
    canvas.alpha_composite(glow, dest=(fx + border_w - 320, fy + border_h - 90))
    canvas.alpha_composite(stamp, dest=(fx + border_w - 320, fy + border_h - 90))

    # Top label
    draw.text((80, 90), "SHOT ON FILM · 35MM", font=font_sans(18, bold=True), fill=SAND + (255,))
    draw.line((80, 128, 480, 128), fill=TERRACOTTA + (255,), width=2)
    draw.text((80, 148), "One frame. One feeling.", font=font_display(36), fill=CREAM + (255,))

    # Caption + quote below
    below_y = fy + border_h + 40
    _draw_wrapped(draw, (80, below_y), caption, font_serif(46, bold=True),
                  CREAM + (255,), max_width=CANVAS_W - 160, line_gap=6)
    _draw_wrapped(draw, (80, below_y + 130), f"“{quote}”", font_serif(26),
                  fill=SAND + (255,), max_width=CANVAS_W - 200, line_gap=6)

    # brand
    _brand_mark(draw, 80, CANVAS_H - 110, color=CREAM)

    # subtle full-frame grain overlay
    grain_layer = _film_grain((CANVAS_W, CANVAS_H), strength=26).convert("RGB")
    canvas_rgb = canvas.convert("RGB")
    blended = Image.blend(canvas_rgb, grain_layer, 0.06)
    return blended


# ==================================================================================
# ENTRY
# ==================================================================================

def compose_collage(image_bytes_list: List[bytes], template: str, caption: str, quote: str) -> Image.Image:
    if template not in VALID_TEMPLATES:
        template = "polaroid_scrapbook"

    photos = [_decode_image(b) for b in image_bytes_list]

    if template == "polaroid_scrapbook":
        return _tpl_polaroid_scrapbook(photos, caption, quote)
    if template == "magazine":
        return _tpl_magazine(photos, caption, quote)
    if template == "postcard":
        return _tpl_postcard(photos, caption, quote)
    if template == "filmstrip":
        return _tpl_filmstrip(photos, caption, quote)
    if template == "moodboard":
        return _tpl_moodboard(photos, caption, quote)
    if template == "film_photo":
        return _tpl_film_photo(photos, caption, quote)

    return _tpl_polaroid_scrapbook(photos, caption, quote)


def image_to_data_url(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def save_collage(img: Image.Image, out_dir: Path) -> Tuple[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    import uuid as _uuid
    uid = _uuid.uuid4().hex
    path = out_dir / f"{uid}.png"
    img.save(path, format="PNG", optimize=True)
    return uid, path
