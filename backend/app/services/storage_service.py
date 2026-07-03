from __future__ import annotations

import shutil
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class StorageBackend(ABC):
    @abstractmethod
    async def save_file(self, filename: str, file_obj: BinaryIO) -> str:
        """
        Saves a file and returns the storage URL or path.
        """
        pass

    @abstractmethod
    async def delete_file(self, file_url: str) -> None:
        """
        Deletes a file by its URL or path.
        """
        pass

    @abstractmethod
    async def get_file(self, file_url: str) -> BinaryIO:
        """
        Retrieves a file by its URL or path.
        """
        pass


class LocalStorageBackend(StorageBackend):
    def __init__(self, base_dir: str = settings.LOCAL_STORAGE_DIR) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info("local_storage_backend_initialized", base_dir=str(self.base_dir))

    async def save_file(self, filename: str, file_obj: BinaryIO) -> str:
        # Generate a unique file name to avoid collisions
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = self.base_dir / unique_name
        
        # Write file to disk
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file_obj, f)
            
        logger.debug("file_saved_locally", path=str(file_path))
        return str(file_path)

    async def delete_file(self, file_url: str) -> None:
        file_path = Path(file_url)
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            logger.debug("file_deleted_locally", path=str(file_path))

    async def get_file(self, file_url: str) -> BinaryIO:
        file_path = Path(file_url)
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_url}")
        return open(file_path, "rb")


class S3StorageBackend(StorageBackend):
    async def save_file(self, filename: str, file_obj: BinaryIO) -> str:
        raise NotImplementedError("S3 storage is not yet implemented")

    async def delete_file(self, file_url: str) -> None:
        raise NotImplementedError("S3 storage is not yet implemented")

    async def get_file(self, file_url: str) -> BinaryIO:
        raise NotImplementedError("S3 storage is not yet implemented")


def get_storage_service() -> StorageBackend:
    backend_type = settings.STORAGE_BACKEND
    if backend_type == "s3":
        return S3StorageBackend()
    return LocalStorageBackend()
