# Requisitos técnicos

## Entrega

- Um repositório **público** com um `docker-compose.yml` na **raiz**.
- A solução precisa subir apenas com `docker compose up`, sem passos manuais e sem depender de arquivos fora do repositório.
- As imagens devem ser **públicas** ou construídas a partir do repositório (`build:`). Registros privados não são aceitos.
- Inclua um `README.md` curto dizendo qual linguagem e quais tecnologias você usou. Isso ajuda na apresentação dos resultados.

Há um modelo pronto em [`exemplo-participante/`](../exemplo-participante).

## Serviços obrigatórios

| Serviço | Regra |
|---|---|
| Balanceador | Escuta na porta **9999** e distribui as requisições entre as duas instâncias |
| `api01` e `api02` | **Exatamente duas** instâncias da API, com esses nomes |
| Armazenamento | Livre (PostgreSQL, MySQL, Redis, MongoDB...), mas obrigatoriamente **compartilhado** entre as instâncias |

Você pode adicionar outros serviços (cache, fila...), desde que caibam nos limites abaixo.

## Limites de recursos

A soma dos limites de **todos os serviços** não pode passar de:

- **1,5 CPU**;
- **3 GB de memória** (3000 MB).

Declare os limites em cada serviço com `deploy.resources.limits` (`cpus` e `memory`). A organização soma os valores declarados e confere com o uso real durante a avaliação.

## Regras de infraestrutura

- Rede em modo `bridge` (o padrão). `network_mode: host` **não** é permitido.
- Sem `privileged: true`.
- Os dados precisam sobreviver à queda de **uma instância da API**. Não é exigido sobreviver à queda do banco.
- A solução tem de responder `200` em `GET /saude` em até **60 segundos** depois do `docker compose up`.

## Regras da solução

- Linguagem e framework livres.
- O estado **não** pode ficar apenas na memória de cada instância, porque as duas precisam enxergar os mesmos dados.
- É permitido usar cache, desde que respeite os [requisitos de comportamento](ESPECIFICACAO-API.md#requisitos-de-comportamento), principalmente ler as próprias escritas.
- É **proibido** tentar reconhecer o executor dos testes ou os dados da carga (por exemplo, pelo `User-Agent`, por cabeçalhos ou pela semente pública) para dar respostas pré-calculadas. Veja a seção de conduta no [edital](../EDITAL.md).

## Ambiente de avaliação

A avaliação roda em uma única máquina, uma solução por vez, sempre partindo de um ambiente limpo (`docker compose down -v` seguido de `docker compose up`). A configuração da máquina será informada em uma Issue antes do prazo de entrega.

Como a máquina de vocês será diferente da nossa, **compare seu resultado com o de outras soluções na mesma máquina, e não os números absolutos**.
