from django.utils.translation import gettext_lazy as _

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
# ADDRESS_LIST_FILTER = ADDRESS_LIST_DISPLAY
ADDRESS_SEARCH_FIELDS = ADDRESS_LIST_DISPLAY
ADDRESS_ORDERING = tuple(reversed(ADDRESS_LIST_DISPLAY))


PERSON_FIELDSETS = (
    (_('Persönliche Informationen'), {
        'classes': ('wide',),
        'fields': (
            'gender',
            'title',
            ('first_name', 'last_name'),
        )
    }),
)

PERSON_LIST_DISPLAY = ('title', 'first_name', 'last_name')
# PERSON_LIST_FILTER = PERSON_LIST_DISPLAY
PERSON_SEARCH_FIELDS = PERSON_LIST_DISPLAY
PERSON_ORDERING = tuple(reversed(PERSON_LIST_DISPLAY))

