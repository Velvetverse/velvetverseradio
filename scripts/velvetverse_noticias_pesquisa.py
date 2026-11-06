#!/usr/bin/env python3
"""VelvetVerse Noticias: recolha experimental, NAO publicar nem emitir.
Recolhe metadados RSS RTP e previsao Open-Meteo. Sem IA, voz ou segredos.
"""
import datetime as dt
import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Toronto")
NOW = dt.datetime.now(TZ)
OUT = Path(os.environ.get("VV_NEWS_OUTPUT", "noticias-teste"))
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "VelvetVerseNoticias-Research/0.1 (radio editorial test)"}
SOURCES = {
    "rtp_ultimas": "https://www.rtp.pt/noticias/rss",
}
CITIES = {
    "Toronto": (43.6532, -79.3832, "America/Toronto"),
    "Lisboa": (38.7167, -9.1333, "Europe/Lisbon"),
    "Porto": (41.1496, -8.6109, "Europe/Lisbon"),
    "Faro": (37.0194, -7.9304, "Europe/Lisbon"),
}

def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as rsp:
        return rsp.read()

def xml_items(payload):
    root = ET.fromstring(payload)
    items = []
    for el in root.findall(".//item")[:35]:
        title = (el.findtext("title") or "").strip()
        link = (el.findtext("link") or "").strip()
        date = (el.findtext("pubDate") or "").strip()
        if title and link.startswith("https://"):
            items.append({"titulo":title, "url":link, "data_publicacao":date})
    return items

def weather(city, lat, lon, tz):
    params = urllib.parse.urlencode({
        "latitude":lat, "longitude":lon, "timezone":tz,
        "daily":"weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "forecast_days":3,
    })
    raw=json.loads(get("https://api.open-meteo.com/v1/forecast?"+params))
    d=raw["daily"]
    result=[]
    localtoday=NOW.astimezone(ZoneInfo(tz)).date()
    for i,date in enumerate(d["time"]):
        day=dt.date.fromisoformat(date)
        if day not in {localtoday, localtoday+dt.timedelta(days=1)}: continue
        result.append({"data":date,"min_c":d["temperature_2m_min"][i],
                       "max_c":d["temperature_2m_max"][i],
                       "prob_chuva_pct":d["precipitation_probability_max"][i],
                       "codigo_tempo":d["weather_code"][i]})
    return result

record={"gerado_em":NOW.isoformat(),"estado":"RASCUNHO - NAO EMITIR",
        "avisos":["RSS: somente metadados para pesquisa; verificar licenca e artigos antes de emitir.",
                  "Nao sao noticias validadas nem prontas para locucao.",
                  "Meteorologia Open-Meteo: atribuicao CC BY 4.0; verificar elegibilidade nao comercial."],
        "noticias":{},"meteorologia":{},"erros":[]}
for label,url in SOURCES.items():
    try: record["noticias"][label]=xml_items(get(url))
    except Exception as exc: record["erros"].append(f"{label}: {type(exc).__name__}: {exc}")
for city,(lat,lon,tz) in CITIES.items():
    try: record["meteorologia"][city]=weather(city,lat,lon,tz)
    except Exception as exc: record["erros"].append(f"{city}: {type(exc).__name__}: {exc}")
(OUT/"pesquisa.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
lines=["# VelvetVerse Noticias — pesquisa experimental","",
       f"Gerado: {NOW.isoformat()} (Toronto)","",
       "**RASCUNHO — NAO EMITIR**. Sem verificação jornalística, sem áudio.","",
       "## Títulos RTP (para revisão, nunca texto de locução)",""]
for item in record["noticias"].get("rtp_ultimas",[])[:20]:
    lines.append(f"- {item['titulo']} — {item['data_publicacao']} — {item['url']}")
lines += ["","## Previsões (Open-Meteo, CC BY 4.0)",""]
for city,days in record["meteorologia"].items():
    lines.append("### "+city)
    for d in days:
        lines.append(f"- {d['data']}: {d['min_c']}–{d['max_c']} °C, precipitação até {d['prob_chuva_pct']}%, código {d['codigo_tempo']}")
    lines.append("")
lines += ["Fonte meteorologia: https://open-meteo.com/ ; dados sujeitos a alterações.",
          "","## Erros",*["- "+e for e in record["erros"]]]
(OUT/"pesquisa.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(f"Resultado guardado em {OUT}. Títulos: {len(record['noticias'].get('rtp_ultimas',[]))}; erros: {len(record['erros'])}")
