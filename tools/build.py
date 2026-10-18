"""Build the GitHub profile README and its SVGs (masthead, project cards, GitHub strip, booking button).

Text is converted to outlines (HarfBuzz shaping + fontTools), so nothing depends on fonts loading inside an <img>.
Each SVG switches to a phone layout with @media (max-width) inside it, and animates once with CSS (skipped with
reduced motion). Light and dark files are paired with <picture>.
Inputs: tools/fonts, tools/logos, tools/stats.json (from fetch_stats.py) and the site's RSS feed.
Usage: python tools/build.py <rss.xml>
"""
import base64
import email.utils
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
FONTS, LOGOS, STATS = TOOLS / "fonts", TOOLS / "logos", TOOLS / "stats.json"
RSS = Path(sys.argv[1])


def oklch_hex(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_, m_, s_ = L + 0.3963377774 * a + 0.2158037573 * b, L - 0.1055613458 * a - 0.0638541728 * b, L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    rgb = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
           -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
           -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
    enc = lambda x: 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
    return "#" + "".join(f"{round(enc(max(0.0, min(1.0, v))) * 255):02x}" for v in rgb)


# Colour tokens from src/app/globals.css
THEMES = {
    "light": dict(ink=oklch_hex(0.15, 0.02, 230), muted=oklch_hex(0.47, 0.015, 245), teal=oklch_hex(0.50, 0.10, 200),
                  rule=oklch_hex(0.87, 0.008, 245), card=oklch_hex(0.987, 0.003, 100)),
    "dark": dict(ink=oklch_hex(0.94, 0.006, 95), muted=oklch_hex(0.72, 0.012, 245), teal=oklch_hex(0.76, 0.10, 195),
                 rule=oklch_hex(0.32, 0.012, 245), card=oklch_hex(0.19, 0.012, 245)),
}


class Face:
    def __init__(self, file, wght=None):
        f = FONTS / file
        self.font = hb.Font(hb.Face(hb.Blob.from_file_path(str(f))))
        if wght:
            self.font.set_variations({"wght": wght})
        self.upem = self.font.face.upem
        self.cap = TTFont(f)["OS/2"].sCapHeight

    def shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {"kern": True, "liga": True})
        return buf.glyph_infos, buf.glyph_positions

    def width(self, text, size, tracking=0.0):
        _, pos = self.shape(text)
        return sum(p.x_advance for p in pos) * size / self.upem + tracking * max(len(pos) - 1, 0)

    def path(self, text, size, x, y, anchor="start", tracking=0.0):
        """SVG path data with the baseline at y. Returns (d, width, ink above baseline, ink below baseline)."""
        infos, pos = self.shape(text)
        s = size / self.upem
        w = self.width(text, size, tracking)
        cx = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        pen = SVGPathPen(None, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
        top = bottom = 0.0
        for info, p in zip(infos, pos):
            gx, gy = cx + p.x_offset * s, y - p.y_offset * s
            self.font.draw_glyph_with_pen(info.codepoint, TransformPen(pen, (s, 0, 0, -s, gx, gy)))
            ext = self.font.get_glyph_extents(info.codepoint)
            if ext:
                top = max(top, ext.y_bearing * s)
                bottom = max(bottom, -(ext.y_bearing + ext.height) * s)
            cx += p.x_advance * s + tracking
        return pen.getCommands(), w, top, bottom

    def wrap(self, text, size, max_w):
        lines, cur = [], ""
        for word in text.split():
            trial = f"{cur} {word}".strip()
            if self.width(trial, size) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        return lines + [cur] if cur else lines


DISPLAY = Face("CaslonDisplay.ttf")
ITALIC = Face("CaslonTextItalic.ttf", 400)
TEXT = Face("CaslonText.ttf", 400)
SANS = Face("Franklin.ttf", 400)
SANS_SEMI = Face("Franklin.ttf", 600)

TILE = "M22 0H78A22 22 0 0 1 100 22V78A22 22 0 0 1 78 100H22A22 22 0 0 1 0 78V22A22 22 0 0 1 22 0Z"
LETTERS = (TOOLS / "jl_letters.txt").read_text().strip()
EASE = "cubic-bezier(0.2, 0.7, 0.2, 1)"  # the site's rise easing (globals.css)


def no_st(text):
    # ZWNJ keeps the Caslon italic's historical s_t ligature out, as on the site
    return text.replace("st", "s‌t")


def svg(w, h, style, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{label}">\n<style>{style}</style>\n{body}\n</svg>\n')


def p(d, fill, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<path{c} fill="{fill}" d="{d}"/>'


def rect(x, y, w, h, fill, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<rect{c} x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"/>'


MOTION_BASE = f"""
@keyframes rise {{ from {{ opacity: 0; transform: translateY(var(--rise, 40px)); }} to {{ opacity: 1; transform: none; }} }}
@keyframes draw {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
@keyframes fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
.rule {{ transform-box: fill-box; transform-origin: center; }}
.rule-left {{ transform-box: fill-box; transform-origin: left; }}
"""


# ---------- masthead ----------
TAGLINE = "Building with fleets of AI agents, and the checks that keep them honest"


def masthead_narrow(c, W):
    """Phones (~308px column): bigger nameplate, tagline on two lines, no strip or ears. Returns (elements, height)."""
    out = [rect(0, 0, W, 4, c["ink"], "rule r1")]
    size = 300
    cap = DISPLAY.cap * size / DISPLAY.upem
    base = 4 + 40 + cap
    d, _, _, desc = DISPLAY.path("Jackson Ly", size, W / 2, base, anchor="middle", tracking=-0.025 * size)
    out.append(p(d, c["ink"], "name"))
    y1 = base + desc + 26
    out += [rect(0, y1, W, 4, c["ink"], "rule r2"), rect(0, y1 + 11, W, 4, c["ink"], "rule r2")]
    tsize = 62
    ty = y1 + 15 + 20 + tsize * 0.8
    for line in ("Building with fleets of AI agents,", "and the checks that keep them honest"):
        d, *_ = ITALIC.path(no_st(line), tsize, W / 2, ty, anchor="middle")
        out.append(p(d, c["ink"], "tag"))
        ty += tsize * 1.18
    yb = ty - tsize * 1.18 + 28
    out.append(rect(0, yb, W, 3, c["rule"], "rule r4"))
    return out, yb + 3


def masthead_wide(c, W, edition, extra=0.0):
    """Desktop: top strip, nameplate flanked by two ears, double rule, one-line tagline. `extra` adds air to match heights."""
    out = [f'<path transform="translate(0 15) scale(0.36)" fill="{c["ink"]}" fill-rule="evenodd" d="{TILE}{LETTERS}"/>']
    d, *_ = SANS.path("jacksonly.xyz", 27, 50, 42)
    out.append(p(d, c["muted"]))
    d, *_ = SANS.path("Engineering notes, case studies and a CV", 27, W, 42, anchor="end")
    out.append(p(d, c["muted"]))
    out.append(rect(0, 64, W, 3, c["ink"], "rule r1"))
    size = 236
    cap = DISPLAY.cap * size / DISPLAY.upem
    base = 67 + 52 + extra * 0.4 + cap
    d, nw, _, desc = DISPLAY.path("Jackson Ly", size, W / 2, base, anchor="middle", tracking=-0.025 * size)
    out.append(p(d, c["ink"], "name"))
    # ears: small boxed notes either side of the nameplate, centred on the capitals
    ear_w, ear_h = (W - nw) / 2 - 56, 118
    ear_y = base - cap / 2 - ear_h / 2
    for side, kicker, line in (("l", "AI systems engineer", "Based in Germany"), ("r", "Lead engineer", "YC-backed startup")):
        x = 0 if side == "l" else W - ear_w
        out.append(f'<rect class="ear" x="{x:.1f}" y="{ear_y:.1f}" width="{ear_w:.1f}" height="{ear_h}" fill="none" '
                   f'stroke="{c["ink"]}" stroke-width="2"/>')
        ks = 21
        while SANS_SEMI.width(kicker.upper(), ks, 2.2) > ear_w - 56:
            ks -= 0.5
        d, *_ = SANS_SEMI.path(kicker.upper(), ks, x + ear_w / 2, ear_y + 46, anchor="middle", tracking=2.2)
        out.append(p(d, c["teal"], "ear"))
        ls = 31
        while ITALIC.width(no_st(line), ls) > ear_w - 56:
            ls -= 0.5
        d, *_ = ITALIC.path(no_st(line), ls, x + ear_w / 2, ear_y + 90, anchor="middle")
        out.append(p(d, c["ink"], "ear"))
    y1 = base + desc + 30 + extra * 0.3
    out += [rect(0, y1, W, 2.5, c["ink"], "rule r2"), rect(0, y1 + 7.5, W, 2.5, c["ink"], "rule r2")]
    eb = y1 + 10 + 58 + extra * 0.15
    d, *_ = ITALIC.path(no_st(TAGLINE), 42, W / 2, eb, anchor="middle")
    out.append(p(d, c["ink"], "tag"))
    yb = eb + 30 + extra * 0.15
    out.append(rect(0, yb, W, 2, c["rule"], "rule r4"))
    return out, yb + 2


def masthead(t, edition):
    W = 1600
    c = THEMES[t]
    narrow, hn = masthead_narrow(c, W)
    wide, hw = masthead_wide(c, W, edition)
    if hn > hw:
        wide, hw = masthead_wide(c, W, edition, extra=hn - hw)
    H = math.ceil(max(hw, hn))
    style = MOTION_BASE + """
.narrow { display: none; }
@media (max-width: 520px) { .wide { display: none; } .narrow { display: inline; } }
@media (prefers-reduced-motion: no-preference) {
  .rule { animation: draw 800ms %(ease)s both; }
  .r2 { animation-delay: 450ms; }
  .r4 { animation-delay: 1000ms; }
  .name { --rise: 42px; animation: rise 900ms %(ease)s 120ms both; }
  .tag { animation: fade 800ms ease-out 850ms both; }
  .ear { animation: fade 700ms ease-out 650ms both; }
}""" % {"ease": EASE}
    body = '<g class="wide">\n' + "\n".join(wide) + '\n</g>\n<g class="narrow">\n' + "\n".join(narrow) + "\n</g>"
    return svg(W, H, style, body, "Jackson Ly. " + TAGLINE + ".")


# ---------- project cards with a proof number ----------
PROJECTS = [
    dict(slug="registercheck", name="Registercheck", kicker="Day job", href="https://www.registercheck.de", link="registercheck.de",
         num="5.8M", cap="companies from 118 register courts",
         text="German company-register data, with a REST API and an MCP server for AI assistants."),
    dict(slug="morndo", name="Morndo", kicker="Open source", href="https://github.com/morndo/morndo", link="github.com/morndo/morndo",
         num="2,219", cap="agent-hours in 427 wall-clock hours, Sep 2026",
         text="A self-hosted control plane for one person running many coding agents."),
    dict(slug="venua", name="Venua", kicker="Co-founder", href="https://www.venua.io", link="venua.io",
         num="820", cap="tickets at IdeaLab! 2026",
         text="Event software for B2B organisers. I co-founded it and I'm its only engineer."),
    dict(slug="sleipa", name="Sleipa", kicker="Research", href="https://jacksonly.xyz/projects/sleipa", link="jacksonly.xyz/projects/sleipa",
         num="16.7%", cap="of my follow-ups exist because the agent fell short",
         text="My research on when coding agents can be trusted to work unsupervised."),
]


def card(pr, t, i):
    W, pad = 800, 40
    c = THEMES[t]
    logo = base64.b64encode((LOGOS / f"{pr['slug']}.png").read_bytes()).decode()
    out = [f'<defs><clipPath id="r"><rect x="{pad}" y="{pad}" width="72" height="72" rx="14"/></clipPath></defs>']
    tx = pad + 72 + 24
    d, *_ = SANS_SEMI.path(pr["kicker"].upper(), 21, tx, pad + 22, tracking=2.2)
    out.append(p(d, c["teal"]))
    d, *_ = DISPLAY.path(pr["name"], 54, tx, pad + 70, tracking=-0.6)
    out.append(p(d, c["ink"]))
    # proof number, with its caption beside it
    nsize = 128
    ncap = DISPLAY.cap * nsize / DISPLAY.upem
    nb = pad + 72 + 34 + ncap
    d, nw, *_ = DISPLAY.path(pr["num"], nsize, pad - 4, nb, tracking=-2)
    out.append(p(d, c["ink"], "num"))
    cx = pad + nw + 26
    cl = SANS.wrap(pr["cap"], 27, W - pad - cx)
    cy = nb - ncap / 2 - (len(cl) - 1) * 18 + 9
    for line in cl:
        d, *_ = SANS.path(line, 27, cx, cy)
        out.append(p(d, c["muted"], "cap"))
        cy += 36
    out.append(rect(pad, nb + 26, W - 2 * pad, 2, c["rule"], "rule-left line"))
    y = nb + 26 + 50
    for line in SANS.wrap(pr["text"], 28, W - 2 * pad):
        d, *_ = SANS.path(line, 28, pad, y)
        out.append(p(d, c["ink"]))
        y += 38
    y += 14
    d, *_ = SANS_SEMI.path(pr["link"], 23, pad, y)
    out.append(p(d, c["teal"]))
    H = math.ceil(y + pad - 4)
    frame = (f'<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="22" fill="{c["card"]}" stroke="{c["rule"]}" stroke-width="3"/>\n'
             f'<image x="{pad}" y="{pad}" width="72" height="72" clip-path="url(#r)" href="data:image/png;base64,{logo}"/>')
    delay = 300 + 120 * i
    style = MOTION_BASE + f"""
@media (prefers-reduced-motion: no-preference) {{
  .num {{ --rise: 24px; animation: rise 900ms {EASE} {delay}ms both; }}
  .cap {{ animation: fade 700ms ease-out {delay + 300}ms both; }}
  .line {{ animation: draw 900ms {EASE} {delay + 200}ms both; }}
}}"""
    return svg(W, H, style, frame + "\n" + "\n".join(out), f"{pr['name']} ({pr['kicker']}): {pr['num']} {pr['cap']}. {pr['text']}"), H


# ---------- latest edition (newest post as a headline) ----------
def latest_layout(c, post, W, narrow, extra=0.0):
    k = 46 if narrow else 24          # kicker size: ~9px on a 308px phone column, ~13px at 846px
    hsize = 92 if narrow else 84
    out = [rect(0, 0, W, 5 if narrow else 3, c["ink"], "rule r1")]
    kb = k + 28
    d, kw, *_ = SANS_SEMI.path("LATEST EDITION", k, 0, kb, tracking=k * 0.11)
    out.append(p(d, c["teal"]))
    d, *_ = SANS.path(post["date"], k, kw + k, kb)
    out.append(p(d, c["muted"]))
    y = kb + k * 1.3 + DISPLAY.cap * hsize / DISPLAY.upem
    for line in DISPLAY.wrap(post["title"], hsize, W):
        d, *_ = DISPLAY.path(line, hsize, -3, y, tracking=-0.8)
        out.append(p(d, c["ink"], "head"))
        y += hsize * 1.08
    y += 6 + extra
    if not narrow:  # the dek only on wide images; on a phone it would be ~7px
        for line in ITALIC.wrap(no_st(post["desc"]), 38, W)[:2]:
            d, *_ = ITALIC.path(line, 38, 0, y)
            out.append(p(d, c["muted"]))
            y += 50
    ls = 52 if narrow else 27
    y += 14 + (ls - 27)
    d, *_ = SANS_SEMI.path("Read it on jacksonly.xyz", ls, 0, y)
    out.append(p(d, c["teal"]))
    h = y + (34 if narrow else 30)
    out.append(rect(0, h - 2, W, 3 if narrow else 2, c["rule"], "rule r4"))
    return out, h


def latest(post, t):
    W = 1600
    c = THEMES[t]
    wide, hw = latest_layout(c, post, W, False)
    narrow, hn = latest_layout(c, post, W, True)
    if hn > hw:
        wide, hw = latest_layout(c, post, W, False, extra=hn - hw)
    elif hw > hn:
        narrow, hn = latest_layout(c, post, W, True, extra=hw - hn)
    H = math.ceil(max(hw, hn))
    style = MOTION_BASE + f"""
.narrow {{ display: none; }}
@media (max-width: 520px) {{ .wide {{ display: none; }} .narrow {{ display: inline; }} }}
@media (prefers-reduced-motion: no-preference) {{
  .r1, .r4 {{ animation: draw 800ms {EASE} both; }}
  .head {{ --rise: 20px; animation: rise 900ms {EASE} 150ms both; }}
}}"""
    body = '<g class="wide">' + "\n".join(wide) + '</g>\n<g class="narrow">' + "\n".join(narrow) + "</g>"
    return svg(W, H, style, body, f"Latest edition, {post['date']}: {post['title']}. {post['desc']}")


# ---------- GitHub strip: odometer numbers and weekly bars ----------
DIGITS = "0123456789"
BG = {"light": oklch_hex(0.987, 0.003, 100), "dark": oklch_hex(0.16, 0.012, 245)}  # page colours, for text on teal


def glyph_defs(face, size, prefix):
    """Digits and comma drawn once at the origin, reused with <use>."""
    defs, adv = [], {}
    for ch in DIGITS + ",":
        d, w, *_ = face.path(ch, size, 0, 0)
        defs.append(f'<path id="{prefix}{"c" if ch == "," else ch}" d="{d}"/>')
        adv[ch] = w
    return defs, adv


def odometer(text, x, base, size, adv, prefix, fill, uid, delay, defs, rest, motion):
    """Each digit is a clipped strip of 0-9 twice over that rolls to its final digit; commas stay still."""
    step = size * 1.15
    cx, parts, di = x, [], 0
    for ch in text:
        w = adv[ch]
        if ch == ",":
            parts.append(f'<use href="#{prefix}c" x="{cx:.1f}" y="{base:.1f}" fill="{fill}"/>')
        else:
            cid = f"{uid}d{di}"
            defs.append(f'<clipPath id="{cid}"><rect x="{cx - 14:.1f}" y="{base - size * 0.85:.1f}" width="{w + 28:.1f}" '
                        f'height="{size * 1.02:.1f}"/></clipPath>')
            strip = "".join(f'<use href="#{prefix}{DIGITS[k % 10]}" x="{cx + (w - adv[DIGITS[k % 10]]) / 2:.1f}" '
                            f'y="{base + k * step:.1f}"/>' for k in range(20))
            final = -(10 + int(ch)) * step
            rest.append(f".{cid} {{ transform: translateY({final:.1f}px); }}")
            motion.append(f"@keyframes {cid}k {{ from {{ transform: translateY(0); }} to {{ transform: translateY({final:.1f}px); }} }}\n"
                          f".{cid} {{ animation: {cid}k {1300 + 110 * di}ms cubic-bezier(0.15, 0.6, 0.15, 1) {delay}ms both; }}")
            parts.append(f'<g clip-path="url(#{cid})"><g class="{cid}" fill="{fill}">{strip}</g></g>')
            di += 1
        cx += w
    return parts, cx - x


def stats_layout(c, st, W, narrow, extra=0.0):
    k, cs, ns, ls = (46, 48, 150, 42) if narrow else (24, 28, 120, 22)
    pre = "n" if narrow else "w"
    out, defs, rest, motion = [rect(0, 0, W, 5 if narrow else 3, c["ink"], "rule r1")], [], [], []
    kb = k + 26
    d, *_ = SANS_SEMI.path("LAST 30 DAYS", k, 0, kb, tracking=k * 0.11)
    out.append(p(d, c["teal"]))
    if not narrow:
        up = dt_label(st["updated"])
        d, *_ = SANS.path(f"Updated {up}", k, W, kb, anchor="end")
        out.append(p(d, c["muted"]))
    gdefs, adv = glyph_defs(DISPLAY, ns, pre)
    defs += gdefs
    ncap = DISPLAY.cap * ns / DISPLAY.upem
    nb = kb + 44 + ncap
    colw = W / 3
    items = [(f"{st['prs_30d']:,}", "pull requests merged"), (f"{st['repos_30d']:,}", "repositories"),
             (f"{st['contrib_30d']:,}", "contributions")]
    bottom = 0
    for i, (num, cap) in enumerate(items):
        x = i * colw + (6 if i == 0 else 40)  # the Caslon 1 overhangs its left edge
        parts, _ = odometer(num, x, nb, ns, adv, pre, c["ink"], f"{pre}{i}", 250 + 160 * i, defs, rest, motion)
        out += parts
        cy = nb + cs * 1.7
        for line in SANS.wrap(cap, cs, colw - 70):
            d, *_ = SANS.path(line, cs, x, cy)
            out.append(p(d, c["muted"], "cap"))
            cy += cs * 1.3
        bottom = max(bottom, cy - cs * 1.3)
        if i:
            out.append(rect(i * colw, nb - ncap - 6, 2, bottom - (nb - ncap - 6) + 12, c["rule"]))
    # weekly contributions, last 12 months
    weeks = st["weeks"]
    ch = (170 if narrow else 120) + extra  # height differences between the layouts go into the chart
    top = bottom + (70 if narrow else 56)
    yb = top + ch
    n, gap = len(weeks), (5 if narrow else 6)
    bw = (W - gap * (n - 1)) / n
    mx = max(w["total"] for w in weeks) or 1
    peak = max(range(n - 1), key=lambda i: weeks[i]["total"])
    for i, w in enumerate(weeks):
        h = max(3, ch * w["total"] / mx)
        fill = c["teal"] if i == peak else (c["rule"] if i == n - 1 else c["muted"])
        out.append(f'<rect class="bar" style="animation-delay: {500 + 14 * i}ms" x="{i * (bw + gap):.1f}" y="{yb - h:.1f}" '
                   f'width="{bw:.1f}" height="{h:.1f}" fill="{fill}"/>')
    px = peak * (bw + gap) + bw / 2
    d, pw, *_ = SANS_SEMI.path(f"{weeks[peak]['total']:,} in one week", ls, px, top - ls * 0.5, anchor="end" if px > W * 0.7 else "middle")
    out.append(p(d, c["teal"], "cap"))
    lb = yb + ls * 1.7
    first = dt_label(weeks[0]["first_day"], month_only=True)
    last = dt_label(weeks[-1]["first_day"], month_only=True)
    for text, anchor, xx in ((first, "start", 0), ("Contributions per week", "middle", W / 2), (last, "end", W)):
        d, *_ = SANS.path(text, ls, xx, lb, anchor=anchor)
        out.append(p(d, c["muted"]))
    h_total = lb + ls * 0.9
    out.append(rect(0, h_total, W, 3 if narrow else 2, c["rule"], "rule r4"))
    return out, defs, rest, motion, h_total + 3


def dt_label(iso, month_only=False):
    import datetime as _dt
    d = _dt.date.fromisoformat(iso)
    return d.strftime("%b %Y") if month_only else f"{d.day} {d.strftime('%b %Y')}"


def stats_svg(st, t):
    W = 1600
    c = THEMES[t]
    wide = stats_layout(c, st, W, False)
    narrow = stats_layout(c, st, W, True)
    if narrow[4] > wide[4]:
        wide = stats_layout(c, st, W, False, extra=narrow[4] - wide[4])
    elif wide[4] > narrow[4]:
        narrow = stats_layout(c, st, W, True, extra=wide[4] - narrow[4])
    H = math.ceil(max(wide[4], narrow[4]))
    style = MOTION_BASE + """
.narrow { display: none; }
@media (max-width: 520px) { .wide { display: none; } .narrow { display: inline; } }
.bar { transform-box: fill-box; transform-origin: bottom; }
""" + "\n".join(wide[2] + narrow[2]) + """
@media (prefers-reduced-motion: no-preference) {
  .r1, .r4 { animation: draw 800ms %(ease)s both; }
  .bar { animation: grow 700ms %(ease)s both; }
  .cap { animation: fade 700ms ease-out 1300ms both; }
  @keyframes grow { from { transform: scaleY(0); } to { transform: scaleY(1); } }
""" % {"ease": EASE} + "\n".join(wide[3] + narrow[3]) + "\n}"
    body = ("<defs>" + "".join(wide[1] + narrow[1]) + "</defs>\n<g class=\"wide\">" + "\n".join(wide[0]) +
            "</g>\n<g class=\"narrow\">" + "\n".join(narrow[0]) + "</g>")
    peak = max(st["weeks"][:-1], key=lambda w: w["total"])
    label = (f"On GitHub in the last 30 days: {st['prs_30d']:,} pull requests merged into {st['repos_30d']} repositories, "
             f"{st['contrib_30d']:,} contributions. Weekly contributions over the last 12 months peak at {peak['total']:,}.")
    return svg(W, H, style, body, label), label


# ---------- booking button ----------
def cta_svg(t):
    W, H = 600, 116
    c = THEMES[t]
    label, size = "Book a 15-minute call", 38
    w = SANS_SEMI.width(label, size)
    aw = 30
    x = (W - (w + 20 + aw)) / 2
    cy = H / 2
    d, *_ = SANS_SEMI.path(label, size, x, cy + size * 0.36)
    ax = x + w + 20
    body = (f'<rect x="0" y="0" width="{W}" height="{H}" rx="16" fill="{c["teal"]}"/>\n{p(d, BG[t])}\n'
            f'<g class="arrow"><path d="M{ax:.1f} {cy:.1f}h{aw}M{ax + aw - 12:.1f} {cy - 12:.1f}l12 12l-12 12" fill="none" '
            f'stroke="{BG[t]}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/></g>')
    style = f"""
@keyframes nudge {{ 0%, 100% {{ transform: none; }} 50% {{ transform: translateX(7px); }} }}
@media (prefers-reduced-motion: no-preference) {{ .arrow {{ animation: nudge 700ms ease-in-out 1600ms 2; }} }}"""
    return svg(W, H, style, body, "Book a 15-minute call")


# ---------- README ----------
def read_rss():
    items = ET.parse(RSS).getroot().findall("./channel/item")
    posts = []
    for it in items:
        dt = email.utils.parsedate_to_datetime(it.findtext("pubDate"))
        posts.append(dict(title=it.findtext("title").strip(), link=it.findtext("link").strip(),
                          desc=(it.findtext("description") or "").strip(), dt=dt,
                          date=f"{dt.day} {dt.strftime('%B %Y')}", short=f"{dt.day} {dt.strftime('%b %Y')}"))
    return sorted(posts, key=lambda x: x["dt"], reverse=True)


def pic(name, alt, width=None, href=None):
    w = f' width="{width}"' if width else ""
    img = f'<img src="assets/{name}-light.svg" alt="{alt}"{w}>'
    if href:  # inside <picture>: GitHub's renderer splits <a><picture>...</picture></a> apart
        img = f'<a href="{href}">{img}</a>'
    return (f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">\n'
            f'  {img}\n</picture>')


posts = read_rss()
STATS_DATA = json.loads(STATS.read_text())
newest = posts[0]
assets = {}
for t in THEMES:
    assets[f"masthead-{t}.svg"] = masthead(t, newest["date"])
    for i, pr in enumerate(PROJECTS):
        assets[f"card-{pr['slug']}-{t}.svg"], _ = card(pr, t, i)
    assets[f"stats-{t}.svg"], stats_alt = stats_svg(STATS_DATA, t)
    assets[f"cta-{t}.svg"] = cta_svg(t)

cells = [pic("card-" + pr["slug"], f"{pr['name']} ({pr['kicker']}): {pr['num']} {pr['cap']}. {pr['text']}", 420, pr["href"])
         for pr in PROJECTS]
recent = "\n".join(f"- [{x['title']}]({x['link']}) · {x['short']}" for x in posts[:4])
readme = f"""<p>
{pic("masthead", "Jackson Ly. Building with fleets of AI agents, and the checks that keep them honest.")}
</p>

I'm Jackson Ly, an AI systems engineer in Germany and lead engineer for [Registercheck](https://www.registercheck.de) at Openlaw, a YC-backed startup (F24). Most of my engineering now runs through AI coding agents, many of them at once, so a lot of my work is what sits around them: clear briefs, checks that don't take an agent's word for "done", and knowing which work shipped.

## AI engineering help

Struggling to get Claude Code or Codex to do real work? I offer AI engineering support: setting them up, writing briefs an agent can finish, and checking the work before it ships.

<p>
{pic("cta", "Book a 15-minute call", 300, "https://cal.com/lyjackson/15min")}
</p>

## What I'm building

<p>
{cells[0]}
{cells[1]}
</p>
<p>
{cells[2]}
{cells[3]}
</p>

## Lately on GitHub

<p>
{pic("stats", stats_alt)}
</p>

## Writing

I write about running many agents at once and checking what they did. The latest:

<!-- RECENT-POSTS:START -->
{recent}
<!-- RECENT-POSTS:END -->

[All posts on jacksonly.xyz](https://jacksonly.xyz/blog)

## Small tools

- [Claudometer](https://github.com/jacksnxly/Claudometer) is a macOS menu-bar app that shows your Claude Code usage against the 5-hour and 7-day limits.
- [keryx](https://github.com/jacksnxly/keryx) writes release notes from pull requests and conventional commits (Rust CLI).
- [claude-issue-toolkit](https://github.com/jacksnxly/claude-issue-toolkit) is a Claude Code plugin that takes an issue from creation through validation to a fix, tracked in Linear or in local Markdown files.

## Stack

Mostly TypeScript and Python, with Next.js, SvelteKit, FastAPI and SQLite. Rust for command-line tools, SwiftUI and Kotlin for native apps.

## Elsewhere

[Book a call](https://cal.com/lyjackson/15min) · [Website](https://jacksonly.xyz) · [LinkedIn](https://www.linkedin.com/in/jackson-ly) · [X](https://x.com/jacksnxly) · [DEV](https://dev.to/jacksonxly) · [Medium](https://medium.com/@lyjackson) · [YouTube](https://www.youtube.com/@jacksonly)
"""

(ROOT / "assets").mkdir(exist_ok=True)
for name, content in assets.items():
    (ROOT / "assets" / name).write_text(content)
(ROOT / "README.md").write_text(readme)
print("built README.md and", len(assets), "SVGs; newest post:", newest["title"])
