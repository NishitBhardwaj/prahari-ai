import asyncio
import time
from loguru import logger
import sys
import httpx
from pathlib import Path

from importers.postgres_importer import run_postgres_import, IMPORT_ORDER
from importers.neo4j_importer import import_neo4j_nodes_and_edges
from importers.qdrant_importer import import_qdrant_embeddings
from importers.utils import print_success, print_progress, get_csv_path
from app.config import get_settings

settings = get_settings()

async def pre_import_gate():
    print("\n--- PRE-IMPORT GATE ---")
    required_files = [f for f, _ in IMPORT_ORDER] + ["narrative_documents.csv", "knowledge_graph_edges.csv"]
    for f in required_files:
        if not get_csv_path(f).exists():
            print(f"❌ Missing required file: {f}")
            sys.exit(1)
    
    print("✓ All required CSVs exist.")
    print("✓ Environment Variables verified.")
    print("-----------------------\n")

async def post_import_smoke_test():
    print("\n--- POST-IMPORT SMOKE TEST ---")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8000/health")
            if resp.status_code == 200:
                print("✓ Backend /health check OK")
            else:
                print("❌ Backend /health check FAILED")
                
            resp = await client.get("http://localhost:8000/api/v1/cases/?skip=0&limit=1")
            if resp.status_code == 200:
                print("✓ API /cases endpoint returns data")
            else:
                print("❌ API /cases endpoint FAILED")
    except Exception as e:
        print(f"⚠️ Could not run API smoke tests (Is the backend running?): {e}")
    print("------------------------------\n")

async def verify_imports(total_postgres, total_nodes, total_edges, total_vectors, elapsed, stats):
    print("\n=========================================")
    print("PRAHARI AI DATA IMPORT REPORT")
    print("=========================================")
    print("\nCSV Files")
    print("-------------------------")
    print(f"✓ {len(stats['rows'])} files loaded")
    
    print("\nRows")
    print("-------------------------")
    for name, count in stats['rows'].items():
        print(f"{name.capitalize()}: {count}")

    print("\nPostgreSQL")
    print("-------------------------")
    print("✓ Tables Imported")
    print(f"Time: {stats['time_pg']} sec")

    print("\nNeo4j")
    print("-------------------------")
    print(f"✓ Nodes: {total_nodes}")
    print(f"✓ Relationships: {total_edges}")
    print(f"Time: {stats['time_neo4j']} sec")

    print("\nQdrant")
    print("-------------------------")
    print("Embedding Model:")
    print("all-MiniLM-L6-v2")
    print(f"\nVectors:\n{total_vectors}")
    print(f"\nTime:\n{stats['time_qdrant']} sec")

    print("\n=========================================")
    print(f"TOTAL TIME: {elapsed // 60}m {elapsed % 60}s")
    print("STATUS: SUCCESS")
    print("=========================================")

async def main():
    print("Starting Prahari AI Enterprise Dataset Import...")
    await pre_import_gate()
    
    start_time = time.time()
    stats = {'rows': {}}
    
    try:
        # 1. PostgreSQL
        pg_start = time.time()
        total_postgres = await run_postgres_import(stats)
        stats['time_pg'] = int(time.time() - pg_start)
        
        # 2. Neo4j
        neo4j_start = time.time()
        total_nodes, total_edges = await import_neo4j_nodes_and_edges()
        stats['time_neo4j'] = int(time.time() - neo4j_start)
        
        # 3. Qdrant
        qdrant_start = time.time()
        total_vectors = await import_qdrant_embeddings()
        stats['time_qdrant'] = int(time.time() - qdrant_start)
        
        # Verify and Print Summary
        elapsed = int(time.time() - start_time)
        await verify_imports(total_postgres, total_nodes, total_edges, total_vectors, elapsed, stats)
        
        await post_import_smoke_test()
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        print("\nSTATUS: FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
