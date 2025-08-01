# /api/runs routes
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...datamodel import Message, Run, RunStatus, Session
from ..deps import (
    get_current_domain_id,
    get_current_tenant_id,
    get_db,
)

router = APIRouter()


class CreateRunRequest(BaseModel):
    session_id: int
    user_id: str


@router.post("/")
async def create_run(
    request: CreateRunRequest,
    tenant_id: int = Depends(get_current_tenant_id),
    domain_id: int = Depends(get_current_domain_id),
    db=Depends(get_db),
) -> Dict:
    """Create a new run with initial state"""
    session_response = db.get(
        Session,
        filters={
            "id": request.session_id,
            "user_id": request.user_id,
            "tenant_id": tenant_id,
            "domain_id": domain_id,
        },
        return_json=False,
    )
    if not session_response.status or not session_response.data:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Create run with default state
        run = db.upsert(
            Run(
                session_id=request.session_id,
                status=RunStatus.CREATED,
                user_id=request.user_id,
                task={},  # Will be set when run starts
                team_result={},
                tenant_id=tenant_id,
                domain_id=domain_id,
            ),
            return_json=False,
        )
        return {"status": run.status, "data": {"run_id": run.data.id}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# We might want to add these endpoints:


@router.get("/{run_id}")
async def get_run(
    run_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    domain_id: int = Depends(get_current_domain_id),
    db=Depends(get_db),
) -> Dict:
    """Get run details including task and result"""
    run = db.get(
        Run,
        filters={"id": run_id, "tenant_id": tenant_id, "domain_id": domain_id},
        return_json=False,
    )
    if not run.status or not run.data:
        raise HTTPException(status_code=404, detail="Run not found")

    return {"status": True, "data": run.data[0]}


@router.get("/{run_id}/messages")
async def get_run_messages(
    run_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    domain_id: int = Depends(get_current_domain_id),
    db=Depends(get_db),
) -> Dict:
    """Get all messages for a run"""
    messages = db.get(
        Message,
        filters={"run_id": run_id, "tenant_id": tenant_id, "domain_id": domain_id},
        order="created_at asc",
        return_json=False,
    )

    return {"status": True, "data": messages.data}
