# End-to-End Testing Checklist

Use this checklist during local and production validation to ensure all Prahari AI modules are stable.

## 1. Authentication & RBAC
- [ ] Login via Zoho Catalyst Auth returns valid JWT.
- [ ] JWT validates properly in FastAPI backend middleware.
- [ ] RBAC enforcement: Standard user cannot access Admin endpoints (e.g., system configuration).

## 2. Progressive FIR Workflow
- [ ] `POST /cases/draft` successfully initializes a new Case draft and timeline event.
- [ ] Autosave (`PATCH /cases/{id}`) updates fields correctly without full page reload.
- [ ] Navigating away and back restores draft state via Zustand/React Query.
- [ ] Adding a Victim successfully attaches entity and updates Neo4j background sync.

## 3. Case Intelligence Workspace
- [ ] Left Navigation correctly routes between Timeline, Tasks, Evidence, etc.
- [ ] Active Case ID persists correctly across the workspace.
- [ ] Right AI Sidebar opens/closes smoothly without layout shifting.

## 4. Universal Timeline
- [ ] Timeline feed renders chronologically.
- [ ] Events appear correctly for: Task updates, Evidence uploads, AI score changes, Draft creation.

## 5. Investigation Tasks (Kanban)
- [ ] Task board fetches tasks for active case.
- [ ] Drag-and-drop (or move button) correctly patches status to backend.
- [ ] Changing task status triggers a Timeline update event.

## 6. Evidence & Chain of Custody
- [ ] Evidence grid renders correctly.
- [ ] Uploading a new evidence version creates a new `EvidenceVersion` record.
- [ ] Version history reflects correct uploader and timestamp.

## 7. Entity Resolution
- [ ] Resolution modal fetches mock matches correctly based on name/phone.
- [ ] Clicking "Soft Merge" triggers correct backend handling without hard-deleting the source entity.

## 8. Context-Aware AI Assistant (RAG)
- [ ] Sending a chat automatically includes the active Case ID in the payload.
- [ ] AI responds accurately based on the specific case data.
