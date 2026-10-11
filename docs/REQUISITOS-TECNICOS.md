# Requisitos técnicos

## Entrega

- Um repositório **público** com um `docker-compose.yml` na **raiz**.
- A solução precisa subir apenas com `docker compose up`, sem passos manuais e sem depender de arquivos fora do repositório.
- As imagens devem ser **públicas** ou construídas a partir do repositório (`build:`). Registros privados não são aceitos.
- Inclua um `README.md` curto dizendo qual linguagem e quais tecnologias você usou. Isso ajuda na apresentação dos resultados. Se usou IA, conte ali como (veja o [edital](../EDITAL.md#11-uso-de-inteligência-artificial)).

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

Declare os limites em cada serviço com `deploy.resources.limits` (`cpus` e `memory`, ambos maiores que zero). A organização soma os valores declarados e rejeita a solução que passar do limite. O uso real durante a avaliação é apenas registrado, mas o Docker encerra o container que estourar a memória declarada, e isso conta como falha da solução.

## O que o `docker-compose.yml` pode ter

A organização roda o seu código na máquina de avaliação, então o `docker-compose.yml` é verificado **antes de subir qualquer coisa**, e quem descumprir uma regra é reprovado na etapa `compose`, com o motivo registrado. A verificação é uma **lista de permissões**: o que não está listado aqui não é aceito.

- **Serviços:** `api01` e `api02` (exatamente essas duas instâncias da API), mais os serviços de apoio que quiser (balanceador, banco, cache...). Cada serviço declara `deploy.resources.limits` maiores que zero, e a soma respeita os [limites](#limites-de-recursos). Não use `scale` nem `deploy.replicas` diferentes de 1.
- **Porta:** só a `9999` pode ser publicada no host, e por um único serviço.
- **Chaves de serviço permitidas:** `build`, `cap_drop`, `command`, `depends_on`, `deploy`, `entrypoint`, `env_file`, `environment`, `expose`, `healthcheck`, `hostname`, `image`, `init`, `labels`, `network_mode` (só `bridge`), `networks`, `ports`, `read_only`, `restart`, `scale`, `shm_size`, `stdin_open`, `stop_grace_period`, `stop_signal`, `tmpfs`, `tty`, `ulimits`, `user`, `volumes` e `working_dir`.
- **`deploy`:** só `resources` (`limits` e `reservations`), `replicas` (igual a 1), `restart_policy` e `placement`.
- **`build`:** só `context`, `dockerfile`, `args`, `target` e `labels`. O contexto e o Dockerfile precisam estar dentro do seu repositório.
- **Volumes:** volumes nomeados simples (driver `local`, sem `driver_opts`, sem `external`) e *bind mounts* somente de caminhos **dentro do repositório**, sempre com `read_only: true`. Não monte `docker.sock`.
- **`env_file`:** só arquivos dentro do repositório.
- **Redes:** só a rede `bridge` do próprio projeto (sem `external`, sem `driver_opts` e sem os nomes `host`, `none` ou `bridge`).
- **Raiz do arquivo:** só `name`, `services`, `networks` e `volumes` (nada de `secrets`, `configs` ou `include`).

Qualquer outra chave (por exemplo `privileged`, `cap_add`, `devices`, `security_opt`, `pid`, `ipc`, `uts`, `cgroup`, `sysctls`, `logging`, `extra_hosts`, `container_name`, `use_api_socket`, `post_start`, `pre_stop`, `cpus` e `mem_limit`) reprova a solução. Chaves iniciadas por `x-` (extensões) são ignoradas. O [modelo de entrega](../exemplo-participante) já cumpre todas as regras.

## Regras de infraestrutura

- Os dados precisam sobreviver à queda de **uma instância da API**. Não é exigido sobreviver à queda do banco.
- A solução tem de responder `200` em `GET /saude` em até **60 segundos** depois do `docker compose up`. O tempo do `build` **não** conta nesses 60 segundos.
- Se o `build` ou a subida falharem por problema de rede ou do registro de imagens (por exemplo, limite de downloads do Docker Hub), a avaliação é repetida e **não** conta contra a equipe. Use imagens públicas e leves, de preferência de versão fixa.

## Regras da solução

- Linguagem e framework livres.
- O estado **não** pode ficar apenas na memória de cada instância, porque as duas precisam enxergar os mesmos dados.
- É permitido usar cache, desde que respeite os [requisitos de comportamento](ESPECIFICACAO-API.md#requisitos-de-comportamento), principalmente ler as próprias escritas.
- É **proibido** tentar reconhecer o executor dos testes ou os dados da carga (por exemplo, pelo `User-Agent`, por cabeçalhos ou pela semente pública) para dar respostas pré-calculadas. Veja a seção de conduta no [edital](../EDITAL.md).

## Ambiente de avaliação

A avaliação roda em uma única máquina, uma solução por vez, sempre partindo de um ambiente limpo (containers, redes e volumes do projeto removidos antes de subir). Antes de cada avaliação a organização confere que a máquina está ociosa, na tomada e fria. O executor dos testes roda na mesma máquina, cuja configuração é esta:

| Item | Configuração |
|---|---|
| Máquina | Notebook Avell A52 HYB |
| Processador | Intel Core i7-12650H (10 núcleos, 16 threads, até 4,7 GHz) |
| Memória | 14 GB de RAM |
| Armazenamento | SSD NVMe |
| Sistema | Ubuntu 26.04 LTS |
| Docker | 29.1.3, com Docker Compose 2.40.3 |

Como a máquina de vocês será diferente da nossa, **compare seu resultado com o de outras soluções na mesma máquina, e não os números absolutos**.
