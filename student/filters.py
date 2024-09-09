import django_filters
from .models import PersonalInfo


class SnippetFiler(django_filters.FilterSet):
    class Meta:
        model = PersonalInfo
        fields = ('name', 'phone_no', 'status')