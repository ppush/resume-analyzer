# 🐳 Resume Analyzer - Docker Setup

Complete Docker configuration for Resume Analyzer with LM Studio support.

## 📁 File Structure

```
├── Dockerfile                 # Main Docker image
├── docker-compose.yml         # Production configuration
├── docker-compose.dev.yml     # Development configuration
├── .dockerignore             # Docker exclusions
├── docker-scripts/           # Management scripts
│   ├── build.sh/.ps1        # Build image
│   ├── run.sh/.ps1          # Run application
│   └── dev.sh/.ps1          # Development mode
├── DOCKER.md                # Detailed documentation
└── README-DOCKER.md         # This file
```

## 🚀 Quick Start

### Windows (PowerShell)
```powershell
# 1. Build image
.\docker-scripts\build.ps1

# 2. Run application
.\docker-scripts\run.ps1

# 3. Development mode
.\docker-scripts\dev.ps1
```

### Linux/macOS (Bash)
```bash
# 1. Build image
chmod +x docker-scripts/build.sh
./docker-scripts/build.sh

# 2. Run application
chmod +x docker-scripts/run.sh
./docker-scripts/run.sh

# 3. Development mode
chmod +x docker-scripts/dev.sh
./docker-scripts/dev.sh
```

## ⚙️ Configuration

### Environment Variables
```yaml
environment:
  - LM_STUDIO_URL=http://host.docker.internal:1234/v1/chat/completions
  - DEFAULT_MODEL=google/gemma-3-12b
  - LLM_TIMEOUT=120
  - LOG_LEVEL=INFO
```

### Mounted Folders
- `./tests/resources` → `/app/tests/resources` - test files
- `./results` → `/app/results` - analysis results
- `./logs` → `/app/logs` - application logs

## 🔧 Operation Modes

### 1. Production Mode
```bash
docker-compose up
```
- Optimized for performance
- Minimal image size
- Automatic restart

### 2. Development Mode
```bash
docker-compose -f docker-compose.dev.yml up
```
- Mounts source code
- Debug logs
- Interactive mode

## 🤖 LM Studio

### Option 1: Local LM Studio
1. Start LM Studio locally on port 1234
2. Docker will automatically connect via `host.docker.internal`

### Option 2: LM Studio in Docker
1. Uncomment `lm-studio` section in `docker-compose.yml`
2. Run: `docker-compose --profile lm-studio up`

## 📊 Monitoring

```bash
# View logs
docker-compose logs -f resume-analyzer

# Resource usage
docker stats resume-analyzer

# Image size
docker images resume-analyzer
```

## 🛠️ Troubleshooting

### Docker Not Running
```bash
# Start Docker Desktop
# Or check status
docker version
```

### LM Studio Unavailable
```bash
# Check that LM Studio is running
curl http://localhost:1234/v1/models

# For Docker use
curl http://host.docker.internal:1234/v1/models
```

### Permission Issues
```bash
# Check folder permissions
ls -la tests/resources/
chmod 755 tests/resources/
```

## 🎯 Usage Examples

### Resume Analysis
```bash
# Run with mounted files
docker run -v $(pwd)/tests/resources:/app/tests/resources \
           -v $(pwd)/results:/app/results \
           -it resume-analyzer:latest
```

### Integration Tests
```bash
# Run tests in container
docker run -v $(pwd)/tests:/app/tests \
           -it resume-analyzer:latest \
           python tests/integration/test_resume_parser_integration.py
```

## 📈 Performance

- **Image size**: ~500MB (Python 3.11-slim)
- **Build time**: ~2-3 minutes
- **Startup time**: ~10-15 seconds
- **Memory**: ~200-300MB at runtime

## 🔒 Security

- User `app` for running (not root)
- Minimal access rights
- Isolated network
- Only necessary ports

## 📝 Logs

Logs are saved to:
- Container: `/app/logs/`
- Host: `./logs/`

Log levels:
- `DEBUG` - for development
- `INFO` - for production
- `ERROR` - errors only

---

**Ready to use!** 🎉

For detailed documentation see [DOCKER.md](DOCKER.md)
