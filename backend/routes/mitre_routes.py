"""
SentinelAI-X MITRE ATT&CK Matrix Routes
=========================================
Endpoints for browsing and searching the MITRE knowledgebase.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from models.mitre import MitreTechnique
from schemas.common import ApiResponse
from schemas.mitre import MitreTechniqueSchema
from services.mitre_service import get_all_mitre_techniques, get_mitre_technique, seed_mitre_database

router = APIRouter(prefix="/mitre", tags=["MITRE ATT&CK Framework"])


@router.get("", response_model=ApiResponse[List[MitreTechniqueSchema]])
def list_mitre_techniques(db: Session = Depends(get_db)):
    """Retrieve all cataloged MITRE ATT&CK enterprise techniques."""
    seed_mitre_database(db)
    techs = db.query(MitreTechnique).all()
    return ApiResponse(
        data=[MitreTechniqueSchema.model_validate(t) for t in techs],
        message="MITRE techniques retrieved"
    )


@router.get("/{technique_id}", response_model=ApiResponse[MitreTechniqueSchema])
def get_technique_detail(technique_id: str, db: Session = Depends(get_db)):
    """Look up a specific MITRE technique by ID (e.g. 'T1110')."""
    tech = db.query(MitreTechnique).filter(MitreTechnique.technique_id == technique_id.upper()).first()
    if not tech:
        local_data = get_mitre_technique(technique_id)
        if not local_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"MITRE Technique {technique_id} not found")
        return ApiResponse(data=MitreTechniqueSchema(**local_data), message="Technique found")

    return ApiResponse(data=MitreTechniqueSchema.model_validate(tech), message="Technique found")
