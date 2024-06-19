import logging

from django.db.models import Count

from sme_ptrf_apps.core.models import Associacao, Periodo

logger = logging.getLogger(__name__)


def ordena_despesas_por_imposto(qs, lista_argumentos_ordenacao=None):

    if lista_argumentos_ordenacao is None:
        lista_argumentos_ordenacao = []

    qs = qs.annotate(c=Count('despesas_impostos'), c2=Count('despesa_geradora')).order_by('-c', '-c2', *lista_argumentos_ordenacao)
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


def migra_despesas_periodos_anteriores():
    """
    Percorre todas as despesas com data de transação anterior ao período inicial de sua associação e atualiza os campos
    despesa_anterior_ao_uso_do_sistema e despesa_anterior_ao_uso_do_sistema_pc_concluida.

    O período inicial de uma associação é o período do seu saldo de implantação
    """
    logger.info('Obtendo lista de todas as associações ativas..')
    associacoes = Associacao.ativas.all()

    for associacao in associacoes:
        if associacao.periodo_inicial is None:
            logger.info(f'Associação {associacao} não possui período inicial.')
            continue

        logger.info(f'Migrando despesas anteriores a {associacao.periodo_inicial.referencia} da associação {associacao}..')

        despesas_anteriores = associacao.despesas.filter(data_transacao__lte=associacao.periodo_inicial.data_fim_realizacao_despesas)

        for despesa in despesas_anteriores:
            logger.info(f'Migrando despesa {despesa}..')
            despesa.despesa_anterior_ao_uso_do_sistema = True
            despesa.despesa_anterior_ao_uso_do_sistema_pc_concluida = associacao.prestacoes_de_conta_da_associacao.exists()
            despesa.save()
