#!/usr/bin/env python3
"""Validação defensiva de um guião experimental: NÃO publica nem produz áudio."""
from pathlib import Path
import json, re

BASE=Path("noticias-teste")
p=BASE/"guiao-ensaio.md"
text=p.read_text(encoding="utf-8") if p.exists() else ""
labels=["NOTÍCIAS INTERNACIONAIS","NOTÍCIAS DE PORTUGAL","DESPORTO DO CANADÁ","FUTEBOL PORTUGUÊS","METEOROLOGIA DO CANADÁ","METEOROLOGIA DE PORTUGAL"]
missing=[label for label in labels if label not in text]
reasons=[]
if missing: reasons.append("Secções em falta: "+", ".join(missing))
for term in ("NÃO EMITIR","NÃO LOCUTAR","[VERIFICAR","[INSERIR","[SEM CANDIDATOS","[PREVISÃO INDISPONÍVEL"):
    if term in text: reasons.append(f"Marcador de bloqueio presente: {term}")
if "VERIFICAR FACTOS E LICENÇA" in text: reasons.append("Notícias ainda sem verificação editorial")
if not text: reasons.append("Ficheiro do guião inexistente ou vazio")
status={"estado":"BLOQUEADO" if reasons else "APARENTA COMPLETO - AINDA EXIGE REVISÃO HUMANA",
        "razoes":reasons,
        "nota":"Este validador nunca autoriza emissão automática; só deteta alguns riscos."}
(BASE/"validacao.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("VALIDAÇÃO EDITORIAL (SEM EMISSÃO):",status["estado"])
for reason in reasons: print(" -",reason)
