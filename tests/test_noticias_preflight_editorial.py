#!/usr/bin/env python3
"""Teste offline de bloqueio de custo por falta de candidatos RSS."""
import sys
import datetime as dt
from zoneinfo import ZoneInfo
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.velvetverse_noticias_preflight_editorial import check
def fixture():
    now=dt.datetime.now(ZoneInfo("America/Toronto"))
    sunday=now.date()+dt.timedelta(days=(6-now.weekday())%7)
    monday=sunday+dt.timedelta(days=1)
    return {"estado":"ALINHAMENTO AUTOMATICO — NÃO EMITIR",
        "edicao":sunday.isoformat(),"gerado_em":now.isoformat(),
        "seccoes":{k:[{"url":"https://example.org/noticia-"+str(i)} for i in range(n)]
            for k,n in (("noticias_internacionais",2),("noticias_portugal",2),
                        ("desporto_canada",1),("futebol_portugal",3))},
        "meteorologia":{city:[{"data":sunday.isoformat()},{"data":monday.isoformat()}] for city in
                       ("Toronto","Lisboa","Porto","Faro")}}
def test():
    good=fixture()
    assert not check(good)
    good["seccoes"]["futebol_portugal"]=[]
    assert any("futebol_portugal" in x for x in check(good))
    good=fixture()
    good["meteorologia"]["Toronto"]=[]
    assert any("Toronto" in x for x in check(good))
    good=fixture()
    good["edicao"]="2001-01-01"
    assert any("Data da edição" in x for x in check(good))
    good=fixture()
    good["gerado_em"]=(dt.datetime.now(ZoneInfo("America/Toronto"))-dt.timedelta(hours=12)).isoformat()
    assert any("antiga" in x for x in check(good))
    print("PASS: bloqueio por candidatos, previsões, data e antiguidade da pesquisa.")
if __name__=="__main__":test()
