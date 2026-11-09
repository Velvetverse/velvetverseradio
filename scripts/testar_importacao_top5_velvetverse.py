#!/usr/bin/env python3
"""Testes locais sem dados reais de ouvintes; nenhuma chamada de rede."""
import csv,importlib.util, tempfile
from pathlib import Path

script=Path(__file__).with_name("importar_top5_velvetverse_csv.py")
spec=importlib.util.spec_from_file_location("top5_importer",str(script))
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/"relatorio.csv"
 rows=[
  ["Track Title","Artist","Playbacks"],
  ["Música A","Artista A","31"],
  ["Música B","Artista B","28"],
  ["Música C","Artista C","26"],
  ["Música D","Artista D","25"],
  ["Música E","Artista E","20"],
  ["Música F","Artista F","10"],
 ]
 with p.open("w",encoding="utf-8-sig",newline="") as f:
  csv.writer(f,delimiter=";").writerows(rows)
 data=mod.import_csv(p,"2026-11-09")
 assert len(data["songs"])==5
 assert data["songs"][0]["title"]=="Música A"
 assert data["songs"][4]["title"]=="Música E"
 assert data["voting_enabled"] is False
 assert data["preview_permission_confirmed"] is False
 assert all(not s["preview"] for s in data["songs"])
 rows[-1][2]="20"
 with p.open("w",encoding="utf-8-sig",newline="") as f:
  csv.writer(f,delimiter=";").writerows(rows)
 try:
  mod.import_csv(p,"2026-11-09")
 except ValueError as e:
  assert "Empate" in str(e)
 else:raise AssertionError("Deveria bloquear empate em quinto lugar")
print("TESTES PASSARAM: ranking, cinco faixas, bloqueio de empate e nao publicacao.")
