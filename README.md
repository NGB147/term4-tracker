# Term IV Tracker — MBA 2025-27 (IIM Sambalpur)

A zero-backend schedule & attendance tracker for the batch. Live at the GitHub Pages URL of this repo.

## How it works

- **`index.html`** — the whole app. Pick yourself by roll number; the app shows only *your* section + electives. Attendance (P/A/Off), notes, assignments and friends are stored in your browser (localStorage) — private to your device.
- **`data/data.json`** — the database: schedule + course catalog + batch roster (307 students, section per elective). Loaded by the app on every visit.
- **`scripts/sync_schedule.py` + `.github/workflows/sync.yml`** — GitHub Action that re-fetches the schedule from the live Google Sheet **every 12 hours** (and on manual dispatch from the Actions tab) and commits the refreshed `data.json`.
- **In-app 🔄 Sync** — the app also fetches the live sheet directly in your browser: on open, when the tab regains focus, **every 30 minutes**, and on click. Freshest source wins.

## Features

- **Today / Week** — your personal timetable, per-course sections handled (you can be Sec A in one elective, Sec B in another).
- **Attendance** — mark P/A/Off per class; per-course % vs your target, plus how many classes you can still miss.
- **Friends** — add batchmates by name/roll number, see their classes, find common free slots.
- **Holidays** — days when you (and your whole friend group) are free — for planning trips.

## Updating the roster

Electives/section data comes from the official (IIM-restricted) sheet and is baked into `data/data.json`. If enrollments change, regenerate the `students` block and commit.

---
made out of boredom by **H&N** 🏏🏀
