# Rinha do Placar

Competição de back-end aberta, parte do **Esquenta da Maratona de Programação**, com resultado apresentado ao vivo na abertura do evento, em **27 de outubro de 2026, às 8h**.

Todas as equipes constroem a mesma API: o **placar de uma maratona de programação** no estilo ICPC. A gente simula uma competição, manda milhares de submissões de uma vez, e a sua API tem que manter o ranking **certo** e **rápido**. Quem passa em todos os testes é ranqueado pela latência.

> Você não precisa saber programação competitiva. A regra de ranking está explicada em [`docs/REGRA-DE-RANKING.md`](docs/REGRA-DE-RANKING.md).

## Datas

| Data | O que acontece |
|---|---|
| 30/09 | Edital publicado, **inscrições abertas** |
| 16/10, 23h59 | Fim das inscrições |
| 20/10, 23h59 | **Fim da entrega** |
| 21 a 24/10 | Avaliação |
| 24/10 | Resultado preliminar |
| 25/10, 23h59 | Fim dos recursos |
| 27/10, 8h | **Resultado oficial no Esquenta** |

Leia o [edital](EDITAL.md) completo antes de começar.

## Comece por aqui

1. Leia o [edital](EDITAL.md) e a [regra de ranking](docs/REGRA-DE-RANKING.md).
2. **Inscreva sua equipe** (de 1 a 3 pessoas) abrindo uma Issue com o modelo [Inscrição](https://github.com/EduardoMilani8/rinha-do-placar/issues/new/choose).
3. Estude a [especificação da API](docs/ESPECIFICACAO-API.md).
4. Copie o [modelo de entrega](exemplo-participante) para o seu repositório e escreva a sua API, em qualquer linguagem.
5. Rode os [testes](testes/README.md) na sua máquina até tudo passar.
6. **Entregue** abrindo uma Issue com o modelo [Entrega](https://github.com/EduardoMilani8/rinha-do-placar/issues/new/choose) até o prazo.

## Teste em um minuto

Com Python 3.10 ou mais novo, sem instalar nada, você já pode ver o comportamento esperado:

```bash
python3 testes/servidor_ingenuo.py --porta 9999
```

Em outro terminal:

```bash
python3 testes/executar.py corretude
python3 testes/executar.py carga --submissoes 5000 --equipes 100
```

O servidor ingênuo passa em tudo, mas guarda os dados na memória de um único processo. Ele **não** serve como solução, porque a sua precisa funcionar com duas instâncias.

## Como é avaliado

Em resumo, a sua solução precisa:

1. **Subir** com `docker compose up` e responder em até 60 segundos;
2. **Passar** nos 12 [cenários públicos](testes/cenarios);
3. **Aguentar a carga** (30 mil submissões, 64 envios simultâneos e 16 leitores do placar) mantendo o placar final idêntico ao esperado;
4. **Sobreviver** à queda de uma instância no meio da carga.

Quem passa em tudo é ordenado pela **latência p99**. Os detalhes estão em [`docs/AVALIACAO.md`](docs/AVALIACAO.md).

## O que tem neste repositório

| Caminho | Conteúdo |
|---|---|
| [`EDITAL.md`](EDITAL.md) | Regras, cronograma, conduta e recursos |
| [`docs/REGRA-DE-RANKING.md`](docs/REGRA-DE-RANKING.md) | Como o placar é calculado |
| [`docs/ESPECIFICACAO-API.md`](docs/ESPECIFICACAO-API.md) | Rotas, formatos e códigos de status |
| [`docs/REQUISITOS-TECNICOS.md`](docs/REQUISITOS-TECNICOS.md) | Docker, limites de recursos e regras da infraestrutura |
| [`docs/AVALIACAO.md`](docs/AVALIACAO.md) | Etapas de avaliação e critério de ranking |
| [`docs/FAQ.md`](docs/FAQ.md) | Perguntas frequentes |
| [`exemplo-participante/`](exemplo-participante) | Modelo de `docker-compose.yml` e balanceador |
| [`testes/`](testes) | Executor, oráculo, gerador de dados e cenários |

## Dúvidas

Abra uma Issue com o modelo [Dúvida](https://github.com/EduardoMilani8/rinha-do-placar/issues/new/choose). As respostas são públicas, para todas as equipes terem a mesma informação.

## Licença

[MIT](LICENSE)
