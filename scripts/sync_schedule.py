#!/usr/bin/env python3
"""Sync data/data.json's schedule from the live Google Sheet (public mirror).

Runs in GitHub Actions every 12 hours (and on manual dispatch). The mirror is an
IMPORTRANGE of the official IIM sheet, shared "anyone with link", so it can be
fetched anonymously via the gviz endpoint. Roster/courses in data.json are
maintained separately (they come from the restricted official sheet).
"""
import json, re, sys, urllib.request
from datetime import datetime, timezone, date

SHEET_ID = "1kyLrZ_j2TTeJqiAt4N2W1FkgMXPl_Cwx1RbYXDml4ic"
DATA = "data/data.json"
SLOT_COLS = [3, 4, 5, 7, 8, 9, 10]  # skip col 6 = lunch break
OK_SEC = re.compile(r"^(Section A|Section B|Single Section)$", re.I)


def fetch(sheet_param: bool) -> dict:
    url = (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq"
        f"?tqx=out:json&headers=0" + ("&sheet=Schedule" if sheet_param else "")
    )
    with urllib.request.urlopen(url, timeout=60) as r:
        text = r.read().decode("utf-8")
    # strip the JSONP wrapper: google.visualization.Query.setResponse({...});
    start, end = text.find("("), text.rfind(")")
    return json.loads(text[start + 1 : end])


def parse(resp: dict) -> list:
    rows = resp.get("table", {}).get("rows", [])
    recs, cur_d = [], None
    for row in rows:
        c = row.get("c") or []
        def gv(i):
            if i < len(c) and c[i] and c[i].get("v") is not None:
                return c[i]["v"]
            return ""
        dv = gv(0)
        if dv:
            m = re.match(r"Date\((\d+),(\d+),(\d+)", str(dv))
            if m:
                cur_d = f"{m.group(1)}-{int(m.group(2)) + 1:02d}-{int(m.group(3)):02d}"
        sec = str(gv(2) or "").strip()
        if not cur_d or "section" not in sec.lower():
            continue
        slots = [re.sub(r"\s+", " ", str(gv(i) or "")).strip() for i in SLOT_COLS]
        recs.append({"date": cur_d, "section": sec, "slots": slots})
    clean = [
        {
            "date": r["date"],
            "day": date.fromisoformat(r["date"]).strftime("%A"),
            "section": r["section"],
            "slots": r["slots"],
        }
        for r in recs
        if re.match(r"^\d{4}-\d{2}-\d{2}$", r["date"]) and OK_SEC.match(r["section"])
        and len(r["slots"]) == 7
    ]
    return clean


def main() -> int:
    resp = fetch(True)
    if resp.get("status") == "error":
        resp = fetch(False)  # tab may not be named "Schedule"
    sched = parse(resp)
    days = len({r["date"] for r in sched})
    if len(sched) < 50 or days < 15:
        print(f"refusing to update: only {len(sched)} rows / {days} days parsed", file=sys.stderr)
        return 1
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    if data.get("schedule") == sched:
        print(f"unchanged ({days} days)")
        return 0
    data["schedule"] = sched
    data["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"updated ({days} days, {len(sched)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
