from django.db.models import Model
from django.contrib.auth import get_user_model
from typing import TypeVar, Type, Union, Optional
from .schemas import (
    BaseSchema, TimeStampedSchema, TrackedSchema,
    UniversalState, LockType
)
from dj_core_utils.db.models import (
    TimeStampedModel,
    UserTrackedModel,
    OperationLog
)

T = TypeVar('T', bound=Model)
User = get_user_model()


def model_to_schema(
    django_instance: Model,
    schema_class: Type[Union[BaseSchema, TimeStampedSchema, TrackedSchema]]
) -> Union[BaseSchema, TimeStampedSchema, TrackedSchema]:
    model_dict = {}

    for field in django_instance._meta.fields:
        field_name = field.name
        field_value = getattr(django_instance, field_name)

        # Relaciones ForeignKey
        if field.is_relation:
            if isinstance(field_value, User):
                model_dict[f'{field_name}_id'] = field_value.id
            elif hasattr(field_value, 'id'):
                model_dict[f'{field_name}_id'] = field_value.id
            continue

        model_dict[field_name] = field_value

    # TimeStampedModel
    if isinstance(django_instance, TimeStampedModel):
        if not issubclass(schema_class, (TimeStampedSchema, TrackedSchema)):
            raise ValueError(
                'TimeStampedModel models require '
                'TimeStampedSchema or TrackedSchema'
            )

    # UserTrackedModel incluye universal_state,
    # lock_type, object_locked, created_by, updated_by
    if isinstance(django_instance, UserTrackedModel):
        if not issubclass(schema_class, TrackedSchema):
            raise ValueError('UserTrackedModel models require TrackedSchema')

        model_dict.update({
            'created_by': django_instance.created_by_id,
            'updated_by': django_instance.updated_by_id,
            'universal_state': UniversalState(django_instance.universal_state),
            'lock_type': LockType(django_instance.lock_type),
            'object_locked': django_instance.object_locked
        })

    # Caso especial: OperationLog
    if isinstance(django_instance, OperationLog):
        model_dict['user_id'] = (
            django_instance.user_id if django_instance.user else None
        )
        model_dict['changes'] = django_instance.changes

    return schema_class(**model_dict)


def schema_to_model(
    schema: Union[BaseSchema, TimeStampedSchema, TrackedSchema],
    django_model: Type[T],
    exclude_fields: Optional[set] = None
) -> T:
    if exclude_fields is None:
        exclude_fields = set()

    create_data = schema.model_dump(exclude_unset=True)

    # Campos base que no deben sobreescribirse
    base_excludes = {'id', 'created_at', 'updated_at'} | exclude_fields

    if isinstance(schema, TrackedSchema):
        base_excludes.update(
            {
                'created_by',
                'updated_by',
                'universal_state',
                'lock_type',
                'object_locked'
            })

        if hasattr(django_model, 'universal_state'):
            create_data['universal_state'] = schema.universal_state.value

        if hasattr(django_model, 'lock_type'):
            create_data['lock_type'] = schema.lock_type.value

        if hasattr(django_model, 'object_locked'):
            create_data['object_locked'] = schema.object_locked

    # Eliminar campos excluidos
    for field in base_excludes:
        create_data.pop(field, None)

    # Relaciones especiales
    if hasattr(django_model, 'created_by'):
        if 'created_by_id' in create_data:
            create_data['created_by'] = create_data.pop('created_by_id')

    if hasattr(django_model, 'updated_by'):
        if 'updated_by_id' in create_data:
            create_data['updated_by'] = create_data.pop('updated_by_id')

    return django_model(**create_data)
