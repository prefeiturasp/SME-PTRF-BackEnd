from django.db.models import Sum


def get_total_receita_sem_filtro(queryset):
    total_receitas_sem_filtro = queryset.aggregate(Sum('valor'))['valor__sum']
    return total_receitas_sem_filtro


def get_total_receita_com_filtro(queryset, filter_fields, request):
    filtered_queryset = queryset

    for field in filter_fields:
        filter_value = request.query_params.get(field)

        if filter_value:
            filtered_queryset = filtered_queryset.filter(**{field: filter_value})

    total_receitas_com_filtro = filtered_queryset.aggregate(Sum('valor'))['valor__sum']

    return total_receitas_com_filtro
