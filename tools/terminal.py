#!/usr/bin/env python3
"""Draws the animated terminal for the subinternal GitHub profile, in light and dark, as SVG.

GitHub shows a README's images through its own proxy as plain images: no script runs, but CSS animation inside an SVG
does. Each line fades in in turn, the score counts up, and the whole run loops. Fonts come from the viewer's system
(monospace), since an SVG shown as an image cannot load one. An example run on a made-up site, and it says so.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'profile' / 'assets'
W, H = 960, 456
LOOP = 16.0  # seconds for one whole run, then it starts again
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    'light': dict(bg='#f6f5f2', panel='#ffffff', edge='#e3e1dc', ink='#16171a', muted='#6b6e75', faint='#a3a6ad', good='#1f8a5b', accent='#c8326a', score='#16171a', bar='#e9e7e2'),
    'dark': dict(bg='#0f1013', panel='#16171b', edge='#2a2c32', ink='#eceae6', muted='#9a9da5', faint='#5d6068', good='#46c08a', accent='#ff6a9a', score='#ffffff', bar='#26282e'),
}

# (text pieces, start second). Each piece is (words, colour key, weight).
LINES = [
    ([('$ ', 'faint', 400), ('npx skills add subinternal/mttr', 'ink', 500)], 0.0),
    ([('  added 6 skills to .claude/skills', 'muted', 400)], 0.0),
    ([('> ', 'accent', 600), ('Check yoursite.com with mttr and fix what’s worth the most.', 'ink', 500)], 0.8),
    ([('  mttr  ', 'accent', 600), ('read 100 pages, ranked 14 fixes by worth', 'muted', 400)], 1.8),
    ([('  ✓ ', 'good', 600), ('Text in the HTML, 12 pages', 'ink', 400)], 2.6),
    ([('  ✓ ', 'good', 600), ('One main heading, 31 pages', 'ink', 400)], 3.2),
    ([('  ✓ ', 'good', 600), ('Structured data, 18 pages', 'ink', 400)], 3.8),
    ([('  mttr  ', 'accent', 600), ('read it again', 'muted', 400)], 4.8),
]
FIXES = [('+9', 2.6), ('+6', 3.2), ('+4', 3.8)]
SCORE_AT = 5.6


def esc(text: str) -> str:
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def keyframes(name: str, start: float) -> str:
    """Hidden until `start`, shown until the run ends, then hidden for the restart."""
    a = start / LOOP * 100
    if start == 0:
        return f'@keyframes {name}{{0%,100%{{opacity:1}}}}'
    b = min(a + 2.5, 99)
    return f'@keyframes {name}{{0%,{a:.2f}%{{opacity:0;transform:translateY(6px)}}{b:.2f}%,94%{{opacity:1;transform:none}}98%,100%{{opacity:0}}}}'


def draw(theme: str) -> str:
    t = THEMES[theme]
    css: list[str] = [f'text{{font-family:{MONO};font-size:17px}}']
    body: list[str] = []
    x0, y0, step = 56, 132, 34
    for i, (pieces, start) in enumerate(LINES):
        css.append(keyframes(f'l{i}', start))
        css.append(f'.l{i}{{animation:l{i} {LOOP}s ease-out infinite}}')
        spans = ''.join(f'<tspan fill="{t[colour]}" font-weight="{weight}">{esc(words)}</tspan>' for words, colour, weight in pieces)
        body.append(f'<text class="l l{i}" x="{x0}" y="{y0 + i * step}" xml:space="preserve">{spans}</text>')
    for k, (gain, start) in enumerate(FIXES):
        name = f'f{k}'
        css.append(keyframes(name, start + 0.3))
        css.append(f'.{name}{{animation:{name} {LOOP}s ease-out infinite}}')
        body.append(f'<text class="l {name}" x="{W - 56}" y="{y0 + (4 + k) * step}" text-anchor="end" fill="{t["good"]}" font-weight="600">{gain}</text>')
    # The score: 61 fades out as 88 fades in, beside a bar that grows from 61 to 88 of 100.
    sy = y0 + len(LINES) * step + 14
    bar_x, bar_w = x0 + 150, 360
    css.append(keyframes('sc', SCORE_AT))
    css.append(f'.sc{{animation:sc {LOOP}s ease-out infinite}}')
    a = SCORE_AT / LOOP * 100
    css.append(f'@keyframes grow{{0%,{a:.2f}%{{width:{bar_w * 0.61:.0f}px}}{a + 8:.2f}%,94%{{width:{bar_w * 0.88:.0f}px}}100%{{width:{bar_w * 0.61:.0f}px}}}}')
    css.append(f'.bar{{animation:grow {LOOP}s cubic-bezier(.2,.8,.2,1) infinite}}')
    css.append(f'@keyframes old{{0%,{a:.2f}%{{opacity:1}}{a + 3:.2f}%,100%{{opacity:0}}}}@keyframes new{{0%,{a:.2f}%{{opacity:0}}{a + 3:.2f}%,94%{{opacity:1}}98%,100%{{opacity:0}}}}')
    css.append(f'.old{{animation:old {LOOP}s ease-out infinite}}.new{{animation:new {LOOP}s ease-out infinite}}')
    body.append(f'<g class="l sc"><text x="{x0}" y="{sy}" fill="{t["muted"]}">  score</text>'
                f'<rect x="{bar_x}" y="{sy - 13}" width="{bar_w}" height="14" rx="7" fill="{t["bar"]}"/>'
                f'<rect class="bar" x="{bar_x}" y="{sy - 13}" width="{bar_w * 0.88:.0f}" height="14" rx="7" fill="url(#g)"/>'
                f'<text class="old" x="{bar_x + bar_w + 22}" y="{sy}" fill="{t["score"]}" font-weight="700" font-size="20" opacity="0">61</text>'
                f'<text class="new" x="{bar_x + bar_w + 22}" y="{sy}" fill="{t["score"]}" font-weight="700" font-size="20">88</text></g>')
    css.append('@media (prefers-reduced-motion: reduce){.l,.bar,.old,.new{animation:none!important}}')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="An example run of mttr in a terminal: the skills are added, mttr reads 100 pages and ranks 14 fixes, three fixes land, mttr reads the site again, and the score goes from 61 to 88.">
<title>An example run of mttr on a made-up site</title>
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#ff4f9f"/><stop offset=".55" stop-color="#ff8a4c"/><stop offset="1" stop-color="#ffc233"/></linearGradient></defs>
<style>{''.join(css)}</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="{t["panel"]}" stroke="{t["edge"]}"/>
<line x1="1" y1="78" x2="{W - 1}" y2="78" stroke="{t["edge"]}"/>
<circle cx="56" cy="51" r="6" fill="{t["edge"]}"/><circle cx="76" cy="51" r="6" fill="{t["edge"]}"/><circle cx="96" cy="51" r="6" fill="{t["edge"]}"/>
<text x="128" y="56" fill="{t["muted"]}" font-size="14">claude  ~/your-site</text>
{chr(10).join(body)}
<text x="{W - 32}" y="56" text-anchor="end" fill="{t["faint"]}" font-size="13">An example run on a made-up site.</text>
</svg>
'''


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (OUT / f'terminal-{theme}.svg').write_text(draw(theme), encoding='utf-8')
        print(f'wrote terminal-{theme}.svg')
