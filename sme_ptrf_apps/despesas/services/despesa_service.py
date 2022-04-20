from django.db.models import Count, Max


def ordena_despesas_por_imposto(qs):
    qs = qs.annotate(c=Count('despesas_impostos'), c2=Count('despesa_geradora'),
                     c3=Max('data_transacao')).order_by('-c', '-c2', '-c3')
    despesas_ordenadas = []
    for despesa in qs:
        despesa_geradora_do_imposto = despesa.despesa_geradora_do_imposto.first()
        despesas_impostos = despesa.despesas_impostos.all()

        if not despesa_geradora_do_imposto:
            despesas_ordenadas.append(despesa)

        if despesas_impostos:
            for despesa_imposto in despesas_impostos:
                despesas_ordenadas.append(despesa_imposto)

    return despesas_ordenadas
