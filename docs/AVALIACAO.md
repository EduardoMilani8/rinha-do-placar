# Como as soluções são avaliadas

A avaliação é automática. Os testes públicos de [`testes/`](../testes) servem para você validar a solução antes de entregar. O ranking, porém, é definido por **testes próprios da organização, que não são divulgados**. Eles seguem a mesma [especificação](ESPECIFICACAO-API.md) e a mesma [regra de ranking](REGRA-DE-RANKING.md), então uma solução correta segundo esses documentos deve passar, mas passar nos testes públicos não garante a aprovação. Todas as soluções passam pelo mesmo caminho, uma por vez, na mesma máquina.

## Visão geral

```
Compose  →  Subida  →  Corretude  →  Carga (5 execuções)  →  Falha  →  Ranking
    └──────────────── qualquer reprovação elimina a solução ────────────────┘
```

Só entram no ranking as soluções **aprovadas em todas as etapas**. Quem for reprovado recebe o motivo em uma Issue, para poder aprender com ele, mas não há nova entrega (veja o [edital](../EDITAL.md#9-entrega)).

**Problema do ambiente não é culpa da equipe.** Se a máquina de avaliação estiver ocupada, se o Docker não conseguir baixar imagens por falha de rede ou limite do registro, ou se houver um defeito nos testes, a avaliação é **repetida** e não conta contra a equipe.

## Etapa 1: compose

Antes de subir qualquer coisa, a organização lê o `docker-compose.yml` do commit informado na entrega e confere as regras de [`REQUISITOS-TECNICOS.md`](REQUISITOS-TECNICOS.md#o-que-o-docker-composeyml-pode-ter): as duas instâncias `api01` e `api02`, só a porta 9999 publicada, limites de recursos declarados e dentro da soma permitida, e apenas as chaves permitidas. Qualquer violação reprova a solução, com o motivo registrado.

## Etapa 2: subida

1. Os containers, redes e volumes de qualquer avaliação anterior são removidos, depois a organização roda `docker compose build` e `docker compose up -d --no-build`. O tempo de `build` **não** conta.
2. `GET /saude` precisa responder `200` em até **60 segundos** depois do `up`.

## Etapa 3: corretude (eliminatória)

A organização roda um conjunto oficial de cenários, que não é divulgado. Os cenários públicos de [`testes/cenarios/`](../testes/cenarios) são exemplos do tipo de verificação feita. Antes de cada cenário o executor chama `POST /admin/reset`. Um cenário passa apenas se todos os status HTTP e o placar (e o detalhe das equipes, quando o cenário pede) forem os esperados.

Falhou em qualquer cenário: a solução é reprovada.

```bash
python3 testes/executar.py corretude
```

## Etapa 4: carga

A carga oficial é gerada pela organização, com dados que não são divulgados, e é aplicada com **taxa fixa de chegada**: todas as soluções recebem exatamente as mesmas requisições, no mesmo ritmo, não importa a velocidade de cada uma. Quem responde mais devagar não recebe menos carga, apenas atrasa. O executor público usa clientes simultâneos (veja abaixo) e serve para treinar; a taxa e os valores da carga oficial podem ser diferentes.

Parâmetros do executor público:

| Parâmetro | Valor |
|---|---|
| Equipes | 300 |
| Submissões | 30.000 (mais cerca de 3% reenviadas em duplicata) |
| Rejulgamentos | cerca de 2% das submissões |
| Envios simultâneos | 64 |
| Leitores simultâneos do `GET /placar` | 16 |
| Tempo limite por requisição | 2 segundos |
| Tentativas por requisição | até 3 (a API é idempotente) |

A carga oficial se desenrola assim:

1. Cadastra as equipes.
2. Roda um aquecimento curto, com dados próprios, que é descartado.
3. Envia as submissões **fora de ordem cronológica** (com desordem de até 30 minutos) e com duplicatas, enquanto o placar é consultado continuamente.
4. Só depois de todas as submissões confirmadas, envia os rejulgamentos, com o placar ainda sendo consultado.
5. Consulta o placar final e o detalhe de algumas equipes e compara com o resultado calculado pelo [oráculo](../testes/oraculo.py).

A carga é **aprovada** se todas estas condições valerem:

- **Taxa de falhas ≤ 1%** (resposta inesperada, erro de rede ou mais de 2 s conta como falha de uma tentativa);
- nenhum envio perdido (todas as tentativas de uma mesma operação falharam);
- **nenhuma iteração descartada**: a solução precisa acompanhar a taxa de chegada. Se ela não aguenta, requisições deixam de ser iniciadas, e isso reprova em vez de melhorar a latência medida;
- **todo** placar lido durante a carga é um ranking completo e corretamente ordenado;
- o **placar final e o detalhe das equipes conferidas são idênticos** ao esperado.

```bash
python3 testes/executar.py carga --seed 42
```

Cada solução roda a carga **5 vezes**, cada uma partindo de `POST /admin/reset`, e as 5 precisam ser aprovadas. O resultado de desempenho é a **mediana** das 3 execuções.

## Etapa 5: falha

Uma quarta execução da carga, com uma diferença: quando a fase de envios atinge cerca de metade, a organização derruba a instância `api02` (`docker compose kill api02`) e confere que ela realmente caiu. A solução precisa continuar atendendo pela `api01`, sem perder nenhum envio já confirmado, e o placar final precisa ser idêntico ao esperado.

Nesta etapa a taxa de falhas tolerada é de **5%**, por causa das requisições que estavam em andamento na instância derrubada. Como os envios são idempotentes, eles são reenviados (até 3 tentativas). Para simular localmente, use `--limite-erros 0.05`.

## Ranking

Entre as soluções aprovadas em todas as etapas:

1. menor **p99**, a latência abaixo da qual ficam 99% das operações, mediana das 5 execuções da carga, com **uma casa decimal** (em milissegundos);
2. em caso de empate, menor **p95**, calculado da mesma forma;
3. persistindo o empate, as equipes dividem a posição.

O p99 considera todas as operações da carga: envios, rejulgamentos e leituras do placar. A latência de uma operação vai do início da **primeira tentativa** até a resposta aceita, e **soma as tentativas que falharam**. Assim, um erro rápido seguido de um acerto não esconde a espera. A vazão não entra no ranking: como a taxa de chegada é fixa, ela é igual para quem acompanha a carga.

## Boas práticas de justiça

- A organização usa a mesma máquina, a mesma versão do Docker e os mesmos testes para todas as soluções.
- Antes de cada avaliação, e entre as execuções da carga, a máquina precisa estar ociosa, na tomada e fria (abaixo de 60 °C), sem nenhum outro container rodando. A organização registra as condições de cada execução.
- O ambiente é limpo entre as soluções e entre as execuções.
- Os resultados brutos de cada execução e os testes oficiais são publicados no dia do resultado oficial.

## Rode antes de entregar

O passo a passo para rodar cada etapa na sua máquina, inclusive a derrubada de uma instância, está em [`testes/README.md`](../testes/README.md).
