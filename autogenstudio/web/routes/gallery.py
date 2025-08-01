# api/routes/gallery.py
from fastapi import APIRouter, Depends, HTTPException

from ...database import DatabaseManager
from ...datamodel import Gallery, Response
from ...gallery.builder import create_default_gallery
from ..deps import (
    get_current_domain_id,
    get_current_tenant_id,
    get_db,
)

router = APIRouter()


@router.put("/{gallery_id}")
async def update_gallery_entry(
    gallery_id: int,
    gallery_data: Gallery,
    user_id: str,
    tenant_id: int = Depends(get_current_tenant_id),
    domain_id: int = Depends(get_current_domain_id),
    db: DatabaseManager = Depends(get_db),
) -> Response:
    # Check ownership first
    result = db.get(
        Gallery,
        filters={"id": gallery_id, "tenant_id": tenant_id, "domain_id": domain_id},
    )
    if not result.status or not result.data:
        raise HTTPException(status_code=404, detail="Gallery entry not found")

    if result.data[0].user_id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this gallery entry"
        )

    # Update if authorized
    gallery_data.id = gallery_id  # Ensure ID matches
    gallery_data.user_id = user_id  # Ensure user_id matches
    gallery_data.tenant_id = tenant_id
    gallery_data.domain_id = domain_id
    return db.upsert(gallery_data)


@router.post("/")
async def create_gallery_entry(
    gallery_data: Gallery,
    tenant_id: int = Depends(get_current_tenant_id),
    domain_id: int = Depends(get_current_domain_id),
    db: DatabaseManager = Depends(get_db),
) -> Response:
    gallery_data.tenant_id = tenant_id
    gallery_data.domain_id = domain_id
    response = db.upsert(gallery_data)
    if not response.status:
        raise HTTPException(status_code=400, detail=response.message)
    return response


@router.get("/")
async def list_gallery_entries(
    user_id: str,
    tenant_id: int = Depends(get_current_tenant_id),
    domain_id: int = Depends(get_current_domain_id),
    db: DatabaseManager = Depends(get_db),
) -> Response:
    try:
        result = db.get(
            Gallery,
            filters={
                "user_id": user_id,
                "tenant_id": tenant_id,
                "domain_id": domain_id,
            },
        )
        if not result.data or len(result.data) == 0:
            # create a default gallery entry
            gallery_config = create_default_gallery()
            default_gallery = Gallery(
                user_id=user_id,
                config=gallery_config.model_dump(),
                tenant_id=tenant_id,
                domain_id=domain_id,
            )
            db.upsert(default_gallery)
            result = db.get(
                Gallery,
                filters={
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "domain_id": domain_id,
                },
            )
        return result
    except Exception as e:
        return Response(
            status=False, data=[], message=f"Error retrieving gallery entries: {str(e)}"
        )


@router.get("/{gallery_id}")
async def get_gallery_entry(
    gallery_id: int,
    user_id: str,
    tenant_id: int = Depends(get_current_tenant_id),
    domain_id: int = Depends(get_current_domain_id),
    db: DatabaseManager = Depends(get_db),
) -> Response:
    result = db.get(
        Gallery,
        filters={
            "id": gallery_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "domain_id": domain_id,
        },
    )
    if not result.status or not result.data:
        raise HTTPException(status_code=404, detail="Gallery entry not found")

    return Response(status=result.status, data=result.data[0], message=result.message)


@router.delete("/{gallery_id}")
async def delete_gallery_entry(
    gallery_id: int,
    user_id: str,
    tenant_id: int = Depends(get_current_tenant_id),
    domain_id: int = Depends(get_current_domain_id),
    db: DatabaseManager = Depends(get_db),
) -> Response:
    # Check ownership first
    result = db.get(
        Gallery,
        filters={
            "id": gallery_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "domain_id": domain_id,
        },
    )

    if not result.status or not result.data:
        raise HTTPException(status_code=404, detail="Gallery entry not found")
    response = db.delete(
        Gallery,
        filters={"id": gallery_id, "tenant_id": tenant_id, "domain_id": domain_id},
    )
    # Delete if authorized
    return response
