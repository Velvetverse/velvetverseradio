#!/usr/bin/env python3
"""Preflight sem custos: impede redacao paga quando pesquisa não tem candidatos suficientes.
Não confirma veracidade, não aprova notícias, não chama APIs.
"""
import datetime as dt
import json
import sys
from zoneinfo import ZoneInfo
from pathlib import Path

PATH=Path("noticias-teste/alinhamento-automatico.json")
QUOTAS={"noticias_internacionais":2,"noticias_portugal":2,
        "desporto_canada":1,"futebol_portugal":3}
CITIES=("Toronto","Lisboa","Porto","Faro")
def check(data):
    reasons=[]
    today=dt.datetime.now(ZoneInfo("America/Toronto")).date()
    sunday=today+dt.timedelta(days=(6-today.weekday())%7)
    monday=sunday+dt.timedelta(days=1)
    if data.get("edicao")!=sunday.isoformat():
        reasons.append("Data da edição não corresponde ao domingo de Toronto")
    try:
        generated=dt.datetime.fromisoformat(data.get("gerado_em",""))
        if generated.tzinfo is None:
            raise ValueError("sem fuso horário")
        age=(dt.datetime.now(dt.timezone.utc)-generated.astimezone(dt.timezone.utc)).total_seconds()
        if age< -300 or age > 6*3600:
            reasons.append("Pesquisa demasiado antiga ou com hora futura")
    except (ValueError,TypeError):
        reasons.append("Data de pesquisa inválida")
    if data.get("estado")!="ALINHAMENTO AUTOMATICO — NÃO EMITIR":
        reasons.append("Alinhamento não identificado como rascunho.")
    for section,min_count in QUOTAS.items():
        rows=data.get("seccoes",{}).get(section,[])
        if len(rows)<min_count:
            reasons.append(f"{section}: {len(rows)}/{min_count} notícias candidatas")
        for row in rows:
            if not row.get("url","").startswith("https://"):
                reasons.append(f"{section}: URL inválido")
    for city in CITIES:
        forecasts=data.get("meteorologia",{}).get(city,[])
        dates={row.get("data") for row in forecasts}
        if not {sunday.isoformat(),monday.isoformat()}.issubset(dates):
            reasons.append(f"{city}: previsões de domingo e segunda incompletas ou desatualizadas")
    return reasons
def main():
    if not PATH.is_file():
        print("BLOQUEADO: alinhamento automático em falta")
        return 2
    data=json.loads(PATH.read_text(encoding="utf-8"))
    reasons=check(data)
    print(json.dumps({"estado":"BLOQUEADO_SEM_CUSTOS" if reasons else "CANDIDATOS_SUFICIENTES_PARA_RASCUNHO",
       "motivos":reasons,"nota":"Nem aprovação factual nem autorização de despesa."},ensure_ascii=False))
    return 2 if reasons else 0
if __name__=="__main__":
    sys.exit(main())
