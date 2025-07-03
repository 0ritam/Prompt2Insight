# Prompt2Insight Backend

## Quick Start

### Option 1: PowerShell (Recommended for Windows)
```powershell
.\start-server.ps1
```

### Option 2: Batch File
```cmd
start-server.bat
```

### Option 3: Direct Python
```bash
python server.py
```

### Option 4: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python server.py
```

## Server Information

- **URL:** http://localhost:8001
- **API Documentation:** http://localhost:8001/docs
- **Health Check:** http://localhost:8001/health

## API Endpoints

- `POST /scrape-structured` - Main scraping endpoint
- `GET /health` - Health check
- `GET /` - Server status

## Environment

The server will automatically:
- Check for Python installation
- Install missing dependencies
- Start the FastAPI server with auto-reload
- Show helpful status messages

## Troubleshooting

If you get import errors, make sure you're running from the `p2i-backend` directory and all dependencies are installed.
