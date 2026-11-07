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
