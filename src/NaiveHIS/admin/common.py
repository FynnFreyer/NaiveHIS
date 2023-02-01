from datetime import datetime
from typing import Callable

from django.http import HttpRequest
from django.contrib.admin import display, ModelAdmin
from django.utils.translation import gettext_lazy as _
from ..models.common import CloseableMixin, PersonMixin

TIMESTAMPED_LIST_DISPLAY = (
    'created_at',
    'updated_at',
)


@display(description=_('Abgeschlossen'))
def _is_closed(obj: CloseableMixin):
    return obj.is_closed


CLOSEABLE_FIELDSETS = (
    (_('Metadaten'), {
        'classes': ('collapse', 'wide',),
        'fields': (
            ('closed_at',),
        )
    }),
)

CLOSEABLE_LIST_DISPLAY = (
    _is_closed,
    *TIMESTAMPED_LIST_DISPLAY,
    'closed_at',
)

ADDRESS_FIELDSETS = (
    (_('Adresse'), {
        'classes': ('wide',),
        'fields': (
            ('street', 'street_number'),
            ('zip_code', 'city')
        )
    }),
)

ADDRESS_LIST_DISPLAY = ('street', 'street_number', 'zip_code', 'city')
ADDRESS_SEARCH_FIELDS = ADDRESS_LIST_DISPLAY
ADDRESS_ORDERING = tuple(reversed(ADDRESS_LIST_DISPLAY))

PERSON_FIELDSETS = (
    (_('Persönliche Informationen'), {
        'classes': ('wide',),
        'fields': (
            ('gender', 'date_of_birth'),
            'title',
            ('first_name', 'last_name'),
        )
    }),
)


@display(description=_('Name'))
def _person(obj: PersonMixin):
    return obj.person


@display(description=_('Alter'))
def _age(obj: PersonMixin) -> int | str:
    now = datetime.now()
    dob = obj.date_of_birth

    if dob is not None:
        dy, dm, dd = (
            now.year - dob.year,
            now.month - dob.month,
            now.day - dob.day
        )

        age = dy
        if dm > 0 or dm == 0 and dd > 0:
            age -= 1
    else:
        age = _('-')

    return age


PERSON_LIST_DISPLAY = (_person, _age)
PERSON_SEARCH_FIELDS = ('title', 'first_name', 'last_name', _person)
PERSON_ORDERING = ('last_name', 'first_name', 'title')


class BlankableAdminMixin(ModelAdmin):
    blanking_conditions: tuple[tuple[Callable[[HttpRequest, object], bool], list[str]]]

    def get_form(self, request, obj=None, **kwargs):
        # TODO not sure what happens if someone still sends the data in the request
        form = super().get_form(request, obj, **kwargs)

        for predicate, fields in self.blanking_conditions:
            if predicate(request, obj):
                for field in fields:
                    if field in form.base_fields:
                        form.base_fields[field].disabled = True
                    else:
                        # TODO log info
                        ...

        return form
