# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["pillow>=10.4", "numpy>=1.26"]
# ///
"""Proof Frame · Нотолгоо хүрээ.

An ad frame that shows off a result: a customer comment as the hook, a huge silver headline,
a tilted BEFORE phone behind a bigger AFTER phone joined by a dotted arc arrow, and a price pill.
The plan's clips are the AFTER video (they play in the big phone, with their sound). The BEFORE clip
or photo ("before" in the plan) is read by a second ffmpeg pipe and plays in the tilted phone.
Usage: uv run render.py plan.json
"""
import math
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import goatcut as g  # noqa: E402
from PIL import Image, ImageColor, ImageDraw, ImageFilter  # noqa: E402

NAME = "proof-frame"
GRADE = ""  # the AFTER video is already the member's finished edit; leave its colour alone
INTER, OSWALD = "Inter[opsz,wght].ttf", "Oswald[wght].ttf"
FIT_SIZE = (504, 896)                 # AFTER phone screen
BS = (344, 612)                       # BEFORE phone screen
EDGE = 6                              # phone bezel
AX, AY = 460, 682                     # AFTER phone top-left; its bottom stays above y 1600
BC, BTILT = (270, 1044), 9            # BEFORE phone centre, tilt (degrees, counter-clockwise)
COMMENT_Y, HEAD_Y, SUB_Y = 280, 382, 528    # the comment starts inside the safe box (y >= 270)
HEAD_H = 130                          # headline ink height cap, so two lines never reach the sub-pill
PRICE = (120, 1150)                   # price pill left, top: inside the safe box
SILVER = [(0, (255, 255, 255)), (0.45, (201, 206, 214)), (0.53, (126, 133, 143)), (0.7, (233, 236, 239)),
          (1, (154, 161, 170))]
ARC = ((268, 722), (328, 637), (548, 620), (635, 668))  # dotted arc, cubic Bezier
ARC_XY = (200, 560)                   # top-left of the arc sprite (500x260)
DELAY = {"comment": 0.0, "headline": 0.2, "sub": 0.4}   # the top stack lands one piece after another


def lerp_stops(stops, x):
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if x <= b:
            k = (x - a) / (b - a) if b > a else 0
            return tuple(round(p + (q - p) * k) for p, q in zip(ca, cb))
    return stops[-1][1]


def rrect(size, radius, fill, outline=None, width=0, s=3):
    """Anti-aliased rounded rectangle sprite (Pillow draws hard edges, so draw 3x and shrink)."""
    w, h = size
    im = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * s - 1, h * s - 1), radius * s, fill=fill,
                                         outline=outline, width=width * s)
    return im.resize((w, h), Image.LANCZOS)


def shadow(size, radius, blur, alpha, pad, dy=0):
    """Soft black drop shadow sprite, pad px bigger than size on each side, dy lower."""
    w, h = size
    a = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
    ImageDraw.Draw(a).rounded_rectangle((pad, pad + dy, pad + w, pad + h + dy), radius, fill=int(255 * alpha))
    im = Image.new("RGBA", a.size, (0, 0, 0, 0))
    im.putalpha(a.filter(ImageFilter.GaussianBlur(blur)))
    return im


# ---------------------------------------------------------------- setup

def setup(ctx):
    try:
        ctx.accent = ImageColor.getrgb(str(ctx.opt("accent", "#E8663A")))[:3]
    except ValueError:
        g.die('look.accent must be a colour like "#E8663A"')
    ctx.labels = str(ctx.opt("before_label", "ӨМНӨ")), str(ctx.opt("after_label", "ДАРАА"))
    ctx.bg = backdrop()
    ctx.after_phone = phone((FIT_SIZE[0] + 2 * EDGE, FIT_SIZE[1] + 2 * EDGE), ctx, ctx.labels[1])
    ctx.before_phone = phone((BS[0] + 2 * EDGE, BS[1] + 2 * EDGE), ctx, ctx.labels[0])
    ctx.after_mask = g.rounded_mask(FIT_SIZE, 22)
    ctx.before_mask = g.rounded_mask(BS, 22)
    open_before(ctx)


def SFX(ctx):
    # a notification as the comment pill appears, a whoosh as the phones fly in, a ding as the price lands
    ev = [{"sound": "notify", "at": x.get("start", 0), "volume": 0.8} for x in ctx.texts("comment")]
    ev.append({"sound": "whoosh", "at": 0.45, "volume": 0.7})
    ev += [{"sound": "ding", "at": x.get("start", 0) + 0.15} for x in ctx.texts("price")]
    return ev


def backdrop():
    """Charcoal glow from the top, then a dark horizon with a bright rim and a soft light above it."""
    s = 8  # the glow is smooth, so work it out on a small grid and scale up
    sm = Image.new("RGB", (1080 // s, 1920 // s))
    stops = [(0, (74, 78, 87)), (0.45, (34, 37, 42)), (0.8, (11, 12, 14)), (1, (11, 12, 14))]
    for y in range(sm.height):
        for x in range(sm.width):
            d = math.hypot((x * s - 540) / 900, y * s / 1700)
            sm.putpixel((x, y), lerp_stops(stops, min(d, 1)))
    bg = sm.resize((1080, 1920), Image.BICUBIC).convert("RGBA")
    box = (-432, 883, 1512, 883 + 1344)
    glow = Image.new("L", (1080, 1920), 0)
    ImageDraw.Draw(glow).ellipse((box[0], box[1] - 8, box[2], box[3] - 8), fill=56)
    bg.paste((255, 255, 255), (0, 0), glow.filter(ImageFilter.GaussianBlur(40)))
    ground = Image.new("RGB", (1, 2))
    ground.putpixel((0, 0), (23, 25, 29))
    ground.putpixel((0, 1), (11, 12, 14))
    ground = ground.resize((1080, 700), Image.BILINEAR).crop((0, 0, 1080, 1920 - box[1]))
    k = 2
    m = Image.new("L", (1080 * k, 1920 * k), 0)
    ImageDraw.Draw(m).ellipse([v * k for v in box], fill=255)
    bg.paste(ground, (0, box[1]), m.resize((1080, 1920), Image.LANCZOS).crop((0, box[1], 1080, 1920)))
    rim = Image.new("L", (1080 * k, 1920 * k), 0)
    ImageDraw.Draw(rim).ellipse([v * k for v in box], outline=204, width=4 * k)
    bg.paste((255, 255, 255), (0, 0), rim.resize((1080, 1920), Image.LANCZOS))
    return bg


def phone(size, ctx, label):
    """Bezel, shadow and corner label for one phone; the screen is pasted into the hole each frame."""
    pad = 60
    sp = shadow(size, 28, 24, 0.55, pad, dy=20)
    sp.alpha_composite(rrect(size, 28, (29, 31, 35, 255)), (pad, pad))
    f = ctx.font(INTER, 22, {"wght": 700})
    tag = g.text_sprite(label, f, tracking=0.06)
    box = rrect((tag.width + 20, tag.height + 14), 8, (0, 0, 0, 115))
    box.alpha_composite(tag, (10, 7))
    return sp, box, pad


def open_before(ctx):
    """Second ffmpeg pipe for the BEFORE clip: trimmed, cover-cropped to the small phone, last frame held."""
    b = ctx.plan.get("before")
    if not isinstance(b, dict) or not b.get("src"):
        g.die('the plan needs "before": {"src": "raw/before.mp4"}, the clip or photo for the tilted phone')
    c = g._clips({"clips": [b]}, ctx.plan_dir)[0]  # same checks as the main clips (file, in/out, HDR)
    w, h = BS
    cx, cy = float(b.get("cx", 0.5)), float(b.get("cy", 0.5))
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,"
          f"crop={w}:{h}:(iw-{w})*{cx}:(ih-{h})*{cy},setsar=1,fps={g.FPS},"
          f"tpad=stop_mode=clone:stop_duration={ctx.dur + 1:.3f},format=rgb24")
    ctx.before = subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", *g._inputs([c]), "-vf", vf,
         "-frames:v", str(int(round(ctx.dur * g.FPS)) + 2), "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ctx.bframe = None


def next_before(ctx):
    buf = ctx.before.stdout.read(BS[0] * BS[1] * 3)
    if len(buf) == BS[0] * BS[1] * 3:
        ctx.bframe = Image.frombytes("RGB", BS, buf)
    elif ctx.bframe is None:
        ctx.before.wait()
        g.die("ffmpeg could not read the BEFORE clip: " + ctx.before.stderr.read().decode(errors="replace")[-600:])
    return ctx.bframe


# ---------------------------------------------------------------- sprites

def comment_pill(ctx, item):
    f = ctx.fit(item["text"], INTER, 840 - 130, 32, 20, {"wght": 800})
    fs = ctx.font(INTER, 20, {"wght": 500})
    text, name = g.drawable(item["text"], f), g.drawable(item.get("name", "хэрэглэгч"), fs)
    w = int(max(f.getlength(text), fs.getlength(name))) + 12 + 56 + 16 + 34
    s = rrect((w, 80), 40, (244, 244, 242, 255))
    g.paste(s, rrect((56, 56), 28, (185, 187, 192, 255)), 12, 12)
    d = ImageDraw.Draw(s)
    d.text((84, 34), name, font=fs, fill=(138, 138, 138), anchor="ls")
    d.text((84, 66), text, font=f, fill=(17, 17, 17), anchor="ls")
    return s


def silver_headline(ctx, text):
    """Huge condensed headline with a chrome-like vertical gradient and a soft shadow, one band per line."""
    longest = max(text.split("\n"), key=len)
    f = ctx.fit(longest, OSWALD, 840, 180, 56, {"wght": 700})
    lines = []
    for ln in text.split("\n"):
        m = g.text_sprite(ln, f).getchannel("A")
        col = Image.new("RGB", (1, m.height))
        for y in range(m.height):
            col.putpixel((0, y), lerp_stops(SILVER, y / max(1, m.height - 1)))
        im = col.resize(m.size, Image.NEAREST).convert("RGBA")
        im.putalpha(m)
        lines.append(im)
    gap = round(f.size * 0.08)
    w, h = max(i.width for i in lines), sum(i.height for i in lines) + gap * (len(lines) - 1)
    pad = 30
    out = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    y = pad
    for i in lines:
        out.alpha_composite(i, (pad + (w - i.width) // 2, y))
        y += i.height + gap
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.putalpha(out.getchannel("A").point(lambda v: v // 2).filter(ImageFilter.GaussianBlur(10)))
    res = Image.new("RGBA", out.size, (0, 0, 0, 0))
    res.alpha_composite(sh, (0, 6))
    res.alpha_composite(out)
    if h > HEAD_H:
        res = res.resize((round(res.width * HEAD_H / h), round(res.height * HEAD_H / h)), Image.LANCZOS)
    return res


def sub_pill(ctx, text):
    f = ctx.fit(text, INTER, 840 - 140, 28, 18, {"wght": 600})
    text = g.drawable(text, f)
    w = int(f.getlength(text)) + 26 + 16 + 16 + 16 + 50 + 10
    s = rrect((w, 70), 35, (246, 245, 242, 255))
    g.paste(s, rrect((16, 16), 8, ctx.accent + (255,)), 26, 27)
    d = ImageDraw.Draw(s)
    d.text((58, 35), text, font=f, fill=(34, 34, 34), anchor="lm")
    g.paste(s, rrect((50, 50), 25, ctx.accent + (255,)), w - 60, 10)
    d.text((w - 35, 35), "↑", font=ctx.font(INTER, 30, {"wght": 700}), fill="white", anchor="mm")
    return s


def price_pill(ctx, text):
    f = ctx.fit(text, INTER, 840 - 90, 36, 20, {"wght": 700})
    text = g.drawable(text, f)
    w = int(f.getlength(text)) + 28 + 18 + 14 + 32
    pad = 40
    s = shadow((w, 76), 38, 15, 0.4, pad, dy=10)
    s.alpha_composite(rrect((w, 76), 38, (255, 255, 255, 255)), (pad, pad))
    g.paste(s, rrect((18, 18), 9, ctx.accent + (255,)), pad + 28, pad + 29)
    ImageDraw.Draw(s).text((pad + 60, pad + 38), text, font=f, fill=(17, 17, 17), anchor="lm")
    return s, pad


def bezier(p, n=400):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p
    pts = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        pts.append((a * x0 + b * x1 + c * x2 + d * x3, a * y0 + b * y1 + c * y2 + d * y3))
    return pts


def arc_dots():
    """Dot positions every 18 px along the arc, plus the end point and direction for the arrowhead."""
    pts, dots, run = bezier(ARC), [], 0.0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        run += math.hypot(bx - ax, by - ay)
        if run >= 18 or not dots:
            dots.append((bx, by))
            run = 0.0
    (ax, ay), (bx, by) = pts[-8], pts[-1]
    return dots, (bx, by), math.atan2(by - ay, bx - ax)


def arc_sprite(ctx, n):
    """The first n dots of the arc (and the arrowhead once all are drawn), 3x supersampled."""
    dots, end, ang = ctx.cache("dots", arc_dots)
    k, (ox, oy) = 3, ARC_XY
    im = Image.new("RGBA", (500 * k, 260 * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x, y in dots[:n]:
        d.ellipse(((x - ox - 3.2) * k, (y - oy - 3.2) * k, (x - ox + 3.2) * k, (y - oy + 3.2) * k),
                  fill=(255, 255, 255, 217))
    if n >= len(dots):
        ex, ey = (end[0] - ox) * k, (end[1] - oy) * k
        for da in (2.5, -2.5):
            d.line((ex, ey, ex - 22 * k * math.cos(ang + da / 5), ey - 22 * k * math.sin(ang + da / 5)),
                   fill=(255, 255, 255, 217), width=5 * k)
    return im.resize((500, 260), Image.LANCZOS)


# ---------------------------------------------------------------- frame

def put_phone(canvas, ctx, spr, screen, mask, x, y, alpha=1.0, tilt=0):
    sp, tag, pad = spr
    ph = sp.copy()
    ph.paste(screen, (pad + EDGE, pad + EDGE), mask)
    ph.alpha_composite(tag, (pad + EDGE + 18, pad + EDGE + 16))
    if tilt:
        ph = ph.rotate(tilt, Image.BICUBIC, expand=True)
    g.paste(canvas, ph, x, y, alpha, anchor="mm")


def frame(img, t, ctx):
    before = next_before(ctx)
    canvas = ctx.bg.copy()

    for item in ctx.active(t, "comment")[-1:]:
        u = t - item.get("start", 0) - DELAY["comment"]
        s = ctx.cache(("comment", item["text"]), lambda: comment_pill(ctx, item))
        g.paste(canvas, s, 540, COMMENT_Y - 30 * (1 - g.ease_out(u / 0.3)), g.clamp(u / 0.3), anchor="mt")
    for item in ctx.active(t, "headline")[-1:]:
        u = t - item.get("start", 0) - DELAY["headline"]
        if u > 0:
            s = ctx.cache(("headline", item["text"]), lambda: silver_headline(ctx, item["text"]))
            z = 1 + 0.15 * (1 - g.ease_out(u / 0.3))
            if z > 1.001:
                s = s.resize((round(s.width * z), round(s.height * z)), Image.BILINEAR)
            g.paste(canvas, s, 540, HEAD_Y - 30 + s.height / 2, g.clamp(u / 0.3), anchor="mm")
    for item in ctx.active(t, "sub")[-1:]:
        u = t - item.get("start", 0) - DELAY["sub"]
        s = ctx.cache(("sub", item["text"]), lambda: sub_pill(ctx, item["text"]))
        g.paste(canvas, s, 540, SUB_Y + 20 * (1 - g.ease_out(u / 0.3)), g.clamp(u / 0.3), anchor="mt")

    a = g.ease_out((t - 0.5) / 0.4)  # BEFORE slides in from the left
    if a > 0:
        put_phone(canvas, ctx, ctx.before_phone, before, ctx.before_mask,
                  BC[0] - 230 * (1 - a), BC[1], a, BTILT)
    a = g.ease_out((t - 0.7) / 0.4)  # AFTER rises in
    if a > 0:
        w, h = ctx.after_phone[0].size
        put_phone(canvas, ctx, ctx.after_phone, img, ctx.after_mask,
                  AX - ctx.after_phone[2] + w / 2, AY - ctx.after_phone[2] + h / 2 + 250 * (1 - a), a)
    dots = len(ctx.cache("dots", arc_dots)[0])
    n = round(dots * g.clamp((t - 1.0) / 0.4))
    if n:
        g.paste(canvas, ctx.cache(("arc", n), lambda: arc_sprite(ctx, n)), *ARC_XY)

    for item in ctx.active(t, "price")[-1:]:
        u = t - item.get("start", 0)
        s, pad = ctx.cache(("price", item["text"]), lambda: price_pill(ctx, item["text"]))
        z = 0.6 + 0.48 * g.ease_out(u / 0.2) if u < 0.2 else 1.08 - 0.08 * g.ease_in_out((u - 0.2) / 0.15)
        sz = s.resize((round(s.width * z), round(s.height * z)), Image.BILINEAR) if abs(z - 1) > 0.001 else s
        g.paste(canvas, sz, PRICE[0] - pad + s.width / 2, PRICE[1] - pad + s.height / 2,
                g.fade(t, item, 0.15, 0.2), anchor="mm")  # pops around its own centre
    return canvas


if __name__ == "__main__":
    g.run(sys.modules[__name__])
