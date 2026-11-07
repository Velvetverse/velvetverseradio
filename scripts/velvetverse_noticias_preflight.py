#!/usr/bin/env python3
"""Verificação SEM despesas e SEM emissão das dependências do Notícias."""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

JINGLES=("intro-noticias.mp3","vinheta-desporto.mp3","vinheta-meteorologia.mp3")
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",default=None,help="guardar relatório sem credenciais")
    args=parser.parse_args()
    result={"modo":"OFFLINE; NÃO GERA, NÃO PUBLICA, NÃO EMITE",
            "vinhetas":{},"ferramentas":{},"segredos_apenas_presenca":{},"bloqueios":[]}
    for name in JINGLES:
        p=Path(name)
        ok=p.is_file() and p.stat().st_size>1000
        result["vinhetas"][name]={"presente":ok,"bytes":p.stat().st_size if ok else 0}
        if not ok: result["bloqueios"].append("Vinheta ausente: "+name)
    for tool in ("python","ffmpeg","ffprobe"):
        result["ferramentas"][tool]=bool(shutil.which(tool) or (tool=="python" and sys.executable))
    for name in ("OPENAI_API_KEY","FISH_AUDIO_API_KEY","FISH_VOICE_REFERENCE_ID",
                 "R2_ACCOUNT_ID","R2_ACCESS_KEY_ID","R2_SECRET_ACCESS_KEY","R2_BUCKET"):
        result["segredos_apenas_presenca"][name]=bool(os.environ.get(name))
    if result["ferramentas"]["ffprobe"]:
        for name in JINGLES:
            if result["vinhetas"][name]["presente"]:
                cp=subprocess.run(["ffprobe","-v","error","-select_streams","a:0",
                    "-show_entries","stream=codec_name,sample_rate,channels",
                    "-of","json",name],capture_output=True,text=True,timeout=20)
                if cp.returncode:
                    result["bloqueios"].append("Áudio inválido: "+name)
                else:
                    streams=json.loads(cp.stdout).get("streams",[])
                    if not streams or streams[0].get("codec_name")!="mp3":
                        result["bloqueios"].append("Formato inválido: "+name)
                    else:
                        result["vinhetas"][name]["audio"]=streams[0]
    result["apto_para_novos_testes"]=not result["bloqueios"]
    # Nunca mostrar o valor de uma credencial, mesmo em erros.
    output=json.dumps(result,ensure_ascii=False,indent=2)
    print(output)
    if args.json:
        p=Path(args.json);p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(output+"\n",encoding="utf-8")
    return 0 if not result["bloqueios"] else 2
if __name__=="__main__":
    sys.exit(main())
