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
 # Simular as colunas reais vistas no painel RCast (novembro 2026)
 rcast=[
  ["Track","Artist","Times played","Listener performances"],
  ["JINGLE PRINCIPAL","cmli","148","128"],
  ["Your Station Slogan","RadioDJ","124","86"],
  ["The Sound of VelvetVerse","cmli","24","14"],
  ["VELVET AFTER DARK Sweepe 1","cmli","16","11"],
  ["Goteira|Vevo","Luedji Luna","7","6"],
  ["Sou Camionista Madrugador","Beto","6","4"],
  ["Deriram","Natiruts","5","4"],
  ["Groove Bom","Natiruts & Hamilton de Holanda","4","4"],
  ["Self Control","Beto","3","2"],
 ]
 with p.open("w",encoding="utf-8-sig",newline="") as f:
  csv.writer(f).writerows(rcast)
 candidate=mod.import_csv(p,"2026-11-09")
 assert [s["title"] for s in candidate["songs"]]==["Goteira|Vevo","Sou Camionista Madrugador","Deriram","Groove Bom","Self Control"]
 assert all("jingle" not in s["title"].lower() for s in candidate["songs"])
print("TESTES PASSARAM: ranking, cinco faixas, bloqueio de empate e nao publicacao.")
