import django_filters
from django.db.models import Q

from core.crm.models import WhatsappMessage


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class WhatsappMessageByNumberFilter(django_filters.FilterSet):
    category = CharInFilter(
        field_name='category__name',
        lookup_expr='in'
    )
    text = django_filters.CharFilter(method='filter_text')
    year = django_filters.NumberFilter(field_name='created_at', lookup_expr='year')
    month = django_filters.NumberFilter(field_name='created_at', lookup_expr='month')
    day = django_filters.NumberFilter(field_name='created_at', lookup_expr='day')

    def filter_text(self, queryset, name, value):
        term = (value or '').strip()

        if len(term) >= 2 and term[0] == term[-1] and term[0] in {'"', "'"}:
            term = term[1:-1].strip()

        if not term:
            return queryset

        return queryset.filter(
            Q(messages__text__body__icontains=term) |
            Q(messages__body__icontains=term)
        )

    class Meta:
        model = WhatsappMessage
        fields = ['category', 'text', 'year', 'month', 'day']