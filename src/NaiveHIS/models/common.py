from datetime import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    updated_at: datetime = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['created_at', 'updated_at']


class CloseableMixin(TimeStampedMixin):
    closed_at: datetime = models.DateTimeField(default=None, blank=True, null=True)

    @property
    def is_open(self) -> bool:
        return self.completed_at is None

    @property
    def is_closed(self) -> bool:
        return not self.is_open

    def close(self):
        self.closed_at = datetime.now()

    def reopen(self):
        self.closed_at = None

    class Meta(TimeStampedMixin.Meta):
        abstract = True
        ordering = ['closed_at', 'created_at', 'updated_at']


def _AddressMixinFactory(address_required: bool):
    params = {} if address_required else {'blank': True, 'null': True}

    class AddressMixin(models.Model):
        city = models.CharField(max_length=64, **params)
        street = models.CharField(max_length=64, **params)
        street_number = models.IntegerField(**params)
        zip_code = models.CharField(max_length=5, **params)

        has_address: bool = address_required

        @property
        def address(self):
            """Adressfeld ohne Namen. Format ist grob an DIN 5008 angelehnt. """
            return f'{self.street} {self.street_number}\n{self.zip_code} {self.city}'

        class Meta(TimeStampedMixin.Meta):
            verbose_name = _('Adresse')
            verbose_name_plural = _('Adressen')
            abstract = True

    return AddressMixin


AddressOptionalMixin = _AddressMixinFactory(address_required=False)
AddressRequiredMixin = _AddressMixinFactory(address_required=True)


class PersonMixin(models.Model):
    gender = models.CharField(max_length=1, verbose_name=_('Geschlecht'),
                              choices=(('m', _('männlich')),
                                       ('w', _('weiblich')),
                                       ('d', _('divers'))),
                              default='d')

    title = models.CharField(max_length=32, verbose_name=_('Titel'),
                             blank=True, null=True)
    first_name = models.CharField(max_length=32, verbose_name=_('Vorname'))
    last_name = models.CharField(max_length=32, verbose_name=_('Nachname'))

    # address = models.ForeignKey(to=Address, on_delete=models.DO_NOTHING, verbose_name=_('Adresse'),
    #                             blank=True, null=True)

    @property
    def salutation(self) -> str:
        return 'Hallo' if self.gender == 'd' else f'Sehr geehrte{"r" if self.gender == "m" else ""}'

    @property
    def postal_address(self) -> str | None:
        if hasattr(self, 'address'):
            return f'{self.person}\n{self.address}'

    @property
    def person(self) -> str:
        return f'{self.title + " " if self.title else ""}{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('Personen')
        abstract = True
