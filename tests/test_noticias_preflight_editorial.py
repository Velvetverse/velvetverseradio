#!/usr/bin/env python3
"""Teste offline de bloqueio de custo por falta de candidatos RSS."""
from scripts.velvetverse_noticias_preflight_editorial import check
def fixture():
    return {"estado":"ALINHAMENTO AUTOMATICO — NÃO EMITIR",
        "seccoes":{k:[{"url":"https://example.org/noticia-"+str(i)} for i in range(n)]
            for k,n in (("noticias_internacionais",2),("noticias_portugal",2),
                        ("desporto_canada",1),("futebol_portugal",3))},
        "meteorologia":{city:[{"data":"domingo"},{"data":"segunda"}] for city in
                       ("Toronto","Lisboa","Porto","Faro")}}
def test():
    good=fixture()
    assert not check(good)
    good["seccoes"]["futebol_portugal"]=[]
    assert any("futebol_portugal" in x for x in check(good))
    good=fixture()
    good["meteorologia"]["Toronto"]=[]
    assert any("Toronto" in x for x in check(good))
    print("PASS: sem custo quando há dados; bloqueia falta de noticias/meteorologia.")
if __name__=="__main__":test()
