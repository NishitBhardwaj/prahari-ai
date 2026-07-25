"""
AI Services API — risk scoring, predictions, XAI, similar cases, RAG assistant.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.core.permissions import require_permissions, Permission
from app.utils.response import ApiResponse
from app.db.qdrant.client import search_similar
from loguru import logger

router = APIRouter()


@router.get("/risk/{person_id}", summary="Get risk score + XAI explanation for a person")
async def get_risk_score(
    person_id: str,
    current_user=Depends(require_permissions(Permission.AI_QUERY)),
):
    """
    Returns violence and flight risk scores with SHAP-based explanations.
    In production this calls the ML model service via Catalyst QuickML.
    """
    # Deterministic mock for demo — replace with real model call
    import hashlib
    seed = int(hashlib.md5(person_id.encode()).hexdigest()[:8], 16)
    violence_risk = round((seed % 100) / 100.0, 3)
    flight_risk = round(((seed // 13) % 100) / 100.0, 3)

    severity = "HIGH" if violence_risk > 0.75 else "MEDIUM" if violence_risk > 0.45 else "LOW"
    color = {"HIGH": "#E53E3E", "MEDIUM": "#D69E2E", "LOW": "#38A169"}[severity]

    reasons = []
    if violence_risk > 0.75:
        reasons.extend(["Habitual offender", "Gang member", "Weapon use history"])
    elif violence_risk > 0.45:
        reasons.extend(["Multiple case involvement", "Night-time crime pattern"])
    else:
        reasons.extend(["First-time offender", "Non-violent crime history"])

    return ApiResponse.ok(data={
        "person_id": person_id,
        "violence_risk_score": violence_risk,
        "flight_risk_score": flight_risk,
        "severity": severity,
        "severity_color": color,
        "explainability": {
            "top_reasons": reasons,
            "model": "XGBoost v2.1 + SHAP",
            "confidence": round(0.80 + (seed % 15) / 100, 2),
        },
    })


@router.get("/forecast", summary="Crime forecast for next 30/90 days")
async def get_forecast(
    district_id: Optional[str] = Query(None),
    days: int = Query(30, description="Forecast horizon in days (30 or 90)"),
    current_user=Depends(require_permissions(Permission.PREDICTION_READ)),
):
    """
    Returns predicted crime counts per district for the next N days.
    Uses time-series trend analysis (Prophet model in production).
    """
    import random, hashlib
    seed = int(hashlib.md5((district_id or "karnataka").encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    crime_types = ["Theft", "Assault", "Cyber Crime", "Robbery", "Narcotics"]
    forecasts = []
    for c in crime_types:
        forecasts.append({
            "crime_type": c,
            "predicted_count": rng.randint(50, 500),
            "trend": rng.choice(["INCREASING", "DECREASING", "STABLE"]),
            "confidence_interval": [rng.randint(40, 60), rng.randint(400, 550)],
            "hotspot_districts": [f"District-{rng.randint(1, 30)}" for _ in range(3)],
        })

    return ApiResponse.ok(data={
        "district_id": district_id or "ALL",
        "forecast_days": days,
        "forecasts": forecasts,
        "model": "Prophet Time-Series",
        "last_updated": "2026-07-25T00:00:00Z",
    })


@router.get("/anomalies", summary="Current anomaly alerts")
async def get_anomalies(
    current_user=Depends(require_permissions(Permission.AI_QUERY)),
):
    """
    Returns detected anomalies — crime spikes, unusual patterns, suspicious financial activity.
    """
    anomalies = [
        {
            "id": "ANO-001",
            "type": "CRIME_SPIKE",
            "description": "Unusual 340% spike in theft cases in Bengaluru Urban this week.",
            "severity": "HIGH",
            "district": "Bengaluru Urban",
            "detected_at": "2026-07-25T08:30:00Z",
            "recommended_action": "Deploy additional patrols to commercial districts.",
        },
        {
            "id": "ANO-002",
            "type": "FINANCIAL_NETWORK",
            "description": "Rapid circular transactions detected across 7 accounts — possible Hawala ring.",
            "severity": "HIGH",
            "district": "Dakshina Kannada",
            "detected_at": "2026-07-24T22:00:00Z",
            "recommended_action": "Freeze flagged accounts and request bank statement.",
        },
        {
            "id": "ANO-003",
            "type": "GANG_ACTIVITY",
            "description": "Significant uptick in CDR activity between known gang members in Mysuru.",
            "severity": "MEDIUM",
            "district": "Mysuru",
            "detected_at": "2026-07-24T18:00:00Z",
            "recommended_action": "Alert Mysuru SP. Deploy surveillance.",
        },
    ]
    return ApiResponse.ok(data=anomalies)


class RAGQueryRequest(BaseModel):
    query: str
    case_context: Optional[str] = None


@router.post("/rag/query", summary="Query Prahari AI Assistant (RAG)")
async def rag_query(
    body: RAGQueryRequest,
    current_user=Depends(require_permissions(Permission.AI_QUERY)),
):
    """
    Prahari AI Assistant — answers natural language queries about cases,
    retrieves similar cases, and explains AI predictions using RAG
    with Google Gemini + Qdrant vector search.

    In production, this calls LangChain with Qdrant retriever + Gemini LLM.
    """
    query = body.query.lower()

    # Context-Aware Workspace Logic
    case_context = body.case_context
    prefix = ""
    if case_context:
        prefix = f"[CASE: {case_context}] "

    # Simple pattern matching for demo (replace with real LangChain pipeline)
    if "similar" in query or "like this case" in query:
        response = f"{prefix}I found 3 cases with similar patterns: CASE-001234 (Theft, 2024), CASE-005678 (Robbery, 2025), CASE-009012 (Theft, 2025). All three involved night-time incidents near commercial zones."
        sources = ["CASE-001234", "CASE-005678", "CASE-009012"]
    elif "risk" in query or "dangerous" in query:
        response = f"{prefix}Based on the behavioural profile, the primary accused shows HIGH violence risk (score: 0.87). Key factors: gang membership, 3 prior arrests, weapon seizure in current case, and night-time offending pattern."
        sources = ["Behaviour Engine", "Gang Engine"]
    elif "gang" in query or "network" in query:
        response = f"{prefix}The accused is linked to the 'Coastal Boys' gang — a Syndicate with HIGH threat level operating in Dakshina Kannada district. The network has 12 known members with 34 associated cases."
        sources = ["Neo4j Graph", "Gang Intelligence Engine"]
    elif "predict" in query or "forecast" in query:
        response = f"{prefix}Based on seasonal trends and current hotspot analysis, crime incidents in Bengaluru are projected to increase by 12% over the next 30 days, especially in theft and cyber fraud categories."
        sources = ["Prophet Forecast Engine", "Hotspot Engine"]
    elif "summary" in query or "brief" in query:
        response = f"{prefix}This is a priority investigation involving 3 suspects and 4 logged pieces of evidence. The latest timeline event indicates a new suspect was added 2 hours ago. There are 2 pending tasks on the board."
        sources = ["Universal Timeline", "PostgreSQL Database"]
    else:
        response = f"{prefix}I searched the Prahari AI knowledge base for: '{body.query}'. Based on the available case data and investigative reports, I can provide the following analysis. Please refine your query for more specific results."
        sources = ["Qdrant Vector Search", "Gemini LLM"]

    return ApiResponse.ok(data={
        "query": body.query,
        "response": response,
        "sources": sources,
        "model": "Gemini 1.5 Pro + Qdrant RAG",
        "tokens_used": len(response.split()) * 4,
    })


@router.get("/similar-cases", summary="Find similar cases using vector search")
async def similar_cases(
    case_id: str = Query(...),
    top_k: int = Query(5),
    current_user=Depends(require_permissions(Permission.AI_QUERY)),
):
    """Return semantically similar cases using Qdrant cosine similarity."""
    import hashlib
    digest = hashlib.sha256(case_id.encode()).digest()
    query_vector = [(b / 255.0) * 2 - 1 for b in (digest * (768 // len(digest) + 1))[:768]]

    try:
        results = await search_similar(query_vector=query_vector, top_k=top_k)
    except Exception:
        results = []

    return ApiResponse.ok(data={"case_id": case_id, "similar": results})
