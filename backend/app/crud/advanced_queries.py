"""
Advanced query features for CRUD operations.
"""
from typing import Any, Dict, List, Optional, Union, Type, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc, text
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import Select
from datetime import datetime, date
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Type variables
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class SortDirection(str, Enum):
    """Sort direction enumeration."""
    ASC = "asc"
    DESC = "desc"


class FilterOperator(str, Enum):
    """Filter operator enumeration."""
    EQ = "eq"  # equals
    NE = "ne"  # not equals
    GT = "gt"  # greater than
    GTE = "gte"  # greater than or equal
    LT = "lt"  # less than
    LTE = "lte"  # less than or equal
    LIKE = "like"  # like (case sensitive)
    ILIKE = "ilike"  # like (case insensitive)
    IN = "in"  # in list
    NOT_IN = "not_in"  # not in list
    IS_NULL = "is_null"  # is null
    IS_NOT_NULL = "is_not_null"  # is not null
    BETWEEN = "between"  # between two values
    CONTAINS = "contains"  # contains substring
    STARTS_WITH = "starts_with"  # starts with
    ENDS_WITH = "ends_with"  # ends with


class FilterCondition:
    """Represents a filter condition."""

    def __init__(
        self,
        field: str,
        operator: FilterOperator,
        value: Any = None,
        values: List[Any] = None
    ):
        self.field = field
        self.operator = operator
        self.value = value
        self.values = values or []

    def __repr__(self):
        return f"FilterCondition(field='{self.field}', operator='{self.operator}', value={self.value})"


class SortCondition:
    """Represents a sort condition."""

    def __init__(self, field: str, direction: SortDirection = SortDirection.ASC):
        self.field = field
        self.direction = direction

    def __repr__(self):
        return f"SortCondition(field='{self.field}', direction='{self.direction}')"


class PaginationParams:
    """Represents pagination parameters."""

    def __init__(self, page: int = 1, page_size: int = 100, max_page_size: int = 1000):
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), max_page_size)
        self.offset = (self.page - 1) * self.page_size
        self.limit = self.page_size

    def __repr__(self):
        return f"PaginationParams(page={self.page}, page_size={self.page_size})"


class SearchParams:
    """Represents search parameters."""

    def __init__(
        self,
        query: str,
        fields: List[str] = None,
        case_sensitive: bool = False,
        exact_match: bool = False
    ):
        self.query = query.strip()
        self.fields = fields or []
        self.case_sensitive = case_sensitive
        self.exact_match = exact_match

    def __repr__(self):
        return f"SearchParams(query='{self.query}', fields={self.fields})"


class AdvancedQueryBuilder:
    """Builder for advanced queries with filtering, sorting, pagination, and search."""

    def __init__(self, model: Type[ModelType]):
        self.model = model
        self._filters: List[FilterCondition] = []
        self._sorts: List[SortCondition] = []
        self._pagination: Optional[PaginationParams] = None
        self._search: Optional[SearchParams] = None
        self._relationships: List[str] = []
        self._distinct: bool = False

    def add_filter(self, condition: FilterCondition) -> "AdvancedQueryBuilder":
        """Add a filter condition."""
        self._filters.append(condition)
        return self

    def add_filters(self, conditions: List[FilterCondition]) -> "AdvancedQueryBuilder":
        """Add multiple filter conditions."""
        self._filters.extend(conditions)
        return self

    def add_sort(self, condition: SortCondition) -> "AdvancedQueryBuilder":
        """Add a sort condition."""
        self._sorts.append(condition)
        return self

    def add_sorts(self, conditions: List[SortCondition]) -> "AdvancedQueryBuilder":
        """Add multiple sort conditions."""
        self._sorts.extend(conditions)
        return self

    def set_pagination(self, pagination: PaginationParams) -> "AdvancedQueryBuilder":
        """Set pagination parameters."""
        self._pagination = pagination
        return self

    def set_search(self, search: SearchParams) -> "AdvancedQueryBuilder":
        """Set search parameters."""
        self._search = search
        return self

    def add_relationship(self, relationship: str) -> "AdvancedQueryBuilder":
        """Add a relationship to load."""
        self._relationships.append(relationship)
        return self

    def add_relationships(self, relationships: List[str]) -> "AdvancedQueryBuilder":
        """Add multiple relationships to load."""
        self._relationships.extend(relationships)
        return self

    def set_distinct(self, distinct: bool = True) -> "AdvancedQueryBuilder":
        """Set distinct flag."""
        self._distinct = distinct
        return self

    def build_query(self) -> Select:
        """Build the SQLAlchemy query."""
        # Start with base query
        query = select(self.model)

        # Add relationships
        for relationship in self._relationships:
            query = query.options(selectinload(getattr(self.model, relationship)))

        # Apply filters
        if self._filters:
            filter_conditions = []
            for filter_cond in self._filters:
                condition = self._build_filter_condition(filter_cond)
                if condition is not None:
                    filter_conditions.append(condition)

            if filter_conditions:
                query = query.where(and_(*filter_conditions))

        # Apply search
        if self._search and self._search.query:
            search_conditions = self._build_search_conditions()
            if search_conditions:
                query = query.where(or_(*search_conditions))

        # Apply sorting
        if self._sorts:
            order_conditions = []
            for sort_cond in self._sorts:
                field = getattr(self.model, sort_cond.field)
                if sort_cond.direction == SortDirection.DESC:
                    order_conditions.append(desc(field))
                else:
                    order_conditions.append(asc(field))
            query = query.order_by(*order_conditions)

        # Apply pagination
        if self._pagination:
            query = query.offset(self._pagination.offset).limit(self._pagination.limit)

        # Apply distinct
        if self._distinct:
            query = query.distinct()

        return query

    def _build_filter_condition(self, filter_cond: FilterCondition):
        """Build a filter condition for SQLAlchemy."""
        try:
            field = getattr(self.model, filter_cond.field)

            if filter_cond.operator == FilterOperator.EQ:
                return field == filter_cond.value
            elif filter_cond.operator == FilterOperator.NE:
                return field != filter_cond.value
            elif filter_cond.operator == FilterOperator.GT:
                return field > filter_cond.value
            elif filter_cond.operator == FilterOperator.GTE:
                return field >= filter_cond.value
            elif filter_cond.operator == FilterOperator.LT:
                return field < filter_cond.value
            elif filter_cond.operator == FilterOperator.LTE:
                return field <= filter_cond.value
            elif filter_cond.operator == FilterOperator.LIKE:
                return field.like(filter_cond.value)
            elif filter_cond.operator == FilterOperator.ILIKE:
                return field.ilike(filter_cond.value)
            elif filter_cond.operator == FilterOperator.IN:
                return field.in_(filter_cond.values)
            elif filter_cond.operator == FilterOperator.NOT_IN:
                return ~field.in_(filter_cond.values)
            elif filter_cond.operator == FilterOperator.IS_NULL:
                return field.is_(None)
            elif filter_cond.operator == FilterOperator.IS_NOT_NULL:
                return field.is_not(None)
            elif filter_cond.operator == FilterOperator.BETWEEN:
                if len(filter_cond.values) == 2:
                    return field.between(filter_cond.values[0], filter_cond.values[1])
            elif filter_cond.operator == FilterOperator.CONTAINS:
                return field.contains(filter_cond.value)
            elif filter_cond.operator == FilterOperator.STARTS_WITH:
                return field.startswith(filter_cond.value)
            elif filter_cond.operator == FilterOperator.ENDS_WITH:
                return field.endswith(filter_cond.value)

            return None
        except AttributeError:
            logger.warning(f"Field '{filter_cond.field}' not found in model {self.model.__name__}")
            return None
        except Exception as e:
            logger.error(f"Error building filter condition {filter_cond}: {str(e)}")
            return None

    def _build_search_conditions(self):
        """Build search conditions."""
        if not self._search or not self._search.query:
            return []

        conditions = []
        search_value = self._search.query

        # If exact match, use equals
        if self._search.exact_match:
            for field_name in self._search.fields:
                try:
                    field = getattr(self.model, field_name)
                    conditions.append(field == search_value)
                except AttributeError:
                    logger.warning(f"Field '{field_name}' not found in model {self.model.__name__}")
        else:
            # Use like/ilike for partial matches
            for field_name in self._search.fields:
                try:
                    field = getattr(self.model, field_name)
                    if self._search.case_sensitive:
                        conditions.append(field.like(f"%{search_value}%"))
                    else:
                        conditions.append(field.ilike(f"%{search_value}%"))
                except AttributeError:
                    logger.warning(f"Field '{field_name}' not found in model {self.model.__name__}")

        return conditions


class AdvancedCRUDMixin:
    """Mixin class that adds advanced query capabilities to CRUD classes."""

    async def get_with_filters(
        self,
        db: AsyncSession,
        *,
        filters: List[FilterCondition] = None,
        sorts: List[SortCondition] = None,
        pagination: PaginationParams = None,
        search: SearchParams = None,
        relationships: List[str] = None,
        distinct: bool = False
    ) -> List[ModelType]:
        """
        Get entities with advanced filtering, sorting, pagination, and search.

        Args:
            db: Database session
            filters: List of filter conditions
            sorts: List of sort conditions
            pagination: Pagination parameters
            search: Search parameters
            relationships: List of relationships to load
            distinct: Whether to use distinct

        Returns:
            List of entities matching the criteria
        """
        try:
            builder = AdvancedQueryBuilder(self.model)

            if filters:
                builder.add_filters(filters)
            if sorts:
                builder.add_sorts(sorts)
            if pagination:
                builder.set_pagination(pagination)
            if search:
                builder.set_search(search)
            if relationships:
                builder.add_relationships(relationships)
            if distinct:
                builder.set_distinct(True)

            query = builder.build_query()
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error in get_with_filters: {str(e)}")
            raise

    async def count_with_filters(
        self,
        db: AsyncSession,
        *,
        filters: List[FilterCondition] = None,
        search: SearchParams = None,
        distinct: bool = False
    ) -> int:
        """
        Count entities with advanced filtering and search.

        Args:
            db: Database session
            filters: List of filter conditions
            search: Search parameters
            distinct: Whether to use distinct

        Returns:
            Number of entities matching the criteria
        """
        try:
            builder = AdvancedQueryBuilder(self.model)

            if filters:
                builder.add_filters(filters)
            if search:
                builder.set_search(search)
            if distinct:
                builder.set_distinct(True)

            # Build count query
            query = builder.build_query()
            count_query = select(func.count()).select_from(query.subquery())

            result = await db.execute(count_query)
            return result.scalar()
        except Exception as e:
            logger.error(f"Error in count_with_filters: {str(e)}")
            raise

    async def search_text(
        self,
        db: AsyncSession,
        *,
        query: str,
        fields: List[str],
        case_sensitive: bool = False,
        exact_match: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Search entities by text in specified fields.

        Args:
            db: Database session
            query: Search query
            fields: List of fields to search in
            case_sensitive: Whether search is case sensitive
            exact_match: Whether to use exact match
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching entities
        """
        search_params = SearchParams(
            query=query,
            fields=fields,
            case_sensitive=case_sensitive,
            exact_match=exact_match
        )

        pagination = PaginationParams(page=1, page_size=limit)
        pagination.offset = skip

        return await self.get_with_filters(
            db,
            search=search_params,
            pagination=pagination
        )

    async def get_by_date_range(
        self,
        db: AsyncSession,
        *,
        date_field: str,
        start_date: Union[datetime, date],
        end_date: Union[datetime, date],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get entities within a date range.

        Args:
            db: Database session
            date_field: Name of the date field
            start_date: Start date
            end_date: End date
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of entities within the date range
        """
        filters = [
            FilterCondition(
                field=date_field,
                operator=FilterOperator.BETWEEN,
                values=[start_date, end_date]
            )
        ]

        pagination = PaginationParams(page=1, page_size=limit)
        pagination.offset = skip

        return await self.get_with_filters(
            db,
            filters=filters,
            pagination=pagination
        )

    async def get_recent(
        self,
        db: AsyncSession,
        *,
        date_field: str = "created_at",
        days: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get recently created/updated entities.

        Args:
            db: Database session
            date_field: Name of the date field
            days: Number of days to look back
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of recent entities
        """
        from datetime import timedelta

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        filters = [
            FilterCondition(
                field=date_field,
                operator=FilterOperator.BETWEEN,
                values=[start_date, end_date]
            )
        ]

        sorts = [
            SortCondition(field=date_field, direction=SortDirection.DESC)
        ]

        pagination = PaginationParams(page=1, page_size=limit)
        pagination.offset = skip

        return await self.get_with_filters(
            db,
            filters=filters,
            sorts=sorts,
            pagination=pagination
        )

    async def get_active_count(self, db: AsyncSession) -> int:
        """Get count of active entities."""
        filters = [
            FilterCondition(
                field="is_active",
                operator=FilterOperator.EQ,
                value=True
            )
        ]
        return await self.count_with_filters(db, filters=filters)

    async def get_inactive_count(self, db: AsyncSession) -> int:
        """Get count of inactive entities."""
        filters = [
            FilterCondition(
                field="is_active",
                operator=FilterOperator.EQ,
                value=False
            )
        ]
        return await self.count_with_filters(db, filters=filters)


# Utility functions for common query patterns
def create_text_search_filter(field: str, query: str, case_sensitive: bool = False) -> FilterCondition:
    """Create a text search filter condition."""
    operator = FilterOperator.LIKE if case_sensitive else FilterOperator.ILIKE
    return FilterCondition(field=field, operator=operator, value=f"%{query}%")


def create_date_range_filter(field: str, start_date: Union[datetime, date], end_date: Union[datetime, date]) -> FilterCondition:
    """Create a date range filter condition."""
    return FilterCondition(
        field=field,
        operator=FilterOperator.BETWEEN,
        values=[start_date, end_date]
    )


def create_in_filter(field: str, values: List[Any]) -> FilterCondition:
    """Create an 'in' filter condition."""
    return FilterCondition(field=field, operator=FilterOperator.IN, values=values)


def create_equals_filter(field: str, value: Any) -> FilterCondition:
    """Create an equals filter condition."""
    return FilterCondition(field=field, operator=FilterOperator.EQ, value=value)


def create_null_filter(field: str, is_null: bool = True) -> FilterCondition:
    """Create a null/not null filter condition."""
    operator = FilterOperator.IS_NULL if is_null else FilterOperator.IS_NOT_NULL
    return FilterCondition(field=field, operator=operator)


def create_sort(field: str, direction: SortDirection = SortDirection.ASC) -> SortCondition:
    """Create a sort condition."""
    return SortCondition(field=field, direction=direction)


def create_pagination(page: int = 1, page_size: int = 100) -> PaginationParams:
    """Create pagination parameters."""
    return PaginationParams(page=page, page_size=page_size)
