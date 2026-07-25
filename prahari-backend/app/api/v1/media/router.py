"""Media upload API — Catalyst Stratus pre-signed URL generation."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.catalyst.client import get_catalyst_stratus
from app.core.permissions import require_permissions, Permission
from app.utils.response import ApiResponse

router = APIRouter()

class UploadRequest(BaseModel):
    file_name: str
    content_type: str

@router.post("/upload-url", summary="Get pre-signed upload URL")
async def get_upload_url(
    body: UploadRequest,
    current_user=Depends(require_permissions(Permission.MEDIA_UPLOAD)),
):
    stratus = get_catalyst_stratus()
    result = await stratus.get_upload_url(body.file_name, body.content_type)
    return ApiResponse.ok(data=result, message="Pre-signed URL generated. Upload directly from browser.")

@router.get("/download/{file_id}", summary="Get signed download URL")
async def get_download_url(
    file_id: str,
    current_user=Depends(require_permissions(Permission.MEDIA_READ)),
):
    stratus = get_catalyst_stratus()
    url = await stratus.get_download_url(file_id)
    return ApiResponse.ok(data={"download_url": url})
