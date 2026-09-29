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

## Aviso

Este modelo só foi validado como YAML. Como o repositório não traz uma API, ele não foi
executado de ponta a ponta com o Docker. Se algo não funcionar, abra uma Issue com o
modelo "Dúvida".
