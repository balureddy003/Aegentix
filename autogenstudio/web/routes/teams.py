# api/routes/teams.py
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException

from ...datamodel import Team
from ...gallery.builder import create_default_gallery
from ..deps import (
    get_current_domain_id,
    get_current_tenant_id,
    get_db,
)

router = APIRouter()


@router.get("/")
async def list_teams(
    user_id: str,
    tenant_id: int = Depends(get_current_tenant_id),
    domain_id: int = Depends(get_current_domain_id),
    db=Depends(get_db),
) -> Dict:
    """List all teams for a user"""
    response = db.get(
        Team,
        filters={"user_id": user_id, "tenant_id": tenant_id, "domain_id": domain_id},
    )

    if not response.data or len(response.data) == 0:
        default_gallery = create_default_gallery()
        default_team = Team(
            user_id=user_id,
            component=default_gallery.components.teams[0].model_dump(),
            tenant_id=tenant_id,
            domain_id=domain_id,
        )

        db.upsert(default_team)
        response = db.get(
            Team,
            filters={
                "user_id": user_id,
                "tenant_id": tenant_id,
                "domain_id": domain_id,
            },
        )

    return {"status": True, "data": response.data}


@router.get("/{team_id}")
async def get_team(
    team_id: int,
    user_id: str,
    tenant_id: int = Depends(get_current_tenant_id),
    domain_id: int = Depends(get_current_domain_id),
    db=Depends(get_db),
) -> Dict:
    """Get a specific team"""
    response = db.get(
        Team,
        filters={
            "id": team_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "domain_id": domain_id,
        },
    )
    if not response.status or not response.data:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"status": True, "data": response.data[0]}


@router.post("/")
async def create_team(
    team: Team,
    tenant_id: int = Depends(get_current_tenant_id),
    domain_id: int = Depends(get_current_domain_id),
    db=Depends(get_db),
) -> Dict:
    """Create a new team"""
    team.tenant_id = tenant_id
    team.domain_id = domain_id
    response = db.upsert(team)
    if not response.status:
        raise HTTPException(status_code=400, detail=response.message)
    return {"status": True, "data": response.data}


@router.delete("/{team_id}")
async def delete_team(
    team_id: int,
    user_id: str,
    tenant_id: int = Depends(get_current_tenant_id),
    domain_id: int = Depends(get_current_domain_id),
    db=Depends(get_db),
) -> Dict:
    """Delete a team"""
    db.delete(
        filters={
            "id": team_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "domain_id": domain_id,
        },
        model_class=Team,
    )
    return {"status": True, "message": "Team deleted successfully"}
