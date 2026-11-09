#!/usr/bin/env python3
"""Auditoria read-only semanal do Top 5 VelvetVerse; sem RCast, R2 ou dados secretos."""
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"top5-velvetverse-weekly.json"

def main():
    data=json.loads(DATA.read_text(encoding="utf-8"))
    errors=[]
    songs=data.get("songs",[])
    if len(songs)!=5: errors.append("Esperadas 5 faixas")
    if [s.get("rank") for s in songs] != [1,2,3,4,5]:errors.append("Posicoes incorretas")
    if len({s.get("id") for s in songs})!=5:errors.append("IDs repetidos")
    for song in songs:
        if not all(isinstance(song.get(x),str) and song[x].strip() for x in ("id","title","artist")):
            errors.append("ID, titulo ou artista ausente")
        url=song.get("preview","")
        if url and not (isinstance(url,str) and url.startswith("https://")):
            errors.append("URL de audio invalida: requer HTTPS")
    if data.get("previews_seconds")!=30:errors.append("Duracao diferente de 30 segundos")
    if not re.fullmatch(r"[a-zA-Z0-9_-]{15,240}",data.get("edition","")):
        errors.append("Identificador da edicao invalido")
    if data.get("voting_enabled") and data.get("status")!="verified":
        errors.append("Votos ativos numa edicao nao verificada")
    if data.get("preview_permission_confirmed") and not all(s.get("preview") for s in songs):
        errors.append("Autorizacao indicada mas URLs de audio incompletas")
    try:
        week=dt.date.fromisoformat(data["week"])
        if week.weekday()!=0:errors.append("Semana deve ser segunda-feira")
        today=dt.datetime.now(dt.timezone.utc).date()
        age=(today-week).days
        if age>7:errors.append(f"Edicao desatualizada: {age} dias")
        if age< -2:errors.append("Edicao datada no futuro")
    except (ValueError,KeyError,TypeError):errors.append("Data da semana invalida")
    print("Top 5 VelvetVerse — auditoria semanal")
    print("Edicao:",data.get("edition"),"Status:",data.get("status"))
    print("Votos:",bool(data.get("voting_enabled")),"Audio autorizado:",bool(data.get("preview_permission_confirmed")))
    print("Faixas:",", ".join(s.get("title","?") for s in songs))
    if data.get("status")!="verified":
        errors.append("Classificacao ainda provisoria — nao publicar automaticamente")
    if not data.get("preview_permission_confirmed"):
        print("Audio permanece bloqueado ate comprovacao de direitos e URLs de excertos.")
    summary=os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a",encoding="utf-8") as f:
            f.write("## Auditoria Top 5 VelvetVerse\n\n")
            f.write(f"Edição: **{data.get('edition','?')}** · estado: **{data.get('status','?')}**\n\n")
            for e in errors:f.write(f"- ⚠️ {e}\n")
            if not errors:f.write("✅ Cinco músicas validadas. Nenhum áudio foi publicado.\n")
    if errors:
        print("AUDITORIA PENDENTE:")
        for e in errors:print(" -",e)
        return 1
    print("Validacao concluida. Nao houve alteracoes, publicacoes nem votos.")
    return 0

if __name__=="__main__":sys.exit(main())
