# Prahari AI - Architecture Overview

## High-Level System Design

Prahari AI is a distributed, polyglot-persistence intelligence platform.

### Frontend (`/prahari-frontend`)
- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS v4, shadcn/ui
- **State Management**: Zustand (Global UI state), React Query (Server state, optimistic updates)
- **Mapping**: MapLibre GL JS, Deck.gl
- **Graph Visualization**: Cytoscape.js
- **Charts**: Apache ECharts

### Backend (`/prahari-backend`)
- **Framework**: FastAPI (Python 3.12+)
- **Architecture**: Clean Architecture (Routers -> Workflows -> Services -> Repositories -> Models)
- **ORM**: SQLAlchemy (Async) + Alembic

### Data Layer (Polyglot Persistence)
1. **PostgreSQL / PostGIS (Primary Source of Truth)**
   - Relational data: Users, Cases, Evidence, Tasks, Timelines.
2. **Neo4j (Knowledge Graph)**
   - Link analysis: Criminal networks, communication pathways (CDRs), financial transactions.
3. **Qdrant (Vector Database)**
   - Semantic search, RAG document retrieval, case similarity.
4. **Zoho Catalyst Data Store / Stratus**
   - Cloud backup, media storage (PDFs, Images, Video).

### Zoho Catalyst Integration
- **AppSail**: Containerized hosting for Frontend (Node.js) and Backend (Python).
- **Authentication**: JWT-based Catalyst Auth.
- **Cache**: Ephemeral storage for dashboard metrics.
- **Signals & Cron**: Background task execution (e.g., async Graph Sync, AI Scoring).
- **QuickML**: ML Pipeline for risk scores and anomaly detection.

## Progressive FIR Workflow Architecture
Instead of massive monolithic POST requests, Prahari utilizes a **Draft-Based Incremental Workflow**:
1. `POST /cases/draft` creates an initial record.
2. `PATCH /cases/{id}` autosaves core fields.
3. Dedicated entity endpoints (`/victims`, `/accused`) attach linked data instantly.
4. All actions produce `TimelineEvent` records for the Universal Timeline Engine.
