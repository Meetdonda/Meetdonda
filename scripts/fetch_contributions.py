from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from util import ROOT, load_config


COUNT_RE = re.compile(r"([\d,]+|No) contributions?", re.IGNORECASE)


def parse_count(text: str) -> int:
    match = COUNT_RE.search(text)
    if not match or match.group(1).lower() == "no":
        return 0
    return int(match.group(1).replace(",", ""))


def streaks(days: list[dict]) -> tuple[int, int]:
    ordered = sorted(days, key=lambda item: item["date"])
    longest = running = 0
    for day in ordered:
        if day["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    by_date = {date.fromisoformat(item["date"]): item["count"] for item in ordered}
    cursor = max(by_date, default=date.today())
    # An unfinished current day should not break an otherwise-active streak.
    if by_date.get(cursor, 0) == 0:
        cursor -= timedelta(days=1)
    current = 0
    while by_date.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)
    return current, longest


def fetch(username: str) -> dict:
    url = f"https://github.com/users/{username}/contributions"
    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": "animated-profile-readme/1.0", "Accept": "text/html"},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day[data-date][data-level]")
    if not cells:
        raise RuntimeError("GitHub returned no contribution cells; verify the username and try again.")

    days: list[dict] = []
    for cell in cells:
        tooltip = soup.find("tool-tip", attrs={"for": cell.get("id")})
        count = parse_count(tooltip.get_text(" ", strip=True) if tooltip else "")
        days.append(
            {
                "date": cell["data-date"],
                "count": count,
                "level": max(0, min(4, int(cell["data-level"]))),
            }
        )

    days.sort(key=lambda item: item["date"])
    current, longest = streaks(days)
    monthly: dict[str, int] = defaultdict(int)
    for day in days:
        monthly[day["date"][:7]] += day["count"]
    best = max(days, key=lambda item: item["count"])
    return {
        "username": username,
        "fetched_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": url,
        "days": days,
        "stats": {
            "total": sum(item["count"] for item in days),
            "current_streak": current,
            "longest_streak": longest,
            "best_day": best,
            "monthly": dict(sorted(monthly.items())),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch a public GitHub contribution calendar.")
    parser.add_argument("--username", help="Override config.json username")
    parser.add_argument("--config", help="Path to config.json")
    parser.add_argument("--output", default=str(ROOT / "data" / "contributions.json"))
    args = parser.parse_args()

    username = args.username or load_config(args.config)["username"]
    if not username or username == "YOUR_GITHUB_USERNAME":
        raise SystemExit("Set username in config.json or pass --username.")
    payload = fetch(username)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(payload['days'])} days and {payload['stats']['total']:,} contributions to {output}")


if __name__ == "__main__":
    main()
