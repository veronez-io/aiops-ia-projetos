# Logs do incidente — checkout-service (janela de ~10 minutos)

Coleta simulada de um incidente real de produção do serviço `checkout-service`,
consolidando três fontes: logs da **aplicação**, eventos do **cluster Kubernetes**
e logs do **banco de dados PostgreSQL**. Use este arquivo como entrada para o
subagente investigador de logs na demo da Aula 10.

O incidente segue uma falha em cascata: começa no banco (réplica de leitura cai),
sobe para o cluster (pods saturam, sofrem OOM e reinício) e estoura na aplicação
(timeouts de pagamento e respostas 504 para o usuário final).

---

## 1. Logs da aplicação — checkout-service

```log
2026-05-26T14:00:03Z INFO  app  checkout-service v2.14.1 started, listening on :8080
2026-05-26T14:00:03Z INFO  app  config loaded: pool_max=50 payment_timeout=5000ms read_replica=enabled
2026-05-26T14:00:04Z INFO  app  connected to postgres write=db-primary:5432 read=db-replica:5432
2026-05-26T14:00:04Z INFO  app  connected to redis cache:6379
2026-05-26T14:00:31Z INFO  app  POST /checkout user=4821 amount=129.90 status=200 duration=138ms
2026-05-26T14:01:12Z INFO  app  POST /checkout user=1190 amount=49.90 status=200 duration=151ms
2026-05-26T14:01:48Z INFO  app  POST /checkout user=7733 amount=312.00 status=200 duration=167ms
2026-05-26T14:02:55Z WARN  app  read query slow: SELECT orders WHERE user_id=$1 took 1180ms (replica)
2026-05-26T14:03:10Z WARN  app  read query slow: SELECT orders WHERE user_id=$1 took 1640ms (replica)
2026-05-26T14:03:42Z ERROR app  read pool error: connection refused db-replica:5432
2026-05-26T14:03:42Z WARN  app  read pool degraded, falling back reads to db-primary:5432
2026-05-26T14:03:58Z INFO  app  POST /checkout user=2204 amount=89.90 status=200 duration=2410ms
2026-05-26T14:04:11Z WARN  app  primary pool pressure: 41/50 connections active
2026-05-26T14:04:30Z ERROR app  payment gateway timeout: provider=stripe user=5510 after 5000ms
2026-05-26T14:04:31Z INFO  app  POST /checkout user=5510 amount=199.00 status=504 duration=5008ms
2026-05-26T14:04:52Z WARN  app  primary pool pressure: 49/50 connections active
2026-05-26T14:05:03Z ERROR app  primary pool exhausted: could not acquire connection within 3000ms
2026-05-26T14:05:04Z INFO  app  POST /checkout user=8821 amount=59.90 status=503 duration=3050ms
2026-05-26T14:05:20Z ERROR app  payment gateway timeout: provider=stripe user=3092 after 5000ms
2026-05-26T14:05:21Z INFO  app  POST /checkout user=3092 amount=420.00 status=504 duration=5011ms
2026-05-26T14:05:48Z FATAL app  received SIGTERM, shutting down gracefully
2026-05-26T14:05:49Z INFO  app  draining 12 in-flight requests
2026-05-26T14:06:02Z INFO  app  checkout-service v2.14.1 started, listening on :8080
2026-05-26T14:06:03Z INFO  app  connected to postgres write=db-primary:5432 read=db-replica:5432
2026-05-26T14:06:35Z ERROR app  payment gateway timeout: provider=stripe user=6610 after 5000ms
2026-05-26T14:06:36Z INFO  app  POST /checkout user=6610 amount=29.90 status=504 duration=5006ms
2026-05-26T14:07:55Z WARN  app  read pool reconnect attempt to db-replica:5432 failed
2026-05-26T14:09:40Z INFO  app  read pool reconnected to db-replica:5432
2026-05-26T14:09:58Z INFO  app  POST /checkout user=7012 amount=74.50 status=200 duration=176ms
```

---

## 2. Eventos do cluster Kubernetes — namespace `payments`

```log
2026-05-26T14:03:40Z Warning Unhealthy   pod/checkout-7d9f-abc12   Readiness probe failed: HTTP 500 from /healthz
2026-05-26T14:04:15Z Warning Unhealthy   pod/checkout-7d9f-abc12   Liveness probe failed: timeout after 3s
2026-05-26T14:04:55Z Warning BackOff     pod/checkout-7d9f-abc12   Back-off restarting failed container
2026-05-26T14:05:10Z Normal  Scheduled   pod/checkout-7d9f-def34   Successfully assigned payments/checkout-7d9f-def34 to node-2
2026-05-26T14:05:33Z Warning OOMKilled   pod/checkout-7d9f-abc12   Container checkout exceeded memory limit 512Mi (used 538Mi)
2026-05-26T14:05:48Z Normal  Killing     pod/checkout-7d9f-abc12   Stopping container checkout
2026-05-26T14:05:50Z Warning FailedScheduling pod/checkout-7d9f-ghi56  0/3 nodes available: 1 Insufficient cpu, 2 Insufficient memory
2026-05-26T14:06:01Z Normal  Started     pod/checkout-7d9f-def34   Started container checkout
2026-05-26T14:06:12Z Warning CPUThrottling pod/checkout-7d9f-def34  Container throttled: cpu usage 980m of 1000m limit
2026-05-26T14:06:40Z Warning Unhealthy   pod/checkout-7d9f-def34   Readiness probe failed: HTTP 503 from /healthz
2026-05-26T14:07:20Z Normal  ScalingReplicaSet deployment/checkout    Scaled up replica set to 4 from 2 (HPA: cpu 91%)
2026-05-26T14:08:05Z Normal  Started     pod/checkout-7d9f-jkl78   Started container checkout
2026-05-26T14:09:50Z Normal  Healthy     pod/checkout-7d9f-def34   Readiness probe succeeded
```

---

## 3. Logs do banco de dados — PostgreSQL (cluster `orders-db`)

```log
2026-05-26T14:02:40Z LOG   db-replica  streaming replication lag: 1.2s
2026-05-26T14:03:05Z LOG   db-replica  streaming replication lag: 4.8s
2026-05-26T14:03:38Z FATAL db-replica  terminating connection due to administrator command (node restart)
2026-05-26T14:03:39Z LOG   db-replica  replica node went down (planned maintenance not coordinated with app team)
2026-05-26T14:03:45Z LOG   db-primary  unexpected read traffic spike: read QPS 120 -> 540
2026-05-26T14:04:20Z WARN  db-primary  active connections 410/500, approaching max_connections
2026-05-26T14:04:58Z WARN  db-primary  active connections 486/500
2026-05-26T14:05:02Z ERROR db-primary  FATAL: sorry, too many clients already
2026-05-26T14:05:15Z LOG   db-primary  checkpoint starting: time
2026-05-26T14:05:44Z WARN  db-primary  long-running transaction holding locks for 28s (pid=44921)
2026-05-26T14:06:30Z ERROR db-primary  FATAL: sorry, too many clients already
2026-05-26T14:08:10Z LOG   db-replica  replica node back online, resuming streaming replication
2026-05-26T14:09:35Z LOG   db-replica  streaming replication lag: 0.3s (caught up)
2026-05-26T14:09:36Z LOG   db-primary  read traffic normalized: read QPS 540 -> 130
```

---

## Notas de contexto (metadados do ambiente)

- **Serviço:** `checkout-service` v2.14.1 — Go, roda no namespace `payments`
- **Limites do pod:** memória 512Mi, CPU 1000m, réplicas mínimas 2 (HPA até 6)
- **Banco:** PostgreSQL com primary + 1 réplica de leitura; `max_connections=500`, pool da app `pool_max=50` por pod
- **Gateway de pagamento:** Stripe, timeout configurado em 5000ms
- **Janela de pico:** o incidente ocorreu durante horário de pico de vendas (14h)
