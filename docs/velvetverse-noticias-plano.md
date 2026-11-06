# VelvetVerse Notícias — plano técnico (fase de testes)

Estado: desenho técnico; não está em produção e NÃO altera eventos RadioDJ.

## Objetivo
- Domingo às 12:00 America/Toronto, integrado em Alma Portuguesa.
- 8–10 minutos, PT-PT, locução séria e profissional.
- 2 notícias internacionais, 2–3 Portugal, 2 desporto Portugal/Canadá; previsão para domingo e segunda-feira.
- Emissão autónoma; se a edição não estiver válida, manter a música normal, nunca emitir notícias antigas.

## Pipeline proposto
1. GitHub Actions inicia de manhã no domingo (considerar horário de verão de Toronto).
2. Recolha de fontes autorizadas, com título, URL, data e identificação de origem; não copiar artigos.
3. Validação dos factos, datas, resultados e previsão meteorológica; bloquear informação não confirmada.
4. Redação de script PT-PT, sem inventar conteúdo para preencher duração.
5. Fish Audio API gera a voz. Usar segredo FISH_AUDIO_API_KEY nas Actions Secrets; nunca incorporar chave em código ou logs. O modelo gratuito anunciado termina em 30/11/2026.
6. FFmpeg monta e verifica o MP3 com intro, vinheta, loudness e metadados de edição.
7. Publicar apenas áudio validado em armazenamento protegido; agente do computador Windows recebe-o e verifica data/integridade.
8. Testar um método suportado para introduzir o ficheiro no RadioDJ, sem mexer diretamente na base MariaDB.
9. Transmissão às 12:00 apenas se edição válida e disponível; caso contrário prossegue Alma Portuguesa.

## Condições antes de ativar
- Verificar licenças das fontes noticiosas e meteorologia para emissão.
- Rever política editorial e incidentes em notícias de última hora.
- Testar primeiro workflow manual e saída sem publicação.
- Testar o RadioDJ offline/em ambiente controlado e plano de contingência.
- Não criar cron de produção nem modificar eventos RadioDJ nesta fase.

## Inventário GitHub já existente
- .github/workflows/billboard-top5-latino.yml: apenas manual (arquivado).
- .github/workflows/test-shazam-top5.yml: ainda tem schedule automático para Top 5 Latino, apesar de estar em standby; não alterado.
