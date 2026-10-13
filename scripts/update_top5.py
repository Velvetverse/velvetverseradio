#!/usr/bin/env python3
"""Atualiza o Top 5 Latino semanal a partir do ranking Most Played do Apple Music (México)."""
import datetime as dt
import json
import os
import re
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "top5-weekly.json"
now = dt.datetime.now(ZoneInfo("America/Toronto"))
# GitHub Actions executa de hora a hora; só publica às segundas, 10h de Toronto.
if not (now.weekday() == 0 and now.hour == 10):
    print("Fora da janela de atualização semanal.")
    raise SystemExit(0)
week = now.date().isoformat()
if OUT.exists():
    existing = json.loads(OUT.read_text(encoding="utf-8"))
    if existing.get("week") == week:
        print("Edição da semana já publicada.")
        raise SystemExit(0)
url = "https://rss.applemarketingtools.com/api/v2/mx/music/most-played/25/songs.json"
req = urllib.request.Request(url, headers={"User-Agent": "VelvetVerseRadioTop5/1.0"})
with urllib.request.urlopen(req, timeout=30) as response:
    payload = json.load(response)
songs = []
for item in payload.get("feed", {}).get("results", []):
    link = item.get("url", "")
    ident = re.search(r"[?&]i=(\d+)", link) or re.search(r"/(\d+)(?:\?|$)", link)
    song_id = ident.group(1) if ident else str(item.get("id", ""))
    if not re.fullmatch(r"\d+", song_id):
        continue
    songs.append({"id": song_id, "title": str(item["name"]), "artist": str(item["artistName"])})
    if len(songs) >= 5:
        break
if len(songs) != 5:
    raise RuntimeError("Ranking Apple Music incompleto; edição anterior conservada.")
OUT.write_text(json.dumps({"week": week, "source": "Apple Music Most Played — México", "songs": songs}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Publicada edição", week, songs)
