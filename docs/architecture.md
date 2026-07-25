# Prahari AI — System Architecture

Prahari AI utilizes a **Polyglot Persistence Architecture**, decoupling operational workloads from analytical, search, and graph traversal workloads. The entire stack is orchestrated for deployment on **Zoho Catalyst**.

## High-Level Architecture

```mermaid
graph TD
    %% Clients
    UI[Next.js Frontend]
    Mobile[React Native Field App]

    %% Gateway
    Gateway[Zoho Catalyst API Gateway]

    %% Backend Services (FastAPI)
    subgraph FastAPI Backend Services
        Core[Core API & Workflows]
        Intelligence[Intelligence Engines]
        DemoEngine[Simulation / Demo Engine]
    end

    %% Data Layer
    subgraph Polyglot Persistence Layer
        PG[(PostgreSQL / PostGIS)]
        N4J[(Neo4j Graph Database)]
        QDR[(Qdrant Vector DB)]
        Storage[(Catalyst Object Storage)]
    end

    %% Connections
    UI -->|HTTPS/WSS| Gateway
    Mobile -->|HTTPS| Gateway
    Gateway --> Core
    Gateway --> Intelligence
    Gateway --> DemoEngine

    Core --> PG
    Core --> Storage
    Intelligence --> N4J
    Intelligence --> QDR

    %% Sync
    PG -.->|Change Data Capture / Events| N4J
    PG -.->|Embeddings Sync| QDR
```

## Technology Stack

1. **Frontend**: Next.js (React 19), TailwindCSS, Zustand
2. **Visualizations**: MapLibre GL JS (Geospatial), Cytoscape.js (Graph), Apache ECharts (Analytics)
3. **Backend**: FastAPI (Python 3.12), Pydantic, SQLAlchemy
4. **Relational Database**: PostgreSQL (Operational state, RBAC, Core Entities)
5. **Graph Database**: Neo4j (Link Analysis, Criminal Networks, Shortest Path)
6. **Vector Database**: Qdrant (Semantic Search, AI RAG)
7. **Cloud Infrastructure**: Zoho Catalyst (Serverless, AppSail, Object Storage)

## Core Workflows

- **FIR Registration**: The Progressive FIR Workflow saves drafts to PostgreSQL incrementally. Upon submission, a background task synchronizes the FIR entities into Neo4j nodes and Qdrant vectors.
- **Simulation Engine**: Developed in Python, generates realistic synthetic cases spanning decades to ensure the system is evaluated under high-volume stress (100,000+ records).
