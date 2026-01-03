!!! info "Source Repository"
    This documentation is from [amiable-dev/litellm-langfuse-railway](https://github.com/amiable-dev/litellm-langfuse-railway).
    Last synced: 2026-01-03 | Commit: `5a45454`

# LiteLLM + Langfuse: LLM Gateway with Full Observability

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/litellm-langfuse)

A production-ready LLM gateway that provides a unified API for 100+ LLM providers with full observability, cost tracking, and rate limiting.

## 🎯 What You Get

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Your Applications                            │
│         (Any app using OpenAI SDK format - Python, JS, etc.)       │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         LiteLLM Proxy                               │
│  • Unified OpenAI-compatible API                                    │
│  • 100+ LLM providers (OpenAI, Claude, Gemini, Bedrock, etc.)      │
│  • Virtual keys with budgets                                        │
│  • Rate limiting & load balancing                                   │
│  • Cost tracking per key/team                                       │
│  • Automatic fallbacks                                              │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          Langfuse                                   │
│  • Full trace visibility                                            │
│  • Token usage & cost analytics                                     │
│  • Prompt management & versioning                                   │
│  • Evaluation pipelines                                             │
│  • Team collaboration                                               │
└─────────────────────────────────────────────────────────────────────┘
```

## 🏗️ Architecture

| Service | Purpose | Port |
|---------|---------|------|
| **LiteLLM** | LLM Gateway/Proxy | 4000 |
| **Langfuse Web** | Observability UI & API | 3000 |
| **Langfuse Worker** | Async trace processing | 3030 |
| **PostgreSQL** | Transactional data | 5432 |
| **ClickHouse** | Analytics (traces, scores) | 8123/9000 |
| **Redis** | Caching & queues | 6379 |
| **MinIO** | Object storage (S3-compatible) | 9000 |

## 🚀 Quick Start

### 1. Deploy to Railway

Click the button above or use Railway CLI:

```bash
railway init --template litellm-langfuse
railway up
```

### 2. Get Your Endpoints

After deployment, you'll have two public URLs:

- **LiteLLM**: `https://litellm-xxx.up.railway.app`
- **Langfuse**: `https://langfuse-web-xxx.up.railway.app`

### 3. Configure LiteLLM with Your API Keys

Access the LiteLLM Admin UI:
```
URL: https://litellm-xxx.up.railway.app/ui
Username: admin
Password: (from LITELLM_MASTER_KEY or UI_PASSWORD env var)
```

Add your LLM provider keys via the UI or API:

```bash
# Add OpenAI
curl -X POST 'https://litellm-xxx.up.railway.app/model/new' \
  -H 'Authorization: Bearer YOUR_LITELLM_MASTER_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "model_name": "gpt-4o",
    "litellm_params": {
      "model": "openai/gpt-4o",
      "api_key": "sk-YOUR_OPENAI_KEY"
    }
  }'

# Add Claude
curl -X POST 'https://litellm-xxx.up.railway.app/model/new' \
  -H 'Authorization: Bearer YOUR_LITELLM_MASTER_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "model_name": "claude-sonnet",
    "litellm_params": {
      "model": "anthropic/claude-sonnet-4-20250514",
      "api_key": "sk-ant-YOUR_ANTHROPIC_KEY"
    }
  }'
```

### 4. Connect Langfuse to LiteLLM

Get your Langfuse API keys from the Langfuse UI:
1. Open `https://langfuse-web-xxx.up.railway.app`
2. Create an account and project
3. Go to Settings → API Keys
4. Copy the public and secret keys

Update LiteLLM environment variables in Railway:
```
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_SECRET_KEY=sk-lf-xxx
```

### 5. Start Using It!

```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_LITELLM_MASTER_KEY",  # or a virtual key
    base_url="https://litellm-xxx.up.railway.app"
)

response = client.chat.completions.create(
    model="gpt-4o",  # or "claude-sonnet", etc.
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

All requests are automatically traced in Langfuse! 🎉

## 💰 Cost Tracking & Budgets

### Create Virtual Keys with Budgets

```bash
# Create a key with $100/month budget
curl -X POST 'https://litellm-xxx.up.railway.app/key/generate' \
  -H 'Authorization: Bearer YOUR_LITELLM_MASTER_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "models": ["gpt-4o", "claude-sonnet"],
    "max_budget": 100,
    "budget_duration": "1mo",
    "metadata": {"team": "engineering"}
  }'
```

### Track Spending

```bash
# Get spend by key
curl 'https://litellm-xxx.up.railway.app/spend/keys' \
  -H 'Authorization: Bearer YOUR_LITELLM_MASTER_KEY'

# Get spend by model
curl 'https://litellm-xxx.up.railway.app/spend/models' \
  -H 'Authorization: Bearer YOUR_LITELLM_MASTER_KEY'
```

## 📊 Observability with Langfuse

### View Traces

Open Langfuse UI to see:
- Every LLM request with full context
- Token usage and costs
- Latency metrics
- Error rates
- User sessions

### Prompt Management

1. Create prompt templates in Langfuse UI
2. Version and A/B test prompts
3. Fetch prompts via API:

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk-lf-xxx",
    secret_key="sk-lf-xxx",
    host="https://langfuse-web-xxx.up.railway.app"
)

prompt = langfuse.get_prompt("my-prompt-template")
compiled = prompt.compile(variable="value")
```

### Evaluations

Run LLM-as-judge evaluations:

```python
from langfuse import Langfuse

langfuse = Langfuse(...)

# Score a trace
langfuse.score(
    trace_id="xxx",
    name="helpfulness",
    value=0.9,
    comment="Response was helpful"
)
```

## 🔧 Configuration

### LiteLLM Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LITELLM_MASTER_KEY` | Admin API key (starts with sk-) | Yes |
| `LITELLM_SALT_KEY` | Encryption key for stored credentials | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key | For tracing |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key | For tracing |
| `LANGFUSE_HOST` | Langfuse URL | For tracing |

### Langfuse Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXTAUTH_SECRET` | Session encryption | Yes |
| `SALT` | Data encryption salt | Yes |
| `ENCRYPTION_KEY` | 32-byte hex encryption key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `CLICKHOUSE_URL` | ClickHouse HTTP URL | Yes |
| `REDIS_HOST` | Redis hostname | Yes |

## 📈 Scaling

### Horizontal Scaling

For high-throughput scenarios:

1. **LiteLLM**: Add more replicas via Railway settings
2. **Langfuse Worker**: Scale workers for faster trace processing
3. **Redis**: Consider Railway Redis add-on for HA

### Recommended Resources

| Load Level | LiteLLM | Langfuse | PostgreSQL | ClickHouse |
|------------|---------|----------|------------|------------|
| Low (<100 req/min) | 512MB | 512MB | 256MB | 512MB |
| Medium (<1k req/min) | 1GB | 1GB | 512MB | 1GB |
| High (<10k req/min) | 2GB | 2GB | 1GB | 2GB |

## 🔐 Security Best Practices

1. **Rotate keys regularly**: Generate new `LITELLM_MASTER_KEY` periodically
2. **Use virtual keys**: Don't expose master key to applications
3. **Set budgets**: Prevent runaway costs with key budgets
4. **Enable RBAC**: Use Langfuse teams for access control
5. **Audit logs**: Review Langfuse traces for anomalies

## 🛠️ Troubleshooting

### LiteLLM not connecting to models

```bash
# Test model connection
curl -X POST 'https://litellm-xxx.up.railway.app/chat/completions' \
  -H 'Authorization: Bearer YOUR_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"model": "gpt-4o", "messages": [{"role": "user", "content": "test"}]}'
```

Check:
- API keys are correct in LiteLLM model config
- Model name matches what you configured

### Traces not appearing in Langfuse

1. Verify Langfuse keys are set in LiteLLM
2. Check Langfuse worker logs: `railway logs -s langfuse-worker`
3. Ensure Redis is healthy: `railway logs -s redis`

### ClickHouse migrations failing

```bash
# Check ClickHouse logs
railway logs -s clickhouse

# Verify connection
railway run -s langfuse-web -- wget -qO- http://clickhouse:8123/ping
```

## 💵 Estimated Costs

| Component | Railway Usage | Est. Cost/Month |
|-----------|---------------|-----------------|
| LiteLLM | ~$5-15 | Compute |
| Langfuse Web | ~$5-10 | Compute |
| Langfuse Worker | ~$3-8 | Compute |
| PostgreSQL | ~$5-10 | Compute + Storage |
| ClickHouse | ~$5-15 | Compute + Storage |
| Redis | ~$3-5 | Compute |
| MinIO | ~$3-5 | Compute + Storage |
| **Total** | | **$29-68/month** |

*Actual costs depend on usage. Railway charges based on resource consumption.*

## 🔗 Resources

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Langfuse Documentation](https://langfuse.com/docs)
- [Railway Documentation](https://docs.railway.com/)

## 📝 License

This template combines open-source projects:
- LiteLLM: MIT License
- Langfuse: MIT License (self-hosted)

---

Built with ❤️ for the AI developer community.

**Questions?** Open an issue or reach out on [Railway Discord](https://discord.gg/railway).
