#!/usr/bin/env python3
"""Piloto: rascunho OpenAI opcional e TTS Fish Audio somente com guiao aprovado.
Nunca publica MP3 nem altera RadioDJ.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

OUT=Path("noticias-teste")
SECTIONS=("internacional","portugal","desporto_canada","futebol_portugal","meteorologia_canada","meteorologia_portugal")
VINHETAS={"abertura":"intro-noticias.mp3","desporto":"vinheta-desporto.mp3","meteorologia":"vinheta-meteorologia.mp3"}
VINHETAS_DIR=Path(os.getenv("VV_VINHETAS_DIR","."))
def target_date():
    today=dt.datetime.now(ZoneInfo("America/Toronto")).date()
    return (today+dt.timedelta(days=(6-today.weekday())%7)).isoformat()
def post_json(url,payload,key,headers=None):
    req=urllib.request.Request(url,method="POST",data=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json",**(headers or {})})
    with urllib.request.urlopen(req,timeout=300) as r:
        return r.read()
def draft():
    key=os.getenv("OPENAI_API_KEY")
    model=os.getenv("OPENAI_MODEL") or "gpt-6.1-terra"
    if not key:
        raise ValueError("Falta OPENAI_API_KEY; nenhuma chamada paga realizada.")
    raw=json.loads((OUT/"pesquisa.json").read_text(encoding="utf-8"))
    sample={x["secao"]:x["dados"][:8] for x in raw["ordem_editorial_candidatos"] if x["secao"] in
        ("noticias_internacionais","noticias_portugal","desporto_canada","futebol_portugal")}
    prompt=("Cria RASCUNHO editorial para rádio em português europeu, com pesquisa web e factos atribuídos. "
        "O apresentador oficial é Ricky Sousa (não confundir com o nome da voz sintética). "
        "A abertura deve identificar expressamente: Notícias, com Ricky Sousa. Não mencionar o nome da estação na abertura. "
        "Não copies notícias. Nunca inventes detalhes ou resultados. Se sem confirmação deixa secção vazia. "
        "Estrutura JSON simples: edicao (data YYYY-MM-DD), estado (RASCUNHO), abertura (str), fecho (str), "
        "secoes (objeto: internacional, portugal, desporto_canada, futebol_portugal, meteorologia_canada, "
        "meteorologia_portugal; cada uma lista de objetos com texto, fontes (URLs HTTPS), confirmado (sempre false), "
        "observacoes). Ordem: 2 notícias internacionais, 2-3 Portugal, 1 desporto Canadá, 3 futebol português, "
        "meteorologia Toronto depois Lisboa, Porto, Faro. Meteorologia deve ser atualizada no domingo. "
        "Nunca marques notícia como confirmada. Data do domingo: "+target_date()+". "
        "Dados de pesquisa e previsão: "+json.dumps({"noticias":sample,"meteorologia":raw["meteorologia"]},ensure_ascii=False))
    payload={"model":model,"tools":[{"type":"web_search"}],"input":prompt,"max_output_tokens":6500}
    response=json.loads(post_json("https://api.openai.com/v1/responses",payload,key))
    # Registar consumo reportado pela API, sem inventar preço do modelo nem de pesquisa.
    usage=response.get("usage",{})
    searches=sum(1 for item in response.get("output",[]) if item.get("type") in ("web_search_call","web_search"))
    costs={"edicao":target_date(),"modelo":model,"ferramenta_pesquisa":"web_search",
           "pesquisas_observadas":searches,"tokens_entrada":usage.get("input_tokens"),
           "tokens_saida":usage.get("output_tokens"),
           "tokens_total":usage.get("total_tokens"),
           "usd_faturados":"CONSULTAR PAINEL OFICIAL: sem tarifário verificado pelo script",
           "estado":"MÉTRICAS DE CONSUMO; NÃO APROVA EMISSÃO"}
    (OUT/"consumo-redacao.json").write_text(json.dumps(costs,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("METRICAS REDACAO:",json.dumps(costs,ensure_ascii=False),flush=True)
    text="\n".join(part.get("text","") for item in response.get("output",[])
                     if item.get("type")=="message" for part in item.get("content",[])
                     if part.get("type")=="output_text").strip()
    text=re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$","",text).strip()
    data=json.loads(text)
    if data.get("estado")!="RASCUNHO" or data.get("edicao")!=target_date() or set(data.get("secoes",{}))!=set(SECTIONS):
        raise ValueError("Formato de rascunho inesperado.")
    for name in SECTIONS:
        for item in data["secoes"][name]:
            if item.get("confirmado") is not False: raise ValueError("O modelo tentou declarar factos aprovados.")
    (OUT/"rascunho-ia.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Rascunho criado: não está aprovado e nunca será emitido.")
def validate(data):
    if data.get("edicao")!=target_date() or data.get("estado")!="APROVADO_POR_EDITOR":
        raise ValueError("Guiao não aprovado para o domingo correspondente.")
    if not data.get("aprovado_por") or not data.get("aprovado_em"):raise ValueError("Aprovação sem identificação e data.")
    if set(data.get("secoes",{}))!=set(SECTIONS):raise ValueError("Secções incompletas.")
    if "notícias, com ricky sousa" not in data.get("abertura","").casefold():
        raise ValueError("A abertura deve incluir: Notícias, com Ricky Sousa.")
    parts=["__VV_ABERTURA__",data.get("abertura","")]
    for name in SECTIONS:
        if name=="desporto_canada":
            parts.append("__VV_DESPORTO__")
        if name=="meteorologia_canada":
            parts.append("__VV_METEOROLOGIA__")
        items=data["secoes"][name]
        if not items:raise ValueError("Sem notícias: "+name)
        for x in items:
            if x.get("confirmado") is not True:raise ValueError("Por confirmar: "+name)
            if not x.get("fontes") or not all(u.startswith("https://") for u in x["fontes"]):
                raise ValueError("Fonte em falta: "+name)
            t=x.get("texto","")
            if len(t)<60:raise ValueError("Texto incompleto: "+name)
            parts.append(t)
    parts.append(data.get("fecho",""))
    text="\n\n".join(x for x in parts if not x.startswith("__VV_"))
    if any(x in text.upper() for x in ("NÃO EMITIR","NÃO LOCUTAR","[VERIFICAR","[INSERIR","TODO")) or "[" in text or "]" in text:
        raise ValueError("Marcadores de trabalho presentes.")
    # Contagem editorial mínima, para evitar um jornal com notícias em falta.
    expected={"internacional":2,"portugal":2,"desporto_canada":1,"futebol_portugal":3,
              "meteorologia_canada":1,"meteorologia_portugal":3}
    for name,count in expected.items():
        if len(data["secoes"][name])<count:
            raise ValueError("Quantidade insuficiente para "+name+": esperado "+str(count))
    # A previsão só é válida quando cobre o domingo atual e a segunda-feira.
    # A verificação de factos, incluindo atualizações de última hora, continua manual.
    if len(text.split())<150 or len(text.split())>3400:
        raise ValueError("Duração de locução potencialmente inadequada.")
    return parts
def render():
    source=os.environ.get("VV_APPROVED_SCRIPT")
    if not source:raise ValueError("VV_APPROVED_SCRIPT deve indicar um ficheiro autorizado.")
    data=json.loads(Path(source).read_text(encoding="utf-8"))
    paragraphs=validate(data)
    key=os.getenv("FISH_AUDIO_API_KEY")
    voice=os.getenv("FISH_VOICE_REFERENCE_ID")
    model=os.getenv("FISH_TTS_MODEL") or "s2.1-pro-free"
    if not key or not voice:raise ValueError("Faltam credenciais da API Fish Audio ou referência da voz.")
    # Confirmar todas as vinhetas ANTES de chamar uma API que consome créditos.
    jingles={}
    for vinheta_id,filename in VINHETAS.items():
        j=VINHETAS_DIR/filename
        if not j.is_file() or j.stat().st_size<1000:
            raise ValueError("Vinheta obrigatória em falta: "+str(j))
        jingles["__VV_"+vinheta_id.upper()+"__"]=j.resolve()
    directory=OUT/"audio-parts"
    directory.mkdir(parents=True,exist_ok=True)
    files=[]
    for i,para in enumerate(paragraphs):
        if para in jingles:
            files.append(jingles[para])
            continue
        if len(para.encode("utf-8"))>3000:raise ValueError("Parágrafo demasiado longo para API.")
        audio=post_json("https://api.fish.audio/v1/tts",
           {"text":para,"reference_id":voice,"format":"mp3"},key,{"model":model})
        if not (audio.startswith(b"ID3") or (len(audio)>2 and audio[0]==255 and audio[1]&224==224)):
            raise ValueError("A API não devolveu MP3 válido.")
        p=directory/("segmento-%03d.mp3"%i)
        p.write_bytes(audio);files.append(p)
    # Convert MP3s to matching stereo 48kHz WAV before concatenating.
    # This protects Suno 48kHz stereo vs Fish 44.1kHz mono transitions.
    normalized=directory/"normalizados"
    normalized.mkdir(parents=True,exist_ok=True)
    wavefiles=[]
    for i,p in enumerate(files):
        wav=normalized/("audio-%03d.wav"%i)
        subprocess.run(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
            "-i",str(p),"-vn","-ac","2","-ar","48000",
            "-c:a","pcm_s16le",str(wav)],check=True)
        wavefiles.append(wav)
    manifest=directory/"concat.txt"
    manifest.write_text("\n".join("file '"+p.resolve().as_posix()+"'" for p in wavefiles)+"\n",encoding="utf-8")
    dest=OUT/("velvetverse-noticias-"+data["edicao"]+"-ENSAIO.mp3")
    subprocess.run(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
        "-f","concat","-safe","0","-i",str(manifest),
        "-af","loudnorm=I=-16:TP=-1.5:LRA=11",
        "-codec:a","libmp3lame","-b:a","192k",str(dest)],check=True)
    secs=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(dest)]).strip())
    if secs>1800 or secs<60:
        dest.unlink(missing_ok=True)
        raise ValueError("Áudio excedeu 30 minutos ou ficou demasiado curto.")
    print("ENSAIO PRIVADO CRIADO:",dest,"duração",round(secs),"segundos. SEM ENTREGA AO RADIODJ.")
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=("draft","validate","render"))
    a=parser.parse_args()
    try:
        if a.action=="draft":draft()
        elif a.action=="render":render()
        else:
            p=os.getenv("VV_APPROVED_SCRIPT")
            if not p:raise ValueError("Indicar VV_APPROVED_SCRIPT")
            validate(json.loads(Path(p).read_text(encoding="utf-8")))
            print("Estrutura aprovada passou validação automática; requer revisão da locução.")
    except Exception as e:
        print("BLOQUEADO:",e,file=sys.stderr)
        sys.exit(2)
