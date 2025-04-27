import os
import uuid
from pathlib import Path
from fastapi import UploadFile, File, Request, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, RedirectResponse
from open_webui.models.files import FileForm, Files, FileModelResponse
from open_webui.utils.auth import get_verified_user
from supabase import create_client, Client
from fastapi import APIRouter
from open_webui.constants import ERROR_MESSAGES
from open_webui.storage.provider import Storage
import logging

log = logging.getLogger(__name__)

# Инициализация Supabase клиента
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

router = APIRouter()

@router.post("/", response_model=FileModelResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    user=Depends(get_verified_user),
    file_metadata: dict = {},
    process: bool = Query(True),
):
    try:
        unsanitized_filename = file.filename
        filename = os.path.basename(unsanitized_filename)

        id = str(uuid.uuid4())
        name = filename
        supabase_path = f"{id}_{filename}"

        contents = await file.read()

        res = supabase.storage.from_("uploads").upload(
            path=supabase_path,
            file=contents,
            options={"upsert": True}
        )

        if not res:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка загрузки файла в Supabase Storage"
            )

        public_url = f"{SUPABASE_URL.replace('https://', 'https://storage.')}/object/public/uploads/{supabase_path}"

        file_item = Files.insert_new_file(
            user.id,
            FileForm(
                **{
                    "id": id,
                    "filename": name,
                    "path": public_url,
                    "meta": {
                        "name": name,
                        "content_type": file.content_type,
                        "size": len(contents),
                        "data": file_metadata,
                    },
                }
            ),
        )

        if file_item:
            return file_item
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка записи файла в базу"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка загрузки файла: {str(e)}"
        )


@router.get("/{id}/content")
async def get_file_content_by_id(
    id: str, user=Depends(get_verified_user), attachment: bool = Query(False)
):
    file = Files.get_file_by_id(id)

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if (
        file.user_id == user.id
        or user.role == "admin"
    ):
        try:
            file_path = file.path

            if file_path.startswith("https://storage."):
                return RedirectResponse(url=file_path)

            file_path = Storage.get_file(file_path)
            file_path = Path(file_path)

            if file_path.is_file():
                return FileResponse(file_path)
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=ERROR_MESSAGES.NOT_FOUND,
                )
        except Exception as e:
            log.exception(e)
            log.error("Ошибка при получении файла")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.DEFAULT("Ошибка при получении файла"),
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )
