!!! info "Source Repository"
    This documentation is from [amiable-dev/litellm-langfuse-railway](https://github.com/amiable-dev/litellm-langfuse-railway).
    Last synced: 2026-01-03 | Commit: `5a45454`

# LiteLLM + Langfuse Production Stack

**The only production-ready LLM observability stack on Railway.**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/YOUR_TEMPLATE_ID)

## What Makes This Production-Ready?

| Feature | Starter Templates | **This Template** |
|---------|-------------------|-------------------|
| Automated Backups | ❌ | ✅ PostgreSQL + ClickHouse to MinIO |
| Health Monitoring | ❌ | ✅ All services with alerting |
| Redis Persistence | ❌ Basic | ✅ AOF enabled |
| Alert Integration | ❌ | ✅ Slack, Discord, PagerDuty |
| Prometheus Metrics | ❌ | ✅ `/metrics` endpoint |
| Recovery Runbook | ❌ | ✅ Documented procedures |
| Restart Policies | Basic | ✅ Enhanced with retries |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Your Applications                           │
│                    (OpenAI SDK Compatible)                          │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         LiteLLM Gateway                             │
│              Unified API • Rate Limiting • Cost Tracking            │
│                    Virtual Keys • Load Balancing                    │
└─────────────────────────────────────────────────────────────────────┘
          │                       │                        │
          ▼                       ▼                        ▼
   ┌──────────────┐      ┌──────────────┐        ┌──────────────────┐
   │   OpenAI     │      │   Anthropic   │       │   100+ Providers │
   └──────────────┘      └──────────────┘        └──────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Langfuse Platform                            │
│         Tracing • Prompt Management • Evaluation • Analytics        │
├─────────────────────────────────────────────────────────────────────┤
│  langfuse-web (UI/API)          │        langfuse-worker (async)    │
└─────────────────────────────────────────────────────────────────────┘
          │                       │                        │
          ▼                       ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│    PostgreSQL    │    │    ClickHouse    │    │      Redis       │
│   (Transactional)│    │    (Analytics)   │    │  (Cache/Queue)   │
│                  │    │                  │    │   AOF Enabled    │
└──────────────────┘    └──────────────────┘    └──────────────────┘
          │                       │
          └───────────┬───────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Production Services                           │
├─────────────────────────────────────────────────────────────────────┤
│  backup-service              │        health-monitor                │
│  • Daily PostgreSQL dumps    │        • 60s health checks           │
│  • ClickHouse exports        │        • Slack/Discord/PagerDuty    │
│  • 7-day retention           │        • Prometheus metrics          │
│  • Stored in MinIO           │        • Recovery alerts             │
└─────────────────────────────────────────────────────────────────────┘
                      │
                      ▼
              ┌──────────────────┐
              │      MinIO       │
              │  (S3 Storage)    │
              │  Backups + Logs  │
              └──────────────────┘
```

## Quick Start

### 1. Deploy

Click the deploy button above, or manually deploy from GitHub.

### 2. Configure Alerts (Recommended)

Set up alerting by adding webhook URLs:

**Slack:**
1. Create a Slack App → Incoming Webhooks
2. Copy webhook URL
3. Add to `ALERT_WEBHOOK_URL` in both `backup-service` and `health-monitor`

**Discord:**
1. Server Settings → Integrations → Webhooks
2. Copy webhook URL
3. Add to `ALERT_WEBHOOK_URL`

**PagerDuty:**
1. Services → Events API v2 → Create Integration
2. Copy routing key
3. Add to `PAGERDUTY_ROUTING_KEY` in `health-monitor`

### 3. Connect Langfuse to LiteLLM

After deployment:

1. Open Langfuse UI (langfuse-web public URL)
2. Create account / Sign in
3. Go to Settings → API Keys → Create New
4. Copy `Public Key` and `Secret Key`
5. Update LiteLLM service environment variables:
   - `LANGFUSE_PUBLIC_KEY`
   - `LANGFUSE_SECRET_KEY`
6. Redeploy LiteLLM

### 4. Add Your LLM Providers

In LiteLLM UI or via API:

```python
import requests

# Add OpenAI
requests.post(
    "https://your-litellm-url/model/new",
    headers={"Authorization": "Bearer YOUR_MASTER_KEY"},
    json={
        "model_name": "gpt-4o",
        "litellm_params": {
            "model": "gpt-4o",
            "api_key": "sk-..."
        }
    }
)

# Add Anthropic
requests.post(
    "https://your-litellm-url/model/new",
    headers={"Authorization": "Bearer YOUR_MASTER_KEY"},
    json={
        "model_name": "claude-3-5-sonnet",
        "litellm_params": {
            "model": "anthropic/claude-3-5-sonnet-20241022",
            "api_key": "sk-ant-..."
        }
    }
)
```

## Services

| Service | Port | Purpose | Public? |
|---------|------|---------|---------|
| litellm | 4000 | LLM Gateway + UI | ✅ Yes |
| langfuse-web | 3000 | Observability UI | ✅ Yes |
| langfuse-worker | 3030 | Async processing | ❌ No |
| postgres | 5432 | Transactional DB | ❌ No |
| clickhouse | 8123/9000 | Analytics DB | ❌ No |
| redis | 6379 | Cache + Queues | ❌ No |
| minio | 9000/9001 | Object Storage | ❌ No |
| backup-service | 8080 | Automated Backups | ❌ No |
| health-monitor | 8080 | Health Checks | Optional |

## Backup Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKUP_SCHEDULE` | daily | `hourly`, `daily`, or `weekly` |
| `BACKUP_HOUR` | 3 | Hour (UTC) for daily/weekly backups |
| `BACKUP_RETENTION_DAYS` | 7 | Days to keep old backups |
| `BACKUP_ON_STARTUP` | true | Run backup when service starts |
| `ALERT_WEBHOOK_URL` | - | Webhook for backup notifications |

### Manual Backup

Trigger an immediate backup:

```bash
curl -X GET https://your-backup-service/backup
```

### Restore from Backup

See [RUNBOOK.md](https://github.com/amiable-dev/litellm-langfuse-railway/blob/5a45454c15e0e5e17ff20a3f0d6df421c1f037db/production/docs/RUNBOOK.md) for detailed restore procedures.

## Health Monitoring

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | JSON health status of all services |
| `GET /metrics` | Prometheus-compatible metrics |
| `GET /check` | Trigger immediate health check |

### Example Health Response

```json
{
  "status": "healthy",
  "timestamp": "2025-01-03T10:30:00Z",
  "services": {
    "litellm": {
      "status": "healthy",
      "response_time_ms": 45.2,
      "consecutive_failures": 0
    },
    "langfuse-web": {
      "status": "healthy",
      "response_time_ms": 120.5,
      "consecutive_failures": 0
    },
    "postgres": {
      "status": "healthy",
      "response_time_ms": 12.1,
      "consecutive_failures": 0
    }
  }
}
```

### Alert Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CHECK_INTERVAL` | 60 | Seconds between checks |
| `FAILURE_THRESHOLD` | 3 | Failures before alerting |
| `ALERT_COOLDOWN` | 15 | Minutes between repeat alerts |
| `ALERT_WEBHOOK_URL` | - | Slack/Discord webhook |
| `PAGERDUTY_ROUTING_KEY` | - | PagerDuty integration key |

## Cost Estimate

| Service | Est. Monthly Cost |
|---------|-------------------|
| litellm | $5-15 |
| langfuse-web | $5-10 |
| langfuse-worker | $3-8 |
| postgres | $5-10 |
| clickhouse | $5-15 |
| redis | $3-5 |
| minio | $3-5 |
| backup-service | $2-5 |
| health-monitor | $2-5 |
| **Total** | **$33-78/mo** |

*Costs depend on usage. Light usage (~$35/mo), heavy usage (~$75/mo).*

## Upgrading

### To Railway HA PostgreSQL

When you need higher availability:

1. Deploy Railway HA PostgreSQL cluster
2. Use migration template: `railway.app/template/VgqHWg`
3. Update `DATABASE_URL` references
4. See [UPGRADE.md](https://github.com/amiable-dev/litellm-langfuse-railway/blob/5a45454c15e0e5e17ff20a3f0d6df421c1f037db/production/docs/UPGRADE.md) for detailed steps

### Scaling Workers

For high trace volume:

```bash
# Scale langfuse-worker
railway service langfuse-worker scale --replicas 3
```

## Troubleshooting

### Common Issues

**LiteLLM can't connect to Langfuse:**
- Verify `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are set
- Check Langfuse URL is correct (https, not http)
- Redeploy LiteLLM after changing keys

**Backups failing:**
- Check `backup-service` logs
- Verify MinIO is healthy
- Ensure sufficient disk space

**Health monitor showing unhealthy:**
- Check individual service logs
- Verify private network connectivity
- Look for OOM or restart loops

### Getting Help

1. Check [RUNBOOK.md](https://github.com/amiable-dev/litellm-langfuse-railway/blob/5a45454c15e0e5e17ff20a3f0d6df421c1f037db/production/docs/RUNBOOK.md) for operational procedures
2. Review service logs in Railway dashboard
3. Open issue on GitHub repository

## License

MIT License - see [LICENSE](./LICENSE)

---

**Built for production.** Unlike other templates that leave resilience as an exercise for the reader, this stack includes everything you need to run LLM observability reliably.
