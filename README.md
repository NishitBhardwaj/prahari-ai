# Prahari AI

**Enterprise-Grade AI-Powered Crime Intelligence & Investigation Platform**

Prahari AI is a modern, unified investigation workspace designed for the Karnataka State Police. It transitions law enforcement agencies from disconnected spreadsheets and siloed legacy systems into a unified, intelligence-driven command center.

## Core Modules

1. **Dataset Generator (`/dataset-generator`)**
   A high-performance synthetic data engine that generates millions of interconnected records (persons, cases, evidence, financial transactions, communications) ensuring strict chronological and geographical consistency. Used to simulate 10+ years of state-wide crime data for AI training and graph analysis.
   
2. **Prahari Backend (`/prahari-backend`)**
   Built with **FastAPI**, Clean Architecture, and **Zoho Catalyst**. It acts as the central nerve center for:
   - **Universal Timeline Engine:** A chronological ledger of all events.
   - **Progressive Draft APIs:** For multi-step, auto-saving data entry.
   - **Graph Intelligence:** Powered by **Neo4j** for link analysis.
   - **Vector Search & AI:** Powered by **Qdrant** and Gemini for semantic case similarity and the RAG assistant.

3. **Prahari Frontend (`/prahari-frontend`)**
   Built with **Next.js 15 (App Router)**, **Tailwind CSS v4**, **React Query**, and **Zustand**. The frontend provides a premium, command-center experience heavily inspired by enterprise intelligence platforms. It features:
   - **Unified Case Workspace:** A three-pane layout integrating timelines, evidence grids, and an always-on AI assistant.
   - **Progressive FIR Wizard:** An iterative, draft-based approach to registering complex cases without data loss.
   - **Entity Resolution Center:** AI-assisted deduplication UI.

## Getting Started

### 1. Dataset Generation
```bash
cd dataset-generator
python cli.py generate all
```
*Outputs are saved to `dataset-generator/output/`.*

### 2. Backend Services
```bash
cd prahari-backend
uvicorn app.main:app --reload
```

### 3. Frontend Web App
```bash
cd prahari-frontend
npm install --legacy-peer-deps
npm run dev
```

## Architecture

Prahari AI relies heavily on a polyglot persistence model:
- **PostgreSQL:** Transactional truth (Cases, Entities, Users, Evidence).
- **Neo4j:** Relational truth (Networks, Gangs, Money trails).
- **Qdrant:** Semantic truth (Vector embeddings for AI similarity matching).
- **Zoho Catalyst:** Cloud infrastructure (Datastore, Cache, Cron, Signals, Stratus, SmartBrowz).

## Status

Currently in active development as part of the Zoho Catalyst Hackathon. Phase 4.3 (Unified Case Intelligence Workspace) is fully implemented.
