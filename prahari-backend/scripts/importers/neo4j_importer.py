import pandas as pd
from loguru import logger
import numpy as np

from app.db.neo4j.client import get_neo4j_driver
from .utils import get_csv_path, print_success, print_progress
from .validator import validate_csv

async def clear_neo4j():
    print_progress(1, 4, "Clearing Neo4j Database")
    driver = get_neo4j_driver()
    async with driver._driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
    print_success("Neo4j cleared.")

async def import_neo4j_nodes_and_edges():
    await clear_neo4j()
    print_progress(2, 4, "Building Neo4j Graph")
    
    # We will import nodes first from Postgres CSVs to ensure all nodes exist
    driver = get_neo4j_driver()
    
    nodes_imported = 0
    edges_imported = 0
    
    async with driver._driver.session() as session:
        # Import Cases
        validate_csv("cases.csv")
        cases_df = pd.read_csv(get_csv_path("cases.csv"), nrows=10000).replace({np.nan: None})
        for i in range(0, len(cases_df), 500):
            chunk = cases_df.iloc[i:i+500].to_dict("records")
            await session.run("""
                UNWIND $rows AS row
                MERGE (c:Case {case_id: row.case_id})
                SET c.crime_type = row.crime_type, c.district = row.district
            """, rows=chunk)
            nodes_imported += len(chunk)
        print_success(f"Imported Case nodes")
        
        # Import Persons
        validate_csv("persons.csv")
        persons_df = pd.read_csv(get_csv_path("persons.csv"), nrows=10000).replace({np.nan: None})
        for i in range(0, len(persons_df), 500):
            chunk = persons_df.iloc[i:i+500].to_dict("records")
            await session.run("""
                UNWIND $rows AS row
                MERGE (p:Person {person_id: row.person_id})
                SET p.name = row.name_full, p.gender = row.gender
            """, rows=chunk)
            nodes_imported += len(chunk)
        print_success(f"Imported Person nodes")
        
        # Import Knowledge Graph Edges
        # The dataset generator produces knowledge_graph_edges.csv
        try:
            validate_csv("knowledge_graph_edges.csv")
            edges_df = pd.read_csv(get_csv_path("knowledge_graph_edges.csv"), nrows=10000).replace({np.nan: None})
            for i in range(0, len(edges_df), 500):
                chunk = edges_df.iloc[i:i+500].to_dict("records")
                # source_id, target_id, relation_type, source_label, target_label
                await session.run("""
                    UNWIND $rows AS row
                    // Using apoc.merge.node and apoc.merge.relationship if available, or just generic MATCH since we already imported nodes
                    MATCH (s) WHERE s.case_id = row.source_id OR s.person_id = row.source_id OR s.gang_id = row.source_id
                    MATCH (t) WHERE t.case_id = row.target_id OR t.person_id = row.target_id OR t.gang_id = row.target_id
                    CALL apoc.merge.relationship(s, row.relation_type, {}, {}, t, {}) YIELD rel
                    RETURN rel
                """, rows=chunk)
                edges_imported += len(chunk)
            print_success(f"Imported Graph Edges")
        except FileNotFoundError:
            logger.warning("knowledge_graph_edges.csv not found, skipping edges.")
            
    return nodes_imported, edges_imported
