# Regra de ranking

A regra segue o modelo do ICPC. A implementação de referência é [`testes/oraculo.py`](../testes/oraculo.py); se este texto e o código divergirem, abra uma Issue.

## Conceitos

- **Submissão:** um envio de uma equipe para um problema, feito em um certo **minuto** da prova (inteiro de 0 a 300), com um **veredito**.
- **Vereditos:** `ACEITO`, `ERRADO`, `ERRO_COMPILACAO` e `TEMPO_EXCEDIDO`.
- **Problema:** identificado por 1 ou 2 letras maiúsculas (`A`, `B`, ..., `AB`).

## Cálculo por equipe e problema

Para cada equipe e cada problema, considere as submissões em **ordem cronológica**, ou seja, ordenadas pelo **minuto**. Submissões no mesmo minuto ficam em ordem alfabética de `id`. A ordem de **chegada** à API não importa.

1. Percorra as submissões em ordem.
2. `ERRADO` e `TEMPO_EXCEDIDO` contam como **tentativa errada**.
3. `ERRO_COMPILACAO` **não conta**: não gera penalidade.
4. O primeiro `ACEITO` **resolve** o problema. Todas as submissões seguintes desse problema são **ignoradas**.
5. A penalidade do problema resolvido é:

   ```
   penalidade = minuto do acerto + 20 × (tentativas erradas antes do acerto)
   ```

6. Problema **não resolvido** não gera penalidade, mesmo com muitas tentativas erradas.

## Cálculo por equipe

- `resolvidos`: quantidade de problemas resolvidos.
- `penalidade`: soma das penalidades dos problemas resolvidos.
- `ultimo_acerto`: maior minuto de acerto entre os problemas resolvidos, ou `null` se não resolveu nenhum.

## Ordem do placar

O placar tem **ordem total**: não existem duas equipes na mesma posição. Ordena-se por, nesta ordem de prioridade:

1. mais `resolvidos`;
2. menor `penalidade`;
3. menor `ultimo_acerto` (equipes sem acertos ficam iguais neste critério);
4. `equipe_id` em ordem alfabética crescente (comparação por código de caractere).

A `posicao` é 1 para a primeira linha, 2 para a segunda, e assim por diante.

## Rejulgamento

Um rejulgamento troca o veredito de uma submissão já recebida. O placar deve refletir o **novo estado como se o veredito novo sempre tivesse existido**. Isso pode:

- transformar um `ERRADO` em `ACEITO`, encerrando o problema mais cedo e passando a ignorar as submissões seguintes;
- transformar um `ACEITO` em outro veredito, fazendo o problema voltar a ser avaliado e uma submissão antes ignorada passar a contar.

## Exemplos

**Erros antes do acerto.** Equipe envia `ERRADO` (min 5), `TEMPO_EXCEDIDO` (min 12) e `ACEITO` (min 30) no problema A: penalidade = 30 + 2 × 20 = **70**.

**Erro de compilação.** `ERRO_COMPILACAO` (min 3) e `ACEITO` (min 20): penalidade = **20**.

**Chegada fora de ordem.** As submissões chegam na ordem `ERRADO` (min 50), `ACEITO` (min 45), `ERRADO` (min 30). Cronologicamente: `ERRADO` (30), `ACEITO` (45), e o de 50 é ignorado. Penalidade = 45 + 20 = **65**.

**Desempate.** A resolve 2 problemas (acertos nos minutos 10 e 50, penalidade 60). B resolve 2 (ambos no minuto 30, penalidade 60). Empatam em resolvidos e penalidade, mas B fez o último acerto no minuto 30, contra 50 de A: **B fica na frente**.

Todos esses casos, e mais alguns, estão nos [cenários públicos](../testes/cenarios) com os resultados calculados à mão.
