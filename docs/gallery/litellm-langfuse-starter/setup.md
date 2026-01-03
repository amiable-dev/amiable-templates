!!! info "Source Repository"
    This documentation is from [amiable-dev/litellm-langfuse-railway](https://github.com/amiable-dev/litellm-langfuse-railway).
    Last synced: 2026-01-03 | Commit: `5a45454`

# Quick Setup Guide: LiteLLM + Langfuse on Railway

This guide walks you through manually setting up the stack on Railway using the web dashboard.

## Prerequisites

- Railway account (free tier works for testing)
- LLM API keys (OpenAI, Anthropic, etc.)

## Step 1: Create a New Project

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Empty Project"
4. Name it "LiteLLM-Langfuse"

## Step 2: Deploy Infrastructure Services

### 2.1 PostgreSQL

1. Click "+ New" → "Database" → "PostgreSQL"
2. Wait for deployment
3. Copy the `DATABASE_URL` from variables (you'll need this)

### 2.2 Redis

1. Click "+ New" → "Database" → "Redis"
2. Wait for deployment
3. Note the connection details:
   - `REDIS_HOST` = private domain (e.g., `redis.railway.internal`)
   - `REDIS_PORT` = 6379
   - `REDIS_PASSWORD` = from variables

### 2.3 ClickHouse

1. Click "+ New" → "Docker Image"
2. Enter: `clickhouse/clickhouse-server:24`
3. Add a volume mount: `/var/lib/clickhouse`
4. Add environment variables:
   ```
   CLICKHOUSE_DB=default
   CLICKHOUSE_USER=clickhouse
   CLICKHOUSE_PASSWORD=<generate-strong-password>
   ```
5. Deploy

### 2.4 MinIO (S3-compatible storage)

1. Click "+ New" → "Docker Image"
2. Enter: `minio/minio`
3. Add a volume mount: `/data`
4. Set start command: `minio server /data --console-address :9001`
5. Add environment variables:
   ```
   MINIO_ROOT_USER=minioadmin
   MINIO_ROOT_PASSWORD=<generate-strong-password>
   ```
6. Deploy
7. After deployment, access MinIO console (port 9001) and create a bucket named `langfuse`

## Step 3: Deploy Langfuse

### 3.1 Langfuse Web

1. Click "+ New" → "Docker Image"
2. Enter: `langfuse/langfuse:3`
3. Add environment variables:
   ```
   PORT=3000
   NEXTAUTH_URL=https://<your-langfuse-domain>.up.railway.app
   NEXTAUTH_SECRET=<generate-32-char-secret>
   SALT=<generate-salt>
   ENCRYPTION_KEY=<generate-64-char-hex>
   
   # Database
   DATABASE_URL=<from-postgres>
   
   # ClickHouse
   CLICKHOUSE_URL=http://clickhouse.railway.internal:8123
   CLICKHOUSE_MIGRATION_URL=clickhouse://clickhouse.railway.internal:9000
   CLICKHOUSE_USER=clickhouse
   CLICKHOUSE_PASSWORD=<clickhouse-password>
   
   # Redis
   REDIS_HOST=redis.railway.internal
   REDIS_PORT=6379
   REDIS_AUTH=<redis-password>
   
   # MinIO
   LANGFUSE_S3_EVENT_UPLOAD_ENDPOINT=http://minio.railway.internal:9000
   LANGFUSE_S3_EVENT_UPLOAD_BUCKET=langfuse
   LANGFUSE_S3_EVENT_UPLOAD_ACCESS_KEY_ID=minioadmin
   LANGFUSE_S3_EVENT_UPLOAD_SECRET_ACCESS_KEY=<minio-password>
   LANGFUSE_S3_EVENT_UPLOAD_FORCE_PATH_STYLE=true
   LANGFUSE_S3_EVENT_UPLOAD_REGION=us-east-1
   
   # Disable telemetry
   TELEMETRY_ENABLED=false
   ```
4. Enable public domain under Settings → Networking
5. Deploy

### 3.2 Langfuse Worker

1. Click "+ New" → "Docker Image"
2. Enter: `langfuse/langfuse-worker:3`
3. Copy all environment variables from Langfuse Web EXCEPT:
   - Change `PORT=3030`
   - Remove `NEXTAUTH_URL`
4. Deploy (no public domain needed)

## Step 4: Deploy LiteLLM

1. Click "+ New" → "Docker Image"
2. Enter: `docker.litellm.ai/berriai/litellm-database:main-stable`
3. Add environment variables:
   ```
   PORT=4000
   LITELLM_MASTER_KEY=sk-<generate-secure-key>
   LITELLM_SALT_KEY=<generate-salt>
   
   # Database
   DATABASE_URL=<from-postgres>
   
   # Redis (for caching)
   REDIS_HOST=redis.railway.internal
   REDIS_PORT=6379
   REDIS_PASSWORD=<redis-password>
   
   # Langfuse integration
   LANGFUSE_PUBLIC_KEY=<get-from-langfuse-ui>
   LANGFUSE_SECRET_KEY=<get-from-langfuse-ui>
   LANGFUSE_HOST=https://<your-langfuse-domain>.up.railway.app
   
   # UI settings
   STORE_MODEL_IN_DB=True
   UI_USERNAME=admin
   UI_PASSWORD=<generate-password>
   ```
4. Enable public domain
5. Deploy

## Step 5: Configure LiteLLM with Langfuse

1. Open Langfuse UI: `https://<your-langfuse-domain>.up.railway.app`
2. Create an account
3. Create a new project
4. Go to Settings → API Keys
5. Create a new API key
6. Copy the public and secret keys
7. Update LiteLLM's environment variables with these keys
8. Restart LiteLLM service

## Step 6: Add LLM Models to LiteLLM

Access LiteLLM Admin UI: `https://<your-litellm-domain>.up.railway.app/ui`

Or via API:

```bash
# Add OpenAI GPT-4o
curl -X POST 'https://<litellm-domain>/model/new' \
  -H 'Authorization: Bearer sk-<your-master-key>' \
  -H 'Content-Type: application/json' \
  -d '{
    "model_name": "gpt-4o",
    "litellm_params": {
      "model": "openai/gpt-4o",
      "api_key": "sk-<your-openai-key>"
    }
  }'

# Add Claude Sonnet
curl -X POST 'https://<litellm-domain>/model/new' \
  -H 'Authorization: Bearer sk-<your-master-key>' \
  -H 'Content-Type: application/json' \
  -d '{
    "model_name": "claude-sonnet",
    "litellm_params": {
      "model": "anthropic/claude-sonnet-4-20250514",
      "api_key": "sk-ant-<your-anthropic-key>"
    }
  }'
```

## Step 7: Test the Setup

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-<your-litellm-master-key>",
    base_url="https://<your-litellm-domain>.up.railway.app"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello, world!"}]
)

print(response.choices[0].message.content)
```

Then check Langfuse UI - you should see the trace!

## Generating Secrets

Use these commands to generate secure values:

```bash
# 32-character secret
openssl rand -base64 24

# 64-character hex key (for ENCRYPTION_KEY)
openssl rand -hex 32

# LiteLLM master key (must start with sk-)
echo "sk-$(openssl rand -hex 24)"
```

## Troubleshooting

### Langfuse shows "ClickHouse migration failed"
- Ensure ClickHouse is healthy: check logs
- Verify `CLICKHOUSE_URL` uses port 8123 (HTTP) and `CLICKHOUSE_MIGRATION_URL` uses port 9000 (native)

### LiteLLM can't connect to Langfuse
- Verify Langfuse public domain is enabled
- Check that `LANGFUSE_HOST` starts with `https://`
- Confirm API keys are correct

### Traces not appearing
- Check Langfuse Worker logs
- Verify Redis is connected
- Ensure MinIO bucket `langfuse` exists

## Cost Estimate

With moderate usage:
- PostgreSQL: ~$5/month
- Redis: ~$3/month
- ClickHouse: ~$8/month
- MinIO: ~$3/month
- Langfuse (web + worker): ~$10/month
- LiteLLM: ~$8/month

**Total: ~$35-40/month**

## Next Steps

1. Create virtual keys with budgets for team members
2. Set up prompt templates in Langfuse
3. Configure evaluations and scoring
4. Add more LLM providers for fallbacks
