# Notícias com Ricky Sousa — estado verificado (7 novembro 2026)

## Objetivo
Noticiário dominical às 12h00 de Toronto. Abertura «Notícias, com Ricky Sousa». Secções: internacionais, Portugal, desporto canadiano, futebol português, meteorologia para Toronto, Lisboa, Porto e Faro, fecho. Meta editorial 15–20 minutos.

## Componentes verificados em ensaios
- Ligação privada GitHub → R2: teste de autenticação com sucesso (GitHub run 42430247662).
- MP3 técnico silencioso enviado pelo GitHub para R2 (run 42435870714).
- Receção do MP3 técnico no Windows em `C:\VelvetVerseNoticias\Staging\Teste\NAO-EMITIR-teste-silencio.mp3`, confirmada por output do utilizador.
- A tarefa Windows «VelvetVerse Noticias - Rececao Staging» existe e foi confirmada como **Disabled**, para domingo 11h30.
- Credenciais de leitura guardadas em DPAPI para o utilizador Windows; antigo ficheiro de texto simples foi apagado pelo utilizador.
- Três vinhetas MP3 presentes na raiz do repositório.
- Preflight de pesquisa sem chamadas pagas: GitHub run 42436352419, pesquisa e auditoria executadas.

## Implementado no GitHub (sem afirmar execução completa)
- Pesquisa semanal aos domingos 08h15 Toronto (ajuste DST por duas janelas cron UTC e filtro por hora local).
- Seleção determinística de candidatos recentes, por secção, sem duplicados evidentes; gera alinhamento automático.
- Pipeline manual de redação por API OpenAI com ferramenta web_search e modelo explícito, **exige checkbox de autorização de custos**.
- Relatórios com fontes, data e alertas, não equivalentes a confirmação factual.
- Montagem de locução Fish Audio com três vinhetas, áudio normalizado por FFmpeg; exige guião editorial APROVADO_POR_EDITOR.
- Envio opcional de MP3 aprovado para R2 privado e receção em staging; **não** alteram RadioDJ.
- CI com testes offline de sintaxe, vinhetas, seleção e validação de guião.

## O que permanece bloqueado
1. **Não existe guião factual validado para emissão**; nenhum algoritmo de RSS ou IA confirma sozinho todas as afirmações. Jornal real não pode ser apresentado como verificado apenas por haver links.
2. Não há execução real validada da cadeia redação factual → voz Fish → vinhetas → MP3 final → R2, com texto aprovado. Esta cadeia pode usar APIs cobradas e exige autorização explícita.
3. Não há evento no RadioDJ para emitir as notícias às 12h; a tarefa Windows foi mantida desativada. O script só recebe MP3 privado em staging e não coloca qualquer áudio em emissão.
4. O MP3 técnico de silêncio serve apenas para teste e **nunca** para emitir.
5. O agendamento de pesquisa está configurado, mas a primeira execução automática após estas alterações ainda deve ser observada.

## Política de segurança e custo
- Nenhuma chamada paga foi efetuada durante estas alterações ao código.
- Falha de credenciais, notícias insuficientes, ausência de guião aprovado, vinheta inválida ou transferência incompleta deve bloquear a emissão e deixar a programação musical normal.
- Desativar qualquer tentativa de publicação automática sem verificação editorial satisfatória.
- As chaves não podem constar de ficheiros públicos, logs ou mensagens.
- O objetivo de operação sem seleção manual semanal permanece; a confirmação factual e a autorização de emissão são questões separadas, não mascaradas por automação.

## Acesso
- [Pesquisa automática](../.github/workflows/velvetverse-noticias-pesquisa-semanal.yml)
- [Produção piloto](../.github/workflows/velvetverse-noticias-producao-piloto.yml)
- [Recetor Windows](../radio-pc/receber-noticias-staging.ps1)

## Alterações posteriores — segurança e testes do pipeline
- Seleção de candidatos atualizada com pesquisa internacional RTP e CBC.
- Etapa `preflight_editorial.py` adicionada antes de qualquer tentativa paga de rascunho; confirma quantidades, HTTPS, data de edição, frescura da pesquisa (máximo 6 horas) e meteorologia de domingo/segunda.
- Novo teste offline de transporte completo com R2 simulado: manifesto privado, hash SHA256, receção idempotente e recusa de MP3 modificado.
- CI configurado para executar testes offline de seleção, preflight, transferência e verificação de proteção de custos, sem usar OpenAI/Fish.
- Estas alterações são commits de código, **não confirmação de execução em produção**. É necessário ver CI verde e ensaio real do jornal aprovado antes de transmissão.
- A configuração `VV_OPENAI_MODEL` permanece por verificar; modelo API não deve ser inventado.
- O agendador de receção Windows permanece desativado até haver edição válida e verificação no PC da rádio.

## Segurança reforçada
- Chamadas a OpenAI e Fish agora exigem também `VV_ALLOW_BILLABLE=yes` no próprio script, além da opção explícita de autorização no GitHub Actions. Chamar o Python diretamente não contorna o bloqueio.
- O gerador de rascunhos exige alinhamento presente, datado e válido, sem fallback para títulos RSS não filtrados; o preflight valida domingo e segunda e pesquisa com menos de seis horas.
- O pipeline não escolhe modelos API não verificados automaticamente; o modelo deve estar configurado pelo operador.
- Novo teste `tests/test_noticias_autorizacao.py` e CI ligado; resultado de execução dos testes ainda não foi consultado.
- Emissão RadioDJ e receção agendada continuam desativadas; nenhum jornal real foi emitido.
