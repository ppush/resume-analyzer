# Docker Setup for Resume Analyzer

## Quick Start

### 1. Build Image
```bash
# Using script
chmod +x docker-scripts/build.sh
./docker-scripts/build.sh

# Or manually
docker build -t resume-analyzer:latest .
```

### 2. Run with Local LM Studio
```bash
# Make sure LM Studio is running on localhost:1234
# Then run:
chmod +x docker-scripts/run.sh
./docker-scripts/run.sh

# Or manually:
docker-compose up
```

### 3. Run in Development Mode
```bash
chmod +x docker-scripts/dev.sh
./docker-scripts/dev.sh

# Or manually:
docker-compose -f docker-compose.dev.yml up
```

## Configuration

### Environment Variables

You can override settings through environment variables:

```bash
# In docker-compose.yml or through -e
docker run -e DEFAULT_MODEL="meta-llama-3.1-8b-instruct" resume-analyzer:latest
```

### Mounted Folders

- `./tests/resources` → `/app/tests/resources` - test files
- `./results` → `/app/results` - analysis results
- `./logs` → `/app/logs` - application logs

## File Structure

```
├── Dockerfile                 # Main Docker image
├── docker-compose.yml         # Production configuration
├── docker-compose.dev.yml     # Development configuration
├── .dockerignore             # Docker exclusions
├── docker-scripts/           # Management scripts
│   ├── build.sh             # Build image
│   ├── run.sh               # Run application
│   └── dev.sh               # Development mode
└── DOCKER.md                # This documentation
```

## Docker Commands

### Basic Commands
```bash
# Build
docker build -t resume-analyzer:latest .

# Run
docker run -it resume-analyzer:latest

# Run with mounted folders
docker run -v $(pwd)/tests/resources:/app/tests/resources \
           -v $(pwd)/results:/app/results \
           -it resume-analyzer:latest

# View logs
docker logs resume-analyzer

# Stop
docker stop resume-analyzer
```

### Docker Compose Commands
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop
docker-compose down

# Rebuild
docker-compose up --build

# View logs
docker-compose logs -f resume-analyzer
```

## Operation Modes

### 1. Production Mode
- Uses `docker-compose.yml`
- Optimized for performance
- Minimal image size

### 2. Development Mode
- Uses `docker-compose.dev.yml`
- Mounts source code
- Includes debug logs
- Interactive mode

## LM Studio

### Option 1: Local LM Studio
1. Start LM Studio locally on port 1234
2. Use `LM_STUDIO_URL=http://host.docker.internal:1234/v1/chat/completions`

### Option 2: LM Studio in Docker
1. Uncomment `lm-studio` section in `docker-compose.yml`
2. Run: `docker-compose --profile lm-studio up`

## Troubleshooting

### Problem: LM Studio Unavailable
```bash
# Check that LM Studio is running
curl http://localhost:1234/v1/models

# For Docker use host.docker.internal
curl http://host.docker.internal:1234/v1/models
```

### Problem: No File Access
```bash
# Check permissions
ls -la tests/resources/
chmod 755 tests/resources/
```

### Problem: Container Won't Start
```bash
# Check logs
docker logs resume-analyzer

# Check configuration
docker-compose config
```

## Performance

### Image Optimization
- Uses `python:3.11-slim` for minimal size
- Multi-stage build for dependency caching
- `.dockerignore` excludes unnecessary files

### Monitoring
```bash
# Resource usage
docker stats resume-analyzer

# Image size
docker images resume-analyzer
```
