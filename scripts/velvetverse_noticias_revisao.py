#!/usr/bin/env python3
"""Prepara relatório de revisão do rascunho IA. Nunca aprova notícias automaticamente."""
import json
import sys
from pathlib import Path

P=Path("noticias-teste")
SRC=P/"rascunho-ia.json"
ORDER=(
    ("internacional","NOTÍCIAS INTERNACIONAIS"),
    ("portugal","NOTÍCIAS DE PORTUGAL"),
    ("desporto_canada","DESPORTO DO CANADÁ"),
    ("futebol_portugal","FUTEBOL PORTUGUÊS"),
    ("meteorologia_canada","METEOROLOGIA DO CANADÁ"),
    ("meteorologia_portugal","METEOROLOGIA DE PORTUGAL"),
)
def main():
    if not SRC.exists():
        raise SystemExit("Sem rascunho: execute primeiro rascunho_ia.")
    draft=json.loads(SRC.read_text(encoding="utf-8"))
    lines=[
        "# VelvetVerse Notícias — Caderno de revisão editorial",
        f"**Edição:** {draft.get('edicao','por definir')} · **Estado:** NÃO EMITIR",
        "",
        "Este documento exige leitura e confirmação manual nas fontes originais.",
        "O RSS, a pesquisa web e o texto gerado por IA não constituem aprovação.",
        "Não copiar reportagens de terceiros nem emitir resumos sem verificar direitos.",
        "",
        "## Abertura (rascunho)","",draft.get("abertura",""),""
    ]
    sections=draft.get("secoes",{})
    for key,title in ORDER:
        lines += ["## "+title,""]
        if key=="desporto_canada":lines += ["**Separador desportivo antes desta secção.**",""]
        if key=="meteorologia_canada":lines += ["**Separador meteorológico antes desta secção.**",""]
        items=sections.get(key,[])
        if not items: lines+=["**SEM INFORMAÇÃO VALIDADA — NÃO EMITIR**",""]
        for n,x in enumerate(items,1):
            lines += [
                f"### Peça {n} — NÃO VERIFICADA",
                "",
                x.get("texto","(Sem texto; é necessária pesquisa adicional.)"),
                "",
                "**Fontes propostas:**",
                *["- "+str(u) for u in x.get("fontes",[])],
                "",
                "**Observações:** "+str(x.get("observacoes","")),
                "",
                "- [ ] Factos, data, fontes originais e traduções confirmados",
                "- [ ] Sem citações reproduzidas indevidamente; direitos revistos",
                "- [ ] Texto atual para domingo às 12h00 Toronto",
                ""
            ]
    lines+=["## Fecho",draft.get("fecho",""),"",
       "## Lista final de verificação",
       "- [ ] Internacional 2, Portugal 2–3, desporto Canadá 1, futebol Portugal 3",
       "- [ ] Meteorologia para domingo e segunda, Toronto e 3 cidades portuguesas",
       "- [ ] Notícias atualizadas e sem duplicados; resultados desportivos confirmados",
       "- [ ] Texto integral em português de Portugal; tom profissional",
       "- [ ] Locução entre 15 e 20 min desejáveis; 30 min é limite absoluto",
       "- [ ] Aprovação explícita de um editor identificado antes de criar ficheiro aprovado",
       "- [ ] Reescuta final do MP3 antes de qualquer agendamento",
       "",
       "**IMPORTANTE:** nenhum botão deste caderno cria autorização de transmissão."
    ]
    (P/"caderno-revisao.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("Caderno editorial criado; notícias não aprovadas nem emitidas.")
if __name__=="__main__":
    main()
