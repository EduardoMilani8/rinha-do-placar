# Perguntas frequentes

## Preciso saber o que é uma maratona de programação?

Não. A [regra de ranking](REGRA-DE-RANKING.md) explica tudo. Você não precisa resolver problemas de maratona, só implementar a API que conta os pontos.

## Posso usar qualquer linguagem?

Sim. Qualquer linguagem, framework e banco de dados, desde que rodem no `docker-compose.yml` dentro dos [limites](REQUISITOS-TECNICOS.md#limites-de-recursos).

## Nunca usei Docker. E agora?

O [modelo de entrega](../exemplo-participante) traz o `docker-compose.yml` e o balanceador prontos. Você só precisa escrever a API e o `Dockerfile` dela. Se travar, abra uma Issue com o modelo **Dúvida**.

## Por que duas instâncias da API?

Porque em uma competição real o placar é consultado por muita gente ao mesmo tempo. Com duas instâncias, o estado precisa ficar em um lugar compartilhado, e é aí que aparecem os desafios de concorrência e consistência que queremos explorar.

## Posso guardar tudo em memória?

Não. Cada instância teria a sua própria memória, e o placar de uma não bateria com o da outra.

## Posso usar cache?

Pode, desde que, depois de uma escrita confirmada com `2xx`, qualquer leitura seguinte reflita essa escrita. Cache mal invalidado é um dos erros mais comuns.

## O que é p99?

É a latência abaixo da qual ficam 99% das requisições. Se o p99 é 20 ms, então 99% das respostas levaram até 20 ms. Ele mede o "pior caso comum", e por isso é mais justo que a média.

## O que é idempotência?

Enviar a mesma requisição várias vezes tem o mesmo efeito de enviar uma vez. Aqui, reenviar uma submissão com o mesmo `id` não pode contá-la duas vezes.

## As submissões podem chegar fora de ordem?

Sim, e é de propósito. O que vale é o `minuto` da submissão, e não a hora em que ela chegou à API.

## A semente 42 é a mesma da avaliação?

Não. A 42 é só para treinar. A avaliação oficial usa uma semente secreta, revelada depois do resultado.

## Meu resultado local é bem melhor que o de outra equipe. Vou ganhar?

Não necessariamente. As máquinas são diferentes. O que vale é o resultado da avaliação oficial, todas as soluções na mesma máquina.

## Posso usar IA para ajudar?

Pode, desde que você entenda o que entregou e consiga explicar a solução se a organização pedir.

## Encontrei um erro na especificação ou nos testes. O que faço?

Abra uma Issue com o modelo **Dúvida**. Se for realmente um erro, a correção sai em uma nova versão, avisada em Issue.
