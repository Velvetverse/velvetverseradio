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
    if os.getenv("VV_ALLOW_BILLABLE")!="yes":
        raise ValueError("Chamadas pagas bloqueadas: falta autorização explícita.")
    key=os.getenv("OPENAI_API_KEY")
    model=os.getenv("OPENAI_MODEL","").strip()
    if not key or not model:
        raise ValueError("Falta OPENAI_API_KEY ou OPENAI_MODEL; nenhuma chamada paga realizada.")
    raw=json.loads((OUT/"pesquisa.json").read_text(encoding="utf-8"))
    selected_path=OUT/"alinhamento-automatico.json"
    if not selected_path.is_file():
        raise ValueError("Alinhamento automático ausente; sem chamada paga.")
    from velvetverse_noticias_preflight_editorial import check as check_editorial
    selected=json.loads(selected_path.read_text(encoding="utf-8"))
    blocks=check_editorial(selected)
    if blocks:
        raise ValueError("Preflight bloqueou chamada paga: "+"; ".join(blocks))
    sample={k:v for k,v in selected["seccoes"].items()}
    quotas={"noticias_internacionais":2,"noticias_portugal":3,"desporto_canada":1,"futebol_portugal":3}
    for section,minimum in quotas.items():
        if len(sample.get(section,[]))<minimum:
            raise ValueError(f"Secção {section} sem informação suficiente: nenhuma chamada paga.")
    brief=(
        "És redator de notícias de rádio em PORTUGUÊS DE PORTUGAL (PT-PT). "
        "Elabora apenas um RASCUNHO, nunca uma edição aprovada. Emissão prevista domingo ao MEIO-DIA "
        "em Toronto. O apresentador é Ricky Sousa. Abertura obrigatória: 'Notícias, com Ricky Sousa.' "
        "Cumprimenta com 'Boa tarde', NUNCA com 'Boa noite'. "
        "Pesquisa e consulta, sempre que possível, as fontes originais dos NOVE assuntos candidatos. "
        "Não inventes pormenores, citações, resultados, cargos, datas ou factos para cumprir a extensão. "
        "Se uma notícia não tiver matéria verificável suficiente, escreve-a mais curta e assinala isso "
        "em observacoes; jamais enchas texto com avisos genéricos ou explicações de como se faz jornalismo. "
        "Não copies parágrafos de fontes. Não uses afirmações categóricas sem suporte. "
        "Para cada peça procura explicar O QUÊ, QUEM, ONDE, QUANDO, CONTEXTO, IMPACTO comprovável "
        "e EVENTUAIS INCERTEZAS, em linguagem natural pronta para locução, não frases telegráficas. "
        "Objetivo de redação, APENAS SE HOUVER FACTOS: cada internacional 280-330 palavras, "
        "cada Portugal 260-300 palavras, desporto Canadá 210-260 palavras, cada futebol Portugal "
        "225-270 palavras; abertura 55-80 palavras, fecho 45-65 palavras. "
        "Soma ideal da locução completa 2500-3000 palavras, nunca artificialmente alongada. "
        "Duas internacionais, três de Portugal, uma de desporto Canadá e três de futebol Portugal. "
        "A meteorologia será adicionada DO JSON ESTRUTURADO pelo nosso script: deixa as listas "
        "meteorologia_canada e meteorologia_portugal vazias na resposta. "
        "RESTITUI APENAS JSON VALIDO sem markdown: edicao (YYYY-MM-DD), estado ('RASCUNHO'), "
        "abertura (string), fecho (string), secoes (objeto com internacional, portugal, "
        "desporto_canada, futebol_portugal, meteorologia_canada, meteorologia_portugal; "
        "listas de objetos com texto (parágrafos de locução), fontes (URLs HTTPS relevantes), "
        "confirmado (sempre false), observacoes (limites de verificação)). "
        "Se encontrares factos contraditórios, explicita-os em observacoes e não resolvas por adivinhação. "
        "Data da edição: "+target_date()+". "
        "ALINHAMENTO DE CANDIDATOS: "+json.dumps(sample,ensure_ascii=False)+". "
        "PREVISÕES (só para contextualizar, serão montadas automaticamente): "
        +json.dumps(raw["meteorologia"],ensure_ascii=False)
    )
    prompt=brief
    payload={"model":model,"tools":[{"type":"web_search"}],"input":prompt,"max_output_tokens":11500}
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
    # Fill Sunday/Monday forecast from the structured weather API already collected.
    # Never ask the language model to guess a weather report.
    conditions={0:"céu limpo",1:"céu geralmente limpo",2:"céu parcialmente nublado",
        3:"céu encoberto",45:"nevoeiro",48:"nevoeiro gelado",51:"chuvisco fraco",
        53:"chuvisco moderado",55:"chuvisco intenso",61:"chuva fraca",
        63:"chuva moderada",65:"chuva forte",71:"neve fraca",73:"neve moderada",
        75:"neve forte",80:"aguaceiros fracos",81:"aguaceiros moderados",
        82:"aguaceiros fortes",95:"trovoada"}
    sunday=dt.date.fromisoformat(target_date())
    monday=sunday+dt.timedelta(days=1)
    pt_days={sunday.isoformat():"domingo",monday.isoformat():"segunda-feira"}
    def make_forecast(city):
        by_date={x["data"]:x for x in raw["meteorologia"].get(city,[])}
        if not all(day in by_date for day in pt_days):
            return None
        sentences=[]
        for date,dayname in pt_days.items():
            x=by_date[date]
            desc=conditions.get(x.get("codigo_tempo"),"condições meteorológicas variáveis")
            sentences.append(
                f"{'No' if dayname == 'domingo' else 'Na'} {dayname}, dia {dt.date.fromisoformat(date).day}, em {city}, "
                f"prevê-se {desc}, com temperaturas entre {x['min_c']} e {x['max_c']} graus "
                f"Celsius e probabilidade máxima de precipitação de {x['prob_chuva_pct']} por cento.")
        return {"texto":" ".join(sentences),
                "fontes":["https://open-meteo.com/"],
                "confirmado":False,
                "observacoes":"Previsão automática Open-Meteo, sujeita a alteração. Rever no domingo antes da emissão."}
    toronto=make_forecast("Toronto")
    data["secoes"]["meteorologia_canada"]=[toronto] if toronto else []
    data["secoes"]["meteorologia_portugal"]=[
        x for x in (make_forecast(city) for city in ("Lisboa","Porto","Faro")) if x]
    data["notas_automaticas"]=["Meteorologia criada por dados Open-Meteo, não pelo modelo.",
        "Previsões e notícias exigem verificação editorial no dia da emissão."]
    # Explicit report of editorial completeness: workflow success != broadcast approval.
    counts={name:len(data["secoes"][name]) for name in SECTIONS}
    section_words={name:sum(len(x.get("texto","").split()) for x in data["secoes"][name])
                   for name in SECTIONS}
    spoken_words=sum(section_words.values())+len(data.get("abertura","").split())+len(data.get("fecho","").split())
    word_count=spoken_words
    reasons=[]
    for name,min_count in (("internacional",2),("portugal",2),("desporto_canada",1),
                           ("futebol_portugal",3),("meteorologia_canada",1),("meteorologia_portugal",3)):
        if counts[name]<min_count:
            reasons.append(f"{name}: {counts[name]} de {min_count} peças mínimas")
    if word_count<2500:
        reasons.append(f"Locução com {word_count} palavras: insuficiente para 15-20 minutos.")
    for name,minimum in (("internacional",450),("portugal",600),("desporto_canada",170),
                         ("futebol_portugal",550)):
        if section_words[name]<minimum:
            reasons.append(f"{name}: apenas {section_words[name]} palavras, exigir maior profundidade documental.")
    if word_count>3400:
        reasons.append(f"Texto com {word_count} palavras: rever limite máximo de 30 min.")
    quality={"edicao":target_date(),"estado":"RASCUNHO — NÃO EMITIR",
             "palavras":word_count,"palavras_por_seccao":section_words,"quantidades":counts,
             "pronto_para_locucao":False,
             "motivos_de_revisao":reasons,
             "revisao_de_factos":"OBRIGATÓRIA mesmo que motivos_de_revisao esteja vazio"}
    (OUT/"avaliacao-redacao.json").write_text(
        json.dumps(quality,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("AVALIACAO EDITORIAL:",json.dumps(quality,ensure_ascii=False),flush=True)
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
    if len(text.split())<2400 or len(text.split())>3400:
        raise ValueError("Duração de locução potencialmente inadequada.")
    return parts
def render():
    if os.getenv("VV_ALLOW_BILLABLE")!="yes":
        raise ValueError("Chamadas pagas bloqueadas: falta autorização explícita.")
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
    # Dividir os textos por frases antes de gerar audio; nunca fazer pedido com mais de 3000 bytes.
    def split_for_tts(text,limit=2600):
        if len(text.encode("utf-8"))<=limit:return [text]
        sentences=re.split(r"(?<=[.!?;])\s+",text)
        chunks=[];current=""
        for sentence in sentences:
            if len(sentence.encode("utf-8"))>limit:
                raise ValueError("Frase demasiado longa para TTS; rever antes de gastar.")
            candidate=(current+" "+sentence).strip()
            if current and len(candidate.encode("utf-8"))>limit:
                chunks.append(current);current=sentence
            else:current=candidate
        if current:chunks.append(current)
        return chunks
    expanded=[]
    for para in paragraphs:
        expanded.extend([para] if para in jingles else split_for_tts(para))
    paragraphs=expanded
    for para in paragraphs:
        if para not in jingles and len(para.encode("utf-8"))>3000:
            raise ValueError("Segmento de voz demasiado longo para API Fish.")
    OUT.mkdir(parents=True,exist_ok=True)
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
    # Uma simulação offline com silêncio curto não equivale à duração exigida em antena.
    offline_test=os.getenv("VV_OFFLINE_AUDIO_TEST")=="yes"
    min_secs=60 if offline_test else 780
    max_secs=1800 if offline_test else 1380
    if secs>max_secs or secs<min_secs:
        dest.unlink(missing_ok=True)
        raise ValueError(f"Áudio com {round(secs)} segundos fora dos limites "
                         f"({min_secs}-{max_secs}). MP3 descartado; NÃO EMITIR.")
    print("ENSAIO PRIVADO CRIADO:",dest,"duração",round(secs),
          "segundos. SEM ENTREGA AO RADIODJ.")
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
