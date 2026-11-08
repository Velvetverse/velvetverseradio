#!/usr/bin/env python3
"""Exercita a redação sem chamar a Internet nem cobrar API."""
import datetime as dt
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"scripts"))
import velvetverse_noticias_producao as prod
from velvetverse_noticias_preflight_editorial import check

sunday=dt.datetime.now(ZoneInfo("America/Toronto")).date()
sunday+=dt.timedelta(days=(6-sunday.weekday())%7)
monday=sunday+dt.timedelta(days=1)
names={"noticias_internacionais":2,"noticias_portugal":3,"desporto_canada":1,"futebol_portugal":3}
forecast={city:[
 {"data":d.isoformat(),"min_c":1,"max_c":12,"prob_chuva_pct":20,"codigo_tempo":2}
 for d in (sunday,monday)] for city in ("Toronto","Lisboa","Porto","Faro")}
aligned={"edicao":sunday.isoformat(),"gerado_em":dt.datetime.now(ZoneInfo("America/Toronto")).isoformat(),
         "estado":"ALINHAMENTO AUTOMATICO — NÃO EMITIR",
         "seccoes":{name:[{"titulo":f"Assunto {name} {i}","url":f"https://example.org/{name}/{i}"}
                            for i in range(count)] for name,count in names.items()},
         "meteorologia":forecast}
assert check(aligned)==[],check(aligned)
output_sections={"internacional":[{"texto":"Texto curto sem detalhes.", "fontes":["https://example.org"],"confirmado":False}]*2,
                 "portugal":[{"texto":"Texto curto sem detalhes.","fontes":["https://example.org"],"confirmado":False}]*3,
                 "desporto_canada":[{"texto":"Texto curto sem detalhes.","fontes":["https://example.org"],"confirmado":False}],
                 "futebol_portugal":[{"texto":"Texto curto sem detalhes.","fontes":["https://example.org"],"confirmado":False}]*3,
                 "meteorologia_canada":[],"meteorologia_portugal":[]}
response={"output":[{"type":"message","content":[{"type":"output_text","text":json.dumps({
    "edicao":sunday.isoformat(),"estado":"RASCUNHO","abertura":"Notícias, com Ricky Sousa. Boa tarde.",
    "fecho":"Obrigado por acompanhar.", "secoes":output_sections})}]}],
    "usage":{"input_tokens":300,"output_tokens":600,"total_tokens":900}}
captured={}
def fake_post(url,payload,key):
    captured["prompt"]=payload["input"]
    captured["model"]=payload["model"]
    return json.dumps(response).encode("utf-8")
with tempfile.TemporaryDirectory() as tmp:
    previous=os.getcwd()
    os.chdir(tmp)
    try:
        prod.OUT=Path("noticias-teste")
        prod.OUT.mkdir()
        (prod.OUT/"pesquisa.json").write_text(json.dumps({"meteorologia":forecast}))
        (prod.OUT/"alinhamento-automatico.json").write_text(json.dumps(aligned))
        with patch.dict(os.environ,{"VV_ALLOW_BILLABLE":"yes","OPENAI_API_KEY":"FICTICIA_NAO_USAR",
                                   "OPENAI_MODEL":"MODELO_FICTICIO"}):
            with patch.object(prod,"post_json",side_effect=fake_post):
                prod.draft()
        quality=json.loads((prod.OUT/"avaliacao-redacao.json").read_text())
        assert quality["pronto_para_locucao"] is False
        assert quality["palavras"]<2500
        assert quality["motivos_de_revisao"]
        assert "Boa tarde" in captured["prompt"]
        assert "280-330" in captured["prompt"]
        assert "NUNCA com 'Boa noite'" in captured["prompt"]
        assert "2500-3000" in captured["prompt"]
        assert len(json.loads((prod.OUT/"rascunho-ia.json").read_text())["secoes"]["meteorologia_portugal"])==3
    finally:
        os.chdir(previous)
print("PASS: 9 temas, saudação diurna, meteorologia estruturada e jornal curto bloqueado.")
