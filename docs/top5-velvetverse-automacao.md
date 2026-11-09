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
