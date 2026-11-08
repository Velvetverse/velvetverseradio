#!/usr/bin/env python3
"""Ensaio completo de montagem de MP3 SEM Fish, OpenAI, Internet ou RadioDJ.
Gera silêncio sintético apenas em diretório temporário; nunca notícias reais.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import velvetverse_noticias_producao as prod

def main():
    for name in prod.VINHETAS.values():
        if not (ROOT/name).is_file():
            raise AssertionError("Vinheta em falta no repositório: "+name)
    now=dt.datetime.now(ZoneInfo("America/Toronto")).date()
    sunday=now+dt.timedelta(days=(6-now.weekday())%7)
    paragraph=("Este texto é inteiramente fictício e serve apenas para testar a montagem "
               "de áudio sem notícias verdadeiras ou qualquer publicação. ")
    counts={"internacional":2,"portugal":2,"desporto_canada":1,
            "futebol_portugal":3,"meteorologia_canada":1,"meteorologia_portugal":3}
    approved={"edicao":sunday.isoformat(),"estado":"APROVADO_POR_EDITOR",
              "aprovado_por":"APENAS_TESTE_OFFLINE","aprovado_em":"SEM_EMISSAO",
              "abertura":"Notícias, com Ricky Sousa. Boa tarde.",
              "fecho":"Obrigado por acompanhar esta simulação sem notícias.",
              "secoes":{key:[{"texto":paragraph*13,"fontes":["https://example.org/TESTE"],
                               "confirmado":True} for i in range(n)] for key,n in counts.items()}}
    # Esta aprovação existe SOMENTE no diretório temporário, nunca no repositório.
    prod.validate(approved)
    with tempfile.TemporaryDirectory(prefix="vv-audio-offline-") as tmp:
        root=Path(tmp);script=root/"APROVACAO-FICTICIA-NAO-EMITIR.json"
        script.write_text(json.dumps(approved,ensure_ascii=False),encoding="utf-8")
        demo=root/"silencio-nao-emitir.mp3"
        subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
            "-f","lavfi","-i","anullsrc=r=44100:cl=mono","-t","6",
            "-c:a","libmp3lame","-b:a","64k",str(demo)],check=True)
        sample=demo.read_bytes()
        old_dir=os.getcwd()
        old_out=prod.OUT
        old_vinhetas=prod.VINHETAS_DIR
        try:
            os.chdir(root)
            prod.OUT=Path("noticias-teste")
            prod.VINHETAS_DIR=ROOT
            with patch.dict(os.environ,{
                "VV_ALLOW_BILLABLE":"yes",
                "VV_APPROVED_SCRIPT":str(script),
                "FISH_AUDIO_API_KEY":"FAKE_OFFLINE_KEY",
                "FISH_VOICE_REFERENCE_ID":"FAKE_OFFLINE_VOICE",
                "FISH_TTS_MODEL":"s2.1-pro-free"}):
                with patch.object(prod,"post_json",return_value=sample) as api:
                    prod.render()
                    assert api.call_count>=12,api.call_count
            audio=prod.OUT/("velvetverse-noticias-"+sunday.isoformat()+"-ENSAIO.mp3")
            assert audio.is_file() and audio.stat().st_size>10000
            length=float(subprocess.check_output(["ffprobe","-v","error",
                "-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",
                str(audio)]).strip())
            assert 60<=length<=1800,length
            print("PASS: montagem de áudio offline",round(length,1),"segundos;",
                  api.call_count,"simulações TTS; sem nenhuma chamada paga, emissão ou R2.")
        finally:
            prod.OUT=old_out
            prod.VINHETAS_DIR=old_vinhetas
            os.chdir(old_dir)

if __name__=="__main__":
    main()
