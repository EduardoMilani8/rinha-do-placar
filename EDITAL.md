# Edital da Rinha do Placar

**Edital nº 01/2026 · Rinha de Back-end do Esquenta da Maratona de Programação**

## 1. Apresentação

A **Rinha do Placar** é uma competição de back-end aberta que integra o **Esquenta**, evento de abertura marcado para **27 de outubro de 2026**, às 8h.

Todas as equipes implementam a mesma API: o **placar de uma maratona de programação** no estilo ICPC. Uma competição simulada envia submissões em rajada enquanto várias pessoas consultam o ranking, e a API precisa manter o placar **correto** e **rápido**. Os resultados são apresentados ao vivo na abertura do Esquenta.

## 2. Objetivos

- Aproximar a comunidade da programação competitiva e da Maratona.
- Praticar, com um problema real, temas de back-end: concorrência, consistência de dados, idempotência, cache e desempenho sob carga.
- Estimular a troca de soluções e de aprendizados entre as equipes.

## 3. Quem pode participar

1. A participação é **gratuita** e aberta a qualquer pessoa.
2. As equipes têm de **1 a 3 integrantes**.
3. Cada pessoa pode participar de **uma única equipe**.
4. Membros da organização podem ajudar com dúvidas, mas **não concorrem** ao ranking.

## 4. Cronograma

| Data | O que acontece |
|---|---|
| 30/09/2026 (quarta) | Publicação deste edital e **abertura das inscrições** |
| 16/10/2026 (sexta), 23h59 | **Fim das inscrições** |
| 20/10/2026 (terça), 23h59 | **Fim do prazo de entrega** das soluções |
| 21 a 24/10/2026 | Avaliação das soluções pela organização |
| 24/10/2026 (sábado) | Divulgação do **resultado preliminar** neste repositório |
| 25/10/2026 (domingo), 23h59 | Fim do prazo de **recursos** |
| 27/10/2026 (terça), 8h | **Resultado oficial**, apresentado na abertura do Esquenta |

Todos os horários seguem o fuso de Brasília. Qualquer alteração de data será avisada neste repositório, e a versão vigente do edital é a que está na branch `main`.

## 5. Inscrição

1. Abra uma Issue com o modelo **Inscrição**, informando o nome da equipe e os usuários do GitHub de cada integrante.
2. A organização confirma a inscrição com um comentário na própria Issue.
3. É possível ajustar a formação da equipe até o fim das inscrições, comentando na mesma Issue.

Como as Issues são públicas, **não informe dados pessoais sensíveis** (telefone, documentos, endereço).

## 6. O desafio

Cada equipe deve implementar a API descrita em [`docs/ESPECIFICACAO-API.md`](docs/ESPECIFICACAO-API.md), seguindo exatamente a regra de ranking de [`docs/REGRA-DE-RANKING.md`](docs/REGRA-DE-RANKING.md). Os documentos da pasta `docs/` e os testes da pasta `testes/` fazem parte deste edital.

Em resumo, a API:

- cadastra equipes;
- recebe submissões (equipe, problema, minuto da prova e veredito);
- permite alterar o veredito de uma submissão (rejulgamento);
- devolve o placar completo e o detalhe de cada equipe.

## 7. Requisitos técnicos

Linguagem, framework e banco de dados são livres. A solução é entregue como um `docker-compose.yml` com duas instâncias da API atrás de um balanceador, dentro de um limite de recursos. Todos os requisitos estão em [`docs/REQUISITOS-TECNICOS.md`](docs/REQUISITOS-TECNICOS.md).

## 8. Avaliação

A avaliação é automática e reproduzível, feita pelos mesmos testes públicos de [`testes/`](testes). As etapas e os critérios estão em [`docs/AVALIACAO.md`](docs/AVALIACAO.md). Só quem passa em todas as etapas entra no ranking, ordenado pela **latência p99** (menor é melhor). Assim, não vence quem é rápido, mas errado.

Rode os testes na sua máquina antes de entregar, seguindo [`testes/README.md`](testes/README.md).

## 9. Entrega

1. Deixe a solução em um repositório **público**.
2. Abra uma Issue com o modelo **Entrega**, informando o link do repositório e o **hash do commit** avaliado.
3. Vale a **última** Issue de entrega aberta pela equipe até o prazo. Commits feitos depois do prazo, ou fora do hash informado, não são considerados.
4. **Não há segunda chance.** A solução reprovada em qualquer etapa da avaliação fica fora do ranking e não pode ser corrigida ou reenviada depois do prazo. Teste bastante antes de entregar.

## 10. Premiação

A premiação será divulgada por aviso neste repositório **antes do fim das inscrições**. O ranking final será publicado no arquivo `RESULTADOS.md`.

## 11. Uso de inteligência artificial

O uso de ferramentas de IA (assistentes de código, chats, geradores) é **permitido**. Não vamos proibir, e nem teríamos como fiscalizar.

Mesmo assim, pedimos bom senso. A Rinha existe para você **se desafiar e aprender algo novo**: concorrência, consistência, cache, desempenho sob carga. Entregar o que uma IA gerou sem entender, só para subir no ranking, tira de você justamente o que a competição oferece, e o resultado final não vai dizer nada sobre o que você sabe.

Nossa sugestão: use a IA como quem usa um colega mais experiente ou a documentação, para tirar dúvidas, entender um erro, comparar abordagens e revisar o que escreveu. Tente resolver as partes principais por conta própria, e a IA vira um apoio, não o autor da solução.

Em troca, combinamos três coisas:

1. A equipe precisa **entender e saber explicar** o que entregou. A organização pode pedir uma explicação a qualquer momento, e a incapacidade de explicar a própria solução pode levar à desclassificação (veja a seção 12).
2. Conte no `README.md` da solução, em poucas linhas, **como a IA foi usada**, se foi. Isso não tira pontos e não afeta o ranking: serve para a troca de aprendizados entre as equipes.
3. Usar IA não muda as demais regras: copiar a solução de outra equipe continua proibido, e tentar enganar o executor dos testes também.

## 12. Conduta e desclassificação

Uma equipe pode ser desclassificada se:

- copiar código de outra equipe (é permitido usar bibliotecas e trechos públicos, citando a fonte no repositório);
- tentar **identificar o executor dos testes** ou os dados da carga para dar respostas pré-calculadas (por exemplo, reconhecer o cabeçalho das requisições ou a semente pública);
- tentar prejudicar a máquina de avaliação, as outras equipes ou a organização;
- entregar uma solução que não use os serviços do `docker-compose.yml` como descrito nos requisitos;
- não conseguir explicar a própria solução quando a organização pedir (veja a seção 11).

Espera-se respeito entre todas as pessoas participantes, em Issues e comentários.

## 13. Dúvidas e recursos

- **Dúvidas:** abra uma Issue com o modelo **Dúvida**. As respostas ficam públicas para que todas as equipes tenham a mesma informação.
- **Recursos:** até 25/10, 23h59, abra uma Issue com o modelo **Dúvida** e o título começando por `[RECURSO]`, explicando o que considera incorreto. A organização responde antes do resultado oficial.

## 14. Disposições finais

- Ao participar, a equipe declara ter lido e aceito este edital.
- Este repositório e as soluções entregues são públicos; ao entregar, a equipe autoriza a organização a rodar e a divulgar o resultado da avaliação.
- Os casos omissos serão decididos pela organização, com a justificativa registrada em Issue.
- Se uma correção do edital ou dos testes for necessária, ela é publicada em uma **nova versão** (tag) e avisada em Issue. Cenários públicos já entregues não mudam de significado sem aviso.
