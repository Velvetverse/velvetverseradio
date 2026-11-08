#!/usr/bin/env python3
"""Seleção determinística de candidatos RSS. Não afirma que artigos foram verificados."""
import datetime as dt
import email.utils
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlparse
BASE=Path("noticias-teste")
raw=json.loads((BASE/"pesquisa.json").read_text(encoding="utf-8"))
aud=json.loads((BASE/"auditoria.json").read_text(encoding="utf-8"))
now=dt.datetime.fromisoformat(raw["gerado_em"])
QUOTAS={"noticias_internacionais":2,"noticias_portugal":3,"desporto_canada":1,"futebol_portugal":3}
order=[s for s in aud["seccoes"] if s["nome"] in QUOTAS]
def normalize(s):
    s=unicodedata.normalize("NFKD",s.casefold())
    return re.sub(r"[^a-z0-9]+"," ","".join(c for c in s if not unicodedata.combining(c))).strip()
def topical(s):
    stop={"para","com","sobre","mais","esta","este","entre","após","depois","portugal","canadá","canada"}
    return {w for w in normalize(s).split() if len(w)>3 and w not in stop}
seen_urls=set();seen_topics=[];selected={};alerts=[]
for sec in order:
    name=sec["nome"]; needed=QUOTAS[name]; possibilities=[]
    for item in sec["candidatos"]:
        if item.get("validado") is True: continue
        url=item.get("url",""); title=item.get("titulo","").strip()
        if not url.startswith("https://") or not title or url in seen_urls: continue
        age=item.get("idade_horas")
        if age is None or not (0<=age<=36): continue
        topic=topical(title)
        if topic and any(len(topic&t)/len(topic|t)>=0.65 for t in seen_topics if t):continue
        possibilities.append(item)
    possibilities.sort(key=lambda x:(x["idade_horas"],x["titulo"]))
    picked=[]
    for x in possibilities:
        if len(picked)>=needed:break
        topic=topical(x["titulo"])
        if any(len(topic&t)/len(topic|t)>=.65 for t in seen_topics if t):continue
        picked.append({"titulo":x["titulo"],"fonte":x["fonte"],"url":x["url"],
            "publicado":x["publicado"],"idade_horas":x["idade_horas"],
            "estado":"CANDIDATO — FACTOS NÃO VERIFICADOS"})
        seen_urls.add(x["url"]);seen_topics.append(topic)
    selected[name]=picked
    if len(picked)<needed:alerts.append(f"{name}: apenas {len(picked)} de {needed} candidatos recentes")
meteo=raw.get("meteorologia",{})
for city in ("Toronto","Lisboa","Porto","Faro"):
    if len(meteo.get(city,[]))<2: alerts.append(f"Previsão incompleta: {city}")
output={"edicao":aud["data_alvo_domingo"],"gerado_em":raw["gerado_em"],
        "estado":"ALINHAMENTO AUTOMATICO — NÃO EMITIR",
        "criterios":"RSS HTTPS; até 36 horas; sem URLs repetidas; comparação aproximada de títulos; por ordem de atualidade",
        "seccoes":selected,"meteorologia":meteo,"alertas":alerts,
        "limite":"Metadados RSS não comprovam os factos. Não gerar locução ou agendar emissão com esta lista."}
(BASE/"alinhamento-automatico.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
lines=["# Notícias com Ricky Sousa — alinhamento automático de candidatos",
       f"Edição {output['edicao']} — NÃO EMITIR","","Seleção automática, SEM confirmação factual dos artigos.",""]
for name,items in selected.items():
    lines.append("## "+name.replace("_"," ").title())
    for i,x in enumerate(items,1):
        lines.append(f"{i}. {x['titulo']} — {x['fonte']} — {x['url']}")
    if not items:lines.append("Sem candidatos recentes adequados.")
    lines.append("")
lines += ["## Alertas",*["- "+x for x in alerts],"",
          "Este alinhamento é apenas para pesquisa; não é um guião aprovado."]
(BASE/"alinhamento-automatico.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("ALINHAMENTO AUTOMÁTICO:",sum(map(len,selected.values())),"candidatos; avisos:",len(alerts),"; NÃO EMITIR")
