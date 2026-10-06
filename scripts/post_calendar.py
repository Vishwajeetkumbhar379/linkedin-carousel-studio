"""Posting calendar for a batch: content/calendar.md + content/calendar.ics (import into Google/Apple Calendar).

    python scripts/post_calendar.py out/batch-01
One post per weekday at 08:30 Europe/Berlin, videos and carousels alternating (same order as the batch page).
"""
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from batch_page import posts, schedule  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://buildwithvish.netlify.app"


def main(batch: Path) -> None:
    plan = schedule(posts(batch.resolve()))
    md = ["# Posting calendar", "", "One post per weekday, 08:30 Berlin. Post natively on LinkedIn (upload the MP4 or PDF), paste the caption, add the first comment, reply to comments for the first hour.", "",
          "| # | Day | Format | Hook | File | Article |", "|---|---|---|---|---|---|"]
    ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Build with Vish//content engine//EN", "CALSCALE:GREGORIAN"]
    year = 2026
    for i, (p, day) in enumerate(plan, 1):
        meta = json.loads((p / "meta.json").read_text())
        d = dt.datetime.strptime(f"{day} {year}", "%a %d %b %Y")
        fmt = "Video" if (p / "video.json").exists() else ("Carousel" if (p / "carousel.pdf").exists() and len(list((p / "slides").glob("*.png"))) > 1 else "Image")
        file = f"{p.relative_to(ROOT)}/" + ("video.mp4" if fmt == "Video" else "carousel.pdf" if fmt == "Carousel" else "image.png")
        art = f"{SITE}/#read-{meta.get('site_slug') or meta['slug']}"
        hook = meta.get("hook", "").replace("*", "")
        md.append(f"| {i} | {day} | {fmt} | {hook} | `{file}` | [read]({art}) |")
        stamp = d.strftime("%Y%m%d")
        ics += ["BEGIN:VEVENT", f"UID:bwv-{meta['slug']}@buildwithvish", f"DTSTAMP:{stamp}T060000Z",
                f"DTSTART;TZID=Europe/Berlin:{stamp}T083000", f"DTEND;TZID=Europe/Berlin:{stamp}T090000",
                f"SUMMARY:Post on LinkedIn: {hook[:60]}", f"DESCRIPTION:{fmt}. File: {file}. Caption and first comment on the batch page. Article: {art}",
                "BEGIN:VALARM", "TRIGGER:-PT15M", "ACTION:DISPLAY", "DESCRIPTION:Post time", "END:VALARM", "END:VEVENT"]
    ics.append("END:VCALENDAR")
    (ROOT / "content" / "calendar.md").write_text("\n".join(md) + "\n")
    (ROOT / "content" / "calendar.ics").write_text("\r\n".join(ics) + "\r\n")
    print("\n".join(md[6:]))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
