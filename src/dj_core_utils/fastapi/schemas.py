from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import Generic, TypeVar, Optional, Any, Dict, List

T = TypeVar('T')


class UniversalState(str, Enum):
    CREATED = 'created'
    FROZEN = 'frozen'
    ACTIVE = 'active'
    EFFECTIVE = 'effective'
    TERMINATED = 'terminated'


class LockType(str, Enum):
    FULL_ACCESS = 'full'
    READ_ONLY = 'read'
    NO_ACCESS = 'none'


class BaseSchema(BaseModel):
    """Base schema with common fields"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimeStampedSchema(BaseSchema):
    """Schema for models with timestamps"""
    model_config = ConfigDict(from_attributes=True)


class TrackedSchema(TimeStampedSchema):
    """Schema for models with audit and state tracking"""
    created_by: Optional[int]
    updated_by: Optional[int]
    universal_state: UniversalState
    lock_type: LockType
    object_locked: bool


class OperationLogSchema(TrackedSchema):
    user_id: Optional[int] = Field(
        None, description="ID del usuario que realizó la acción"
    )
    model_changed: str = Field(..., description="Nombre del modelo afectado")
    id_instance: int = Field(..., description="ID de la instancia afectada")
    operation_type: str = Field(..., description="Tipo de operación")
    changes: Optional[Dict[str, Any]] = Field(
        None, description="Cambios realizados"
    )


class UserSchema(TrackedSchema):
    email: str = Field(..., description="Email del usuario")
    is_active: bool = Field(
        ..., description="Indica si el usuario está activo"
    )
    is_staff: bool = Field(..., description="Indica si el usuario es staff")


class PaginatedResponse(BaseModel, Generic[T]):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[T]
