# Top 5 VelvetVerse — automatização segura

## Estado em 9 de novembro de 2026
- Página de teste: `top-5-velvetverse-teste.html`.
- Edição única: `top5-velvetverse-weekly.json`, independente do **Top 5 Latino**.
- Os cinco MP3 foram gerados localmente no PC do RadioDJ, na pasta `TOP5_EXCERTOS_30S`.
- A página não publica áudio enquanto `preview_permission_confirmed` for `false`.
- A votação do Top 5 VelvetVerse começa **desativada**, evitando misturar edições e votos existentes do Top 5 Latino.
- O ranking de 9/11 representa a ordem dos ficheiros do BAT, **não foi confirmado como ranking RCast**.

## Automatizado agora
O workflow `.github/workflows/top5-velvetverse-auditoria.yml` corre **todas as segundas-feiras** e também manualmente em GitHub Actions. Valida cinco posições únicas, edição, semana, configuração de votação, restrições de áudio e frescura da classificação. Quando estiver desatualizada ou provisória, a execução sinaliza erro e escreve os motivos no resumo do workflow. Não altera ficheiros, não altera o RadioDJ, não publica MP3 e não usa as credenciais do R2 de outro programa.

## Ainda requer ligação operacional antes de ativar publicação automática
1. **RCast**: descobrir uma fonte autenticada e estável (exportação CSV ou API) que devolva *reproduções por faixa e período*, com data/hora em Toronto. O RCast não foi ainda configurado como fonte verificável no repositório. Não é seguro inventar uma API, posições ou contagens.
2. **Biblioteca local**: a tarefa semanal deve correr no PC do RadioDJ com o acesso ao disco `D:`. GitHub Actions não tem acesso ao PC; o BAT V3 atual é uma seleção local, não uma integração RCast validada.
3. **R2**: confirmar bucket e URL público específicos de previews e configurar credenciais apenas para esse destino. As credenciais `R2_*` do piloto de notícias são de outro bucket e não devem ser reutilizadas cegamente.
4. **Direitos de reprodução no website**: obter a autorização pertinente para os excertos antes de publicar. Excertos de 30 segundos não são automaticamente livres de direitos.
5. **Publicação atómica**: após testes, carregar os cinco excertos e capas de uma edição em prefixo imutável, verificar acesso HTTPS a todos e só depois atualizar o JSON; permitir rollback da edição anterior.
6. **Supabase**: confirmar política por edição/limite de votos do Top 5 VelvetVerse, distinta da do Top 5 Latino, antes de ativar `voting_enabled`.

Não editar `index.html`, os workflows do Top 5 Latino, a fila do RadioDJ ou o SECaster enquanto estes passos estiverem pendentes.

## Módulo de importação instalado
- `scripts/importar_top5_velvetverse_csv.py` transforma um relatório CSV com **Título / Artista / Reproduções** num **candidato** `top5-velvetverse-candidato.json`.
- Reconhece cabeçalhos comuns em português e inglês, ordena por reproduções, verifica cinco músicas distintas e bloqueia empate no quinto lugar.
- Exemplo (com CSV de teste, não é preciso executar agora): `python scripts/importar_top5_velvetverse_csv.py relatorio.csv --week 2026-11-09`.
- `scripts/testar_importacao_top5_velvetverse.py` contém testes sem ligação à Internet. O workflow semanal inclui esses testes antes da auditoria.
- O importador **não assume que o RCast fornece este CSV**; a exportação e respetivo formato ainda têm de ser confirmados. O painel público RCast documenta estatísticas de audiência e logs, mas não encontramos confirmação de um endpoint público autenticável para top de reproduções por faixa.
- A lista candidata nunca é publicada automaticamente e não atualiza os votos.

## Segurança na passagem a produção
Não copiar chaves do R2 para GitHub nem iniciar uma tarefa automática de upload enquanto não existir um bucket específico e autorização para disponibilização dos excertos. Não alegar automatização completa enquanto a ligação ao relatório do RCast e a publicação autorizada não estiverem testadas.

## Rotina única de preparação local (adicionada em 09/11)
- `scripts/TOP5_VELVETVERSE_SEMANAL.bat` chama `scripts/TOP5_VELVETVERSE_SEMANAL.ps1`, que recebe um CSV exportado do RCast.
- O script PowerShell usa as colunas **Track**, **Artist** e **Times played**, exclui jingles/intros/sweepers, faz ranking por reproduções e bloqueia empates no quinto lugar.
- Antes de converter, exige encontrar de forma **inequívoca** na biblioteca `D:\mp3` as cinco faixas usando artista + título do nome do ficheiro; se não encontrar, não inventa substitutos.
- Reutiliza o FFmpeg da preparação anterior e cria uma nova pasta `D:\mp3\Top 5 Velvetverse\SEMANAIS_CANDIDATOS\AAAA-MM-DD` com 5 ficheiros de 30 segundos e `top5-candidato.json`.
- Não altera o RadioDJ/RCast, não executa upload, não publica no site, não inicia votos. Não elimina ficheiros anteriores.
- **Ainda não instalado no PC** e não executado com o CSV real. A existência do CSV mensal não satisfaz uma classificação estritamente semanal; é preciso confirmar intervalo/periodicidade que o RCast oferece.
- Para evitar expectativas erradas, não há agendamento local real até executar uma vez no PC e verificar a exportação automática do CSV.
