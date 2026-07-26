import pandas as pd
from loguru import logger
import numpy as np
from sentence_transformers import SentenceTransformer
import uuid

from app.db.qdrant.client import get_qdrant
from .utils import get_csv_path, print_success, print_progress
from .validator import validate_csv
from app.config import get_settings

settings = get_settings()

async def import_qdrant_embeddings():
    print_progress(3, 4, "Building Qdrant Embeddings")
    
    validate_csv("cases.csv")
    validate_csv("narrative_documents.csv")
    
    cases_df = pd.read_csv(get_csv_path("cases.csv"), nrows=10000).replace({np.nan: ""})
    narratives_df = pd.read_csv(get_csv_path("narrative_documents.csv"), nrows=10000).replace({np.nan: ""})
    
    # Merge narratives with cases to get metadata
    merged = pd.merge(narratives_df, cases_df, on="case_id", how="left")
    
    logger.info("Loading local embedding model: sentence-transformers/all-MiniLM-L6-v2")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    qdrant = get_qdrant()
    collection_name = settings.QDRANT_COLLECTION
    
    # The default vector size for all-MiniLM-L6-v2 is 384! 
    # Qdrant collection might be created with 768. 
    # If the collection size mismatch, we should recreate it!
    # We will assume Qdrant collection needs to be recreated for 384 dim.
    from qdrant_client.models import VectorParams, Distance
    try:
        await qdrant.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
    except Exception as e:
        logger.warning(f"Failed to recreate Qdrant collection (ignoring if it exists): {e}")
        
    texts = merged["content"].tolist()
    case_ids = merged["case_id"].tolist()
    districts = merged["district"].tolist()
    
    chunk_size = 64
    vectors_imported = 0
    
    for i in range(0, len(texts), chunk_size):
        chunk_texts = texts[i:i+chunk_size]
        chunk_ids = case_ids[i:i+chunk_size]
        chunk_districts = districts[i:i+chunk_size]
        
        # Generate embeddings locally!
        embeddings = model.encode(chunk_texts, show_progress_bar=False)
        
        points = []
        for j, emb in enumerate(embeddings):
            from qdrant_client.models import PointStruct
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=emb.tolist(),
                    payload={
                        "case_id": chunk_ids[j],
                        "district": chunk_districts[j],
                        "content": chunk_texts[j]
                    }
                )
            )
        
        await qdrant.upsert(
            collection_name=collection_name,
            points=points
        )
        vectors_imported += len(points)
        print(f"  ... embedded and uploaded {vectors_imported}/{len(texts)} vectors", end="\r")
        
    print_success(f"Imported {vectors_imported} vectors to Qdrant")
    return vectors_imported
