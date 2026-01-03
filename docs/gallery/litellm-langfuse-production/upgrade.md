!!! info "Source Repository"
    This documentation is from [amiable-dev/litellm-langfuse-railway](https://github.com/amiable-dev/litellm-langfuse-railway).
    Last synced: 2026-01-03 | Commit: `5a45454`

# Upgrade Guide

This guide covers upgrading components of the LiteLLM + Langfuse Production Stack.

## Table of Contents

1. [Upgrading to HA PostgreSQL](#upgrading-to-ha-postgresql)
2. [Upgrading LiteLLM](#upgrading-litellm)
3. [Upgrading Langfuse](#upgrading-langfuse)
4. [Upgrading Redis](#upgrading-redis)

---

## Upgrading to HA PostgreSQL

Railway offers a High Availability PostgreSQL cluster with automatic failover. This upgrade is recommended when:

- You need 99.9%+ uptime for your database
- You're processing >10,000 LLM requests/day
- You have compliance requirements for data redundancy

### Prerequisites

- Current stack deployed and healthy
- Recent backup (verify in MinIO)
- 30-60 minutes maintenance window

### Step 1: Deploy HA PostgreSQL Cluster

1. Open Railway Dashboard
2. Click "New" → "Template"
3. Search for "PostgreSQL HA" or use: `railway.app/template/high-availability-postgresql`
4. Deploy into your existing project

The HA cluster includes:
- 3 PostgreSQL nodes (pg-0, pg-1, pg-2)
- PgPool for connection pooling and failover
- Automatic replication

### Step 2: Run Migration

1. Deploy the migration service:
   - Template: `railway.app/template/VgqHWg`
   - Or repository: `github.com/railwayapp-templates/pg-migrate-ha`

2. Configure variables:
   ```
   STANDALONE_URL=${{postgres.DATABASE_URL}}
   PRIMARY_URL=${{pg-0.DATABASE_URL}}
   ```

3. Deploy and monitor logs for completion

### Step 3: Verify Migration

```bash
# Connect to HA cluster
psql "$HA_DATABASE_URL" -c "SELECT count(*) FROM litellm_keys"
psql "$HA_DATABASE_URL" -c "SELECT count(*) FROM langfuse_projects"
```

Compare counts with original database.

### Step 4: Update Service References

Update all services to point to PgPool:

1. In Railway Dashboard, update each service's `DATABASE_URL`:
   - litellm
   - langfuse-web
   - langfuse-worker
   - backup-service
   - health-monitor

2. Use PgPool's DATABASE_URL (not individual nodes):
   ```
   DATABASE_URL=${{pgpool.DATABASE_URL}}
   ```

### Step 5: Verify Connectivity

```bash
# Check each service can connect
curl https://your-litellm-url/health
curl https://your-langfuse-url/api/public/health
curl https://your-health-monitor-url/health
```

### Step 6: Remove Old Database

Once verified (recommend waiting 24-48 hours):

1. Take final backup of old database
2. Delete standalone postgres service
3. Update backup-service to backup HA cluster

### Rollback Plan

If issues arise:

1. Update all `DATABASE_URL` references back to standalone
2. Restart all services
3. Investigate HA cluster issues

---

## Upgrading LiteLLM

### Minor Version Updates

LiteLLM releases frequently. For minor updates:

1. **Check changelog:**
   - https://github.com/BerriAI/litellm/releases

2. **Update image tag in railway.toml:**
   ```toml
   [services.litellm.source]
   image = "ghcr.io/berriai/litellm-database:main-stable"
   ```

3. **Deploy:**
   ```bash
   railway up
   ```

4. **Verify:**
   ```bash
   curl https://your-litellm-url/health
   ```

### Major Version Updates

For major versions (e.g., v1 → v2):

1. Review breaking changes in changelog
2. Test in staging environment first
3. Schedule maintenance window
4. Update and deploy
5. Run smoke tests
6. Monitor for errors

### Rollback

If issues occur:

1. Update image tag to previous version
2. Deploy immediately
3. Investigate issue in logs

---

## Upgrading Langfuse

### Version Updates

Langfuse follows semantic versioning. Check releases at:
- https://github.com/langfuse/langfuse/releases

#### Langfuse 2.x → 3.x Migration

Langfuse 3.x introduced ClickHouse as analytics database. This template already uses v3.

For v2 → v3:
1. Deploy ClickHouse service
2. Update Langfuse images to v3
3. Configure CLICKHOUSE_* environment variables
4. Historical data will be migrated automatically

### Update Procedure

1. **Update both images together:**
   ```toml
   [services.langfuse-web.source]
   image = "langfuse/langfuse:3"
   
   [services.langfuse-worker.source]
   image = "langfuse/langfuse-worker:3"
   ```

2. **Deploy:**
   ```bash
   railway up
   ```

3. **Verify:**
   ```bash
   curl https://your-langfuse-url/api/public/health
   ```

4. **Check migrations:**
   - View langfuse-web logs for migration status
   - Confirm UI loads correctly

---

## Upgrading Redis

### Minor Version Updates

1. **Update image:**
   ```toml
   [services.redis.source]
   image = "bitnami/redis:7.4"  # New version
   ```

2. **Deploy:**
   - Redis will restart with data preserved (AOF enabled)

3. **Verify:**
   ```bash
   redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD ping
   ```

### Major Version Updates (6.x → 7.x)

1. Create backup:
   ```bash
   redis-cli -h $REDIS_HOST -a $REDIS_PASSWORD BGSAVE
   ```

2. Update image and deploy

3. If issues, Redis will recover from AOF on restart

### Upgrading to Redis Cluster

For high availability Redis (rare requirement):

1. Deploy Redis Sentinel or Redis Cluster template
2. Update all REDIS_* environment variables
3. Test connectivity from all services
4. Remove standalone Redis

---

## General Upgrade Best Practices

### Before Any Upgrade

1. ✅ Review changelog for breaking changes
2. ✅ Verify recent backup exists
3. ✅ Test in staging if possible
4. ✅ Schedule maintenance window
5. ✅ Notify stakeholders

### During Upgrade

1. Monitor deployment logs
2. Check health endpoints immediately
3. Run smoke tests
4. Watch for error spikes

### After Upgrade

1. Verify all services healthy
2. Check key functionality
3. Monitor for 24 hours
4. Document any issues

### Rollback Triggers

Immediately rollback if:
- Health checks fail after 5 minutes
- Error rate >5% for 10 minutes
- Core functionality broken
- Data integrity issues

---

## Version Compatibility Matrix

| Component | Minimum | Recommended | Maximum |
|-----------|---------|-------------|---------|
| LiteLLM | 1.30+ | latest stable | - |
| Langfuse | 3.0+ | latest v3 | - |
| PostgreSQL | 14 | 16 | 16 |
| ClickHouse | 23+ | 24 | - |
| Redis | 7.0 | 7.2 | 7.4 |
| MinIO | 2023+ | latest | - |

---

## Support

If you encounter issues during upgrades:

1. Check service logs in Railway Dashboard
2. Review this guide's troubleshooting sections
3. Open issue on GitHub repository
4. Contact Railway support for infrastructure issues
