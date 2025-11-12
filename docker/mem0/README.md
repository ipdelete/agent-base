# Mem0 Semantic Memory - Docker Compose

This directory contains the Docker Compose configuration for running mem0 semantic memory locally with PostgreSQL + pgvector.

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

- **PostgreSQL (pgvector)**: Port 5432
  - Vector database for storing embeddings
  - User: mem0, Password: mem0, DB: mem0

- **mem0 Server**: Port 8000
  - Semantic memory API
  - Health check: http://localhost:8000/health

## Data Persistence

Data is persisted in a Docker volume: `mem0_postgres_data`

To completely remove data:
```bash
docker compose -f docker/mem0/docker-compose.yml down -v
```

## Configuration

Environment variables can be customized in the docker-compose.yml file:

- `POSTGRES_DB`: Database name (default: mem0)
- `POSTGRES_USER`: Database user (default: mem0)
- `POSTGRES_PASSWORD`: Database password (default: mem0)

## Troubleshooting

### Check logs
```bash
# All services
docker compose -f docker/mem0/docker-compose.yml logs

# Specific service
docker compose -f docker/mem0/docker-compose.yml logs mem0
docker compose -f docker/mem0/docker-compose.yml logs postgres
```

### Restart services
```bash
docker compose -f docker/mem0/docker-compose.yml restart
```

### Port conflicts
If port 8000 or 5432 is already in use, modify the ports in docker-compose.yml:
```yaml
ports:
  - "8001:8000"  # Map to different host port
```

Then update your configuration:
```bash
export MEM0_HOST=http://localhost:8001
```
