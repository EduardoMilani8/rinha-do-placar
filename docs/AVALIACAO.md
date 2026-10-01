# Como as soluções são avaliadas

A avaliação é automática e usa o mesmo executor que você pode rodar: [`testes/executar.py`](../testes/executar.py). Todas as soluções passam pelo mesmo caminho, uma por vez, na mesma máquina.

## Visão geral

```
Subida  →  Corretude  →  Carga (3 execuções)  →  Falha  →  Ranking
   └─────────── qualquer reprovação elimina a solução ───────────┘
```

Só entram no ranking as soluções **aprovadas em todas as etapas**. Quem for reprovado recebe o motivo em uma Issue, para poder aprender com ele, mas não há nova entrega (veja o [edital](../EDITAL.md#9-entrega)).

## Etapa 1: subida

1. `docker compose down -v` e `docker compose up -d --build` no repositório, no commit informado na entrega.
2. `GET /saude` precisa responder `200` em até **60 segundos**.
3. A soma dos limites de CPU e memória declarados precisa respeitar o [limite](REQUISITOS-TECNICOS.md#limites-de-recursos).

## Etapa 2: corretude (eliminatória)

O executor roda os cenários de [`testes/cenarios/`](../testes/cenarios), que são **públicos e exatamente os mesmos** usados na avaliação. Antes de cada cenário ele chama `POST /admin/reset`. Um cenário passa apenas se todos os status HTTP e o placar (e o detalhe das equipes, quando o cenário pede) forem os esperados.

Falhou em qualquer cenário: a solução é reprovada.

```bash
python3 testes/executar.py corretude
```

## Etapa 3: carga

Uma competição simulada é gerada por [`testes/gerador.py`](../testes/gerador.py) a partir de uma **semente secreta**, revelada depois do resultado oficial. Os parâmetros oficiais são:

| Parâmetro | Valor |
|---|---|
| Equipes | 300 |
| Submissões | 30.000 (mais cerca de 3% reenviadas em duplicata) |
| Rejulgamentos | cerca de 2% das submissões |
| Envios simultâneos | 64 |
| Leitores simultâneos do `GET /placar` | 16 |
| Tempo limite por requisição | 2 segundos |
| Tentativas por requisição | até 3 (a API é idempotente) |

Como a carga se desenrola:

1. Cadastra as equipes.
2. Envia as submissões **fora de ordem cronológica** (com desordem de até 30 minutos) e com duplicatas, enquanto 16 leitores consultam o placar sem parar.
3. Só depois de todas as submissões confirmadas, envia os rejulgamentos.
4. Consulta o placar final e compara com o resultado calculado pelo [oráculo](../testes/oraculo.py).

A carga é **aprovada** se todas estas condições valerem:

- **Taxa de falhas ≤ 1%** (resposta inesperada, erro de rede ou mais de 2 s conta como falha de uma tentativa);
- nenhum envio perdido (todas as tentativas de um mesmo envio falharam);
- **todo** placar lido durante a carga é um ranking completo e corretamente ordenado;
- o **placar final é idêntico** ao esperado.

```bash
python3 testes/executar.py carga --seed 42
```

Cada solução roda a carga **3 vezes**, cada uma partindo de `POST /admin/reset`, e as 3 precisam ser aprovadas. O resultado de desempenho é a **mediana** das 3 execuções.

## Etapa 4: falha

Uma quarta execução da carga, com uma diferença: quando ela atinge cerca de metade dos envios, a organização derruba a instância `api02` (`docker compose kill api02`). A solução precisa continuar atendendo pela `api01`, sem perder nenhum envio já confirmado, e o placar final precisa ser idêntico ao esperado.

Nesta etapa a taxa de falhas tolerada é de **5%**, por causa das requisições que estavam em andamento na instância derrubada. Como os envios são idempotentes, o executor os reenvia. Para simular localmente, use `--limite-erros 0.05`.

## Ranking

Entre as soluções aprovadas em todas as etapas:

1. menor **p99 global** (a latência abaixo da qual ficam 99% das requisições), mediana das 3 execuções da carga, arredondado para milissegundo inteiro;
2. em caso de empate, maior **vazão** (requisições por segundo);
3. persistindo o empate, as equipes dividem a posição.

O p99 global considera todas as requisições da carga: envios, rejulgamentos e leituras do placar.

## Boas práticas de justiça

- A organização usa a mesma máquina, a mesma versão do Docker e o mesmo executor para todas as soluções, na versão marcada com a tag `avaliacao`.
- O ambiente é reiniciado entre as soluções.
- Os resultados brutos de cada execução são publicados junto com o resultado oficial.

## Rode antes de entregar

O passo a passo para rodar cada etapa na sua máquina, inclusive a derrubada de uma instância, está em [`testes/README.md`](../testes/README.md).
