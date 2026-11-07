# Notícias, com Ricky Sousa — estado de implementação (7 novembro 2026)

## Objetivo aprovado
Emissão dominical às **12h00 Toronto** no RadioDJ, de preferência 15–20 minutos, máximo absoluto 30 minutos. Voz PT-PT séria. Ordem: abertura, internacionais (2), Portugal (2–3), vinheta desporto, desporto Canadá (1), futebol Portugal (3), vinheta meteorologia, previsão domingo e segunda para Toronto e depois Lisboa, Porto e Faro, fecho. A identificação em antena é **«Notícias, com Ricky Sousa»**.

## O que foi observado e testado
- **Voz Fish:** ensaio com 15 segmentos, 1.823 palavras, ~10 min 19 s, montagem MP3 concluída com FFmpeg. É texto experimental e não é um jornal factual.
- **OpenAI API:** teste real `rascunho_ia` em 7/11/2026, 24.902 tokens de entrada, 2.111 de saída, duas pesquisas web. O rascunho foi gerado, mas demasiado curto para emitir. Confirmar custo efetivo no painel OpenAI.
- **Vinhetas:** `intro-noticias.mp3`, `vinheta-desporto.mp3`, `vinheta-meteorologia.mp3` confirmados na **raiz do repositório**.
- **Montagem:** o script normaliza MP3 mono/estéreo a WAV 48 kHz e só depois concatena. Existe relato de teste técnico curto; não é um teste completo com notícias verificadas.
- **GitHub Secrets:** screenshots do proprietário mostraram `OPENAI_API_KEY`, `FISH_AUDIO_API_KEY` e `FISH_VOICE_REFERENCE_ID` criados. Valores nunca devem aparecer em código ou mensagens.
- **Sem emissão:** nenhum evento do RadioDJ criado ou modificado; não há confirmação de transferência R2 nem de receção no Windows.

## Preparado no código, ainda não validado ponta a ponta
- `scripts/velvetverse_noticias_pesquisa.py`: recolha RSS RTP/CBC e previsão Open-Meteo; datas de domingo/segunda agora baseadas em Toronto para as quatro cidades.
- `scripts/velvetverse_noticias_producao.py`: produção de rascunho OpenAI, previsão estruturada, relatório de extensão/quantidades, bloqueio de notícia não aprovada, montagem de voz Fish e vinhetas.
- `scripts/velvetverse_noticias_revisao.py`: caderno de revisão por fontes; **não aprova automaticamente**.
- `scripts/velvetverse_noticias_preflight.py`: diagnóstico local sem APIs nem despesas, apenas presença de credenciais e validação de vinhetas.
- `scripts/velvetverse_noticias_transferencia.py`: transferência para/do R2 **privado**, com manifesto e SHA256; modo receção destina-se só a staging.
- `radio-pc/diagnostico-noticias.ps1`: diagnóstico de leitura do Windows, não altera RadioDJ.
- `radio-pc/receber-noticias-teste.bat`: receção manual para `C:\VelvetVerseNoticias\Staging` **se** credenciais R2 estiverem disponíveis.
- `.github/workflows/velvetverse-noticias-producao-piloto.yml`: piloto manual; chamadas pagas agora exigem autorização explícita, opção desmarcada por defeito; R2 desligado por defeito.
- `.github/workflows/velvetverse-noticias-ci.yml`: validações offline em commits; testes de CI ainda devem ser confirmados em GitHub Actions após as últimas alterações.

## Três obstáculos reais para emissão autónoma
1. **Editorial:** roteiro completo, factos/referências/licenças verificados por uma pessoa e edição aprovada. Não existe revisão factual independente totalmente automática fiável. Não transformar a indicação do modelo em aprovação.
2. **Transporte e receção:** configurar R2 privado (credenciais ainda não confirmadas), receber no computador do RadioDJ e testar integridade.
3. **RadioDJ:** verificar menus da versão instalada, escolher e testar `File By Date` ou `Variable Duration File`, preparar evento de domingo 12h00 e garantir que uma edição ausente deixa a rotação normal intacta. Testar fora de antena antes de ativar.

## Regras de segurança
- Não voltar a executar testes pagos repetidamente. O GitHub exige confirmação explícita para etapas pagas.
- Não escrever chaves em GitHub público, screenshots, logs nem mensagens; só GitHub Secrets ou armazenamento Windows apropriado.
- Não importar diretamente faixas não aprovadas, não editar MariaDB por scripts e não substituir ficheiros em utilização.
- Ficheiro em staging **não é autorizacão de emissão**. Sem edição aprovada, a música continua.
- Verificar duração real e consistência de áudio antes de autorizar a estreia.

## Próximo contacto no PC da rádio
Executar apenas o diagnóstico de leitura `radio-pc/diagnostico-noticias.ps1` e observar os eventos atuais do RadioDJ. **Não agendar ainda a estreia.** Consultar [plano de entrega ao RadioDJ](noticias-radioDJ-entrega-segura.md).

## Pasta Windows definitiva
A receção do jornal fica isolada em `C:\VelvetVerseNoticias\Staging` no computador da rádio. Não utilizar `C:\RadioWeb` para os MP3 do jornal. O script de receção Windows e o diagnóstico foram atualizados, mas a pasta ainda precisa de ser criada no PC; nenhuma tarefa foi ativada.
