# Prahari AI - API Reference

## Authentication
Prahari AI uses OAuth2 with JWT tokens, integrated with Zoho Catalyst Auth.

- `POST /api/v1/auth/login`: Issue access & refresh tokens.
- `POST /api/v1/auth/refresh`: Refresh access token.
- `GET /api/v1/auth/me`: Get current user context & RBAC permissions.

## Case Management
- `GET /api/v1/cases`: List paginated cases (Supports filtering by Status, IO).
- `GET /api/v1/cases/{case_id}`: Fetch full case payload.
- `POST /api/v1/cases/draft`: Initialize a Progressive FIR draft. Returns `case_id`.
- `PATCH /api/v1/cases/{case_id}`: Autosave incremental updates to core case details.
- `POST /api/v1/cases/{case_id}/victims`: Add victim entity.
- `POST /api/v1/cases/{case_id}/accused`: Add accused entity.
- `GET /api/v1/cases/{case_id}/timeline`: Retrieve Universal Timeline events.

## Investigation Tasks
- `GET /api/v1/tasks/case/{case_id}`: Get all tasks for Kanban board.
- `PATCH /api/v1/tasks/{task_id}`: Update task status (e.g., IN_PROGRESS, COMPLETED).

## Evidence & Chain of Custody
- `GET /api/v1/evidence/case/{case_id}`: Get physical/digital evidence items and their version histories.
- `POST /api/v1/evidence/case/{case_id}`: Log new evidence.
- `POST /api/v1/evidence/{evidence_id}/versions`: Upload new forensic document/version.

## AI & Graph Intelligence
- `GET /api/v1/ai/risk/{person_id}`: Fetch AI violence/flight risk scores with XAI reasoning.
- `POST /api/v1/ai/rag/query`: Context-aware Assistant querying.
- `GET /api/v1/graph/person/{person_id}`: Fetch Neo4j ego-network for link analysis.
- `POST /api/v1/graph/resolution/check`: Query AI for potential duplicate entities in the graph.
- `POST /api/v1/graph/resolution/merge`: Execute a "Soft Merge" for entity resolution.
