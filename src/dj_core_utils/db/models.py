from django.db import models
from django_currentuser.db.models import CurrentUserField
from django.contrib.contenttypes.fields import (
    GenericForeignKey
)
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from .mixins import UniversalStateMixin


class TimeStampedModel(models.Model):
    """Modelo base con campos de timestamp"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'dj_core_utils'
        abstract = True
        ordering = ['-created_at']


class UserTrackedModel(TimeStampedModel, UniversalStateMixin):
    """Modelo con auditoría de usuario"""
    created_by = CurrentUserField(
        on_delete=models.PROTECT,
        related_name='%(class)s_created',
        editable=False
    )
    updated_by = CurrentUserField(
        on_delete=models.PROTECT,
        related_name='%(class)s_updated',
        on_update=True,
        editable=False
    )

    class Meta:
        app_label = 'dj_core_utils'
        abstract = True


class CoreBaseModel(UserTrackedModel):
    pass

    class Meta:
        app_label = 'dj_core_utils'
        abstract = True


class ClasificationFile(CoreBaseModel):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        app_label = 'dj_core_utils'
        verbose_name = 'Clasificación de archivo'
        verbose_name_plural = 'Clasificaciones de archivos'


class File(CoreBaseModel):
    file = models.FileField('Archivo', upload_to='archivos/%Y/%m/%d/')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    clasificacion = models.ForeignKey(
        ClasificationFile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Clasificación de archivo"
    )

    class Meta:
        app_label = 'dj_core_utils'
        verbose_name = 'archivo'
        verbose_name_plural = 'archivos'

    def __str__(self):
        return self.file.name if self.file else 'Archivo sin nombre'


class Comments(CoreBaseModel):
    comment = models.TextField('Comentario')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        app_label = 'dj_core_utils'
        verbose_name = 'comentario'
        verbose_name_plural = 'comentarios'

    def __str__(self):
        text = self.comment
        if len(text) > 100:
            text = text[:100] + '...'
        return text


class OperationType(models.TextChoices):
    CREATE = 'create', 'Create'
    UPDATE = 'update', 'Update'
    DELETE = 'delete', 'Delete'


class OperationLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    model_changed = models.CharField(max_length=100)
    id_instance = models.PositiveIntegerField()
    # 'create', 'update', 'delete'
    operation_type = models.CharField(
        max_length=10,
        choices=OperationType.choices
    )
    date = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(null=True, blank=True)

    class Meta:
        app_label = 'dj_core_utils'
        verbose_name = 'log'
        verbose_name_plural = 'logs'

    def __str__(self):
        return (
            f'{self.operation_type.upper()} - '
            f'{self.model_changed} ({self.id_instance})'
        )
