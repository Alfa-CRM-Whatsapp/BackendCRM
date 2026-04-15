import django_filters
from core.crm.models import WhatsappMessage

class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass

class WhatsappMessageFilter(django_filters.FilterSet):
    category = CharInFilter(
        field_name='category__name',
        lookup_expr='in'
    )

    class Meta:
        model = WhatsappMessage
        fields = ['category']