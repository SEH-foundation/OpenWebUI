import os
import uuid
from fastapi import UploadFile, File, Request, Depends, HTTPException, status, Query
from open_webui.models.files import FileForm, Files, FileModelResponse
from open_webui.utils.auth import get_verified_user
from supabase import create_client, Client

# Инициализация Supabase клиента
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

from fastapi import APIRouter

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

        # Генерация уникального id для файла
        id = str(uuid.uuid4())
        name = filename
        supabase_path = f"{id}_{filename}"

        # Читаем содержимое файла
        contents = await file.read()

        # Загружаем файл в Supabase Storage в бакет "uploads"
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

        # Формируем публичный URL к файлу
        public_url = f"{SUPABASE_URL.replace('https://', 'https://storage.')}/object/public/uploads/{supabase_path}"

        # Сохраняем информацию о файле в базе
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
