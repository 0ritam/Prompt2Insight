flowchart TD
    START([User Query: &quot;Find best laptops under 50k&quot;]) --> ROUTER

   %% Router Agent Decision Making
    subgraph "🧠 Router Agent (Master Brain)"
        ROUTER[Query Analysis]
        CLASSIFY[Intent Classification]
        DECISION[Route Decision]
        ROUTER --> CLASSIFY
        CLASSIFY --> DECISION
  end

  %% Product Discovery Workflow
    subgraph "🔍 Product Discoverer Agent"
        RESEARCH[Gemini AI Research]
        EXTRACT[Structured Data Extraction]
        VALIDATE[Price & Specs Validation]
        PRODUCTS[Return: 5 Laptop Products]
        RESEARCH --> EXTRACT
        EXTRACT --> VALIDATE
        VALIDATE --> PRODUCTS
  end

  %% Chart Generation Process
    subgraph "📊 Chart Generator Agent"
        PRICE_CHART[Price Comparison Chart]
        SPECS_CHART[Specification Radar Chart]
        BASE64[Base64 Image Generation]
        PRICE_CHART --> BASE64
        SPECS_CHART --> BASE64
  end

  %% Frontend Display
    subgraph "💻 Frontend Display"
        GRID[Product Cards Grid]
        TOGGLE[Interactive Chart Toggle]
        VISUAL[Real-time Visualization]
        GRID --> TOGGLE
        TOGGLE --> VISUAL
  end

  %% Flow Connections
    DECISION -->|discovery_query| RESEARCH
    PRODUCTS --> PRICE_CHART
    PRODUCTS --> SPECS_CHART
    BASE64 --> GRID

  %% Alternative Flows
    DECISION -->|analytical_query| RAG[RAG Pipeline]
    DECISION -->|fallback| FALLBACK[Default Response]

  %% External Connections
    RESEARCH -.->|API Call| GEMINI_API[Gemini AI API]
    RESEARCH -.->|Web Scraping| WEB_SCRAPERS[Web Scrapers]

  %% Styling
    classDef router fill:#4A5568,stroke:#2D3748,stroke-width:3px,color:#ffffff
    classDef discoverer fill:#E6FFFA,stroke:#2C7A7B,stroke-width:3px
    classDef charts fill:#EBF4FF,stroke:#4C51BF,stroke-width:3px
    classDef frontend fill:#F7FAFC,stroke:#718096,stroke-width:3px
    classDef external fill:#FFFBEB,stroke:#D69E2E,stroke-width:2px,stroke-dasharray: 5 5

  class ROUTER,CLASSIFY,DECISION router
    class RESEARCH,EXTRACT,VALIDATE,PRODUCTS discoverer
    class PRICE_CHART,SPECS_CHART,BASE64 charts
    class GRID,TOGGLE,VISUAL frontend
    class GEMINI_API,WEB_SCRAPERS external
