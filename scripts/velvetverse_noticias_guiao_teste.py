#!/usr/bin/env python3
"""Gera um GUIAO DE ENSAIO, sem noticiário factual e sem qualquer emissão.
Só a meteorologia é redigida a partir dos valores estruturados disponíveis.
"""
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo

BASE=Path("noticias-teste")
record=json.loads((BASE/"pesquisa.json").read_text(encoding="utf-8"))
sections={x["secao"]:x["dados"] for x in record.get("ordem_editorial_candidatos", [])}
weather=record.get("meteorologia",{})
now=dt.datetime.fromisoformat(record["gerado_em"]).astimezone(ZoneInfo("America/Toronto"))
sunday=now.date()+dt.timedelta(days=(6-now.weekday())%7)
monday=sunday+dt.timedelta(days=1)
def numbers(v):
    return str(round(v))
def weather_name(code):
    if code in (0,): return "céu limpo"
    if code in (1,2,3): return "céu pouco nublado a muito nublado"
    if code in (45,48): return "nevoeiro"
    if code in (51,53,55,56,57): return "possibilidade de chuvisco"
    if code in (61,63,65,66,67,80,81,82): return "possibilidade de chuva"
    if code in (71,73,75,77,85,86): return "possibilidade de neve"
    if code in (95,96,99): return "possibilidade de trovoada"
    return "condições variáveis"
def daily(city):
    data={x["data"]:x for x in weather.get(city,[])}
    if not all(d.isoformat() in data for d in (sunday,monday)):
        return None
    return data
def say(city):
    data=daily(city)
    if data is None: return f"[PREVISÃO INDISPONÍVEL: {city}; NÃO EMITIR]"
    parts=[]
    for label,date in (("domingo",sunday),("segunda-feira",monday)):
        x=data[date.isoformat()]
        parts.append(f"Para {city}, {label}: {weather_name(x['codigo_tempo'])}, "
                     f"mínima de {numbers(x['min_c'])} graus e máxima de {numbers(x['max_c'])} graus. "
                     f"Probabilidade máxima diária de precipitação: {numbers(x['prob_chuva_pct'])} por cento.")
    return "\n\n".join(parts)
def candidates(name,n):
    data=sections.get(name,[])
    if not data: return "[SEM CANDIDATOS; NÃO EMITIR]\n"
    return "\n".join(f"- {x['titulo']} | {x['data_publicacao']} | {x['url']} | [VERIFICAR FACTOS E LICENÇA]"
                     for x in data[:n])
text=[
"# VELVETVERSE NOTÍCIAS — GUIÃO DE ENSAIO",
"",
"ESTADO: INCOMPLETO — NÃO LOCUTAR, NÃO PUBLICAR, NÃO EMITIR.",
f"Data-alvo: domingo, {sunday.strftime('%d/%m/%Y')}, 12h00 (Toronto). Janela máxima até 12h30.",
"",
"## 1. ABERTURA (texto de demonstração)",
"Boa tarde. Está a ouvir a VelvetVerse Radio. Este é o VelvetVerse Notícias, com os principais acontecimentos de Portugal e do mundo, o desporto e a meteorologia.",
"",
"## 2. NOTÍCIAS INTERNACIONAIS (selecionar 2; títulos por verificar)",
candidates("noticias_internacionais",7),"",
"## 3. NOTÍCIAS DE PORTUGAL (selecionar 2 ou 3; títulos por verificar)",
candidates("noticias_portugal",9),"",
"## SEPARADOR SONORO — DESPORTO",
"[INSERIR VINHETA DE DESPORTO APROVADA]","",
"## 4. DESPORTO DO CANADÁ (selecionar 1; traduzir do inglês e verificar)",
candidates("desporto_canada",7),"",
"## 5. FUTEBOL PORTUGUÊS (selecionar 3; verificar resultados e evitar outras modalidades)",
candidates("futebol_portugal",10),"",
"## SEPARADOR SONORO — METEOROLOGIA",
"[INSERIR VINHETA DE METEOROLOGIA APROVADA]","",
"## 6. METEOROLOGIA DO CANADÁ (texto de demonstração, fonte Open-Meteo)",
say("Toronto"),"",
"## 7. METEOROLOGIA DE PORTUGAL (texto de demonstração, fonte Open-Meteo)",
say("Lisboa"),"",say("Porto"),"",say("Faro"),"",
"## 8. FECHO (texto de demonstração)",
"Este foi o VelvetVerse Notícias. A informação continua a ser acompanhada nas fontes identificadas. Prossegue o Alma Portuguesa, na VelvetVerse Radio.",
"",
"## CONTROLOS OBRIGATÓRIOS ANTES DE EMISSÃO",
"- Notícias: ler fontes originais, verificar factos, horas, resultados, versões atualizadas e permissões de reutilização.",
"- Escolher os melhores temas, não apenas os primeiros do feed; eliminar duplicações do mesmo acontecimento.",
"- Reescrever em PT-PT com linguagem neutra, sem reproduzir textos protegidos.",
"- Meteorologia: atualizar no domingo, confirmar previsões e condições de uso e atribuição da fonte.",
"- Verificar duração (idealmente 15–20 min, nunca mais de 30), audição final e ausência de texto entre parênteses retos.",
"- Nunca gerar MP3 público nem acionar RadioDJ a partir deste guião de ensaio.",
]
(BASE/"guiao-ensaio.md").write_text("\n".join(text)+"\n",encoding="utf-8")
print(f"Guião de ensaio gerado para {sunday.isoformat()}, sem voz nem emissão.")
