#!/usr/bin/env python3
"""Preflight sem custos: impede redacao paga quando pesquisa não tem candidatos suficientes.
Não confirma veracidade, não aprova notícias, não chama APIs.
"""
import json
import sys
from pathlib import Path

PATH=Path("noticias-teste/alinhamento-automatico.json")
QUOTAS={"noticias_internacionais":2,"noticias_portugal":2,
        "desporto_canada":1,"futebol_portugal":3}
CITIES=("Toronto","Lisboa","Porto","Faro")
def check(data):
    reasons=[]
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
        if len(data.get("meteorologia",{}).get(city,[]))<2:
            reasons.append(f"{city}: falta previsão para dois dias")
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
