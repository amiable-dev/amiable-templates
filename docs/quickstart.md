---
title: Quick Start
---

# Quick Start

Get a production-ready AI infrastructure stack deployed to Railway in under 5 minutes.

## Prerequisites

- A [Railway](https://railway.app) account
- API keys for your preferred LLM providers (OpenAI, Anthropic, etc.)

## Choose Your Template

### Option 1: LiteLLM + Langfuse Starter

Best for: Getting started quickly, development, small teams.

**Includes:**

- LiteLLM proxy (unified LLM API)
- Langfuse (observability & tracing)
- PostgreSQL database

**Deploy:**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/litellm-langfuse)

### Option 2: LiteLLM + Langfuse Production

Best for: Production workloads, enterprise teams.

**Includes everything in Starter, plus:**

- Automated daily backups
- Health monitoring & alerts
- Redis with AOF persistence
- Operations runbook

[View Production Template →](gallery/index.md)

## Post-Deployment Setup

### 1. Configure Environment Variables

After deployment, configure these required variables in Railway:

```bash
# Required: Your LLM API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Additional providers
AZURE_API_KEY=...
GOOGLE_API_KEY=...
```

### 2. Access Your Services

Once deployed, you'll have URLs for:

| Service | Purpose | URL Pattern |
|---------|---------|-------------|
| LiteLLM | LLM API Gateway | `https://litellm-xxx.railway.app` |
| Langfuse | Observability UI | `https://langfuse-xxx.railway.app` |

### 3. Test Your Setup

Test the LiteLLM proxy:

```bash
curl https://your-litellm-url.railway.app/health
```

Make your first request:

```bash
curl https://your-litellm-url.railway.app/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_LITELLM_KEY" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### 4. View Traces in Langfuse

1. Open your Langfuse URL
2. Log in with the default credentials (check Railway variables)
3. Navigate to **Traces** to see your requests

## Next Steps

- [Configure LiteLLM models](gallery/index.md) - Add more providers
- [Set up monitoring](gallery/index.md) - Configure alerts
- [Read the runbook](gallery/index.md) - Operations guide

## Troubleshooting

### Common Issues

**Service not starting:**

- Check Railway logs for errors
- Verify all required environment variables are set

**API requests failing:**

- Verify your LLM API keys are valid
- Check the LiteLLM `/health` endpoint

**Can't access Langfuse:**

- Ensure the Langfuse service has finished deploying
- Check that PostgreSQL is healthy

### Getting Help

- [GitHub Discussions](https://github.com/amiable-dev/amiable-templates/discussions) - Ask questions
- [GitHub Issues](https://github.com/amiable-dev/amiable-templates/issues) - Report bugs
- [SUPPORT.md](https://github.com/amiable-dev/amiable-templates/blob/main/SUPPORT.md) - Support channels
