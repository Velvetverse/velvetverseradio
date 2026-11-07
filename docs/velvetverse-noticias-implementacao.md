# VelvetVerse Notícias — implementação e limites (6 nov 2026)

## Estado
**PILOTO MANUAL, SEM EMISSÃO, SEM PUBLICAÇÃO.** O GitHub Actions recolhe RTP e CBC (metadados RSS), produz previsão Open-Meteo e relatório editorial. Novo workflow opcional separado gera rascunho por IA com pesquisa web ou MP3 de ensaio a partir de um guião aprovado; pode opcionalmente copiar o MP3 para Cloudflare R2 privado. Não há cron automático do noticiário, nem eventos RadioDJ, nem publicação em R2.

## Identidade em antena
**Apresentador do VelvetVerse Notícias: Ricky Sousa.** A abertura deve dizer «Notícias, com Ricky Sousa», sem repetir o nome da rádio. A voz de síntese atualmente testada no Fish Audio é uma implementação técnica e não altera o nome do apresentador.\n\n## Linha editorial aprovada
Domingo, às 12h00 de Toronto, janela até 12h30 (não duração obrigatória). Linguagem PT-PT, tom profissional. Ordem: abertura; 2 internacionais; 2 a 3 de Portugal; separador; 1 desporto Canadá; 3 futebol português; separador; meteorologia Toronto domingo e segunda-feira; meteorologia Lisboa, Porto e Faro domingo e segunda-feira; fecho. Tempo ideal 15-20 min, sem forçar extensão.

## Ficheiros e ferramentas
- scripts/velvetverse_noticias_pesquisa.py — recolha RSS e meteorologia (apenas pesquisa)
- scripts/velvetverse_noticias_auditoria.py — sinaliza idade e semelhança dos títulos, não verifica factos
- scripts/velvetverse_noticias_guiao_teste.py — rascunho determinístico incompleto
- scripts/velvetverse_noticias_validar.py — bloqueia marcadores de ensaio
- scripts/velvetverse_noticias_producao.py — nova fase opcional; geração de rascunho com OpenAI Responses/web_search; validação de guião aprovado; TTS Fish e FFmpeg no modo privado
- .github/workflows/velvetverse-noticias-teste.yml — ensaio sem custos de APIs, manual
- .github/workflows/velvetverse-noticias-producao-piloto.yml — **novo**, manual: rascunho_ia OU audio_aprovado; sem horário, sem deploy

## Segredos e variáveis (não configurados automaticamente)
Em Settings > Secrets and variables > Actions do repositório:
- Secret OPENAI_API_KEY: conta API OpenAI separada do ChatGPT Plus (uso de modelos e web search cobrado).
- Variable VV_OPENAI_MODEL: modelo com web_search autorizado (validar preço e compatibilidade antes de ativar).
- Secret FISH_AUDIO_API_KEY: chave Fish Audio recriada após exposição; nunca colocar no código nem no chat.
- Secret FISH_VOICE_REFERENCE_ID: ID de voz autorizada no Fish Audio (não é nome exibido).
- Variable VV_FISH_MODEL: modelo de voz escolhido; se em branco, s2.1-pro-free, sujeito a disponibilidade e condições de 2026.
Não introduzir segredos no repositório público. A chave não permite por si só aceder ao PC do RadioDJ.

## Fluxo editorial
1. Gerar pesquisa/meteorologia atualizada.
2. Opcional: modo rascunho_ia usa OPENAI_API_KEY e web_search para criar noticias-teste/rascunho-ia.json.
3. Rascunho continua bloqueado: toda a informação deve ser revista na origem, especialmente afirmações políticas, factos internacionais, resultados, traduções e direitos de utilização.
4. Só pode ser criado noticias-aprovado.json por processo editorial externo controlado, com estado APROVADO_POR_EDITOR, edicao correspondente ao domingo, aprovado_por, aprovado_em, abertura, fecho e secoes com entradas texto, fontes e confirmado=true. Esse ficheiro não é criado pelo workflow nem pelo modelo.
5. Modo audio_aprovado verifica estrutura e datas, invoca Fish TTS, junta segmentos em MP3 normalizado com FFmpeg e mede duração real. MP3 **fica apenas como artefacto temporário privado**, nunca é transmitido.
6. Adicionar no futuro vinhetas musicais aprovadas; atualmente existem transições faladas entre blocos, não separadores musicais acabados.

## Transporte R2 para Windows: preparado, não configurado
- scripts/velvetverse_noticias_transferencia.py usa boto3 para enviar um MP3 aprovado para o Cloudflare R2 PRIVADO, com manifesto e SHA256. O upload é opcional e está desligado por defeito no novo workflow.
- Segredos GitHub adicionais necessários: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY e R2_BUCKET. A política R2 deve restringir permissões à pasta privada de staging; nunca utilizar bucket público.
- Num PC Windows da rádio, depois de configurar Python e boto3 e as mesmas credenciais R2 numa forma segura, executar: python scripts/velvetverse_noticias_transferencia.py receive --destination "C:\\RadioWeb\\Noticias\\Staging". Recebe o MP3 do próximo domingo, valida o SHA256 e coloca-o na pasta temporária; não mexe no RadioDJ.
- O agente receptor ainda NÃO está agendado e o PC ainda NÃO foi configurado. Este mecanismo não é o evento de emissão.

## Entrega ao RadioDJ: ainda NÃO implementada
Para completar 100% autónomo, precisamos definir armazenamento privado/Cloudflare R2, agente Windows autenticado que descarregue apenas a edição correta com checksum, modo seguro de carregar o MP3 na biblioteca RadioDJ, e evento agendado com fallback para a rotação normal. Validar com ensaio sem antena; não copiar diretamente ficheiros por cima dos já indexados nem editar MariaDB.

## Falhas seguras
- Qualquer dúvida editorial => NÃO PRODUZIR.
- Data, secção ou fontes não confirmadas => NÃO PRODUZIR.
- Chave, quota ou API em falta => NÃO PRODUZIR.
- Áudio >30 min ou incompleto => APAGAR e não enviar.
- Sem edição pronta às 12h00 => Alma Portuguesa continua normalmente.
- Ainda não existe aprovação editorial automática fiável: o código proíbe uma IA de atribuir a si mesma o estado aprovado.

## Custos e limitações
O GitHub Actions pode ter limites de minutos/armazenamento; APIs OpenAI/Fish podem cobrar independentemente das assinaturas web. Nada foi debitado por criar estes ficheiros, e o novo workflow não corre até ser acionado. Verificar licenças de notícias, voz e meteorologia antes da emissão pública.

## Estado de verificação
Os fluxos de pesquisa 1 a 7 foram executados com êxito. Os novos modos de IA/TTS/R2 foram **escritos, mas não executados**, por falta de chaves privadas e do guião aprovado. Um êxito de GitHub Actions não constitui verificação jornalística.


## Evolução técnica concluída após o ensaio completo
- O Fish Audio com a voz Beto e modelo gratuito gerou **15/15 segmentos**, que foram unidos com FFmpeg: **10,31 minutos**, 1.823 palavras, cerca de 14,8 MB. Este é um ensaio narrativo, **não um noticiário factual pronto para emissão**.
- Foi corrigida a ausência de FFmpeg no GitHub Actions e o teste seguinte concluiu-se com sucesso.
- O teste de voz gratuito reportou custo calculado US$0,00 para o modelo escolhido; confirmar custo efetivamente faturado na conta Fish Audio.
- O modo `rascunho_ia` agora regista `consumo-redacao.json` com modelo, tokens e chamadas de pesquisa reportados, para consulta e comparação com o extrato faturado. Este modo ainda não foi testado porque faltam a chave da API OpenAI e `VV_OPENAI_MODEL`.
- Foi incluído `caderno-revisao.md`, com o texto do rascunho, fontes propostas e lista editorial de validação. A presença de um caderno não significa aprovação.
- Os scripts de validação exigem secções e quantidades mínimas; não verificam sozinhos a verdade de cada notícia.
- A CI tem um ensaio offline do custo e da estrutura dos 15 segmentos; não depende de credenciais.

## Pendências intransponíveis sem intervenção autorizada
1. **Conta OpenAI API:** criar a chave e definir limite orçamental na consola da API; inserir em `OPENAI_API_KEY` como secret GitHub e escolher `VV_OPENAI_MODEL` como variável. ChatGPT Plus não dá automaticamente crédito API.
2. **Custos reais de redação:** uma execução `rascunho_ia` com a API e a pesquisa web necessárias. Medir tokens/pesquisas e confirmar faturação na consola; a estimativa de US$1–5/mês continua não verificada.
3. **Licenças e verificação editorial:** definir como confirmar factos recentes, contexto, duplicações, traduções e direitos das notícias antes de emissão. A IA não certifica independentemente o que escreveu.
4. **Vinhetas:** faltam os ficheiros de separadores desportivos e meteorológicos aprovados e a respetiva montagem, em vez de simples transições faladas.
5. **R2 e PC Windows:** configurar credenciais privadas, agente receptor e permissões, e testar a integração de uma edição de demonstração com o RadioDJ num ambiente sem antena.
6. **Agendamento real:** só criar o evento de domingo às 12h00 depois de comprovar as salvaguardas, o fallback musical e a duração absoluta de 30 minutos.

**Segurança:** Não pôr senhas, tokens ou chaves em páginas, prints ou mensagens. Não desativar avisos de malware do browser para descarregar artefactos.
