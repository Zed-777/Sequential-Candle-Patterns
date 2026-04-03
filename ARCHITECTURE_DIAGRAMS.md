# Architecture Diagrams — Candlestick Patterns

**Purpose:** Visual representations of system components, data flows, and interactions.  
**Format:** Mermaid diagram syntax  
**Last Updated:** April 3, 2026

---

## 1. Component Architecture Diagram

Hierarchical view of system layers and their dependencies.

```mermaid
graph TB
    subgraph UI["🎨 User Interface Layer"]
        Dashboard["📊 Dash Dashboard<br/>(12 tabs, ~31 callbacks)"]
        API["🔗 REST API<br/>(/api/scan, /api/discover, etc)"]
        CLI["⌨️ CLI Tools<br/>(run, cleanup, train, predict)"]
    end

    subgraph AppLayer["🎯 Application Layer"]
        DashImpl["dashboard.py<br/>(Dash routes & callbacks)"]
        APIImpl["api.py<br/>(Flask blueprint)"]
        CLIImpl["cli.py<br/>(Click commands)"]
        Portfolio["portfolio.py<br/>(Multi-symbol scan)"]
    end

    subgraph BusinessLogic["💼 Business Logic Layer"]
        Core["⚙️ patterns.py<br/>(Core sequential engine)"]
        Detection["🕯️ detection.py<br/>(Candle features)"]
        ML["🧠 ml_sequence.py<br/>(GradientBoosting predictor)"]
        Alerts["🚨 alerts.py<br/>(Rules & dispatch)"]
        Backtest["📈 backtesting.py<br/>(Performance analysis)"]
        MultiTF["🔄 multi_timeframe.py<br/>(Cross-interval)"]
        Performance["⚡ performance.py<br/>(Vectorized ops)"]
        Watchlist["📋 watchlist.py<br/>(JSON persistence)"]
    end

    subgraph DataAccess["📁 Data Access Layer"]
        DataFeeds["🌐 data_feeds.py<br/>(Yahoo Finance + LRU cache)"]
        Ingestion["📥 ingestion.py<br/>(CSV validation)"]
        Storage["💾 storage.py<br/>(SQLite ops)"]
        Preferences["⚙️ preferences.py<br/>(User settings)"]
        MLBaseline["🎓 ml_baseline.py<br/>(RandomForest)"]
    end

    subgraph External["🌍 External Services"]
        YF["Yahoo Finance API"]
        SQLite["SQLite Database<br/>(alerts, history)"]
        Webhook["Webhook Endpoint<br/>(HTTPS dispatch)"]
        SMTP["SMTP Server<br/>(Email alerts)"]
    end

    Dashboard --> DashImpl
    API --> APIImpl
    CLI --> CLIImpl
    
    DashImpl --> Core
    DashImpl --> Detection
    DashImpl --> ML
    DashImpl --> Alerts
    DashImpl --> Backtest
    DashImpl --> MultiTF
    DashImpl --> DataFeeds
    DashImpl --> Preferences
    
    APIImpl --> Core
    APIImpl --> Portfolio
    APIImpl --> DataFeeds
    
    CLIImpl --> Core
    CLIImpl --> ML
    CLIImpl --> Backtest
    
    Portfolio --> Core
    Portfolio --> DataFeeds
    
    Core --> Performance
    Core --> Detection
    Core --> Watchlist
    
    ML --> Performance
    Alerts --> Storage
    Alerts --> Webhook
    Alerts --> SMTP
    Backtest --> Core
    MultiTF --> Core
    MultiTF --> DataFeeds
    
    DataFeeds --> YF
    Ingestion --> DataFeeds
    Storage --> SQLite
    Preferences --> SQLite
    Watchlist --> Ingestion
    MLBaseline --> Performance
    
    style UI fill:#c2e0c6
    style AppLayer fill:#fff4c6
    style BusinessLogic fill:#ffe0b6
    style DataAccess fill:#e0d9ff
    style External fill:#ffcccb
```

---

## 2. Data Flow Diagram — Sequence Scanning (Primary User Flow)

Step-by-step flow from user input to results display.

```mermaid
sequenceDiagram
    actor User
    participant Dashboard as Dash<br/>Dashboard
    participant patterns as patterns.py<br/>(Core)
    participant performance as performance.py<br/>(Vectorized)
    participant detection as detection.py<br/>(Features)
    participant Store as Data Store<br/>(JSON/SQLite)
    participant Chart as Chart<br/>Component

    User->>Dashboard: ① Define sequence<br/>"5R -> 2G"
    User->>Dashboard: ② Load data<br/>(CSV or Yahoo Finance)
    Dashboard->>Store: Load historical OHLCV
    Store->>Dashboard: Return DataFrame
    
    User->>Dashboard: ③ Click "Scan"
    Dashboard->>patterns: find_sequence_occurrences(df, "5R -> 2G")
    
    patterns->>detection: Classify candle colors<br/>(Red vs Green)
    detection->>performance: Build binary array [1,1,1,1,1,0,0,1,1,...]
    
    performance->>performance: Vectorized scan<br/>(numpy operations)
    performance->>performance: Find segment matches<br/>[matching indices]
    
    patterns->>patterns: Calculate statistics<br/>(win rate, avg return)
    patterns->>Dashboard: Return matches + stats
    
    Dashboard->>Chart: Update with highlights<br/>(colored rectangles)
    Chart->>User: ④ Display results<br/>(Chart + Matches table)
    User->>Dashboard: ✅ View pattern matches
```

---

## 3. Module Dependency Graph

Core module relationships and import paths.

```mermaid
graph LR
    patterns["<b>patterns.py</b><br/>Core<br/>Sequential Engine"]
    
    detection["detection.py<br/>Candle Feature<br/>Detection"]
    performance["performance.py<br/>Vectorized<br/>Optimization"]
    alerts["alerts.py<br/>Alert Rules &<br/>Dispatch"]
    ml["ml_sequence.py<br/>GradientBoosting<br/>Predictor"]
    backtest["backtesting.py<br/>Backtesting<br/>Engine"]

    dashboard["dashboard.py<br/>Dash Web App<br/>12 tabs"]
    api["api.py<br/>REST API<br/>Endpoints"]
    cli["cli.py<br/>CLI Tools<br/>5 commands"]
    portfolio["portfolio.py<br/>Multi-Symbol<br/>Scanning"]
    
    data_feeds["data_feeds.py<br/>Yahoo Finance<br/>+ LRU Cache"]
    storage["storage.py<br/>SQLite CRUD"]
    ingestion["ingestion.py<br/>CSV Validation"]
    preferences["preferences.py<br/>JSON Preferences"]
    watchlist["watchlist.py<br/>Sequence Storage"]

    patterns --> detection
    patterns --> performance
    
    dashboard --> patterns
    dashboard --> detection
    dashboard --> ml
    dashboard --> alerts
    dashboard --> backtest
    dashboard --> data_feeds
    dashboard --> preferences
    
    api --> patterns
    api --> portfolio
    api --> data_feeds
    
    cli --> patterns
    cli --> ml
    cli --> backtest
    
    portfolio --> patterns
    portfolio --> data_feeds
    
    ml --> performance
    alerts --> storage
    backtest --> patterns
    
    data_feeds --> ingestion
    watchlist --> ingestion
    
    style patterns fill:#ff9999
    style detection fill:#ff9999
    style performance fill:#ff9999
    style alerts fill:#99ccff
    style ml fill:#99ccff
    style backtest fill:#99ccff
    style dashboard fill:#99ff99
    style api fill:#99ff99
    style cli fill:#99ff99
    style data_feeds fill:#ffcc99
    style storage fill:#ffcc99
```

---

## 4. Alert Dispatch Flow (Background Process)

How alerts are triggered and delivered to users.

```mermaid
stateDiagram-v2
    [*] --> CheckRules: Every 5 seconds<br/>check_and_trigger()
    
    CheckRules --> QueryDB: Query SQLite<br/>alert_rules table
    QueryDB --> RuleActive{Alert rule<br/>enabled?}
    
    RuleActive -->|No| CheckRules
    RuleActive -->|Yes| CheckSequence{Sequence<br/>occurred?}
    
    CheckSequence -->|No| CheckRules
    CheckSequence -->|Yes| LogHistory: Log to<br/>alert_history
    
    LogHistory --> SendWebhook{Webhook<br/>configured?}
    SendWebhook -->|Yes| WebhookDispatch: Dispatch HTTPS<br/>POST request
    WebhookDispatch --> WebhookResult{Success?}
    WebhookResult -->|Yes| SendEmail
    WebhookResult -->|No| LogError: Log error
    
    SendEmail{Email<br/>configured?}
    SendEmail -->|Yes| EmailDispatch: Send via SMTP<br/>TLS
    EmailDispatch --> NotifyDash: Update dashboard<br/>Alerts tab
    SendEmail -->|No| NotifyDash
    
    LogError --> CheckRules
    NotifyDash --> [*]: Alert<br/>delivered
```

---

## 5. ML Prediction Pipeline (Advanced Analytics)

Process from user input to ML inference.

```mermaid
graph TD
    A["User Input:<br/>Sequence + Symbol"] --> B["Load Pre-trained<br/>GradientBoosting Model"]
    
    B --> C["Engineer Features<br/>from Context"]
    
    C --> C1["Volume Trend<br/>(5-period avg)"]
    C --> C2["Win Rate<br/>(historical)"]
    C --> C3["Price Momentum<br/>(recent candles)"]
    C --> C4["Volatility<br/>(High-Low spread)"]
    C --> C5["13 More Features<br/>..."]
    
    C1 --> D["Feature Vector<br/>(17 dimensions)"]
    C2 --> D
    C3 --> D
    C4 --> D
    C5 --> D
    
    D --> E["GradientBoosting<br/>Classifier"]
    
    E --> F["Raw Prediction<br/>(0-1 confidence)"]
    
    F --> G["Calibrate Probability<br/>(Platt scaling)"]
    
    G --> H["Result:<br/>72% likely to<br/>continue up"]
    
    H --> I["Display in<br/>ML Predict Tab"]
    I --> J["Show Feature<br/>Importance Plot"]
    
    J --> K["User Reviews<br/>Prediction +<br/>Confidence"]
    
    style A fill:#e1f5ff
    style B fill:#fff3e0
    style E fill:#f3e5f5
    style H fill:#e8f5e9
    style K fill:#fce4ec
```

---

## 6. Dashboard Tab Topology

All 12 tabs and their relationships.

```mermaid
graph TB
    Sidebar["📍 Sidebar Controls<br/>━━━━━━━━━━<br/>🔼 Upload/Load Data<br/>🌐 Yahoo Finance<br/>🔍 Scanner Input<br/>⚙️ Settings"]
    
    subgraph Tabs["📋 Dashboard Tabs (12 Total)"]
        T1["① Candlestick Chart<br/>━━━━━━━━━<br/>OHLCV + matches<br/>highlighted"]
        T2["② Sequence Matches<br/>━━━━━━━━━<br/>Detailed match list<br/>with timestamps"]
        T3["③ Auto-Discovery<br/>━━━━━━━━━<br/>Top 25 sequences<br/>by win rate"]
        T4["④ Statistics &<br/>Predictions<br/>━━━━━━━━━<br/>Per-sequence stats<br/>+ what-next"]
        T5["⑤ Heatmap<br/>━━━━━━━━━<br/>Pattern density<br/>across time"]
        T6["⑥ Reverse Finder<br/>━━━━━━━━━<br/>Sequences before<br/>big moves"]
        T7["⑦ Backtesting<br/>━━━━━━━━━<br/>Equity curve<br/>+ metrics"]
        T8["⑧ Multi-Timeframe<br/>━━━━━━━━━<br/>Cross-interval<br/>alignment"]
        T9["⑨ Watchlist<br/>━━━━━━━━━<br/>Save/load<br/>libraries"]
        T10["⑩ Alerts<br/>━━━━━━━━━<br/>Rules CRUD<br/>+ history"]
        T11["⑪ ML Predict<br/>━━━━━━━━━<br/>GradientBoosting<br/>predictor"]
        T12["⑫ Settings<br/>━━━━━━━━━<br/>User preferences<br/>+ defaults"]
    end
    
    Sidebar --> T1
    Sidebar --> T2
    Sidebar --> T3
    Sidebar --> T4
    Sidebar --> T5
    Sidebar --> T6
    Sidebar --> T7
    Sidebar --> T8
    Sidebar --> T9
    Sidebar --> T10
    Sidebar --> T11
    Sidebar --> T12
    
    T1 -.->|Shared Data| T2
    T1 -.->|Shared Data| T4
    T1 -.->|Shared Data| T7
    T3 -.->|Feed into| T4
    T4 -.->|Feed into| T7
    T10 -.->|Alert History| T1
    T11 -.->|Predictions| T4
    T12 -.->|Settings| T1
    
    style Sidebar fill:#fff9c4
    style T1 fill:#c8e6c9
    style T4 fill:#bbdefb
    style T7 fill:#ffe0b2
    style T11 fill:#f8bbd0
```

---

## 7. Deployment Architecture (Docker)

Multi-stage build and containerization.

```mermaid
graph LR
    DEV["Developer<br/>Local Machine"]
    
    BUILD1["Stage 1:<br/>Builder<br/>━━━━━━<br/>python:3.12<br/>+ build tools"]
    BUILD1_WORK["Setup venv<br/>Install deps<br/>Run tests<br/>Build wheel"]
    
    BUILD2["Stage 2:<br/>Runtime<br/>━━━━━━<br/>python:3.12-slim<br/>+ runtime"]
    BUILD2_WORK["Copy wheels<br/>from stage 1<br/>Install deps<br/>Configure app"]
    
    REGISTRY["Docker Registry<br/>docker.io"]
    
    PROD["Production<br/>Deploy to<br/>━━━━━━<br/>Cloud (AWS/GCP)<br/>or On-Premise"]
    
    DEV -->|git push| GITHUB["GitHub Repo<br/>━━━━━━<br/>feature/mvp-setup<br/>branch"]
    
    GITHUB -->|Webhook| CI["CI/CD Pipeline<br/>GitHub Actions<br/>━━━━━━<br/>Test (pytest)<br/>Lint (ruff)<br/>Build (Dockerfile)"]
    
    CI --> BUILD1
    BUILD1 --> BUILD1_WORK
    BUILD1_WORK --> BUILD2
    BUILD2 --> BUILD2_WORK
    
    BUILD2_WORK --> REGISTRY
    REGISTRY --> PROD
    
    PROD --> RUN["Running Container<br/>━━━━━━<br/>Port 8050<br/>(Dash)<br/>Port 5000<br/>(Flask API)"]
    
    RUN --> USER["End User<br/>━━━━━━<br/>Browser<br/>localhost:8050"]
    
    style BUILD1 fill:#e3f2fd
    style BUILD1_WORK fill:#bbdefb
    style BUILD2 fill:#e3f2fd
    style BUILD2_WORK fill:#bbdefb
    style CI fill:#fff3e0
    style PROD fill:#e8f5e9
    style RUN fill:#f3e5f5
```

---

## 8. Authentication & Authorization (Future)

Path to multi-user system with role-based access.

```mermaid
graph TD
    LOGIN["User Login<br/>━━━━━━━━━━<br/>Username/Password"]
    
    LOGIN --> AUTH["Authentication<br/>━━━━━━━━━━<br/>Query users table<br/>Verify password_hash<br/>Create session"]
    
    AUTH --> ROLES{Check Role}
    
    ROLES -->|viewer| PERMS_V["Permissions:<br/>✓ View dashboard<br/>✓ View reports<br/>✗ Create alerts<br/>✗ Admin panel"]
    
    ROLES -->|trader| PERMS_T["Permissions:<br/>✓ View dashboard<br/>✓ Create alerts<br/>✓ Run backtest<br/>✗ Admin panel"]
    
    ROLES -->|admin| PERMS_A["Permissions:<br/>✓ Full system access<br/>✓ User management<br/>✓ Settings<br/>✓ Audit logs"]
    
    PERMS_V --> ENFORCE["Enforce<br/>━━━━━━━━━━<br/>@require_role<br/>decorator"]
    PERMS_T --> ENFORCE
    PERMS_A --> ENFORCE
    
    ENFORCE --> ACCESS{User Action}
    
    ACCESS -->|Allowed| GRANT["✅ Grant Access<br/>Execute request"]
    ACCESS -->|Denied| DENY["❌ Deny Access<br/>403 Forbidden"]
    
    GRANT --> LOG["Log to<br/>audit_log table"]
    DENY --> LOG
    
    LOG --> [*]
    
    style LOGIN fill:#c8e6c9
    style AUTH fill:#bbdefb
    style PERMS_V fill:#ffe0b2
    style PERMS_T fill:#ffe0b2
    style PERMS_A fill:#ffccbc
    style GRANT fill:#c8e6c9
    style DENY fill:#ffcdd2
```

---

## Usage Notes

These diagrams complement the textual [architecture.md](architecture.md) documentation:

- **Component Diagram** — Understand which modules talk to which
- **Data Flow (Sequence)** — Follow a typical user interaction step-by-step
- **Dependency Graph** — Identify circular dependencies or tightly coupled modules
- **Alert Flow** — Understand how background alerts work
- **ML Pipeline** — See the steps from input to prediction
- **Dashboard Tabs** — Know what each tab does and how they relate
- **Deployment** — Understand Docker build and production deployment
- **Auth (Future)** — Plan for multi-user/RBAC rollout in Phase 13

For implementation details, see [architecture.md](architecture.md) and [MPDP.md](MPDP.md).
