from typing import Any
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.db.models import JSONField, ForeignKey, ManyToManyField, Model

from dj_core_utils.middleware.context import get_current_user
from dj_core_utils.db.models import OperationLog, OperationType


class AuditHandler:
    EXCLUDED_MODELS = ['OperationLog']

    @classmethod
    def model_to_dict_safe(cls, instance: Model) -> dict[str, Any]:
        """Serializes a model securely for auditing."""
        data = {}
        for field in instance._meta.get_fields():
            if isinstance(field, ManyToManyField):
                continue  # Los M2M se manejan aparte
            try:
                value = getattr(instance, field.name, None)

                if isinstance(field, ForeignKey):
                    data[field.name] = str(value) if value else None
                elif isinstance(field, JSONField):
                    data[field.name] = (
                        value if isinstance(value, dict) else dict(value or {})
                    )
                else:
                    data[field.name] = value
            except Exception:
                data[field.name] = None
        return data

    @classmethod
    def get_changes(
            cls,
            before: dict[str, Any],
            after: dict[str, Any]) -> dict[str, Any]:
        """Detects which fields changed between 'before' and 'after'."""
        all_keys = set(before.keys()) | set(after.keys())
        return {
            key: {'before': before.get(key), 'after': after.get(key)}
            for key in all_keys
            if before.get(key) != after.get(key)
        }


@receiver(post_save)
def handle_save(sender, instance, created, **kwargs):
    if sender.__name__ in AuditHandler.EXCLUDED_MODELS:
        return

    user = get_current_user()

    audit_data: dict[str, Any] = {
        'user': user,
        'model_changed': sender.__name__,
        'id_instance': instance.pk,
        'operation_type': (
            OperationType.CREATE if created else OperationType.UPDATE
        ),
    }

    if created:
        audit_data['changes'] = {
            'new': AuditHandler.model_to_dict_safe(instance)}
    else:
        try:
            before_instance = sender.objects.get(pk=instance.pk)
            before = AuditHandler.model_to_dict_safe(before_instance)
            after = AuditHandler.model_to_dict_safe(instance)
            audit_data['changes'] = AuditHandler.get_changes(before, after)
        except sender.DoesNotExist:
            audit_data['changes'] = {}

    OperationLog.objects.create(**audit_data)


@receiver(post_delete)
def handle_delete(sender, instance, **kwargs):
    if sender.__name__ in AuditHandler.EXCLUDED_MODELS:
        return

    OperationLog.objects.create(
        user=get_current_user(),
        model_changed=sender.__name__,
        id_instance=instance.pk,
        operation_type=OperationType.DELETE,
        changes=None,
    )


@receiver(m2m_changed)
def handle_m2m_change(
    action,
    instance,
    reverse,
    model,
    pk_set,
    sender,
    **kwargs
):
    model_name = instance.__class__.__name__
    if model_name in AuditHandler.EXCLUDED_MODELS:
        return

    if action not in ['post_add', 'post_remove', 'post_clear']:
        return

    user = get_current_user()

    OperationLog.objects.create(
        user=user,
        model_changed=model_name,
        id_instance=instance.pk,
        operation_type=f'm2m_{action}',
        changes={
            'related_model': model.__name__,
            'field': sender.__name__.lower(),
            'pks': list(pk_set) if pk_set else []
        }
    )
