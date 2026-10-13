# VelvetVerse Radio — Plano de trabalho: Top 5 Latino

**Estado:** plano de referência; automação da Billboard ainda NÃO implementada.  
**Regra:** não trocar a fonte, o calendário, nem reescrever o sistema sem consultar primeiro este documento e o código que já funciona. Toda a alteração deve registar o resultado aqui.

## 1. Decisões aprovadas (não voltar a discutir)

- **Classificação oficial:** Billboard **Hot Latin Songs**, exatamente as posições 1 a 5 da edição datada escolhida. Nunca substituir pela Apple Music, Apple Music México, rankings regionais, Latin Airplay, nem votações dos ouvintes.
- **Apple Music:** apenas os leitores incorporados e os identificadores das cinco músicas. Se um título não existir no catálogo, não inventar correspondência ou trocar a música.
- **Locutor:** Adrian Vega (Noia), programa **Ritmo Latino**, às **sextas-feiras, 08:15**, hora de **Toronto (America/Toronto)**.
- **Prioridade:** disponibilizar informação fiável antecipadamente para produção do programa. A votação é secundária e não altera as posições oficiais Billboard.
- **Calendário editorial pretendido:** segunda 10:00 disponibilizar uma edição para votação; quarta 18:00 fechar a votação; quinta-feira livre para produzir; sexta 08:15 emissão. Atenção: a Billboard publica habitualmente os rankings às terças. Para manter segunda-feira, a edição publicada será a **última tabela oficial já disponível nessa segunda-feira**, sempre com a respetiva **data real da Billboard**, nunca apresentada como uma tabela futura. Uma mudança para usar o ranking lançado na terça requer aprovação prévia.
- **Fuso horário:** Toronto, incluindo mudança automática de horário de verão.

## 2. Estado real verificado a 13/10/2026

- Website: repositório `Velvetverse/velvetverseradio`, página principal em `index.html`, secção `#top5latino`.
- Leitores Apple Music: implementados em `<script id="top5-inline-script">` e hoje usam cinco itens **fixos no código**, não uma alimentação semanal.
- Votação via Supabase: `<script id="top5-vote-script">`; é independente da classificação Billboard e usa a edição para separar votos.
- O título/data da edição ainda está **fixo/teste** no script. Não prometer ao utilizador atualizações automáticas até o novo sistema estar validado.
- **Não há automação ativa da Billboard.** Foram criados por engano e imediatamente removidos dois ficheiros destinados ao ranking Apple Music (`scripts/update_top5.py`, `.github/workflows/top5-latino.yml`). NÃO recriar essa solução errada.
- Classificação oficial verificável em: https://www.billboard.com/charts/latin-songs/ ; verificar se a fonte mostra a **data do chart** e as posições reais.

## 3. Plano técnico, por ordem — não saltar etapas

1. **Fonte Billboard verificável:** pesquisar e testar se é possível recolher legal e tecnicamente o Top 5 e data da edição de forma fiável, sem conta paga, cookies interativos, violar restrições ou scraping frágil. Não há uma API pública estável confirmada. Se não houver acesso robusto, **não inventar uma automação**: usar revisão editorial semanal assistida com dados oficiais e atualização programada do ficheiro de dados.
2. **Formato único de dados:** criar uma fonte versionada (por exemplo `top5-weekly.json`) com `chart_date`, `published_at`, `week`, `source` e cinco itens com `rank`, `title`, `artist`, `apple_music_id`. Guardar também a data de publicação e conservar histórico para auditoria. Nunca publicar uma edição sem 5 músicas e 5 IDs Apple Music confirmados.
3. **Separar dados e apresentação:** adaptar `index.html` para ler o JSON e usar os leitores Apple Music existentes, sem alterar o design. Implementar fallback: em caso de falha, manter a edição anterior com data correta, sem reiniciar votos.
4. **Publicação semanal:** somente depois de testar a fonte e validação, configurar GitHub Actions com fuso Toronto e ativação à segunda 10:00, com verificação de data real da Billboard e lançamento idempotente (uma vez por semana). Não modificar outras páginas.
5. **Votação:** permitir voto só de segunda-feira 10:00 até quarta-feira 18:00 (Toronto); mostrar resultado final após fecho; não bloquear a publicação do programa se a votação falhar. Preservar regra 1 voto por edição.
6. **Preparação do Noia:** disponibilizar quarta-feira 18:00 cinco posições oficiais e resultado separado do público. Quinta-feira reservada para montar/gravar, sexta 08:15 para emitir.
7. **Teste e entrega:** confirmar 5 players e capas corretos, data Billboard, mudança de semana, fuso Toronto, comportamento com link Apple em falta, voto fechado, edição anterior preservada; fazer commit e registar ficheiros alterados e estado.

## 4. Política de trabalho com o assistente

- **Antes de modificar:** ler este plano e o `index.html` atual; confirmar o estado no GitHub. Não assumir que uma conversa anterior corresponde ao código publicado.
- **Uma fase de cada vez:** diagnóstico → alteração mínima → teste → commit → anotação neste plano.
- **Sem experiências no site em direto** quando faltam dados ou há incerteza. Não apresentar rascunhos como tarefas concluídas.
- **Não exigir que o utilizador edite código:** as mudanças aprovadas são feitas diretamente no GitHub.
- **Não repetir perguntas resolvidas:** Billboard = ranking; Apple Music = leitor; Noia = produção; quarta 18:00 = prazo limite.
- **Critério de sucesso:** edição e data verificadas, programa preparável a tempo, votação não interfere, alterações persistem e estão documentadas.

## 5. Próxima tarefa concreta

**Validar uma fonte estável e legítima para a Billboard Hot Latin Songs e o mapeamento por música para Apple Music, ANTES de escrever ou ativar automatizações.** Se não houver fonte fiável, apresentar ao utilizador o bloqueio e uma alternativa editorial simples para aprovação.

## 6. Diário de alterações

- **13/10/2026:** fonte oficial e leitores confirmados separadamente; identificada a necessidade de resolver o calendário da Billboard (publicação habitualmente à terça); publicado este plano, **nenhuma automação Billboard ativada**.

## 7. Verificação de fonte — 13/10/2026

- Testado o endereço oficial https://www.billboard.com/charts/latin-songs/ : o acesso automatizado devolveu **HTTP 402 (Payment Required)**. Não há, neste teste, uma API oficial pública/estável confirmada que possa ser usada sem contrato.
- Fontes indexadas/cópias podem apresentar edições antigas. Exemplo encontrado: uma cópia com **Week of October 3, 2026**, que não deve ser confundida com a edição mais recente.
- Conclusão: **não ativar um scraper nem uma tarefa que anuncie edição nova sem validar data + posições 1–5 diretamente na fonte oficial.**
- O processo editorial assistido é o único caminho pronto para usar de imediato: verificar semanalmente a fonte oficial, confirmar títulos/artistas e IDs Apple Music e só então publicar uma edição versionada. O acesso direto a dados através de licenciamento/API oficial pode ser avaliado no futuro.
- **Próxima execução:** implementar um arquivo JSON de edições validadas, adaptar o site para o ler mantendo fallback, e introduzir janela de votação segunda 10:00–quarta 18:00; **não escrever uma rotina de recolha Billboard até haver fonte fiável confirmada**.

## 8. Implementação realizada em 13/10/2026

- **`top5-weekly.json` criado** com cinco músicas da Billboard Hot Latin Songs de **10 de outubro de 2026**, com posições, identificadores Apple Music e data de origem. Edição inicial validada por anúncio do Top 10 da Billboard publicado em 07/10.
- **`index.html` atualizado**: carrega o JSON verificado; preserva os players Apple Music, a votação e o design; se faltar o JSON ou estiver inválido, conserva os cinco leitores anteriores. A data da classificação exibida é a data oficial da edição, não uma data fictícia de publicação.
- **Janela de votação implementada no cliente:** abre segunda 10:00 e encerra quarta 18:00, em Toronto; resultados permanecem visíveis. A votação usa IDs de edição separados. Nota técnica: a verificação de janela é do browser; para proteção contra submissão direta à API, a regra também deve existir no Supabase. Não afirmar segurança de fecho absoluto sem validar backend.
- **Automação experimental fail-safe criada:** `.github/workflows/billboard-top5-latino.yml` + `scripts/update_billboard_top5.py`: tenta consultar a Billboard Hot Latin Songs com a biblioteca `billboard.py`, identifica as cinco posições, procura correspondências exatas de título no catálogo iTunes/Apple Music e só atualiza o JSON se os cinco IDs forem encontrados e a data for adequada. É executada por GitHub Actions à segunda-feira a cada hora, mas o script só publica na hora local 10:00 Toronto. Em caso de bloqueio de acesso Billboard ou falha na correspondência, encerra com erro **sem alterar os cinco leitores públicos**.
- **Limitação não resolvida:** a origem Billboard está sujeita a bloqueios e a integração não foi testada num runner Actions. A automação foi implementada, mas o funcionamento semanal sem intervenção **não está ainda demonstrado**. GitHub Actions pode começar alguns minutos atrasado, inclusive fora da janela de uma hora; nesse caso a edição anterior permanece segura. Não anunciar como totalmente concluída até haver uma execução bem-sucedida.
- **Próxima verificação:** observar a primeira execução agendada no GitHub Actions (segunda-feira 19/10/2026 às 10:00 Toronto), rever erros, corrigir apenas a etapa bloqueada. Se a Billboard impedir o acesso, definir fonte licenciada ou alternativa com validação humana; nunca apresentar outro ranking como Billboard.

## 9. Separação página/emissão — decisão 13/10/2026

- **Nova decisão aprovada:** a página pública do Top 5 Latino é independente da primeira emissão falada. Pode publicar novos rankings **já**, sempre que estiver disponível uma nova edição oficial da Billboard. Não aguardar 19/10 nem as sextas-feiras.
- **Implementação:** remover o bloqueio que restringia a recolha às segundas-feiras às 10:00, e passar a consultar por GitHub Actions de hora a hora em horários úteis. Quando a data Billboard recebida for mais recente e os cinco leitores Apple Music tiverem correspondência, o JSON público é atualizado automaticamente; caso contrário, mantém a edição anterior.
- **Aviso:** a recolha direta pela biblioteca `billboard.py` ainda depende de acesso ao site Billboard e não foi verificada numa execução GitHub Actions. Não confundir o agendamento implementado com garantia de obtenção dos dados.
- **O programa do Noia permanece à sexta às 08:15.** A votação continua com a janela segunda 10:00–quarta 18:00; esta janela não retarda a página nem o ranking oficial.
