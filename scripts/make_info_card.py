from __future__ import annotations

import argparse

from util import ROOT, esc, load_config, write_text


def render(config: dict, static: bool = False) -> str:
    theme = config["theme"]
    profile = config["profile"]
    rows = profile.get("rows", [])
    colors = [theme["accent"], theme.get("accent2", theme["accent"]), theme.get("accent3", theme["accent"]), "#fbbf24"]
    height = max(270, 132 + len(rows) * 34)
    row_svg: list[str] = []
    for index, row in enumerate(rows):
        y = 133 + index * 34
        delay = 0 if static else 0.55 + index * 0.16
        row_svg.append(
            f'<g class="line" style="animation-delay:{delay:.2f}s">'
            f'<text x="30" y="{y}" class="key" style="fill:{colors[index % len(colors)]}">{esc(row["label"])}</text>'
            f'<text x="126" y="{y}" class="value">{esc(row["value"])}</text></g>'
        )
    animation = "opacity:1;transform:none" if static else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="490" height="{height}" viewBox="0 0 490 {height}" role="img" aria-labelledby="title desc">
<title id="title">Profile information for {esc(profile['name'])}</title>
<desc id="desc">{esc(profile['tagline'])}</desc>
<defs>
  <linearGradient id="titleGradient" x1="0" x2="1"><stop stop-color="{theme['accent']}"/><stop offset=".5" stop-color="{theme.get('accent2', theme['accent'])}"/><stop offset="1" stop-color="{theme.get('accent3', theme['accent'])}"/></linearGradient>
  <linearGradient id="borderGradient" x1="0" x2="1"><stop stop-color="{theme['accent']}"/><stop offset=".5" stop-color="{theme.get('accent2', theme['accent'])}"/><stop offset="1" stop-color="{theme.get('accent3', theme['accent'])}"/></linearGradient>
</defs>
<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  .frame {{ fill: {theme['panel']}; stroke: url(#borderGradient); }}
  .bar {{ fill: {theme['background']}; }}
  .dot1 {{ fill:#ff5f56 }} .dot2 {{ fill:#ffbd2e }} .dot3 {{ fill:#27c93f }}
  .name {{ fill:url(#titleGradient);font-size:20px;font-weight:700 }}
  .tagline {{ fill:{theme['muted']};font-size:12px }}
  .key {{ font-size:13px;font-weight:700 }}
  .value {{ fill:{theme['text']};font-size:13px }}
  .line {{ opacity:0;transform:translateX(-9px);animation:print .42s ease-out forwards;{animation} }}
  @keyframes print {{ to {{ opacity:1;transform:translateX(0) }} }}
  @media (prefers-reduced-motion: reduce) {{ .line {{ opacity:1;transform:none;animation:none }} }}
</style>
<rect class="frame" x="0.5" y="0.5" width="489" height="{height - 1}" rx="10"/>
<path class="bar" d="M10 1h470a9 9 0 0 1 9 9v27H1V10a9 9 0 0 1 9-9z"/>
<circle class="dot1" cx="20" cy="19" r="5"/><circle class="dot2" cx="38" cy="19" r="5"/><circle class="dot3" cx="56" cy="19" r="5"/>
<text x="245" y="23" text-anchor="middle" style="fill:{theme['muted']};font-size:11px">whoami</text>
<g class="line" style="animation-delay:{0 if static else .16}s"><text x="30" y="76" class="name">{esc(profile['name'])}</text></g>
<g class="line" style="animation-delay:{0 if static else .34}s"><text x="30" y="99" class="tagline">{esc(profile['tagline'])}</text></g>
{''.join(row_svg)}
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the animated neofetch-style profile card.")
    parser.add_argument("--config", help="Path to config.json")
    parser.add_argument("--output", default=str(ROOT / "info-card.svg"))
    parser.add_argument("--static", action="store_true", help="Disable animation for previewing")
    args = parser.parse_args()
    write_text(args.output, render(load_config(args.config), args.static))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
