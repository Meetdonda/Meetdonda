from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from util import ROOT, load_config


def run(script: str, *args: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build all configured GitHub profile assets.")
    parser.add_argument("--skip-fetch", action="store_true", help="Reuse data/contributions.json")
    parser.add_argument("--skip-portrait", action="store_true", help="Keep the existing profile-ascii.svg")
    args = parser.parse_args()
    config = load_config()
    if config["username"] == "YOUR_GITHUB_USERNAME":
        raise SystemExit("Edit config.json and set your GitHub username first.")
    run("make_info_card.py")
    run("make_readme.py")
    if not args.skip_fetch:
        run("fetch_contributions.py")
    run("render_heatmap_svg.py")
    if not args.skip_portrait:
        source = ROOT / "source-prepped.png"
        if source.exists():
            run("make_ascii_svg.py", str(source))
        else:
            print("Skipped portrait: add source-prepped.png or pass --skip-portrait.")


if __name__ == "__main__":
    main()
