from __future__ import annotations

import argparse

from util import ROOT, esc, load_config, write_text


def render(config: dict) -> str:
    username = config["username"]
    terminal = config.get("terminal_name") or username
    links = config.get("links", [])
    link_markup = " · ".join(f'<a href="{esc(item["url"])}">{esc(item["label"])}</a>' for item in links)
    return f'''<div align="center">

### `{esc(terminal)}@github ~ $ ./contributions.sh`

<img src="./contrib-heatmap.svg" width="860" alt="Animated GitHub contribution heatmap" />

<br>

### `{esc(terminal)}@github ~ $ whoami`

<table>
  <tr>
    <td valign="top"><img src="./profile-ascii.svg" width="370" alt="Animated ASCII portrait" /></td>
    <td valign="top"><img src="./info-card.svg" width="490" alt="Profile information" /></td>
  </tr>
</table>

### `{esc(terminal)}@github ~ $ ./links.sh`

{link_markup}

</div>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate README.md from config.json.")
    parser.add_argument("--config", help="Path to config.json")
    parser.add_argument("--output", default=str(ROOT / "README.md"))
    args = parser.parse_args()
    write_text(args.output, render(load_config(args.config)))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
