# Mem0 Semantic Memory - Docker Compose

⚠️ **Note**: The self-hosted Docker setup is currently experiencing compatibility issues with the official `mem0/mem0-api-server` Docker image. For immediate use, please use the **cloud-hosted mem0.ai service** instead.

## Cloud Setup (Recommended)

Sign up for a free account at https://app.mem0.ai and configure:

```bash
# Add to your .env file
MEMORY_TYPE=mem0
MEM0_API_KEY=your-mem0-api-key
MEM0_ORG_ID=your-org-id
```

Then restart your agent and it will automatically use mem0 cloud storage.

## Self-Hosted Setup (Experimental)

⚠️ This configuration is experimental and may require custom Docker image builds.

### Prerequisites

**Required**: You must have an OpenAI API key configured. The mem0 server uses OpenAI for embedding generation and memory extraction.

```bash
# Add to your .env file in the project root
echo "OPENAI_API_KEY=your-api-key-here" >> .env

# Or export it
export OPENAI_API_KEY=your-api-key-here
```

### Known Issues

- The official `mem0/mem0-api-server` Docker image has dependency issues with PostgreSQL/pgvector
- Working on a custom Docker image with proper dependencies
- For production use, please use the cloud-hosted service

## Quick Start

### 1. Start the mem0 server

```bash
# From project root
docker compose -f docker/mem0/docker-compose.yml up -d

# Or using agent CLI (recommended)
agent --memory start
```

### 2. Verify services are running

```bash
docker compose -f docker/mem0/docker-compose.yml ps

# Or using agent CLI
agent --memory status
```

### 3. Configure your agent

```bash
# Add to .env or export
export MEMORY_TYPE=mem0
export MEM0_HOST=http://localhost:8000
```

### 4. Stop the services

```bash
docker compose -f docker/mem0/docker-compose.yml down

# Or using agent CLI
agent --memory stop
```

## Services

- **Qdrant**: Ports 6333, 6334
  - Vector database for storing embeddings
  - Dashboard: http://localhost:6333/dashboard
  - Health check: http://localhost:6333/health

- **mem0 Server**: Port 8000
  - Semantic memory API
  - API docs: http://localhost:8000/docs
  - Health check: http://localhost:8000/

## Data Persistence

Data is persisted in a Docker volume: `mem0_qdrant_data`

To completely remove data:
```bash
docker compose -f docker/mem0/docker-compose.yml down -v
```

## Configuration

Environment variables can be customized in the docker-compose.yml file:

**Required:**
- `OPENAI_API_KEY`: Your OpenAI API key (read from host environment)

**Vector Store (Optional):**
- `VECTOR_STORE_PROVIDER`: Vector database provider (default: qdrant)
- `QDRANT_HOST`: Qdrant hostname (default: qdrant)
- `QDRANT_PORT`: Qdrant port (default: 6333)

## Troubleshooting

### Check logs
```bash
# All services
docker compose -f docker/mem0/docker-compose.yml logs

# Specific service
docker compose -f docker/mem0/docker-compose.yml logs mem0
docker compose -f docker/mem0/docker-compose.yml logs qdrant
```

### Restart services
```bash
docker compose -f docker/mem0/docker-compose.yml restart
```

### Port conflicts
If port 8000, 6333, or 6334 is already in use, modify the ports in docker-compose.yml:
```yaml
ports:
  - "8001:8000"  # Map to different host port
```

Then update your configuration:
```bash
export MEM0_HOST=http://localhost:8001
```
