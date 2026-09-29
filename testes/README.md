# Testes

Tudo aqui usa apenas a biblioteca padrão do **Python 3.10 ou mais novo**. Não há nada para instalar.

| Arquivo | Para que serve |
|---|---|
| `executar.py` | O executor oficial: fases `corretude` e `carga` |
| `oraculo.py` | A regra de ranking implementada de forma simples e correta |
| `gerador.py` | Gera a competição simulada da carga a partir de uma semente |
| `cenarios/` | Os 12 cenários de corretude, com resultados calculados à mão |
| `servidor_ingenuo.py` | Uma API mínima em memória, para ver o comportamento esperado |
| `test_oraculo.py` | Confere o oráculo contra os cenários |

## Rodar contra a sua solução

Com a sua solução no ar em `localhost:9999`:

```bash
python3 testes/executar.py corretude
python3 testes/executar.py carga
```

Opções úteis:

```bash
python3 testes/executar.py carga --seed 7                        # outros dados
python3 testes/executar.py carga --submissoes 5000 --equipes 100  # carga menor, para depurar
python3 testes/executar.py carga --url http://localhost:8080      # outra porta
python3 testes/executar.py carga --limite-erros 0.05              # como na etapa de falha
python3 testes/executar.py carga --saida resultado.json           # grava o resumo
```

A semente padrão (42) é pública. A avaliação oficial usa uma semente secreta, então uma solução que só funcione para a 42 será reprovada.

O código de saída é `0` se tudo passou e `1` se algo falhou. Se o executor não conseguir falar com a API, ele sai com `2`.

## Testar o próprio ambiente com o servidor ingênuo

```bash
python3 testes/servidor_ingenuo.py --porta 9999   # em um terminal
python3 testes/executar.py corretude              # em outro
```

O servidor ingênuo passa em tudo, mas **não serve como solução**: ele guarda os dados na memória de um único processo, então não funciona com duas instâncias.

## Ver os dados gerados

```bash
python3 testes/gerador.py --seed 42 --saida dados/
```

Cria `equipes.jsonl`, `envios.jsonl` (na ordem de envio, com duplicatas), `rejulgamentos.jsonl` e `esperado.json` (o placar final correto).

## Conferir o oráculo

```bash
python3 testes/test_oraculo.py
```

## Como as latências são medidas

O executor mede o tempo de cada requisição, incluindo a resposta completa, com uma conexão persistente por thread e `TCP_NODELAY`. Se você achar um problema na medição, abra uma Issue.
