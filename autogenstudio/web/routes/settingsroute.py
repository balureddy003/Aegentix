# api/routes/settings.py
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException

from ...datamodel import Settings, SettingsConfig
from ..deps import (
    get_current_domain_id,
    get_current_tenant_id,
    get_db,
)

router = APIRouter()


@router.get("/")
async def get_settings(
    user_id: str,
    tenant_id: int = Depends(get_current_tenant_id),
    domain_id: int = Depends(get_current_domain_id),
    db=Depends(get_db),
) -> Dict:
    try:
        response = db.get(
            Settings,
            filters={
                "user_id": user_id,
                "tenant_id": tenant_id,
                "domain_id": domain_id,
            },
        )
        if not response.status or not response.data:
            # create a default settings
            config = SettingsConfig()
            default_settings = Settings(
                user_id=user_id,
                config=config.model_dump(),
                tenant_id=tenant_id,
                domain_id=domain_id,
            )
            db.upsert(default_settings)
            response = db.get(
                Settings,
                filters={
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "domain_id": domain_id,
                },
            )
        # print(response.data[0])
        return {"status": True, "data": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/")
async def update_settings(
    settings: Settings,
    tenant_id: int = Depends(get_current_tenant_id),
    domain_id: int = Depends(get_current_domain_id),
    db=Depends(get_db),
) -> Dict:
    settings.tenant_id = tenant_id
    settings.domain_id = domain_id
    response = db.upsert(settings)
    if not response.status:
        raise HTTPException(status_code=400, detail=response.message)
    return {"status": True, "data": response.data}
