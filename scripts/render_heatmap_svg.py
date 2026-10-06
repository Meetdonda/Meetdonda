from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from util import ROOT, esc, load_config, write_text


def month_labels(days: list[dict], start: date, cell: int, gap: int, left: int) -> str:
    labels: list[str] = []
    seen: set[tuple[int, int]] = set()
    for item in days:
        current = date.fromisoformat(item["date"])
        key = (current.year, current.month)
        if key in seen or current.day > 7:
            continue
        seen.add(key)
        week = (current - start).days // 7
        x = left + week * (cell + gap)
        labels.append(f'<text x="{x}" y="31" class="month">{current.strftime("%b")}</text>')
    return "\n".join(labels)


def render(data: dict, config: dict, static: bool = False) -> str:
    theme = config["theme"]
    palette = theme["green"]
    days = sorted(data["days"], key=lambda item: item["date"])
    first = date.fromisoformat(days[0]["date"])
    start = first
    cell, gap, left, top = 11, 4, 42, 42
    width, height = 860, 190

    rects: list[str] = []
    for index, item in enumerate(days):
        current = date.fromisoformat(item["date"])
        week = (current - start).days // 7
        weekday = (current.weekday() + 1) % 7  # Sunday first, like GitHub.
        x = left + week * (cell + gap)
        y = top + weekday * (cell + gap)
        delay = min(1.8, (week + weekday) * 0.018)
        label = f"{item['count']} contributions on {current.strftime('%B %d, %Y')}"
        rects.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
            f'fill="{palette[item["level"]]}" class="day" style="animation-delay:{delay:.3f}s">'
            f'<title>{esc(label)}</title></rect>'
        )

    stats = data["stats"]
    labels = month_labels(days, start, cell, gap, left)
    weekdays = "".join(
        f'<text x="8" y="{top + row * (cell + gap) + 9}" class="weekday">{name}</text>'
        for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )
    legend_x = width - 137
    legend = [f'<text x="{legend_x - 34}" y="154" class="legend">Less</text>']
    for level, color in enumerate(palette):
        legend.append(
            f'<rect x="{legend_x + level * 15}" y="144" width="11" height="11" rx="2" fill="{color}"/>'
        )
    legend.append(f'<text x="{legend_x + 80}" y="154" class="legend">More</text>')
    footer = (
        f"{stats['total']:,} contributions · current streak {stats['current_streak']} days · "
        f"longest {stats['longest_streak']} days"
    )
    day_style = "opacity:1;transform:none" if static else "opacity:0;transform:translateY(-9px);animation:reveal .38s ease-out forwards"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">GitHub contribution activity for {esc(data['username'])}</title>
<desc id="desc">{esc(footer)}</desc>
<defs><linearGradient id="borderGradient" x1="0" x2="1"><stop stop-color="{theme['accent']}"/><stop offset=".5" stop-color="{theme.get('accent2', theme['accent'])}"/><stop offset="1" stop-color="{theme.get('accent3', theme['accent'])}"/></linearGradient></defs>
<style>
  .bg {{ fill: {theme['background']}; }}
  .frame {{ fill: none; stroke: url(#borderGradient); }}
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: {theme['muted']}; }}
  .month {{ font-size: 11px; }} .weekday, .legend {{ font-size: 10px; }}
  .footer {{ font-size: 12px; fill: {theme.get('accent2', theme['text'])}; }}
  .day {{ {day_style}; }}
  @keyframes reveal {{ to {{ opacity: 1; transform: translateY(0); }} }}
  @media (prefers-reduced-motion: reduce) {{ .day {{ opacity: 1; transform: none; animation: none; }} }}
</style>
<rect class="bg" width="100%" height="100%" rx="10"/>
<rect class="frame" x="0.5" y="0.5" width="859" height="189" rx="9.5"/>
{labels}
{weekdays}
{''.join(rects)}
<text x="42" y="154" class="footer">{esc(footer)}</text>
{''.join(legend)}
<text x="42" y="177" class="legend">updated daily from github.com/users/{esc(data['username'])}/contributions</text>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description="Render contribution JSON as an animated SVG.")
    parser.add_argument("--input", default=str(ROOT / "data" / "contributions.json"))
    parser.add_argument("--config", help="Path to config.json")
    parser.add_argument("--output", default=str(ROOT / "contrib-heatmap.svg"))
    parser.add_argument("--static", action="store_true", help="Disable animation for previewing")
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    svg = render(data, load_config(args.config), args.static)
    write_text(args.output, svg)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
