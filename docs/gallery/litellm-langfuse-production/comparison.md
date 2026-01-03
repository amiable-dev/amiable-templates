!!! info "Source Repository"
    This documentation is from [amiable-dev/litellm-langfuse-railway](https://github.com/amiable-dev/litellm-langfuse-railway).
    Last synced: 2026-01-03 | Commit: `5a45454`

# Starter vs Production: Which Template Do You Need?

## Quick Decision Guide

| You Need... | Choose |
|-------------|--------|
| Quick POC or development | **Starter** |
| Team evaluation | **Starter** |
| Side project | **Starter** |
| Production API | **Production** |
| Customer-facing product | **Production** |
| Enterprise deployment | **Production** |

---

## Feature Comparison

### Core Features (Both Templates)

| Feature | Starter | Production |
|---------|:-------:|:----------:|
| LiteLLM Gateway | ✅ | ✅ |
| 100+ LLM Provider Support | ✅ | ✅ |
| Langfuse Observability | ✅ | ✅ |
| Virtual Keys & Budgets | ✅ | ✅ |
| Cost Tracking | ✅ | ✅ |
| Prompt Management | ✅ | ✅ |
| PostgreSQL Database | ✅ | ✅ |
| ClickHouse Analytics | ✅ | ✅ |
| Redis Caching | ✅ | ✅ |
| MinIO Storage | ✅ | ✅ |

### Resilience Features

| Feature | Starter | Production |
|---------|:-------:|:----------:|
| Automated DB Backups | ❌ | ✅ Daily |
| ClickHouse Backups | ❌ | ✅ Daily |
| Backup Retention | ❌ | ✅ 7 days |
| Redis AOF Persistence | ❌ | ✅ |
| Health Monitoring | ❌ | ✅ All services |
| Slack/Discord Alerts | ❌ | ✅ |
| PagerDuty Integration | ❌ | ✅ |
| Prometheus Metrics | ❌ | ✅ |
| Enhanced Restart Policies | Basic | ✅ 10 retries |
| Operations Runbook | ❌ | ✅ |
| Upgrade Documentation | ❌ | ✅ |

### Observability

| Feature | Starter | Production |
|---------|:-------:|:----------:|
| Service Health Dashboard | ❌ | ✅ JSON API |
| Response Time Tracking | ❌ | ✅ Per service |
| Failure Alerting | ❌ | ✅ Configurable |
| Recovery Notifications | ❌ | ✅ |
| Metrics Endpoint | ❌ | ✅ /metrics |

---

## Cost Comparison

### Starter Template

| Service | Est. Monthly |
|---------|-------------|
| LiteLLM | $5-15 |
| Langfuse Web | $5-10 |
| Langfuse Worker | $3-8 |
| PostgreSQL | $5-10 |
| ClickHouse | $5-15 |
| Redis | $3-5 |
| MinIO | $3-5 |
| **Total** | **$29-68/mo** |

### Production Template

| Service | Est. Monthly |
|---------|-------------|
| (All Starter services) | $29-68 |
| Backup Service | $2-5 |
| Health Monitor | $2-5 |
| **Total** | **$33-78/mo** |

**Production adds ~$4-10/mo for significant resilience improvements.**

---

## Use Case Examples

### Starter is Right For:

**1. Development Environment**
- Testing LLM integrations
- Prompt development
- Team experimentation

**2. Early Stage Startup**
- MVP development
- Initial customer pilots
- Budget constraints

**3. Personal Projects**
- Side projects
- Learning/exploration
- Open source contributions

### Production is Right For:

**1. Customer-Facing API**
- SaaS products using LLMs
- AI-powered features
- Revenue-generating services

**2. Enterprise Internal Tools**
- Company-wide LLM gateway
- Compliance requirements
- Audit trails needed

**3. High-Stakes Applications**
- Healthcare AI assistants
- Financial analysis tools
- Legal document processing

---

## Migration Path

### Starter → Production

If you start with Starter and need to upgrade:

1. **Deploy Production template** alongside existing
2. **Migrate data** using pg_dump/restore
3. **Update DNS/endpoints** to point to new stack
4. **Verify functionality**
5. **Decommission Starter** stack

### Timeline: 1-2 hours for small deployments

---

## FAQ

**Q: Can I add backups to Starter myself?**

A: Yes, but Production template saves you time:
- Pre-configured backup service
- Tested retention policies
- Alert integration included
- Documentation for restore

**Q: Is Production overkill for my use case?**

A: Ask yourself:
- Would 4 hours of downtime cost you customers?
- Would data loss set you back weeks?
- Do you need audit trails?

If any answer is "yes," Production is worth $5-10/mo extra.

**Q: Can I upgrade later?**

A: Yes, but it's easier to start with Production if you expect to need it. Migration requires:
- Database export/import
- Service reconfiguration
- Testing period

**Q: What about Railway's HA PostgreSQL?**

A: Production template is designed to work with it. See [UPGRADE.md](https://github.com/amiable-dev/litellm-langfuse-railway/blob/5a45454c15e0e5e17ff20a3f0d6df421c1f037db/production/docs/docs/UPGRADE.md) for migration steps when you're ready for even higher availability.

---

## Summary

| Criteria | Starter | Production |
|----------|---------|------------|
| **Setup Time** | 5 min | 5 min |
| **Monthly Cost** | $30-70 | $35-80 |
| **Recovery Time** | Hours-Days | Minutes |
| **Data Loss Risk** | High | Low |
| **Alert Coverage** | None | Full |
| **Documentation** | Basic | Comprehensive |
| **Maintenance Burden** | Higher | Lower |

**Our Recommendation:**
- **Experimenting?** → Starter
- **Building a product?** → Production from Day 1
