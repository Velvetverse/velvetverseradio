#!/usr/bin/env python3
"""Publica apenas um Billboard Hot Latin Songs Top 5 completo, com IDs Apple confirmados.
Falha sem modificar o site se Billboard bloquear ou qualquer faixa não corresponder.
"""
import datetime as dt
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

import billboard

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "top5-weekly.json"
toronto = dt.datetime.now(ZoneInfo("America/Toronto"))
if toronto.weekday() != 0 or toronto.hour != 10:
    print("Fora da janela de publicação (segunda, 10:00 Toronto).")
    sys.exit(0)

current = json.loads(FILE.read_text(encoding="utf-8"))
try:
    chart = billboard.ChartData("latin-songs")
    date = str(chart.date)
    chart_day = dt.date.fromisoformat(date)
    if not (toronto.date() - dt.timedelta(days=21) <= chart_day <= toronto.date() + dt.timedelta(days=7)):
        raise ValueError("Data de Billboard fora da janela segura: " + date)
    if chart_day <= dt.date.fromisoformat(current["chart_date"]):
        print("A edição já é a mais recente confirmada:", date)
        sys.exit(0)
    top = list(chart)[:5]
    if len(top) != 5 or any(x.rank != i + 1 for i, x in enumerate(top)):
        raise ValueError("Ranking incompleto ou com posições inválidas")

    def norm(txt):
        txt = unicodedata.normalize("NFKD", txt.casefold())
        txt = "".join(c for c in txt if not unicodedata.combining(c))
        return re.sub(r"[^a-z0-9]+", " ", txt).strip()

    def tokens(txt):
        return set(norm(txt).split())

    def apple_id(title, artist):
        query = urllib.parse.urlencode({"term": title+" "+artist, "entity":"song", "country":"us", "limit": 40})
        url = "https://itunes.apple.com/search?" + query
        req = urllib.request.Request(url, headers={"User-Agent":"VelvetVerseRadio/1.0"})
        with urllib.request.urlopen(req, timeout=20) as res:
            found = json.load(res).get("results", [])
        t = norm(title)
        expected = tokens(artist)
        for item in found:
            if norm(item.get("trackName", "")) != t:
                continue
            matched = tokens(item.get("artistName", ""))
            # Exige concordância do artista principal para evitar versões alternativas.
            if not matched or len(expected & matched) < 1:
                continue
            track_id = str(item.get("trackId",""))
            if re.fullmatch(r"\d+", track_id):
                return track_id
        return None

    songs=[]
    for i, entry in enumerate(top,1):
        title,artist=entry.title,entry.artist
        ident=apple_id(title,artist)
        if not ident:
            raise ValueError(f"Não foi possível confirmar Apple Music #{i}: {title} — {artist}")
        songs.append({"rank": i, "title": title, "artist": artist, "id": ident})
    if len({x["id"] for x in songs}) != 5:
        raise ValueError("IDs Apple Music repetidos")
    value={"source":"Billboard Hot Latin Songs","chart_date":date,
           "week":toronto.date().isoformat(),"verified":True,
           "source_url":"https://www.billboard.com/charts/latin-songs/"+date+"/",
           "songs":songs}
    FILE.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Edição publicada:",date)
except Exception as exc:
    print("Atualização bloqueada por falta de verificação; edição anterior preservada:",str(exc),file=sys.stderr)
    sys.exit(1)
