"""
Case Repository — domain-specific queries for Cases (FIRs).
"""

from typing import List, Optional, Tuple
from datetime import date
from sqlalchemy import select, func, and_, or_, desc, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres.models.case import Case
from app.repositories.base import BaseRepository


class CaseRepository(BaseRepository[Case]):
    def __init__(self, session: AsyncSession):
        super().__init__(Case, session)

    async def get_by_fir(self, fir_number: str) -> Optional[Case]:
        result = await self.session.execute(
            select(Case).where(Case.fir_number == fir_number)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        q: Optional[str] = None,
        district_id: Optional[str] = None,
        station_id: Optional[str] = None,
        crime_head: Optional[str] = None,
        status: Optional[str] = None,
        year: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        is_gang_related: Optional[bool] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> Tuple[List[Case], int]:
        """Full-featured search with all filter combinations."""
        filters = []

        if q:
            filters.append(
                or_(
                    Case.fir_number.ilike(f"%{q}%"),
                    Case.crime_head_name.ilike(f"%{q}%"),
                    Case.place_of_occurrence.ilike(f"%{q}%"),
                    Case.station_name.ilike(f"%{q}%"),
                )
            )
        if district_id:
            filters.append(Case.district_id == district_id)
        if station_id:
            filters.append(Case.station_id == station_id)
        if crime_head:
            filters.append(Case.crime_head_name.ilike(f"%{crime_head}%"))
        if status:
            filters.append(Case.status_name == status)
        if year:
            filters.append(Case.year == year)
        if date_from:
            filters.append(Case.date_of_report >= date_from)
        if date_to:
            filters.append(Case.date_of_report <= date_to)
        if is_gang_related is not None:
            filters.append(Case.label_is_gang_related == is_gang_related)

        return await self.list(
            filters=filters,
            order_by=desc(Case.date_of_report),
            limit=limit,
            offset=offset,
        )

    async def get_district_stats(self, district_id: str, year: int) -> dict:
        """Aggregate stats for dashboard district drill-down."""
        result = await self.session.execute(
            select(
                Case.crime_head_name,
                func.count(Case.case_id).label("count"),
            )
            .where(and_(Case.district_id == district_id, Case.year == year))
            .group_by(Case.crime_head_name)
            .order_by(desc("count"))
        )
        return {row.crime_head_name: row.count for row in result.all()}

    async def get_heatmap_data(
        self,
        year: Optional[int] = None,
        crime_head: Optional[str] = None,
    ) -> List[dict]:
        """Return lat/lon/count data for heatmap rendering."""
        query = select(
            Case.latitude,
            Case.longitude,
            Case.crime_head_name,
            Case.district_id,
            func.count(Case.case_id).label("count"),
        ).where(
            and_(Case.latitude.isnot(None), Case.longitude.isnot(None))
        )
        if year:
            query = query.where(Case.year == year)
        if crime_head:
            query = query.where(Case.crime_head_name == crime_head)

        query = query.group_by(
            Case.latitude, Case.longitude, Case.crime_head_name, Case.district_id
        )

        result = await self.session.execute(query)
        return [
            {
                "lat": row.latitude,
                "lon": row.longitude,
                "crime": row.crime_head_name,
                "district_id": row.district_id,
                "count": row.count,
            }
            for row in result.all()
        ]

    async def get_trend_data(self, years: List[int]) -> List[dict]:
        """Monthly crime counts across the selected years."""
        result = await self.session.execute(
            select(
                Case.year,
                extract("month", Case.date_of_report).label("month"),
                Case.crime_head_name,
                func.count(Case.case_id).label("count"),
            )
            .where(Case.year.in_(years))
            .group_by(Case.year, "month", Case.crime_head_name)
            .order_by(Case.year, "month")
        )
        return [
            {
                "year": row.year,
                "month": int(row.month),
                "crime": row.crime_head_name,
                "count": row.count,
            }
            for row in result.all()
        ]
