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
    "rtp_desporto": "https://www.rtp.pt/noticias/rss/desporto",
    "cbc_sports": "https://www.cbc.ca/webfeed/rss/rss-sports",
    "cbc_world": "https://www.cbc.ca/webfeed/rss/rss-world",
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
        "forecast_days":8,
    })
    raw=json.loads(get("https://api.open-meteo.com/v1/forecast?"+params))
    d=raw["daily"]
    result=[]
    localtoday=NOW.astimezone(ZoneInfo(tz)).date()
    days_until_sunday=(6-localtoday.weekday())%7
    target_sunday=localtoday+dt.timedelta(days=days_until_sunday)
    target_monday=target_sunday+dt.timedelta(days=1)
    for i,date in enumerate(d["time"]):
        day=dt.date.fromisoformat(date)
        if day not in {target_sunday, target_monday}: continue
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
# Alinhamento experimental por secção: apenas candidatos, NÃO texto pronto a emitir.
def select(items, limit, predicate=lambda item: True):
    found=[]
    used=set()
    for item in items:
        title=item["titulo"].strip().casefold()
        if title in used or not predicate(item): continue
        if title.startswith(("20h ", "21h ", "22h ", "19h ", "18h ")): continue
        found.append(item)
        used.add(title)
        if len(found)>=limit: break
    return found

rtp=record["noticias"].get("rtp_ultimas",[])
rtps=record["noticias"].get("rtp_desporto",[])
international=lambda x: "/mundo/" in x["url"] or "/guerra-" in x["url"]
portugal=lambda x: any(k in x["url"] for k in ("/pais/","/politica/","/economia/"))
football=lambda x: (any(k in x["url"] for k in ("/futebol","/benfica/","/sporting/","/fc-porto/","/selecao-nacional/")) or any(k in x["titulo"].casefold() for k in ("i liga", "liga dos campeões", "futebol", "benfica", "sporting", "fc porto", "seleção")))
ordem=[
    ("noticias_internacionais", select(rtp, 7, international)),
    ("noticias_portugal",select(rtp, 9, portugal)),
    ("separador_desporto",[]),
    ("desporto_canada", select(record["noticias"].get("cbc_sports",[]),7)),
    ("futebol_portugal",select(rtps+rtp, 10, football)),
    ("separador_meteorologia",[]),
    ("meteorologia_canada",record["meteorologia"].get("Toronto",[])),
    ("meteorologia_portugal",{city:record["meteorologia"].get(city,[]) for city in ("Lisboa","Porto","Faro")}),
]
record["ordem_editorial_candidatos"]=[{"secao":name,"dados":data} for name,data in ordem]
record["avisos"].append("A selecção por palavras-chave é preliminar e pode conter erros de categoria; requer leitura, confirmação independente e aprovação editorial.")

(OUT/"pesquisa.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
lines=["# VelvetVerse Noticias — pesquisa experimental","",
       f"Gerado: {NOW.isoformat()} (Toronto)","",
       "**RASCUNHO — NAO EMITIR**. Sem verificação jornalística, sem áudio.","",
       "## Títulos RTP (para revisão, nunca texto de locução)",""]
lines += ["## Alinhamento de candidatos (NÃO EMITIR)",""]
for sec in record["ordem_editorial_candidatos"]:
    lines.append("### "+sec["secao"].replace("_"," ").title())
    dados=sec["dados"]
    if isinstance(dados,list):
        for item in dados:
            if "titulo" in item:
                lines.append(f"- {item['titulo']} — {item['data_publicacao']} — {item['url']}")
            else:
                lines.append(f"- {json.dumps(item,ensure_ascii=False)}")
    elif isinstance(dados,dict):
        for cidade, dias in dados.items():
            lines.append(f"- {cidade}: {json.dumps(dias,ensure_ascii=False)}")
    lines.append("")
lines += ["## Títulos RTP (consulta geral)",""]
for item in record["noticias"].get("rtp_ultimas",[])[:20]:
    lines.append(f"- {item['titulo']} — {item['data_publicacao']} — {item['url']}")
lines += ["","## Candidatos desporto RTP (pesquisa, não emitidos)",""]
for item in record["noticias"].get("rtp_desporto",[])[:12]:
    lines.append(f"- {item['titulo']} — {item['data_publicacao']} — {item['url']}")
lines += ["","## Candidatos desporto Canadá CBC (pesquisa, não emitidos)",""]
for item in record["noticias"].get("cbc_sports",[])[:12]:
    lines.append(f"- {item['titulo']} — {item['data_publicacao']} — {item['url']}")
lines += ["","## Candidatos internacionais CBC (pesquisa, não emitidos)",""]
for item in record["noticias"].get("cbc_world",[])[:12]:
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
