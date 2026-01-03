!!! info "Source Repository"
    This documentation is from [amiable-dev/litellm-langfuse-railway](https://github.com/amiable-dev/litellm-langfuse-railway).
    Last synced: 2026-01-03 | Commit: `5a45454`

# Operations Runbook

This runbook covers common operational procedures for the LiteLLM + Langfuse Production Stack.

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Backup & Restore](#backup--restore)
3. [Incident Response](#incident-response)
4. [Scaling](#scaling)
5. [Maintenance](#maintenance)

---

## Daily Operations

### Health Check

```bash
# Check all services
curl https://your-health-monitor-url/health | jq .

# Check specific service
curl https://your-litellm-url/health
curl https://your-langfuse-url/api/public/health
```

### View Recent Backups

```bash
# In MinIO console or via mc client
mc ls myminio/backups/postgres/
mc ls myminio/backups/clickhouse/
```

### Check Logs

In Railway Dashboard:
1. Select project
2. Click on service
3. View "Deployments" → "Logs"

---

## Backup & Restore

### Manual Backup Trigger

```bash
curl -X GET https://your-backup-service-url/backup
```

### Restore PostgreSQL

#### 1. Download backup from MinIO

```bash
# Using mc client
mc cp myminio/backups/postgres/postgres_backup_20250103_030000.sql.gz ./

# Or via MinIO console UI
```

#### 2. Stop dependent services

In Railway Dashboard, pause:
- litellm
- langfuse-web
- langfuse-worker

#### 3. Restore to PostgreSQL

```bash
# Decompress
gunzip postgres_backup_20250103_030000.sql.gz

# Connect to Railway PostgreSQL and restore
# Get DATABASE_URL from Railway service variables
psql "$DATABASE_URL" < postgres_backup_20250103_030000.sql
```

#### 4. Restart services

Unpause services in Railway Dashboard in order:
1. postgres (if restarted)
2. langfuse-worker
3. langfuse-web
4. litellm

### Restore ClickHouse

#### 1. Download backup

```bash
mc cp myminio/backups/clickhouse/clickhouse_backup_20250103_030000.tar.gz ./
tar -xzf clickhouse_backup_20250103_030000.tar.gz
```

#### 2. Restore tables

```bash
# For each table in the backup
clickhouse-client --host $CLICKHOUSE_HOST \
  --user $CLICKHOUSE_USER \
  --password $CLICKHOUSE_PASSWORD \
  --query "INSERT INTO tablename FORMAT TabSeparatedWithNames" \
  < clickhouse_backup_20250103/tablename.tsv
```

---

## Incident Response

### Service Unhealthy

#### Symptoms
- Health monitor alerts
- 503 errors from service
- Slow response times

#### Diagnosis

1. **Check health endpoint:**
   ```bash
   curl https://your-health-monitor-url/health | jq '.services'
   ```

2. **Check service logs:**
   - Railway Dashboard → Service → Logs

3. **Check resource usage:**
   - Railway Dashboard → Service → Metrics

#### Resolution

| Symptom | Likely Cause | Resolution |
|---------|--------------|------------|
| OOM restart | Insufficient memory | Increase RAM allocation |
| Connection refused | Service crashed | Check logs, restart |
| Timeout | Downstream dependency | Check database connections |
| 5xx errors | Application error | Check application logs |

### Database Connection Issues

#### PostgreSQL

```bash
# Test connection
psql "$DATABASE_URL" -c "SELECT 1"

# Check connection count
psql "$DATABASE_URL" -c "SELECT count(*) FROM pg_stat_activity"

# Kill idle connections if needed
psql "$DATABASE_URL" -c "
  SELECT pg_terminate_backend(pid) 
  FROM pg_stat_activity 
  WHERE state = 'idle' 
  AND query_start < now() - interval '1 hour'
"
```

#### ClickHouse

```bash
# Test connection
curl "http://clickhouse:8123/ping"

# Check running queries
curl "http://clickhouse:8123" --data "SELECT * FROM system.processes"
```

#### Redis

```bash
# Test connection
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD ping

# Check memory usage
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD info memory
```

### Complete Service Outage

1. **Triage:**
   - Which services are affected?
   - When did it start?
   - Any recent deployments?

2. **Communicate:**
   - Update status page if applicable
   - Notify stakeholders

3. **Investigate:**
   ```bash
   # Check all health
   curl https://your-health-monitor-url/health | jq .
   ```

4. **Recover:**
   - Restart failed services
   - Scale horizontally if needed
   - Restore from backup if data corruption

5. **Post-mortem:**
   - Document timeline
   - Identify root cause
   - Create action items

---

## Scaling

### Horizontal Scaling

#### LiteLLM

For high request volume:

```bash
# Railway CLI
railway service litellm scale --replicas 3
```

Or in `railway.toml`:
```toml
[services.litellm.deploy]
numReplicas = 3
```

#### Langfuse Worker

For high trace ingestion:

```bash
railway service langfuse-worker scale --replicas 3
```

### Vertical Scaling

In Railway Dashboard:
1. Service → Settings → Resources
2. Adjust memory/CPU limits

Recommended minimums for production:

| Service | Memory | vCPU |
|---------|--------|------|
| litellm | 512MB | 0.5 |
| langfuse-web | 512MB | 0.5 |
| langfuse-worker | 256MB | 0.25 |
| postgres | 1GB | 1.0 |
| clickhouse | 1GB | 1.0 |
| redis | 256MB | 0.25 |

### Database Scaling

#### PostgreSQL → HA Cluster

1. Deploy HA PostgreSQL template: `railway.app/template/high-availability-postgresql`
2. Run migration service: `railway.app/template/VgqHWg`
3. Update all `DATABASE_URL` references
4. Verify connections
5. Remove old standalone instance

#### ClickHouse Optimization

For large trace volumes, consider:
- Increasing memory allocation
- Adding materialized views for common queries
- Implementing data retention policies

---

## Maintenance

### Regular Tasks

| Task | Frequency | Procedure |
|------|-----------|-----------|
| Review backup logs | Daily | Check backup-service logs |
| Check disk usage | Weekly | Review volume metrics |
| Update dependencies | Monthly | Deploy new image versions |
| Review alerts | Weekly | Tune thresholds if needed |
| Test restore | Monthly | Restore to test environment |

### Updating Services

#### LiteLLM

```bash
# Update image tag in railway.toml
image = "ghcr.io/berriai/litellm-database:main-stable"

# Deploy
railway up
```

#### Langfuse

```bash
# Update image tags
image = "langfuse/langfuse:3"
image = "langfuse/langfuse-worker:3"

# Deploy
railway up
```

### Data Retention

#### ClickHouse (Traces)

Add retention policy in Langfuse settings or manually:

```sql
-- Keep last 90 days of traces
ALTER TABLE traces DELETE WHERE created_at < now() - INTERVAL 90 DAY;
```

#### PostgreSQL

Consider archiving old data:

```sql
-- Archive keys older than 1 year
INSERT INTO archived_keys SELECT * FROM litellm_keys 
WHERE created_at < now() - INTERVAL '1 year';

DELETE FROM litellm_keys 
WHERE created_at < now() - INTERVAL '1 year';
```

#### MinIO (Backups)

Backup service automatically cleans up based on `BACKUP_RETENTION_DAYS`.

To manually clean:
```bash
mc rm --recursive --older-than 30d myminio/backups/
```

---

## Emergency Contacts

| Role | Contact | When to Escalate |
|------|---------|------------------|
| On-call Engineer | (your contact) | Any P1 incident |
| Database Admin | (your contact) | Data corruption, restore needed |
| Platform Team | Railway Support | Infrastructure issues |

---

## Appendix: Environment Variables Reference

### backup-service

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | - | PostgreSQL connection |
| CLICKHOUSE_HOST | Yes | - | ClickHouse hostname |
| CLICKHOUSE_PASSWORD | Yes | - | ClickHouse password |
| MINIO_ENDPOINT | Yes | - | MinIO endpoint |
| BACKUP_SCHEDULE | No | daily | hourly/daily/weekly |
| BACKUP_RETENTION_DAYS | No | 7 | Retention period |
| ALERT_WEBHOOK_URL | No | - | Slack/Discord webhook |

### health-monitor

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | - | PostgreSQL connection |
| REDIS_HOST | Yes | - | Redis hostname |
| CHECK_INTERVAL | No | 60 | Seconds between checks |
| FAILURE_THRESHOLD | No | 3 | Failures before alert |
| ALERT_WEBHOOK_URL | No | - | Slack/Discord webhook |
| PAGERDUTY_ROUTING_KEY | No | - | PagerDuty integration |
