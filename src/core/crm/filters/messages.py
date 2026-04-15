import django_filters
from core.crm.models import WhatsappMessage

class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass

class WhatsappMessageFilter(django_filters.FilterSet):
    category = CharInFilter(
        field_name='category__name',
        lookup_expr='in'
    )
    year = django_filters.NumberFilter(field_name='created_at', lookup_expr='year')
    month = django_filters.NumberFilter(field_name='created_at', lookup_expr='month')
    day = django_filters.NumberFilter(field_name='created_at', lookup_expr='day')

    class Meta:
        model = WhatsappMessage
        fields = ['category', 'year', 'month', 'day']