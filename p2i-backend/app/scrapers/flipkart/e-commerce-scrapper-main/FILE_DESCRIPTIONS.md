# Flipkart Scraper Microservice - File Descriptions

## 📁 Project Structure & File Descriptions

### 🔧 **Core Application Files**

**`flipkart_api.py`** - Main FastAPI application
- RESTful API server with endpoints for scraping
- Handles structured queries, natural language processing
- Endpoints: `/scrape`, `/scrape-structured`, `/scrape-natural`, `/scrape-exact`, `/health`
- Request/response models and validation
- Background task management for async operations

**`flipkart_microservice_scraper.py`** - Core scraping engine
- Contains FlipkartScraper class with requests-based scraping
- Product data extraction using BeautifulSoup
- Multiple CSS selector fallbacks for robustness
- Price/rating filtering and data normalization
- Session management and error handling

### ⚙️ **Configuration & Health**

**`scraper_config.json`** - Scraper configuration
- CSS selectors for product containers, titles, prices, ratings
- HTTP headers for web requests
- Scraping timeouts and retry settings
- Easily updatable without code changes

**`scraper_health_checker.py`** - Health monitoring system
- Validates CSS selectors against live Flipkart pages
- Checks API connectivity and response times
- Automated selector health reporting
- Maintenance alerts and diagnostic tools

### 📚 **Documentation**

**`MAINTENANCE_GUIDE.md`** - Complete maintenance documentation
- How to update selectors when Flipkart changes
- Troubleshooting common issues
- Performance optimization tips
- Production deployment guidelines

**`README_microservice.md`** - API documentation and usage guide
- Complete API endpoint documentation
- Installation and setup instructions
- Code examples and integration patterns
- Performance benchmarks and architecture overview

### 📦 **Dependencies & Setup**

**`requirements_microservice.txt`** - Python package dependencies
- FastAPI, requests, BeautifulSoup4, pydantic
- Minimal production-ready package list
- Version-pinned for stability

**`.gitignore`** - Git ignore rules
- Excludes debug files, logs, scraped data
- Protects sensitive configuration
- Keeps repository clean

**`.gitattributes`** - Git line ending configuration
- Ensures consistent file formatting across platforms

### 🐳 **Deployment**

**`Dockerfile`** - Container configuration
- Multi-stage build for optimized image size
- Production-ready Python environment
- Health checks and proper signal handling

## 🎯 **How to Structure as API Routes**

This microservice can be integrated into larger systems as:

### **Option 1: Standalone Service**
```
/api/scraper/
├── /health          # Health check
├── /scrape          # General scraping
├── /scrape-exact    # URL-specific scraping
└── /scrape-natural  # Natural language queries
```

### **Option 2: E-commerce Platform Routes**
```
/api/products/
├── /search          # Product search (maps to /scrape)
├── /compare         # Product comparison (maps to /scrape-exact)
├── /recommendations # AI-powered suggestions (maps to /scrape-natural)
└── /health          # Service health
```

### **Option 3: AI Agent Integration**
```
/api/ai/
├── /scrape-structured  # Structured agent queries
├── /scrape-context     # Context-aware scraping
├── /product-intel      # Product intelligence
└── /market-data        # Market analysis
```

## 🔄 **Route Integration Pattern**

Each file serves a specific purpose in creating a production-ready scraping service that can be easily integrated into larger applications through well-defined API routes with proper configuration, monitoring, and documentation.
