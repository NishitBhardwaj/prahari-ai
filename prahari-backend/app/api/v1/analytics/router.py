"""Analytics API — heatmaps, trends, district stats, Sankey data."""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.db.postgres.session import get_async_session
from app.db.postgres.models.case import Case
from app.repositories.case_repository import CaseRepository
from app.core.permissions import require_permissions, Permission
from app.utils.response import ApiResponse

router = APIRouter()


@router.get("/heatmap", summary="Crime heatmap data (lat/lon/count)")
async def get_heatmap(
    year: Optional[int] = Query(None),
    crime_head: Optional[str] = Query(None),
    district_id: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.ANALYTICS_READ)),
):
    """Return aggregated lat/lon/count data suitable for MapLibre GL JS heatmap layer."""
    repo = CaseRepository(session)
    data = await repo.get_heatmap_data(year=year, crime_head=crime_head)

    # Apply optional district filter
    if district_id:
        data = [d for d in data if d.get("district_id") == district_id]

    return ApiResponse.ok(data=data)


@router.get("/trends", summary="Monthly crime trends")
async def get_trends(
    years: str = Query("2022,2023,2024,2025", description="Comma-separated years"),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.ANALYTICS_READ)),
):
    """Return monthly crime counts by type for trend charts."""
    year_list = [int(y.strip()) for y in years.split(",")]
    repo = CaseRepository(session)
    data = await repo.get_trend_data(years=year_list)
    return ApiResponse.ok(data=data)


@router.get("/district/{district_id}", summary="District drill-down statistics")
async def get_district_stats(
    district_id: str,
    year: int = Query(2025),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.ANALYTICS_READ)),
):
    """Return crime breakdown for a specific district."""
    repo = CaseRepository(session)
    stats = await repo.get_district_stats(district_id=district_id, year=year)

    # Also get total
    total = sum(stats.values())
    return ApiResponse.ok(data={
        "district_id": district_id,
        "year": year,
        "total_cases": total,
        "by_crime_head": stats,
    })


@router.get("/summary", summary="Executive KPI summary")
async def get_summary(
    year: int = Query(2025),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.ANALYTICS_READ)),
):
    """High-level KPI stats for the executive command center."""
    result = await session.execute(
        select(
            func.count(Case.case_id).label("total"),
            func.sum(Case.label_is_solved.cast(Integer)).label("solved"),
            func.sum(Case.label_is_gang_related.cast(Integer)).label("gang_related"),
            func.sum(Case.label_is_cyber.cast(Integer)).label("cyber"),
        ).where(Case.year == year)
    )
    row = result.one_or_none()

    total = row.total or 0
    solved = int(row.solved or 0)
    gang = int(row.gang_related or 0)
    cyber = int(row.cyber or 0)

    return ApiResponse.ok(data={
        "year": year,
        "total_cases": total,
        "cases_solved": solved,
        "solve_rate_pct": round(solved / total * 100, 1) if total else 0,
        "gang_related": gang,
        "cyber_crime": cyber,
        "open_cases": total - solved,
    })


@router.get("/sankey", summary="Legal flow Sankey data")
async def get_sankey(
    year: int = Query(2025),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.ANALYTICS_READ)),
):
    """
    Return flow data for Sankey diagram:
    Crime Type → Case Status → Court Outcome
    """
    result = await session.execute(
        select(
            Case.crime_head_name,
            Case.status_name,
            func.count(Case.case_id).label("count"),
        )
        .where(Case.year == year)
        .group_by(Case.crime_head_name, Case.status_name)
        .order_by(desc("count"))
        .limit(100)
    )

    nodes = set()
    links = []
    for row in result.all():
        nodes.add(row.crime_head_name)
        nodes.add(row.status_name)
        links.append({
            "source": row.crime_head_name,
            "target": row.status_name,
            "value": row.count,
        })

    return ApiResponse.ok(data={
        "nodes": [{"id": n} for n in nodes],
        "links": links,
    })


@router.get("/hotspots", summary="Predicted crime hotspot clusters")
async def get_hotspots(
    crime_head: Optional[str] = Query(None),
    year: int = Query(2025),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.PREDICTION_READ)),
):
    """
    Returns clustered hotspot polygons using simple grid aggregation.
    In production, this would use PostGIS ST_ClusterWithin or ST_ClusterKMeans.
    """
    repo = CaseRepository(session)
    points = await repo.get_heatmap_data(year=year, crime_head=crime_head)

    # Simple bucket grid: round lat/lon to 2 decimal places for clustering
    clusters: dict = {}
    for p in points:
        key = (round(p["lat"], 2), round(p["lon"], 2))
        if key not in clusters:
            clusters[key] = {"lat": key[0], "lon": key[1], "count": 0, "crimes": {}}
        clusters[key]["count"] += p["count"]
        clusters[key]["crimes"][p["crime"]] = clusters[key]["crimes"].get(p["crime"], 0) + p["count"]

    hotspots = sorted(clusters.values(), key=lambda x: x["count"], reverse=True)[:50]
    return ApiResponse.ok(data=hotspots)
