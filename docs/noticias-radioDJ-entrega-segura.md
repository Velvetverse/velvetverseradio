# Notícias, com Ricky Sousa — entrega ao RadioDJ (plano de integração)

**Estado em 7/11/2026:** preparação técnica; nenhuma alteração feita no PC, MariaDB, eventos ou emissão. Não ativar o evento do jornal até completar o ensaio em ambiente de teste.

## O que existe

- Notícias e meteorologia: pesquisa e rascunho pela API, **sempre sujeitos a revisão**.
- 3 MP3 aprovados na raiz do GitHub: `intro-noticias.mp3`, `vinheta-desporto.mp3`, `vinheta-meteorologia.mp3`.
- Locução sintetizada testada; nome em antena **Ricky Sousa**, anúncio «Notícias, com Ricky Sousa».
- Montagem Fish+FFmpeg e upload opcional para R2 privado — **ainda não validados ponta a ponta**.
- Transporte de R2 para `C:\RadioWeb\Noticias\Staging` — só staging, não é uma ordem de emissão.

## Escolha técnica recomendada para estudar no PC

RadioDJ dispõe de tipos de faixa **File By Date** e **Variable Duration File**.
O primeiro seleciona ficheiros pelo nome da data; o segundo reanalisa a duração de um MP3 que mudou. Ambas são funções documentadas em [tipos de faixa do RadioDJ](https://www.radiodj.ro/tutorials/track-types-in-radiodj.html).

**Preferência a validar sem antena:** `File By Date` numa pasta exclusiva de edições autorizadas, com nomes `YYYY-MM-DD.mp3`. Apenas o jornal do próprio domingo deve existir nessa pasta. Não reutilizar nomes de semanas anteriores.

1. Produzir rascunho antes do domingo, com referências e meteorologia. **Não é locução aprovada.**
2. Editor responsável confirma notícias, licenças, previsões e pronúncia; regista aprovação.
3. Gerar MP3 final, medir duração real (até 30 minutos), ouvir e aprovar.
4. Transferir para staging privado, verificar data/size/hash.
5. *Apenas após aprovação* promover por operação atómica para uma pasta de edições autorizadas do PC. A promoção ainda não está implementada, nem ativada.
6. Configurar em RadioDJ um evento de domingo às 12h00, apontando para a faixa do dia, e testar com saída sem antena. Confirmar se a ausência de ficheiro é ignorada sem causar interrupção. Se o teste não garantir fallback, usar um método diferente.
7. **Fallback obrigatório:** sem edição válida, manter a rotação musical atual; nunca transmitir a edição da semana anterior.

## O que falta observar no computador

- Instalação real de RadioDJ e localização das pastas utilizadas.
- Versão e menu de eventos; eventos existentes perto das 12h00 e conflitos com sinais horários.
- Comportamento do tipo File By Date e ausência de MP3 no RadioDJ v2.0.4.5.
- Autorização e acesso de R2 privado no PC (nenhuma credencial fica em GitHub público).
- Segurança do processo de aprovação e de promoção; recuperação após falha de rede, reinício ou desconexão.
- Teste da duração completa e da retoma de música sem cortes.

### Diagnóstico disponível (só leitura)

`radio-pc/diagnostico-noticias.ps1` lista presença de software, pastas e variáveis **sem mostrar chaves** e sem alterar o PC. `radio-pc/receber-noticias-teste.bat` só descarrega áudio aprovado para staging privado se as credenciais R2 estiverem disponíveis.

### Bloqueios de segurança

Não copiar ficheiros por cima de faixas já indexadas sem validar o comportamento real do RadioDJ. Não alterar tabelas MariaDB nem eventos por scripts externos. Não ativar recargas, horários ou emissões automáticas enquanto não existir segurança editorial e fallback comprovado.

## Configuração observada no PC (capturas de 7 de novembro de 2026)
Capturas reais do RadioDJ **v2.0.4.5** mostram:

- `12 CLOCK ALMA PORTUGUESA` executa-se às **12:00** em **Repeat by Day**, com **todos os dias MON–SUN marcados**, **Smart Timing ativo**.
- Ações desse evento: **Load Track By ID** (locução de horas) e, a seguir, **Load Track From Category** (música da rotação).
- `ALMA PORTUGUESA SWEEPER 3` aparece às **12:30** todos os dias; seu comportamento detalhado ainda não foi inspecionado.
- `CORAÇÕES & MEMÓRIAS` aparece às **12:59** e continua a ter de assumir a hora seguinte.
- O campo de data do gestor de eventos não filtrou a lista como esperado; as linhas continuaram com 7/11 apesar de selecionar 8/11. Não inferir execução exclusiva de domingo pela apresentação da data.

**Importante: ainda NÃO retirar domingo ao evento das 12h00 nem criar evento concorrente.** A primeira ação é locução horária; a segunda carrega uma música e pode colidir com o jornal se forem criados dois eventos no mesmo momento. Também é necessário verificar se o sweeper das 12h30 pode entrar antes de terminar um jornal mais longo. Verificar modo de inserção, Smart Timing e efeito da ausência do MP3 antes de permitir emissão automática.

**Fluxo de configuração de domingo após validação e MP3 aprovado:** preservar a configuração original, separar o evento diário de 12:00 em Seg–Sáb e um evento dominical (horário e comportamento a testar), sem duplicar ações. Configurar uma única chamada às Notícias com fallback validado, e nunca interromper a programação de 12:59. A programação musical continua no caso de falta da edição. O RadioDJ suporta oficialmente o tipo de faixa `File By Date` que seleciona `yyyy-MM-dd.mp3` na pasta configurada; testar o comportamento concreto na instalação antes de confiar nesse fallback: https://www.radiodj.ro/tutorials/track-types-in-radiodj.html.

## Atualização — eventos reais e receptor automático preparado

A janela de edição do RadioDJ confirmou que **ALMA PORTUGUESA SWEEPER 3** está às **12:30**, com **Repeat by Day** para todos os dias, **Smart Timing** ativado e uma única ação `Load Track From Category` (sweeper da categoria Alma Portuguesa). Não alterar este evento antes de testes sem antena.

Foi acrescentado `radio-pc/receber-noticias-staging.ps1` para receber automaticamente edições privadas, sem pausas nem interação, usando o Python/boto3 e o mecanismo já existente em `scripts/velvetverse_noticias_transferencia.py`. Este último agora não substitui silenciosamente um MP3 existente no staging: se já estiver íntegro, termina sem novo download; se houver divergência, bloqueia.

O ficheiro `radio-pc/instalar-rececao-staging.ps1` **apenas prepara uma tarefa Windows DESATIVADA**, com calendário de domingo às 11h30. Ainda não foi executado no PC e não cria nenhum evento RadioDJ. Antes de ativar é preciso verificar fuso horário, credenciais R2 e receção no Windows, e testar o fallback sem antena.
