# Mem0 Semantic Memory

## 🎯 Recommended: Cloud-Hosted mem0.ai

The **cloud-hosted** mem0.ai service is the **easiest and most reliable** option:

### Setup (2 steps)

1. **Sign up** for a free account at https://app.mem0.ai

2. **Configure** your agent:
   ```bash
   # Add to .env file
   MEMORY_TYPE=mem0
   MEM0_API_KEY=your-mem0-api-key
   MEM0_ORG_ID=your-org-id
   ```

3. **Restart** your agent - semantic memory is now active!

### Benefits
- ✅ Zero setup - works immediately
- ✅ No Docker, no dependencies
- ✅ Automatic persistence across sessions
- ✅ Team collaboration support
- ✅ Free tier available

---

## ⚠️ Self-Hosted Docker (Currently Broken)

**Status**: The official `mem0/mem0-api-server:latest` Docker image is **broken** due to missing dependencies.

**Issue**: The image has a hardcoded configuration that requires PostgreSQL+pgvector, but doesn't include the `psycopg/psycopg2` Python libraries. This affects **all Docker deployment methods** (simple `docker run`, docker-compose, etc.).

**Upstream Issue**: This is a problem with the mem0 project's official Docker image, not our configuration.

### What We Tried

```bash
# Simple approach (also fails)
docker run --rm \
  -e OPENAI_API_KEY=sk-yourkey \
  -p 8000:8000 \
  mem0/mem0-api-server:latest

# Error: ImportError: Neither 'psycopg' nor 'psycopg2' library is available
```

### Workarounds (if you need self-hosted)

1. **Wait for mem0 team to fix** the official Docker image
2. **Build custom image** with required dependencies (adds complexity)
3. **Use cloud service** (recommended - works now)

---

## 🧪 Self-Hosted Attempts (For Reference)

We tried both simple and complex approaches - **both fail due to the broken upstream image**:

### Simple Docker Run (Doesn't Work)

```bash
docker run --rm \
  -e OPENAI_API_KEY=sk-yourkey \
  -p 8000:8000 \
  mem0/mem0-api-server:latest

# Error: ImportError: Neither 'psycopg' nor 'psycopg2' library is available
```

### Docker Compose (Also Doesn't Work)

```bash
# Using the included docker-compose.yml
docker compose -f docker/mem0/docker-compose.yml up -d

# Or via CLI
agent --memory start

# Same error - image is broken
```

### Why It Fails

The `mem0/mem0-api-server:latest` image:
1. Has a hardcoded `DEFAULT_CONFIG` that tries to use PostgreSQL+pgvector
2. Doesn't include the required `psycopg`/`psycopg2` Python libraries
3. Crashes on startup before it can accept HTTP requests

### If You Really Need Self-Hosted

**Option 1**: Wait for mem0 team to fix the image (check https://github.com/mem0ai/mem0/issues)

**Option 2**: Build custom image (adds complexity):
```dockerfile
FROM mem0/mem0-api-server:latest
RUN pip install psycopg[pool] qdrant-client
# Then configure with custom config.yaml
```

**Option 3**: Use the Python `mem0ai` package directly without Docker:
```bash
pip install mem0ai
# Use as library in your code
```

---

## 📝 Keeping Docker Files for Future

The `docker-compose.yml` is kept in this directory for when the official image is fixed. It's configured as simply as possible:
- Just the mem0 container
- OPENAI_API_KEY from environment
- Ephemeral storage (no persistence)
- Port 8000 exposed

Once the upstream image is fixed, `agent --memory start` will work immediately.
