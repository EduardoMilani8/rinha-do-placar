# Modelo de entrega

Estes arquivos são um ponto de partida para o `docker-compose.yml` e o balanceador
da sua solução. **Não há uma API aqui**: a API é o seu desafio.

## Como usar

1. Crie um repositório **público** para a sua solução.
2. Copie `docker-compose.yml` e `nginx.conf` para a **raiz** dele.
3. Crie a pasta `api/` com o seu `Dockerfile` e o seu código, em qualquer linguagem.
4. Suba tudo com `docker compose up --build`.
5. Em outro terminal, rode os testes deste repositório (veja [`testes/README.md`](../testes/README.md)).

## O que pode e o que não pode mudar

| Pode | Não pode |
|---|---|
| Trocar o banco (Redis, MySQL, MongoDB...) | Passar de 1,5 CPU e 3 GB no total |
| Trocar o balanceador (HAProxy, Caddy...) | Mudar a porta 9999 do balanceador |
| Ajustar como o limite é dividido entre os serviços | Ter mais ou menos que duas instâncias da API |
| Adicionar serviços (cache, fila...) dentro do limite | Renomear `api01` e `api02` |

## O que foi testado

Este modelo foi executado com Docker, usando uma API de teste no lugar da sua: o `docker compose up` sobe, o balanceador responde na porta 9999, divide as requisições entre `api01` e `api02` e os limites declarados somam 1,5 CPU e 3000 MB. Derrubando a `api02` no meio das requisições, o balanceador continuou respondendo pela `api01` sem erros.

Isso **não** valida a sua API. O `nginx.conf` já trata a queda de uma instância (`proxy_connect_timeout` e `proxy_next_upstream`); se trocar o balanceador, confira a etapa de falha. Se algo não funcionar, abra uma Issue com o modelo "Dúvida".
