import asyncio
import pandas as pd
from loguru import logger
import numpy as np
import sys
import os

from app.db.postgres.engine import AsyncSessionFactory, engine, Base
from app.db.postgres import models
from .utils import get_csv_path, print_success, print_progress
from .validator import validate_csv

IMPORT_ORDER = [
    ("districts.csv", models.station.District),
    ("police_stations.csv", models.station.PoliceStation),
    ("persons.csv", models.person.Person),
    ("employees.csv", models.user.User),
    ("cases.csv", models.case.Case),
    ("accused_records.csv", models.accused.AccusedRecord),
    ("evidence.csv", models.evidence.Evidence),
    ("crime_events.csv", models.evidence.CrimeEvent),
    ("investigation_diaries.csv", models.evidence.InvestigationDiary),
    ("chargesheet_details.csv", models.chargesheet.Chargesheet),
    ("court_proceedings.csv", models.chargesheet.CourtProceeding),
    ("gangs.csv", models.gang.Gang)
]

async def clear_database():
    print_progress(0, 4, "Clearing PostgreSQL Database")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print_success("Database cleared and schema recreated.")

async def import_csv_to_table(session, filename: str, model):
    try:
        validate_csv(filename)
    except FileNotFoundError:
        logger.warning(f"File {filename} not found, skipping...")
        return 0
    except ValueError as e:
        logger.error(f"Validation failed for {filename}: {e}")
        return 0
        
    path = get_csv_path(filename)
    df = pd.read_csv(path, low_memory=False, nrows=10000)
    
    # Pre-parse dates to avoid string issues
    for c in model.__table__.columns:
        if c.name in df.columns:
            tname = type(c.type).__name__
            if tname == 'Date':
                df[c.name] = pd.to_datetime(df[c.name], errors='coerce').dt.date
            elif tname in ('DateTime', 'TIMESTAMP'):
                df[c.name] = pd.to_datetime(df[c.name], errors='coerce')
                
    df = df.replace({np.nan: None, pd.NaT: None})
    records = df.to_dict(orient="records")
    
    model_columns = {c.name: type(c.type).__name__ for c in model.__table__.columns}
    cleaned_records = []
    for r in records:
        cleaned = {}
        for k, v in r.items():
            if k in model_columns:
                if v is None:
                    cleaned[k] = None
                else:
                    tname = model_columns[k]
                    if tname in ('String', 'VARCHAR', 'Text', 'UUID', 'CHAR'):
                        if isinstance(v, float) and v.is_integer():
                            cleaned[k] = str(int(v))
                        else:
                            cleaned[k] = str(v)
                    elif tname in ('Integer', 'BigInteger', 'SmallInteger'):
                        cleaned[k] = int(v)
                    elif tname in ('Float', 'Numeric', 'REAL', 'DOUBLE_PRECISION'):
                        cleaned[k] = float(v)
                    elif tname == 'Boolean':
                        cleaned[k] = bool(v)
                    else:
                        cleaned[k] = v
        cleaned_records.append(cleaned)
        
    chunk_size = 500
    inserted = 0
    for i in range(0, len(cleaned_records), chunk_size):
        chunk = cleaned_records[i:i + chunk_size]
        await session.run_sync(lambda s: s.bulk_insert_mappings(model, chunk))
        await session.commit()
        inserted += len(chunk)
        
    return inserted

async def run_postgres_import(stats: dict):
    await clear_database()
    print_progress(1, 4, "Importing PostgreSQL Data")
    total_cases = 0
    
    async with AsyncSessionFactory() as session:
        for filename, model in IMPORT_ORDER:
            try:
                count = await import_csv_to_table(session, filename, model)
                stats['rows'][filename.replace(".csv", "")] = count
                print_success(f"Imported {count} records into {model.__tablename__} from {filename}")
                if filename == "cases.csv":
                    total_cases = count
            except Exception as e:
                logger.error(f"Failed to import {filename}: {e}")
                raise e
        await session.commit()
    return total_cases
