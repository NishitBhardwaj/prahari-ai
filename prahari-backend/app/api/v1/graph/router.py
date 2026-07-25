"""Graph Intelligence API — Neo4j-powered relationship and network queries."""

from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.db.neo4j.client import execute_query
from app.core.permissions import require_permissions, Permission
from app.utils.response import ApiResponse

from app.api.v1.graph.resolution import router as resolution_router

router = APIRouter()
router.include_router(resolution_router, prefix="/resolution", tags=["Entity Resolution"])


@router.get("/person/{person_id}", summary="Get all graph relationships for a person")
async def get_person_graph(
    person_id: str,
    depth: int = Query(2, ge=1, le=3, description="Relationship traversal depth"),
    current_user=Depends(require_permissions(Permission.GRAPH_READ)),
):
    """
    Return the ego network for a person — all nodes and edges within N hops.
    Suitable for Cytoscape.js rendering on the link analysis dashboard.
    """
    try:
        records = await execute_query(
            f"""
            MATCH path = (p {{id: $person_id}})-[*1..{depth}]-(connected)
            RETURN nodes(path) as nodes, relationships(path) as rels
            LIMIT 200
            """,
            {"person_id": person_id},
        )

        nodes_seen = set()
        edges_seen = set()
        nodes = []
        edges = []

        for record in records:
            for node in (record.get("nodes") or []):
                nid = node.get("id", str(id(node)))
                if nid not in nodes_seen:
                    nodes_seen.add(nid)
                    nodes.append({
                        "id": nid,
                        "labels": list(node.labels) if hasattr(node, "labels") else [],
                        "data": dict(node),
                    })
            for rel in (record.get("rels") or []):
                eid = str(rel.id) if hasattr(rel, "id") else str(id(rel))
                if eid not in edges_seen:
                    edges_seen.add(eid)
                    edges.append({
                        "id": eid,
                        "source": str(rel.start_node.get("id", "")) if hasattr(rel, "start_node") else "",
                        "target": str(rel.end_node.get("id", "")) if hasattr(rel, "end_node") else "",
                        "type": rel.type if hasattr(rel, "type") else "",
                        "data": dict(rel),
                    })

        return ApiResponse.ok(data={"nodes": nodes, "edges": edges, "depth": depth})

    except Exception as e:
        # Return empty graph if Neo4j is unavailable
        return ApiResponse.ok(data={"nodes": [], "edges": [], "error": str(e)})


@router.get("/case/{case_id}", summary="Get full entity graph for a case")
async def get_case_graph(
    case_id: str,
    current_user=Depends(require_permissions(Permission.GRAPH_READ)),
):
    """Return all entities connected to a case — accused, victims, evidence, CDRs."""
    try:
        records = await execute_query(
            """
            MATCH path = (c:Case {id: $case_id})-[*1..2]-(connected)
            RETURN nodes(path) as nodes, relationships(path) as rels
            LIMIT 300
            """,
            {"case_id": case_id},
        )
        return ApiResponse.ok(data={"graph": records})
    except Exception as e:
        return ApiResponse.ok(data={"nodes": [], "edges": [], "error": str(e)})


@router.get("/gang/{gang_id}", summary="Get gang network subgraph")
async def get_gang_graph(
    gang_id: str,
    current_user=Depends(require_permissions(Permission.GRAPH_READ)),
):
    """Return full gang network — all members, associated cases, and communication links."""
    try:
        records = await execute_query(
            """
            MATCH (g:Gang {id: $gang_id})<-[:MEMBER_OF]-(member)
            OPTIONAL MATCH (member)-[r:ACCUSED_IN|CALLS|TRANSACTS_WITH]-(related)
            RETURN g, member, r, related
            LIMIT 300
            """,
            {"gang_id": gang_id},
        )
        return ApiResponse.ok(data={"graph": records, "gang_id": gang_id})
    except Exception as e:
        return ApiResponse.ok(data={"nodes": [], "edges": [], "error": str(e)})


@router.get("/community", summary="Detected criminal communities / clusters")
async def get_communities(
    current_user=Depends(require_permissions(Permission.GRAPH_READ)),
):
    """
    Return detected criminal communities using Louvain or Label Propagation.
    In production this calls Neo4j GDS (Graph Data Science) library.
    """
    # Demo data — replace with Neo4j GDS community detection call
    return ApiResponse.ok(data=[
        {"community_id": "C1", "size": 14, "threat_level": "HIGH", "dominant_crime": "Narcotics", "districts": ["Dakshina Kannada", "Udupi"]},
        {"community_id": "C2", "size": 8, "threat_level": "MEDIUM", "dominant_crime": "Cyber Fraud", "districts": ["Bengaluru Urban"]},
        {"community_id": "C3", "size": 22, "threat_level": "HIGH", "dominant_crime": "Robbery", "districts": ["Mysuru", "Hassan"]},
    ])
