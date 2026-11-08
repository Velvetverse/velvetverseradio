#!/usr/bin/env python3
"""Transporte PRIVADO do piloto de notícias com Cloudflare R2 via API S3.
Comando upload: do GitHub runner para R2 privado; comando receive: PC rádio para pasta de staging.
Nunca altera biblioteca, base MariaDB, fila ou evento RadioDJ.
Dependência adicional: pip install boto3
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

def config():
    import boto3
    needed=("R2_ACCOUNT_ID","R2_ACCESS_KEY_ID","R2_SECRET_ACCESS_KEY","R2_BUCKET")
    for k in needed:
        if not os.getenv(k):raise RuntimeError("Falta configuração privada: "+k)
    endpoint="https://"+os.environ["R2_ACCOUNT_ID"]+".r2.cloudflarestorage.com"
    s3=boto3.client("s3",endpoint_url=endpoint,aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],region_name="auto")
    return s3,os.environ["R2_BUCKET"]
def sunday():
    try:
        day=dt.datetime.now(ZoneInfo("America/Toronto")).date()
    except __import__("zoneinfo").ZoneInfoNotFoundError:
        # Windows sem tzdata: computador da rádio usa Eastern Standard Time (Toronto).
        # Não usar este fallback noutros fusos horários.
        day=dt.datetime.now().date()
    return (day+dt.timedelta(days=(6-day.weekday())%7)).isoformat()
def hfile(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("action",choices=["upload","receive","test-receive"])
    ap.add_argument("--file",help="MP3 previamente aprovado a enviar")
    ap.add_argument("--destination",help="pasta local temporária (sem RadioDJ)")
    args=ap.parse_args()
    target=sunday()
    objbase="noticias/piloto/"+target
    s3,bucket=config()
    if args.action=="test-receive":
        if not args.destination:raise ValueError("--destination obrigatório")
        base=Path(args.destination)
        base.mkdir(parents=True,exist_ok=True)
        key="noticias/teste-tecnico/NAO-EMITIR-teste-silencio.mp3"
        dest=base/"NAO-EMITIR-teste-silencio.mp3"
        temp=base/"NAO-EMITIR-teste-silencio.download"
        temp.unlink(missing_ok=True)
        try:
            obj=s3.head_object(Bucket=bucket,Key=key)
            if obj.get("ContentLength",0)<100:
                raise RuntimeError("MP3 de teste inválido ou demasiado pequeno")
            s3.download_file(bucket,key,str(temp))
            if temp.stat().st_size != obj["ContentLength"]:
                raise RuntimeError("Transferência de teste incompleta")
            temp.replace(dest)
        finally:
            temp.unlink(missing_ok=True)
        print("SUCESSO: MP3 técnico descarregado:",dest)
        print("NAO EMITIR — nenhuma alteração feita no RadioDJ.")
        return
    if args.action=="upload":
        if not args.file:raise ValueError("--file obrigatório")
        p=Path(args.file)
        if not p.is_file() or p.suffix.lower()!=".mp3" or target not in p.name:
            raise ValueError("Ficheiro MP3 inexistente ou data da edição incorreta.")
        # MP3 já validado e aprovado pelo passo anterior.
        metadata={"edicao":target,"sha256":hfile(p),"tamanho":p.stat().st_size,
                  "estado":"PRIVADO_STAGING_NAO_EMITIR"}
        s3.upload_file(str(p),bucket,objbase+"/edicao.mp3",
            ExtraArgs={"ContentType":"audio/mpeg","Metadata":{"edicao":target,"sha256":metadata["sha256"]}})
        s3.put_object(Bucket=bucket,Key=objbase+"/manifest.json",
            Body=json.dumps(metadata).encode("utf-8"),ContentType="application/json")
        print("Áudio enviado para armazenamento R2 PRIVADO, sem alterar RadioDJ.")
    else:
        if not args.destination:raise ValueError("--destination obrigatório")
        base=Path(args.destination)
        base.mkdir(parents=True,exist_ok=True)
        manifest=json.loads(s3.get_object(Bucket=bucket,Key=objbase+"/manifest.json")["Body"].read())
        if manifest.get("edicao")!=target or manifest.get("estado")!="PRIVADO_STAGING_NAO_EMITIR":
            raise RuntimeError("Manifesto fora de data ou não autorizado.")
        dest=base/("vv-noticias-"+target+"-STAGING.mp3")
        # Idempotência: nao voltar a descarregar nem substituir ficheiro validado.
        if dest.is_file():
            if dest.stat().st_size==manifest["tamanho"] and hfile(dest)==manifest["sha256"]:
                print("Edição já recebida e verificada:",dest)
                print("SEM EMISSAO AUTOMATICA; ficheiro de staging inalterado.")
                return
            raise RuntimeError("Ja existe MP3 diferente em staging: revisao manual necessaria.")
        staged=base/("vv-noticias-"+target+".download")
        # Limpar apenas a transferencia temporaria, nunca apagar um MP3 existente.
        staged.unlink(missing_ok=True)
        try:
            s3.download_file(bucket,objbase+"/edicao.mp3",str(staged))
            if staged.stat().st_size!=manifest["tamanho"] or hfile(staged)!=manifest["sha256"]:
                raise RuntimeError("Integridade do áudio inválida.")
            staged.replace(dest)
        finally:
            staged.unlink(missing_ok=True)
        print("MP3 recebido e verificado:",dest)
        print("STAGING APENAS: ainda não está carregado no RadioDJ ou agendado para emissão.")
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("TRANSFERÊNCIA BLOQUEADA:",e,file=sys.stderr)
        sys.exit(2)
