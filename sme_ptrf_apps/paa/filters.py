from django_filters import rest_framework as filters
from sme_ptrf_apps.core.choices.tipos_unidade import TIPOS_CHOICE


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class UUIDInFilter(filters.BaseInFilter, filters.UUIDFilter):
    pass


class PaaDreFilter(filters.FilterSet):
    periodo = UUIDInFilter()
    unidade = UUIDInFilter()
    tipo_unidade = filters.ChoiceFilter(
        choices=TIPOS_CHOICE,
        error_messages={
            'invalid_choice': 'Tipo de unidade inválido.'
        }
    )
    status = CharInFilter()

    class Meta:
        fields = ['periodo', 'unidade', 'tipo_unidade', 'status']
