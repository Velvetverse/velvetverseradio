#!/usr/bin/env python3
"""Teste offline da seleção semanal de notícias sem usar quaisquer APIs."""
import datetime as dt
import json
import subprocess
import sys
import tempfile
from pathlib import Path

script=Path(__file__).resolve().parents[1]/"scripts"/"velvetverse_noticias_selecao.py"
from zoneinfo import ZoneInfo
now=dt.datetime.now(ZoneInfo("America/Toronto"))
date=now.date().isoformat()
names={"noticias_internacionais":2,"noticias_portugal":3,
       "desporto_canada":1,"futebol_portugal":3}
with tempfile.TemporaryDirectory() as tmp:
    base=Path(tmp)/"noticias-teste";base.mkdir()
    sections=[];total=0
    distinct_titles = [
        "Aeroportos internacionais anunciam horários de ligação transatlântica",
        "Investigadores apresentam relatório sobre conservação marinha",
        "Hospitais portugueses atualizam serviços de atendimento regional",
        "Assembleia debate propostas de apoio ao arrendamento",
        "Autarquias divulgam calendário de obras rodoviárias",
        "Equipa canadiana prepara competição nacional de hóquei",
        "Treinador encarnado apresenta convocados para próximo encontro",
        "Federação confirma datas da taça de clubes portugueses",
        "Jogadores portistas regressam aos treinos após intervalo",
    ]
    k=0
    for section,count in names.items():
        items=[]
        for i in range(count):
            title=distinct_titles[k]
            k+=1
            items.append({"titulo":title,"url":f"https://example.org/{section}/{i}",
                          "fonte":"example.org","publicado":date,"idade_horas":2,
                          "validado":False})
            total+=1
        sections.append({"nome":section,"candidatos":items})
    pesquisa={"gerado_em":now.isoformat(),
              "meteorologia":{city:[{"data":date},{"data":date}] for city in ("Toronto","Lisboa","Porto","Faro")}}
    auditoria={"data_alvo_domingo":date,"seccoes":sections}
    (base/"pesquisa.json").write_text(json.dumps(pesquisa),encoding="utf-8")
    (base/"auditoria.json").write_text(json.dumps(auditoria),encoding="utf-8")
    cp=subprocess.run([sys.executable,str(script)],cwd=tmp,text=True,capture_output=True)
    assert cp.returncode==0,(cp.stdout,cp.stderr)
    result=json.loads((base/"alinhamento-automatico.json").read_text(encoding="utf-8"))
    assert result["estado"].endswith("NÃO EMITIR")
    assert sum(len(v) for v in result["seccoes"].values())==total,result["seccoes"]
    assert not result["alertas"],result["alertas"]
    print("OK: seleção automática offline de 9 candidatos; não autoriza emissão.")
