# Especificação da API

A API atende na **porta 9999** (o balanceador), fala **JSON** e usa HTTP/1.1. Campos desconhecidos nos corpos das requisições são ignorados. O corpo das respostas de sucesso de escrita é livre, e os testes só olham o **status**.

## Resumo

| Método | Rota | Função |
|---|---|---|
| `GET` | `/saude` | Diz que a API está pronta |
| `POST` | `/equipes` | Cadastra uma equipe |
| `POST` | `/submissoes` | Registra uma submissão |
| `PATCH` | `/submissoes/{id}` | Rejulga uma submissão (troca o veredito) |
| `GET` | `/placar` | Ranking completo |
| `GET` | `/equipes/{id}` | Detalhe de uma equipe |
| `POST` | `/admin/reset` | Apaga todos os dados (usado entre testes) |

## `GET /saude`

Devolve **200** quando a API está pronta para receber requisições. O executor só começa os testes depois disso.

## `POST /equipes`

```json
{ "id": "eq-0001", "nome": "Equipe Alfa" }
```

| Status | Quando |
|---|---|
| `201` | Equipe cadastrada |
| `409` | Já existe uma equipe com esse `id` |
| `422` | `id` ou `nome` ausente, vazio, com mais de 64 caracteres ou que não seja texto |

## `POST /submissoes`

```json
{
  "id": "sub-000123",
  "equipe_id": "eq-0001",
  "problema": "C",
  "minuto": 87,
  "veredito": "ERRADO"
}
```

| Campo | Regra |
|---|---|
| `id` | Texto de 1 a 64 caracteres. Identifica a submissão e garante a **idempotência** |
| `equipe_id` | Texto de 1 a 64 caracteres |
| `problema` | 1 ou 2 letras maiúsculas (`A` a `Z`) |
| `minuto` | **Inteiro** de 0 a 300 (número decimal ou texto é inválido) |
| `veredito` | `ACEITO`, `ERRADO`, `ERRO_COMPILACAO` ou `TEMPO_EXCEDIDO` |

| Status | Quando |
|---|---|
| `201` | Submissão registrada |
| `200` | Já existia uma submissão com esse `id`: **nada muda** (idempotência) |
| `404` | A `equipe_id` não existe |
| `422` | Algum campo inválido |

Ordem de verificação: primeiro a validação do corpo (`422`), depois o `id` repetido (`200`), depois a equipe (`404`).

## `PATCH /submissoes/{id}`

```json
{ "veredito": "ACEITO" }
```

| Status | Quando |
|---|---|
| `200` | Veredito atualizado (inclusive se for igual ao anterior) |
| `404` | A submissão não existe |
| `422` | `veredito` ausente ou inválido |

Ordem de verificação, a mesma do `POST /submissoes`: primeiro a validação do corpo (`422`), depois a existência da submissão (`404`). Portanto, um `veredito` inválido em uma submissão que não existe devolve `422`.

## `GET /placar`

Devolve **200** com uma lista de todas as equipes, já ordenada conforme a [regra de ranking](REGRA-DE-RANKING.md):

```json
[
  { "posicao": 1, "equipe_id": "eq-0007", "nome": "Equipe Alfa", "resolvidos": 5, "penalidade": 412, "ultimo_acerto": 287 },
  { "posicao": 2, "equipe_id": "eq-0002", "nome": "Equipe Beta", "resolvidos": 5, "penalidade": 431, "ultimo_acerto": 260 },
  { "posicao": 3, "equipe_id": "eq-0009", "nome": "Equipe Gama", "resolvidos": 0, "penalidade": 0, "ultimo_acerto": null }
]
```

Equipes sem nenhum acerto **também aparecem**, com `resolvidos: 0`, `penalidade: 0` e `ultimo_acerto: null`. Sem equipes cadastradas, a resposta é `[]`.

## `GET /equipes/{id}`

Devolve **200** com o detalhe (ou **404** se a equipe não existe). A lista `problemas` traz os problemas em que a equipe enviou ao menos uma submissão, em ordem alfabética:

```json
{
  "equipe_id": "eq-0007",
  "nome": "Equipe Alfa",
  "resolvidos": 1,
  "penalidade": 70,
  "ultimo_acerto": 30,
  "problemas": [
    { "problema": "A", "resolvido": true,  "tentativas_erradas": 2, "minuto_acerto": 30,   "penalidade": 70 },
    { "problema": "B", "resolvido": false, "tentativas_erradas": 3, "minuto_acerto": null, "penalidade": 0 }
  ]
}
```

`tentativas_erradas` conta as submissões `ERRADO` e `TEMPO_EXCEDIDO` que **valem**: as anteriores ao acerto, se o problema foi resolvido, ou todas, se não foi.

## `POST /admin/reset`

Apaga equipes e submissões e devolve **204**. O executor chama esta rota antes de cada teste. Ela deve terminar em poucos segundos.

## Requisitos de comportamento

1. **Ler as próprias escritas.** Depois que a API respondeu `2xx` a uma escrita, qualquer `GET` seguinte, atendido por **qualquer instância**, precisa refletir essa escrita.
2. **Idempotência.** Reenviar o mesmo `id` de submissão não pode mudar o resultado. O executor reenvia requisições que falharam.
3. **Independência da ordem de chegada.** O resultado depende do `minuto`, não de quando a submissão chegou.
4. **Concorrência.** Várias submissões da mesma equipe no mesmo problema podem chegar ao mesmo tempo. Nenhuma tentativa pode se perder.
5. **Placar sempre válido.** Mesmo durante escritas, o `GET /placar` precisa devolver uma lista completa, com todas as equipes, posições de 1 a N e a ordem correta. Nunca uma lista pela metade nem fora de ordem. O executor confere isso a cada leitura durante a carga.
6. **Tempo de resposta.** Respostas que demoram mais de **2 segundos** contam como falha.
