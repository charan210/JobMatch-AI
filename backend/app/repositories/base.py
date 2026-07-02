from __future__ import annotations

from typing import Any, Generic, Optional, TypeVar

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.exceptions import DatabaseError
from app.repositories.filters import FilterParams
from app.repositories.pagination import PaginatedResult, PageParams
from app.repositories.sort import SortOrder, SortParams

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    async def create(
        self,
        db: AsyncSession,
        obj_in: dict[str, Any] | ModelType,
    ) -> ModelType:
        try:
            if isinstance(obj_in, dict):
                obj = self.model(**obj_in)
            else:
                obj = obj_in
            db.add(obj)
            await db.flush()
            return obj
        except sa.exc.IntegrityError as exc:
            raise DatabaseError(str(exc)) from exc
        except sa.exc.SQLAlchemyError as exc:
            raise DatabaseError(str(exc)) from exc

    async def get_by_id(
        self,
        db: AsyncSession,
        model_id: Any,
        options: list[Any] | None = None,
    ) -> ModelType | None:
        try:
            query = select(self.model).where(getattr(self.model, "id") == model_id)
            if options:
                for option in options:
                    query = query.options(option)
            result = await db.execute(query)
            return result.scalars().first()
        except sa.exc.SQLAlchemyError as exc:
            raise DatabaseError(str(exc)) from exc

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: dict[str, Any] | ModelType,
    ) -> ModelType:
        try:
            values = obj_in if isinstance(obj_in, dict) else vars(obj_in)
            for field, value in values.items():
                if hasattr(db_obj, field) and field != "id":
                    setattr(db_obj, field, value)
            await db.flush()
            return db_obj
        except sa.exc.SQLAlchemyError as exc:
            raise DatabaseError(str(exc)) from exc

    async def delete(self, db: AsyncSession, db_obj: ModelType) -> ModelType:
        try:
            await db.delete(db_obj)
            await db.flush()
            return db_obj
        except sa.exc.SQLAlchemyError as exc:
            raise DatabaseError(str(exc)) from exc

    async def exists(
        self,
        db: AsyncSession,
        filters: dict[str, Any] | FilterParams | None = None,
    ) -> bool:
        try:
            clause = self._build_filter_clause(filters)
            if clause is None:
                clause = sa.true()
            query = select(sa.exists().where(clause))
            result = await db.execute(query)
            return bool(result.scalar())
        except sa.exc.SQLAlchemyError as exc:
            raise DatabaseError(str(exc)) from exc

    async def count(
        self,
        db: AsyncSession,
        filters: dict[str, Any] | FilterParams | None = None,
    ) -> int:
        try:
            query = select(sa.func.count()).select_from(self.model)
            clause = self._build_filter_clause(filters)
            if clause is not None:
                query = query.where(clause)
            result = await db.execute(query)
            return int(result.scalar_one())
        except sa.exc.SQLAlchemyError as exc:
            raise DatabaseError(str(exc)) from exc

    async def list(
        self,
        db: AsyncSession,
        filters: dict[str, Any] | FilterParams | None = None,
        sort_params: SortParams | None = None,
        page_params: PageParams | None = None,
        options: list[Any] | None = None,
    ) -> PaginatedResult[ModelType]:
        try:
            query = select(self.model)
            clause = self._build_filter_clause(filters)
            if clause is not None:
                query = query.where(clause)

            if options:
                for option in options:
                    query = query.options(option)

            if sort_params and sort_params.sort_by:
                sort_column = getattr(self.model, sort_params.sort_by)
                query = query.order_by(
                    sort_column.desc()
                    if sort_params.sort_order == SortOrder.DESC
                    else sort_column.asc()
                )

            page = page_params.page if page_params else 1
            page_size = page_params.page_size if page_params else 25
            offset = (page - 1) * page_size
            result = await db.execute(query.limit(page_size).offset(offset))
            items = list(result.scalars().all())
            total = await self.count(db, filters=filters)
            return PaginatedResult.create(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
            )
        except sa.exc.SQLAlchemyError as exc:
            raise DatabaseError(str(exc)) from exc

    def _build_filter_clause(
        self,
        filters: dict[str, Any] | FilterParams | None = None,
    ) -> Optional[Any]:
        if filters is None:
            return None

        params = filters.to_dict() if isinstance(filters, FilterParams) else filters
        clauses: list[Any] = []
        for field, value in params.items():
            if value is None:
                clauses.append(getattr(self.model, field).is_(None))
            else:
                clauses.append(getattr(self.model, field) == value)
        if not clauses:
            return None
        return sa.and_(*clauses)
