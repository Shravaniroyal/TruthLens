# 🏗️ TruthLens System Architecture

**Complete technical architecture and data flow diagrams**

---

## 🔄 System Overview Diagram

```mermaid
flowchart TB
    Start([User Uploads Document]) --> Input[Document Image<br/>JPG/PNG]
    
    Input --> Cache{Check Cache?}
    Cache -->|Cache Hit| CachedResult[Return Cached<br/>Result ⚡]
    Cache -->|Cache Miss| Preprocess
    
    Preprocess[Preprocessing Pipeline] --> Segment{Use<br/>Segmentation?}
    Segment -->|Yes| OCR[Tesseract OCR<br/>Text Detection]
    Segment -->|No| Parallel
    OCR --> Mask[Generate Text Mask]
    Mask --> Parallel
    
    Parallel[Parallel Processing] --> ELA[ELA Detector]
    Parallel --> CopyMove[Copy-Move Detector]
    Parallel --> Font[Font Analyzer]
    
    ELA --> ELAScore[ELA Score: 0-100]
    CopyMove --> CMScore[Duplicates: N]
    Font --> FontScore[Variation: 0-100%]
    
    ELAScore --> Decision
    CMScore --> Decision
    FontScore --> Decision
    
    Decision{Decision Engine<br/>2/3 Voting} --> Evaluate
    
    Evaluate[Evaluate Thresholds] --> Count[Count Suspicious<br/>Detectors]
    
    Count --> Final{Suspicious<br/>Count ≥ 2?}
    
    Final -->|Yes| Fraud[🚨 FRAUD DETECTED]
    Final -->|No| Authentic[✅ AUTHENTIC]
    
    Fraud --> Report
    Authentic --> Report
    
    Report[Generate Report] --> SaveCache[Save to Cache]
    SaveCache --> Output[Return Results<br/>to User]
    CachedResult --> Output
    
    Output --> End([Display Results])
    
    style Start fill:#e1f5ff
    style End fill:#e1f5ff
    style Fraud fill:#ffebee
    style Authentic fill:#e8f5e9
    style Cache fill:#fff3e0
    style Decision fill:#f3e5f5
    style Output fill:#e0f2f1
```

---

## 🔍 Detailed Component Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        WebUI[Web Interface<br/>Gradio]
        CLI[Command Line<br/>Click]
    end
    
    subgraph "Core Processing Layer"
        FD[FraudDetector<br/>Main Orchestrator]
        BP[BatchProcessor<br/>High-Volume Handler]
    end
    
    subgraph "Detection Modules"
        ELA[ELA Detector<br/>ela_detector.py]
        CM[Copy-Move Detector<br/>copymove_detector.py]
        FA[Font Analyzer<br/>font_analyzer.py]
    end
    
    subgraph "Utilities"
        SEG[Document Segmenter<br/>document_segmenter.py]
        CACHE[Cache Manager<br/>MD5-based]
        SAMPLE[Sample Generator<br/>Test Data Creator]
    end
    
    subgraph "External Dependencies"
        CV[OpenCV<br/>Computer Vision]
        TESS[Tesseract<br/>OCR Engine]
        PIL[Pillow<br/>Image Processing]
        NP[NumPy<br/>Numerical Computing]
    end
    
    WebUI --> FD
    CLI --> FD
    CLI --> BP
    BP --> FD
    
    FD --> ELA
    FD --> CM
    FD --> FA
    FD --> SEG
    FD --> CACHE
    
    SEG --> TESS
    ELA --> CV
    ELA --> PIL
    CM --> CV
    CM --> NP
    FA --> TESS
    
    style FD fill:#4CAF50
    style WebUI fill:#2196F3
    style CLI fill:#2196F3
    style ELA fill:#FF9800
    style CM fill:#FF9800
    style FA fill:#FF9800
    style SEG fill:#9C27B0
    style CACHE fill:#FFC107
```

---

## 📊 Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Interface
    participant FraudDetector
    participant Cache
    participant Segmenter
    participant ELA
    participant CopyMove
    participant Font
    participant DecisionEngine
    
    User->>Interface: Upload Document
    Interface->>FraudDetector: analyze_document(path)
    
    FraudDetector->>Cache: Check cache (MD5 hash)
    alt Cache Hit
        Cache-->>FraudDetector: Return cached result
        FraudDetector-->>Interface: Return result
        Interface-->>User: Display result
    else Cache Miss
        FraudDetector->>Segmenter: Identify text regions
        Segmenter-->>FraudDetector: Return text mask
        
        par Parallel Processing
            FraudDetector->>ELA: Detect compression artifacts
            ELA-->>FraudDetector: ELA score (0-100)
        and
            FraudDetector->>CopyMove: Find duplicates (with mask)
            CopyMove-->>FraudDetector: Duplicate count
        and
            FraudDetector->>Font: Analyze font consistency
            Font-->>FraudDetector: Variation percentage
        end
        
        FraudDetector->>DecisionEngine: Evaluate scores
        DecisionEngine->>DecisionEngine: Check thresholds
        DecisionEngine->>DecisionEngine: Count suspicious (2/3 rule)
        DecisionEngine-->>FraudDetector: Final verdict + confidence
        
        FraudDetector->>Cache: Save result
        FraudDetector-->>Interface: Return result
        Interface-->>User: Display result
    end
```

---

## 🧩 Module Dependency Graph

```mermaid
graph LR
    subgraph "Entry Points"
        WEB[truthlens_web.py]
        CLITOOL[truthlens_cli.py]
    end
    
    subgraph "Core"
        FD[fraud_detector.py]
        BP[batch_processor.py]
    end
    
    subgraph "Detection"
        ELA[ela_detector.py]
        CM[copymove_detector.py]
        FA[font_analyzer.py]
    end
    
    subgraph "Utils"
        SEG[document_segmenter.py]
        GEN[sample_generator.py]
    end
    
    WEB --> FD
    CLITOOL --> FD
    CLITOOL --> BP
    BP --> FD
    
    FD --> ELA
    FD --> CM
    FD --> FA
    FD --> SEG
    
    CM --> SEG
    
    style FD fill:#4CAF50,stroke:#2E7D32,stroke-width:3px
    style WEB fill:#2196F3
    style CLITOOL fill:#2196F3
    style BP fill:#FF9800
```

---

## ⚙️ Processing Pipeline Details

### Stage 1: Preprocessing (0.69s - 32%)

```mermaid
flowchart LR
    A[Load Image] --> B{Use Segmentation?}
    B -->|Yes| C[Run Tesseract OCR]
    B -->|No| E[Skip to Detection]
    C --> D[Extract Word Boxes]
    D --> E[Create Text Mask]
    E --> F[Ready for Detection]
    
    style C fill:#9C27B0
    style E fill:#4CAF50
```

**Purpose:** Identify text regions to reduce false positives in copy-move detection

**Impact:**
- 48-64% false positive reduction
- 59% speed improvement (counterintuitive!)

---

### Stage 2: ELA Detection (0.11s - 5%)

```mermaid
flowchart LR
    A[Original Image] --> B[Recompress at 95% JPEG]
    B --> C[Calculate Pixel Differences]
    C --> D[Normalize to 0-100 Scale]
    D --> E{Score > 50?}
    E -->|Yes| F[Suspicious ⚠️]
    E -->|No| G[Clean ✅]
    
    style F fill:#ffebee
    style G fill:#e8f5e9
```

**Detects:** Photoshop edits, image manipulation  
**Threshold:** 50/100  
**FBI Standard:** 95% JPEG quality

---

### Stage 3: Copy-Move Detection (0.60s - 28%)

```mermaid
flowchart LR
    A[Divide into 16x16 Blocks] --> B[Apply Text Mask]
    B --> C[Compare All Block Pairs]
    C --> D[Count Duplicates]
    D --> E{Duplicates > 5?}
    E -->|Yes| F[Suspicious ⚠️]
    E -->|No| G[Normal ✅]
    
    style B fill:#9C27B0
    style F fill:#ffebee
    style G fill:#e8f5e9
```

**Detects:** Copied signatures, logos, image regions  
**Innovation:** Text exclusion via segmentation  
**Threshold:** 5 duplicates

---

### Stage 4: Font Analysis (0.77s - 35%)

```mermaid
flowchart LR
    A[Run Tesseract OCR] --> B[Extract Font Sizes]
    B --> C[Calculate Std Deviation]
    C --> D[Convert to Percentage]
    D --> E{Variation > 30%?}
    E -->|Yes| F[Suspicious ⚠️]
    E -->|No| G[Consistent ✅]
    
    style F fill:#ffebee
    style G fill:#e8f5e9
```

**Detects:** Text tampering, mixed fonts  
**Bottleneck:** Slowest component (35% of time)  
**Threshold:** 30% variation

---

### Stage 5: Decision Engine

```mermaid
flowchart TB
    A[Collect 3 Scores] --> B[Check ELA > 50]
    A --> C[Check Copy-Move > 5]
    A --> D[Check Font > 30%]
    
    B --> E[Count Suspicious]
    C --> E
    D --> E
    
    E --> F{Count >= 2?}
    
    F -->|Yes| G[FRAUD DETECTED 🚨]
    F -->|No| H[AUTHENTIC ✅]
    
    G --> I[Calculate Confidence]
    H --> I
    
    I --> J[Generate Report]
    
    style G fill:#ffebee
    style H fill:#e8f5e9
    style F fill:#f3e5f5
```

**Logic:** 2 out of 3 detectors must agree  
**Rationale:** Reduces false positives while maintaining sensitivity  
**Confidence:** Weighted average of all scores

---

## 🔄 Caching System Architecture

```mermaid
flowchart TB
    A[Document Input] --> B[Calculate MD5 Hash]
    B --> C{Cache Exists?}
    
    C -->|Yes| D[Load JSON from<br/>data/cache/]
    D --> E[Parse Cached Result]
    E --> F[Return Result ⚡<br/>~0.001s]
    
    C -->|No| G[Run Full Analysis<br/>~2.16s]
    G --> H[Generate Result]
    H --> I[Create JSON]
    I --> J[Save to<br/>data/cache/HASH.json]
    J --> K[Return Result]
    
    F --> L[User Receives Result]
    K --> L
    
    style D fill:#FFC107
    style F fill:#4CAF50
    style G fill:#FF9800
```

**Performance:**
- Cache hit: ~0.001 seconds (2,160x faster!)
- Cache storage: ~2KB per document
- Hit rate: 100% on repeated documents
- Overall speedup: 2.4x on typical workloads

---

## 📦 Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV[Local Machine<br/>Windows/Mac/Linux]
        VENV[Python venv<br/>Isolated Dependencies]
    end
    
    subgraph "Web Interface"
        GRADIO[Gradio Server<br/>Port 7860]
        BROWSER[Web Browser<br/>localhost:7860]
    end
    
    subgraph "CLI Interface"
        TERMINAL[Terminal/CMD<br/>truthlens_cli.py]
    end
    
    subgraph "Future: Cloud Deployment"
        AWS[AWS EC2/Lambda]
        API[REST API<br/>Authentication]
        DB[Database<br/>User Data]
    end
    
    DEV --> VENV
    VENV --> GRADIO
    VENV --> TERMINAL
    
    GRADIO <--> BROWSER
    
    GRADIO -.Future.-> AWS
    TERMINAL -.Future.-> API
    AWS --> API
    API --> DB
    
    style DEV fill:#4CAF50
    style AWS fill:#FF9800,stroke-dasharray: 5 5
    style API fill:#FF9800,stroke-dasharray: 5 5
    style DB fill:#FF9800,stroke-dasharray: 5 5
```

---

## 🎯 Performance Optimization Points

```mermaid
graph TD
    A[Original System<br/>No Optimization] --> B[Add Segmentation<br/>59% Faster ✅]
    
    B --> C[Add Caching<br/>2.4x Faster ✅]
    
    C --> D[Future: PaddleOCR<br/>3x Faster 🔜]
    
    D --> E[Future: Parallel<br/>1.5x Faster 🔜]
    
    E --> F[Future: GPU Acceleration<br/>5x Faster 🔜]
    
    style B fill:#4CAF50
    style C fill:#4CAF50
    style D fill:#FFC107
    style E fill:#FFC107
    style F fill:#FFC107
```

**Current:** 2.16s per document  
**With all optimizations:** ~0.15s per document (14x improvement potential)

---

## 📊 Scalability Architecture

```mermaid
graph TB
    subgraph "Current: Single Instance"
        S1[Single Process<br/>~0.5 docs/sec]
    end
    
    subgraph "Phase 2: Queue System"
        Q[Gradio Queue<br/>~5 docs/sec]
    end
    
    subgraph "Phase 3: Multi-Worker"
        LB[Load Balancer]
        W1[Worker 1]
        W2[Worker 2]
        W3[Worker 3]
        W4[Worker 4]
        LB --> W1
        LB --> W2
        LB --> W3
        LB --> W4
    end
    
    subgraph "Phase 4: Cloud Scale"
        CDN[CDN/CloudFront]
        AG[Auto-Scaling Group]
        RDS[Database<br/>User Data]
        S3[S3 Storage<br/>Documents]
    end
    
    S1 -.Upgrade.-> Q
    Q -.Upgrade.-> LB
    LB -.Upgrade.-> CDN
    CDN --> AG
    AG --> RDS
    AG --> S3
    
    style S1 fill:#4CAF50
    style Q fill:#FFC107
    style LB fill:#FF9800
    style CDN fill:#2196F3
```

**Capacity Roadmap:**
- Phase 1: ~40K docs/day (current)
- Phase 2: ~400K docs/day (queue)
- Phase 3: ~1.6M docs/day (multi-worker)
- Phase 4: Unlimited (cloud scale)

---

## 🔐 Security Architecture (Future)

```mermaid
flowchart TB
    A[User Request] --> B{Authenticated?}
    B -->|No| C[Redirect to Login]
    B -->|Yes| D{Rate Limit OK?}
    D -->|No| E[429 Too Many Requests]
    D -->|Yes| F{Valid File Type?}
    F -->|No| G[400 Bad Request]
    F -->|Yes| H{File Size < 10MB?}
    H -->|No| I[413 Payload Too Large]
    H -->|Yes| J[Virus Scan]
    J --> K{Clean?}
    K -->|No| L[403 Forbidden]
    K -->|Yes| M[Process Document]
    M --> N[Log Activity]
    N --> O[Return Result]
    
    style M fill:#4CAF50
    style O fill:#4CAF50
```

**Security Features (Planned):**
- Authentication (JWT tokens)
- Rate limiting (100 requests/hour/user)
- File validation (type, size, virus scan)
- Audit logging (who, what, when)
- Data encryption (at rest and in transit)

---

## 📈 Monitoring & Observability (Future)

```mermaid
graph LR
    A[TruthLens System] --> B[Metrics Collector]
    B --> C[Prometheus]
    C --> D[Grafana Dashboard]
    
    A --> E[Log Aggregator]
    E --> F[ELK Stack]
    
    A --> G[Error Tracker]
    G --> H[Sentry]
    
    D --> I[Alerts]
    F --> I
    H --> I
    
    I --> J[Email/Slack<br/>Notifications]
    
    style A fill:#4CAF50
    style D fill:#2196F3
    style I fill:#FF5722
```

**Metrics to Track:**
- Processing time per document
- Throughput (docs/sec)
- Error rates
- Cache hit rates
- User activity
- System resources (CPU, RAM, disk)

---

## 🧪 Testing Architecture

```mermaid
graph TB
    subgraph "Test Types"
        UT[Unit Tests<br/>pytest]
        IT[Integration Tests<br/>End-to-end]
        PT[Performance Tests<br/>Benchmarks]
        UT2[User Tests<br/>Usability]
    end
    
    subgraph "Test Data"
        SYNTH[Synthetic Documents<br/>45+ samples]
        REAL[Real Documents<br/>1000+ samples]
    end
    
    subgraph "CI/CD Pipeline"
        GH[GitHub Actions]
        TEST[Run Tests]
        BUILD[Build Artifacts]
        DEPLOY[Deploy]
    end
    
    UT --> GH
    IT --> GH
    PT --> GH
    
    SYNTH --> UT
    SYNTH --> IT
    REAL --> PT
    REAL --> UT2
    
    GH --> TEST
    TEST --> BUILD
    BUILD --> DEPLOY
    
    style GH fill:#2196F3
    style TEST fill:#4CAF50
    style DEPLOY fill:#FF9800
```

---

## 📚 Documentation Architecture

```mermaid
graph TB
    subgraph "User Documentation"
        README[README.md<br/>Project Overview]
        INSTALL[INSTALL.md<br/>Setup Guide]
        DEMO[DEMO_SCRIPT.md<br/>Presentations]
    end
    
    subgraph "Developer Documentation"
        API[API_USAGE.md<br/>Python API]
        ARCH[ARCHITECTURE.md<br/>System Design]
        DAILY[Daily Logs<br/>140 pages]
    end
    
    subgraph "Research Documentation"
        SUMMARY[WEEK_1_SUMMARY.md<br/>Achievements]
        PAPERS[Paper Drafts<br/>Research]
        THESIS[Thesis Chapters<br/>7 chapters]
    end
    
    README --> INSTALL
    INSTALL --> API
    API --> ARCH
    
    DEMO --> SUMMARY
    SUMMARY --> PAPERS
    PAPERS --> THESIS
    
    DAILY --> PAPERS
    DAILY --> THESIS
    
    style README fill:#2196F3
    style API fill:#4CAF50
    style SUMMARY fill:#FF9800
    style THESIS fill:#9C27B0
```

---

## 🎯 Technology Stack Summary

| Layer | Technologies | Purpose |
|-------|-------------|---------|
| **Core Language** | Python 3.8+ | Main development |
| **Computer Vision** | OpenCV 4.x | Image processing |
| **OCR** | Tesseract 5.x | Text recognition |
| **Numerical** | NumPy | Array operations |
| **Image Processing** | Pillow (PIL) | Image manipulation |
| **Web UI** | Gradio 3.x | User interface |
| **CLI** | Click 8.x | Command-line tool |
| **Caching** | JSON + MD5 | Result storage |
| **Documentation** | Markdown + Mermaid | Diagrams & docs |

---

## 🔮 Future Architecture Vision

```mermaid
graph TB
    subgraph "Current: Week 1"
        C1[3 CV Detectors]
        C2[Basic Web UI]
        C3[Local Processing]
    end
    
    subgraph "Month 3-4: ML Integration"
        M1[LayoutLM<br/>Deep Learning]
        M2[Vision-Language<br/>Models]
        M3[PaddleOCR<br/>Fast OCR]
    end
    
    subgraph "Month 6-9: Cloud Scale"
        CL1[AWS Deployment]
        CL2[REST API]
        CL3[Multi-Tenant]
        CL4[Real-Time Analytics]
    end
    
    subgraph "Month 10-12: Advanced"
        A1[Explainable AI<br/>LIME/SHAP]
        A2[Active Learning<br/>Human Feedback]
        A3[Mobile App<br/>iOS/Android]
    end
    
    C1 --> M1
    C2 --> M2
    C3 --> M3
    
    M1 --> CL1
    M2 --> CL2
    M3 --> CL3
    
    CL1 --> A1
    CL2 --> A2
    CL3 --> A3
    
    style C1 fill:#4CAF50
    style M1 fill:#FFC107
    style CL1 fill:#FF9800
    style A1 fill:#2196F3
```

---

**END OF ARCHITECTURE DOCUMENTATION**

*These diagrams can be rendered in:*
- *GitHub (automatic Mermaid rendering)*
- *VS Code (with Mermaid extension)*
- *Online: https://mermaid.live/*
- *Thesis (export as PNG/SVG)*