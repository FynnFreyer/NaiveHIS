from datetime import datetime
from django.db import models


class TimeStamped(models.Model):
    created_at: datetime = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at: datetime = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
        ordering = ['created_at', 'updated_at']


class Closeable(TimeStamped):
    closed_at: datetime = models.DateTimeField(default=None, null=True)

    @property
    def is_open(self) -> bool:
        return self.completed_at is None

    @property
    def is_closed(self) -> bool:
        return not self.is_open

    class Meta(TimeStamped.Meta):
        abstract = True
        ordering = ['closed_at', 'created_at', 'updated_at']
