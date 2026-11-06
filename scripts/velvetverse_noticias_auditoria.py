#!/usr/bin/env python3
"""Auditoria editorial de candidatos de notícia; nunca autoriza emissão."""
import datetime as dt
import email.utils
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

BASE=Path("noticias-teste")
record=json.loads((BASE/"pesquisa.json").read_text(encoding="utf-8"))
now=dt.datetime.fromisoformat(record["gerado_em"])
target=now.date()+dt.timedelta(days=(6-now.weekday())%7)
sections={x["secao"]:x["dados"] for x in record.get("ordem_editorial_candidatos",[])}
names=[("noticias_internacionais",2),("noticias_portugal",3),("desporto_canada",1),("futebol_portugal",3)]
def norm(t):
    text=unicodedata.normalize("NFKD",t.casefold())
    return re.sub(r"[^a-z0-9]+"," ", "".join(c for c in text if not unicodedata.combining(c))).strip()
def safe_date(t):
    try:
        d=email.utils.parsedate_to_datetime(t)
        return d.astimezone(ZoneInfo("America/Toronto"))
    except (TypeError,ValueError,OverflowError):
        return None
def topic_key(x):
    # Aproximação: deteta notícias com títulos semelhantes; NÃO garante deduplicação semântica.
    words=[w for w in norm(x["titulo"]).split() if len(w)>3]
    return set(words)
def similar(a,b):
    if not a or not b:return False
    return len(a&b)/len(a|b)>=.72

report={"estado":"REVISÃO OBRIGATÓRIA — NÃO EMITIR","data_alvo_domingo":target.isoformat(),
        "seccoes":[],"alertas":[],"totais":{}}
known=[]
for section,wanted in names:
    candidates=sections.get(section,[])
    clean=[]
    for x in candidates:
        uri=x.get("url","")
        if urlparse(uri).scheme!="https":continue
        pub=safe_date(x.get("data_publicacao",""))
        age=(now-pub).total_seconds()/3600 if pub else None
        if pub is None or age is None or age<-.5:
            status="DATA INVÁLIDA / FUTURA"
        elif age>48:
            status="ANTIGA (>48h À HORA DO ENSAIO)"
        else:
            status="RECENTE À HORA DA PESQUISA (REVALIDAR DOMINGO)"
        key=topic_key(x)
        overlap=next((t for t,other in known if similar(key,other)),None)
        if overlap: status+="; TÍTULO SEMELHANTE A "+overlap[:70]
        known.append((x["titulo"],key))
        clean.append({"titulo":x["titulo"],"publicado":x.get("data_publicacao",""),
                      "idade_horas":round(age,1) if age is not None else None,
                      "estado":status,"fonte":urlparse(uri).netloc,"url":uri,
                      "validado":False})
    if len(clean)<wanted:report["alertas"].append(f"{section}: candidatos insuficientes")
    report["seccoes"].append({"nome":section,"noticias_desejadas":wanted,
                             "candidatos":clean,"selecionadas_e_verificadas":0})
report["totais"]={"candidatos":sum(len(x["candidatos"]) for x in report["seccoes"]),
                  "noticias_verificadas":0,"noticias_para_emitir":0}
report["alertas"] += [
    "Títulos e datas não constituem confirmação dos factos.",
    "A validade às 12h de domingo requer nova consulta, verificação de fontes e controlo editorial.",
    "Os textos da CBC estão em inglês e exigem adaptação PT-PT.",
    "O processo não está ligado a Fish Audio nem RadioDJ."
]
(BASE/"auditoria.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
lines=["# Auditoria editorial — VelvetVerse Notícias",
       f"Domingo-alvo: {target.isoformat()} | ESTADO: NÃO EMITIR", "",
       "Nenhum título de RSS é automaticamente considerado notícia verificada.", ""]
for sec in report["seccoes"]:
    lines.extend([f"## {sec['nome'].replace('_',' ').title()}",
                  f"Necessárias: {sec['noticias_desejadas']} | verificadas: 0", ""])
    for x in sec["candidatos"][:8]:
        lines.append(f"- {x['titulo']} — {x['estado']} — {x['url']}")
    lines.append("")
lines.extend(["## Alertas", *["- "+x for x in report["alertas"]]])
(BASE/"auditoria.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(f"AUDITORIA: {report['totais']['candidatos']} candidatos; 0 notícias verificadas; emissão BLOQUEADA.")
