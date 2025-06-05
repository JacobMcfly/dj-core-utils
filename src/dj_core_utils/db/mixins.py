from django.db import models


class LockType(models.TextChoices):
    FULL_ACCESS = 'full', 'Full Access'
    READ_ONLY = 'read', 'Read Only'
    NO_ACCESS = 'none', 'No Access'


class UniversalState(models.TextChoices):
    CREATED = 'created', 'Created'
    FROZEN = 'frozen', 'Frozen'
    ACTIVE = 'active', 'Active'
    EFFECTIVE = 'effective', 'Effective'
    TERMINATED = 'terminated', 'Terminated'


class UniversalStateMixin(models.Model):
    lock_type = models.CharField(
        max_length=10,
        choices=LockType.choices,
        default=LockType.FULL_ACCESS
    )
    object_locked = models.BooleanField(default=False)
    universal_state = models.CharField(
        max_length=15,
        choices=UniversalState.choices,
        default=UniversalState.ACTIVE,
        db_index=True
    )

    class Meta:
        app_label = 'dj_core_utils'
        abstract = True

    def activate(self):
        self.universal_state = UniversalState.ACTIVE
        self.save()

    def deactivate(self):
        self.universal_state = UniversalState.FROZEN
        self.save()

    def terminate(self):
        self.universal_state = UniversalState.TERMINATED
        self.save()

    def is_active(self):
        return self.universal_state == UniversalState.ACTIVE

    def is_inactive(self):
        return self.universal_state == UniversalState.FROZEN

    def is_terminated(self):
        return self.universal_state == UniversalState.TERMINATED
