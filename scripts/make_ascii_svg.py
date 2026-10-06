from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

from util import ROOT, esc, load_config, write_text


RAMP = " .`:-=+*cs#%@"


def image_to_rows(path: Path, columns: int, rows: int) -> list[str]:
    image = Image.open(path).convert("L")
    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Contrast(image).enhance(1.12)
    image.thumbnail((columns, rows), Image.Resampling.LANCZOS)
    canvas = Image.new("L", (columns, rows), 255)
    offset = ((columns - image.width) // 2, (rows - image.height) // 2)
    canvas.paste(image, offset)
    pixels = list(canvas.tobytes())
    output: list[str] = []
    for y in range(rows):
        chars = []
        for x in range(columns):
            brightness = pixels[y * columns + x]
            index = round((255 - brightness) / 255 * (len(RAMP) - 1))
            chars.append(RAMP[index])
        output.append("".join(chars).rstrip())
    return output


def render(rows: list[str], config: dict, static: bool = False) -> str:
    theme = config["theme"]
    width, height = 370, 270
    top, line_height, font_size = 48, 4.1, 4.4
    definitions: list[str] = []
    content: list[str] = []
    for index, row in enumerate(rows):
        y = top + index * line_height
        delay = 0 if static else index * 0.035
        clip_id = f"clip-{index}"
        if static:
            definitions.append(f'<clipPath id="{clip_id}"><rect x="18" y="{y - 4}" height="5" width="334"/></clipPath>')
        else:
            definitions.append(
                f'<clipPath id="{clip_id}"><rect x="18" y="{y - 4}" height="5" width="0">'
                f'<animate attributeName="width" from="0" to="334" dur=".46s" begin="{delay:.3f}s" fill="freeze"/>'
                f'</rect></clipPath>'
            )
        content.append(
            f'<text x="18" y="{y}" clip-path="url(#{clip_id})" xml:space="preserve">{esc(row)}</text>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">Animated ASCII portrait</title><desc id="desc">A portrait rendered in monochrome text characters.</desc>
<defs>
  <linearGradient id="portraitGradient" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{theme['accent']}"/><stop offset=".48" stop-color="{theme.get('accent2', theme['accent'])}"/><stop offset="1" stop-color="{theme.get('accent3', theme['accent'])}"/></linearGradient>
  <linearGradient id="borderGradient" x1="0" x2="1"><stop stop-color="{theme['accent']}"/><stop offset=".5" stop-color="{theme.get('accent2', theme['accent'])}"/><stop offset="1" stop-color="{theme.get('accent3', theme['accent'])}"/></linearGradient>
  {''.join(definitions)}
</defs>
<style>
  .frame {{ fill:{theme['panel']};stroke:url(#borderGradient) }}
  .bar {{ fill:{theme['background']} }}
  text {{ fill:url(#portraitGradient);font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:{font_size}px }}
</style>
<rect class="frame" x=".5" y=".5" width="369" height="269" rx="10"/>
<path class="bar" d="M10 1h350a9 9 0 0 1 9 9v27H1V10a9 9 0 0 1 9-9z"/>
<circle cx="20" cy="19" r="5" fill="#ff5f56"/><circle cx="38" cy="19" r="5" fill="#ffbd2e"/><circle cx="56" cy="19" r="5" fill="#27c93f"/>
<text x="185" y="23" text-anchor="middle" style="font-size:11px;fill:{theme['muted']}">meet@github: portrait.txt</text>
{''.join(content)}
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a prepared portrait to a self-typing ASCII SVG.")
    parser.add_argument("source", type=Path, nargs="?", default=ROOT / "source-prepped.png")
    parser.add_argument("--config", help="Path to config.json")
    parser.add_argument("--output", default=str(ROOT / "profile-ascii.svg"))
    parser.add_argument("--columns", type=int, default=96)
    parser.add_argument("--rows", type=int, default=53)
    parser.add_argument("--static", action="store_true")
    args = parser.parse_args()
    rows = image_to_rows(args.source, args.columns, args.rows)
    write_text(args.output, render(rows, load_config(args.config), args.static))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
