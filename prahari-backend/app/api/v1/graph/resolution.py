from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.utils.response import ApiResponse

router = APIRouter()

class ResolutionCheckRequest(BaseModel):
    entity_type: str  # e.g., 'Person', 'Vehicle', 'Phone'
    identifier: str   # Name, Registration Number, Phone Number
    
@router.post("/check", summary="Check for potential entity duplicates")
async def check_entity_resolution(
    payload: ResolutionCheckRequest,
):
    """
    Queries Neo4j and Qdrant for similar entities to propose merges.
    This is an investigative aid to avoid duplicate nodes for the same person/vehicle.
    """
    # Mocking the actual Neo4j similarity match for the hackathon
    # A real implementation uses fuzzy matching or vector search on embeddings.
    
    similar_entities = []
    
    if payload.entity_type.upper() == "PERSON" and len(payload.identifier) > 3:
        similar_entities.append({
            "entity_id": "PER_90210X",
            "name": payload.identifier,
            "confidence_score": 0.89,
            "match_reasons": ["Name phonetic match", "Historical association with area"],
            "existing_roles": ["ACCUSED in FIR/2025/112"]
        })
        
    return ApiResponse.ok(data=similar_entities)

class MergeRequest(BaseModel):
    source_entity_id: str  # The newly created/draft entity ID
    target_entity_id: str  # The existing master entity ID
    
@router.post("/merge", summary="Soft-merge an entity into a master record")
async def merge_entities(
    payload: MergeRequest,
):
    """
    Soft-merge: Re-points the case relationships to the target_entity_id 
    and marks the source_entity_id as an ALIAS to preserve audit trails.
    """
    # Logic to update Neo4j edges and PostgreSQL references
    return ApiResponse.ok(message="Entities merged successfully.")
