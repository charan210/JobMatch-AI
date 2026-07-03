from __future__ import annotations


from app.models.async_job import AsyncJob
from app.repositories.base import BaseRepository


class AsyncJobRepository(BaseRepository[AsyncJob]):
    """
    Repository for managing AsyncJob entities in the database.
    Inherits standard CRUD operations from BaseRepository.
    """
    pass
