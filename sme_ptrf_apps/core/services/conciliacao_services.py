from django.db.models import Sum, Max

from sme_ptrf_apps.core.models import Associacao, FechamentoPeriodo
from sme_ptrf_apps.despesas.models import RateioDespesa, Despesa
from sme_ptrf_apps.receitas.models import Receita

from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_COMPLETO


def receitas_conciliadas_por_conta_e_acao_na_conciliacao(conta_associacao, acao_associacao, periodo):
    dataset = periodo.receitas_conciliadas_no_periodo.filter(conta_associacao=conta_associacao)

    if acao_associacao:
        dataset = dataset.filter(acao_associacao=acao_associacao)

    return dataset.all()


def info_conciliacao_pendente(periodo, conta_associacao):
    acoes_associacao = Associacao.acoes_da_associacao(associacao_uuid=conta_associacao.associacao.uuid)
    result = []
    for acao_associacao in acoes_associacao:
        info_acao = info_conciliacao_acao_associacao_no_periodo(acao_associacao=acao_associacao,
                                                                periodo=periodo,
                                                                conta_associacao=conta_associacao)

        info = {
            'acao_associacao_uuid': f'{acao_associacao.uuid}',
            'acao_associacao_nome': acao_associacao.acao.nome,

            'receitas_no_periodo': info_acao['receitas_no_periodo'],

            'despesas_no_periodo': info_acao['despesas_no_periodo'],

            'despesas_nao_conciliadas': info_acao['despesas_nao_conciliadas'],

            'receitas_nao_conciliadas': info_acao['receitas_nao_conciliadas'],

        }
        result.append(info)

    return result


def info_conciliacao_acao_associacao_no_periodo(acao_associacao, periodo, conta_associacao):
    def resultado_vazio():
        return {
            'receitas_no_periodo': 0,
            'despesas_no_periodo': 0,
            'receitas_nao_conciliadas': 0,
            'despesas_nao_conciliadas': 0,
        }

    def sumariza_conciliacao_receitas_do_periodo_e_acao(periodo, conta_associacao, acao_associacao, info):

        receitas_conciliadas = receitas_conciliadas_por_conta_e_acao_na_conciliacao(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo)

        for receita_conciliada in receitas_conciliadas:
            info['receitas_no_periodo'] += receita_conciliada.valor

        receitas_nao_conciliadas = receitas_nao_conciliadas_por_conta_e_acao_no_periodo(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo)

        for receita_nao_conciliada in receitas_nao_conciliadas:
            info['receitas_no_periodo'] += receita_nao_conciliada.valor
            info['receitas_nao_conciliadas'] += receita_nao_conciliada.valor

        return info

    def sumariza_conciliacao_despesas_do_periodo_e_acao(periodo, conta_associacao, acao_associacao, info, ):
        rateios_conciliados = despesas_conciliadas_por_conta_e_acao_na_conciliacao(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo)

        for rateio_conciliado in rateios_conciliados:
            info['despesas_no_periodo'] += rateio_conciliado.valor_rateio

        rateios_nao_conciliados = despesas_nao_conciliadas_por_conta_e_acao_no_periodo(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo)

        for rateio_nao_conciliado in rateios_nao_conciliados:
            info['despesas_no_periodo'] += rateio_nao_conciliado.valor_rateio
            info['despesas_nao_conciliadas'] += rateio_nao_conciliado.valor_rateio

        return info

    info = resultado_vazio()

    info = sumariza_conciliacao_receitas_do_periodo_e_acao(periodo=periodo,
                                                           conta_associacao=conta_associacao,
                                                           acao_associacao=acao_associacao,
                                                           info=info)

    info = sumariza_conciliacao_despesas_do_periodo_e_acao(periodo=periodo,
                                                           conta_associacao=conta_associacao,
                                                           acao_associacao=acao_associacao, info=info)

    return info


def despesas_nao_conciliadas_por_conta_e_acao_no_periodo(conta_associacao, acao_associacao, periodo):
    dataset = RateioDespesa.completos.filter(conta_associacao=conta_associacao)

    if acao_associacao:
        dataset = dataset.filter(acao_associacao=acao_associacao)

    dataset = dataset.filter(conferido=False)

    # No caso de despesas não conciliadas todas devem ser exibidas até a data limite do período
    if periodo.data_fim_realizacao_despesas:
        dataset = dataset.filter(despesa__data_documento__lte=periodo.data_fim_realizacao_despesas)

    return dataset.all()


def despesas_conciliadas_por_conta_e_acao_na_conciliacao(conta_associacao, acao_associacao, periodo):
    dataset = periodo.despesas_conciliadas_no_periodo.filter(despesa__status=STATUS_COMPLETO).filter(conta_associacao=conta_associacao)

    if acao_associacao:
        dataset = dataset.filter(acao_associacao=acao_associacao)

    return dataset.all()


def receitas_nao_conciliadas_por_conta_e_acao_no_periodo(conta_associacao, acao_associacao, periodo):
    dataset = Receita.objects.filter(conta_associacao=conta_associacao)

    if acao_associacao:
        dataset = dataset.filter(acao_associacao=acao_associacao)

    dataset = dataset.filter(conferido=False)

    # No caso de despesas não conciliadas todas devem ser exibidas até a data limite do período
    if periodo.data_fim_realizacao_despesas:
        dataset = dataset.filter(data__lte=periodo.data_fim_realizacao_despesas)

    return dataset.all()


def receitas_conciliadas_por_conta_e_acao_no_periodo(conta_associacao, acao_associacao, periodo):
    dataset = Receita.objects.filter(conta_associacao=conta_associacao)

    if acao_associacao:
        dataset = dataset.filter(acao_associacao=acao_associacao)

    dataset = dataset.filter(conferido=True)

    if periodo.data_fim_realizacao_despesas:
        dataset = dataset.filter(
            data__range=(periodo.data_inicio_realizacao_despesas, periodo.data_fim_realizacao_despesas))
    else:
        dataset = dataset.filter(data__gte=periodo.data_inicio_realizacao_despesas)

    return dataset.all()


def info_resumo_conciliacao(periodo, conta_associacao):
    info_conta = info_conciliacao_conta_associacao_no_periodo(periodo=periodo,
                                                              conta_associacao=conta_associacao)

    saldo_anterior = saldo_anterior_total_conta_associacao_no_periodo(conta_associacao=conta_associacao,
                                                                      periodo=periodo)

    saldo_posterior_total = (
        saldo_anterior +
        info_conta['receitas_no_periodo'] -
        info_conta['despesas_no_periodo']
    )

    saldo_posterior_conciliado = (
        saldo_anterior +
        info_conta['receitas_conciliadas'] -
        info_conta['despesas_conciliadas']
    )

    info = {
        'saldo_anterior': saldo_anterior,

        'receitas_total': info_conta['receitas_no_periodo'],
        'receitas_conciliadas': info_conta['receitas_conciliadas'],
        'receitas_nao_conciliadas': info_conta['receitas_nao_conciliadas'],

        'despesas_total': info_conta['despesas_no_periodo'],
        'despesas_conciliadas': info_conta['despesas_conciliadas'],
        'despesas_nao_conciliadas': info_conta['despesas_nao_conciliadas'],

        'saldo_posterior_total': saldo_posterior_total,
        'saldo_posterior_conciliado': saldo_posterior_conciliado,
        'saldo_posterior_nao_conciliado': saldo_posterior_total - saldo_posterior_conciliado,
    }

    return info


def info_conciliacao_conta_associacao_no_periodo(periodo, conta_associacao):
    def resultado_vazio():
        return {
            'receitas_no_periodo': 0,
            'despesas_no_periodo': 0,
            'receitas_nao_conciliadas': 0,
            'despesas_nao_conciliadas': 0,
            'receitas_conciliadas': 0,
            'despesas_conciliadas': 0,
        }

    def sumariza_conciliacao_receitas_do_periodo_e_conta(periodo, conta_associacao, info):

        receitas_conciliadas = receitas_conciliadas_por_conta_na_conciliacao(
            conta_associacao=conta_associacao,
            periodo=periodo)

        for receita_conciliada in receitas_conciliadas:
            info['receitas_no_periodo'] += receita_conciliada.valor
            info['receitas_conciliadas'] += receita_conciliada.valor

        receitas_nao_conciliadas = receitas_nao_conciliadas_por_conta_no_periodo(
            conta_associacao=conta_associacao,
            periodo=periodo)

        for receita_nao_conciliada in receitas_nao_conciliadas:
            info['receitas_no_periodo'] += receita_nao_conciliada.valor
            info['receitas_nao_conciliadas'] += receita_nao_conciliada.valor

        return info

    def sumariza_conciliacao_despesas_do_periodo_e_conta(periodo, conta_associacao, info, ):
        rateios_conciliados = despesas_conciliadas_por_conta_na_conciliacao(
            conta_associacao=conta_associacao,
            periodo=periodo)

        for rateio_conciliado in rateios_conciliados:
            info['despesas_no_periodo'] += rateio_conciliado.valor_rateio
            info['despesas_conciliadas'] += rateio_conciliado.valor_rateio

        rateios_nao_conciliados = despesas_nao_conciliadas_por_conta_no_periodo(
            conta_associacao=conta_associacao,
            periodo=periodo)

        for rateio_nao_conciliado in rateios_nao_conciliados:
            info['despesas_no_periodo'] += rateio_nao_conciliado.valor_rateio
            info['despesas_nao_conciliadas'] += rateio_nao_conciliado.valor_rateio

        return info

    info = resultado_vazio()

    info = sumariza_conciliacao_receitas_do_periodo_e_conta(periodo=periodo,
                                                            conta_associacao=conta_associacao,
                                                            info=info)

    info = sumariza_conciliacao_despesas_do_periodo_e_conta(periodo=periodo,
                                                            conta_associacao=conta_associacao,
                                                            info=info)

    return info


def receitas_conciliadas_por_conta_na_conciliacao(conta_associacao, periodo):
    dataset = periodo.receitas_conciliadas_no_periodo.filter(conta_associacao=conta_associacao)

    return dataset.all()


def receitas_nao_conciliadas_por_conta_no_periodo(conta_associacao, periodo):
    dataset = Receita.objects.filter(conta_associacao=conta_associacao).filter(
        conferido=False)

    # No caso de despesas não conciliadas todas devem ser exibidas até a data limite do período
    if periodo.data_fim_realizacao_despesas:
        dataset = dataset.filter(data__lte=periodo.data_fim_realizacao_despesas)

    return dataset.all()


def despesas_conciliadas_por_conta_na_conciliacao(conta_associacao, periodo):
    dataset = periodo.despesas_conciliadas_no_periodo.filter(despesa__status=STATUS_COMPLETO)
    dataset = dataset.filter(conta_associacao=conta_associacao)

    return dataset.all()


def despesas_nao_conciliadas_por_conta_no_periodo(conta_associacao, periodo):
    dataset = RateioDespesa.completos.filter(conta_associacao=conta_associacao).filter(conferido=False)

    # No caso de despesas não conciliadas todas devem ser exibidas até a data limite do período
    if periodo.data_fim_realizacao_despesas:
        dataset = dataset.filter(despesa__data_documento__lte=periodo.data_fim_realizacao_despesas)

    return dataset.all()


def saldo_anterior_total_conta_associacao_no_periodo(conta_associacao, periodo):
    def saldo_anterior_periodo_fechado_sumarizado(fechamentos_periodo):
        saldo_anterior_total = 0

        for fechamento_periodo in fechamentos_periodo:
            saldo_anterior_total += fechamento_periodo.saldo_anterior
        return saldo_anterior_total

    def saldo_posterior_periodo_fechado_sumarizado(fechamentos_periodo):
        saldo_posterior_total = 0
        for fechamento_periodo in fechamentos_periodo:
            saldo_posterior_total += fechamento_periodo.saldo_reprogramado
        return saldo_posterior_total

    def saldo_periodo_aberto_sumarizado(periodo, conta_associacao):

        if not periodo or not periodo.periodo_anterior:
            return 0.00

        fechamentos_periodo_anterior = FechamentoPeriodo.fechamentos_da_conta_no_periodo(
            conta_associacao=conta_associacao,
            periodo=periodo.periodo_anterior)

        saldo = saldo_posterior_periodo_fechado_sumarizado(fechamentos_periodo_anterior)

        return saldo

    fechamentos_periodo = FechamentoPeriodo.fechamentos_da_conta_no_periodo(conta_associacao=conta_associacao,
                                                                            periodo=periodo)
    if fechamentos_periodo:
        return saldo_anterior_periodo_fechado_sumarizado(fechamentos_periodo)
    else:
        return saldo_periodo_aberto_sumarizado(periodo, conta_associacao)


def documentos_de_despesa_nao_conciliados_por_conta_e_acao_no_periodo(conta_associacao, acao_associacao, periodo):
    rateios = despesas_nao_conciliadas_por_conta_e_acao_no_periodo(conta_associacao=conta_associacao,
                                                                   acao_associacao=acao_associacao, periodo=periodo)
    despesas_com_rateios = rateios.values_list('despesa__id', flat=True).distinct()

    dataset = Despesa.completas.filter(id__in=despesas_com_rateios)

    return dataset.all()


def documentos_de_despesa_conciliados_por_conta_e_acao_na_conciliacao(conta_associacao, acao_associacao, periodo):
    rateios = despesas_conciliadas_por_conta_e_acao_na_conciliacao(conta_associacao=conta_associacao,
                                                                   acao_associacao=acao_associacao, periodo=periodo)
    despesas_com_rateios = rateios.values_list('despesa__id', flat=True).distinct()

    dataset = Despesa.completas.filter(id__in=despesas_com_rateios)

    return dataset.all()


def transacoes_para_conciliacao(periodo, conta_associacao, conferido=False, acao_associacao=None, tipo_transacao=None):
    from sme_ptrf_apps.despesas.api.serializers.despesa_serializer import DespesaConciliacaoSerializer
    from sme_ptrf_apps.despesas.api.serializers.rateio_despesa_serializer import RateioDespesaConciliacaoSerializer
    from sme_ptrf_apps.receitas.api.serializers.receita_serializer import ReceitaConciliacaoSerializer

    receitas = []
    despesas = []

    if not tipo_transacao or tipo_transacao == "CREDITOS":
        if conferido:
            receitas = receitas_conciliadas_por_conta_e_acao_na_conciliacao(conta_associacao=conta_associacao,
                                                                            acao_associacao=acao_associacao,
                                                                            periodo=periodo)
        else:
            receitas = receitas_nao_conciliadas_por_conta_e_acao_no_periodo(conta_associacao=conta_associacao,
                                                                            acao_associacao=acao_associacao,
                                                                            periodo=periodo)
        receitas = receitas.order_by("data")

    if not tipo_transacao or tipo_transacao == "GASTOS":
        if conferido:
            despesas = documentos_de_despesa_conciliados_por_conta_e_acao_na_conciliacao(
                conta_associacao=conta_associacao,
                acao_associacao=acao_associacao,
                periodo=periodo)
        else:
            despesas = documentos_de_despesa_nao_conciliados_por_conta_e_acao_no_periodo(
                conta_associacao=conta_associacao,
                acao_associacao=acao_associacao,
                periodo=periodo)

        despesas = despesas.order_by("data_transacao")

    # Iniciar a lista de transacoes com a lista de despesas ordenada
    transacoes = []
    for despesa in despesas:

        max_notificar_dias_nao_conferido = 0
        for rateio in despesa.rateios.filter(status=STATUS_COMPLETO, conta_associacao=conta_associacao):
            if rateio.notificar_dias_nao_conferido > max_notificar_dias_nao_conferido:
                max_notificar_dias_nao_conferido = rateio.notificar_dias_nao_conferido

        transacao = {
            'periodo': f'{periodo.uuid}',
            'conta': f'{conta_associacao.uuid}',
            'data': despesa.data_transacao,
            'tipo_transacao': 'Gasto',
            'numero_documento': despesa.numero_documento,
            'descricao': despesa.nome_fornecedor,
            'valor_transacao_total': despesa.valor_total,
            'valor_transacao_na_conta':
                despesa.rateios.filter(status=STATUS_COMPLETO).filter(conta_associacao=conta_associacao).aggregate(Sum('valor_rateio'))[
                    'valor_rateio__sum'],
            'valores_por_conta': despesa.rateios.filter(status=STATUS_COMPLETO).values('conta_associacao__tipo_conta__nome').annotate(
                Sum('valor_rateio')),
            'conferido': despesa.conferido,
            'documento_mestre': DespesaConciliacaoSerializer(despesa, many=False).data,
            'rateios': RateioDespesaConciliacaoSerializer(despesa.rateios.filter(status=STATUS_COMPLETO).filter(conta_associacao=conta_associacao).order_by('id'),
                                                          many=True).data,
            'notificar_dias_nao_conferido': max_notificar_dias_nao_conferido,
        }
        transacoes.append(transacao)

    # Percorrer a lista de créditos ordenada e para cada credito, buscar na lista de transacoes a posição correta
    for receita in receitas:

        nova_transacao = {
            'periodo': f'{periodo.uuid}',
            'conta': f'{conta_associacao.uuid}',
            'data': receita.data,
            'tipo_transacao': 'Crédito',
            'numero_documento': '',
            'descricao': receita.tipo_receita.nome if receita.tipo_receita else '',
            'valor_transacao_total': receita.valor,
            'valor_transacao_na_conta': receita.valor,
            'valores_por_conta': [],
            'conferido': receita.conferido,
            'documento_mestre': ReceitaConciliacaoSerializer(receita, many=False).data,
            'rateios': [],
            'notificar_dias_nao_conferido': receita.notificar_dias_nao_conferido,
        }

        transacao_adicionada = False

        if transacoes:
            for idx, transacao in enumerate(transacoes):
                if nova_transacao['data'] <= transacao['data']:
                    transacoes.insert(idx, nova_transacao)
                    transacao_adicionada = True
                    break

        if not transacao_adicionada:
            transacoes.append(nova_transacao)

    return transacoes


def conciliar_transacao(periodo, conta_associacao, transacao, tipo_transacao):
    from sme_ptrf_apps.despesas.api.serializers.despesa_serializer import DespesaConciliacaoSerializer
    from sme_ptrf_apps.receitas.api.serializers.receita_serializer import ReceitaConciliacaoSerializer

    if tipo_transacao == "CREDITO" and isinstance(transacao, Receita):
        receita_conciliada = transacao.marcar_conferido(periodo_conciliacao=periodo)
        return ReceitaConciliacaoSerializer(receita_conciliada, many=False).data

    if tipo_transacao == "GASTO" and isinstance(transacao, Despesa):
        rateios = transacao.rateios.filter(status=STATUS_COMPLETO).filter(conta_associacao=conta_associacao).filter(conferido=False)
        for rateio in rateios:
            rateio.marcar_conferido(periodo_conciliacao=periodo)
        despesa_conciliada = Despesa.by_uuid(transacao.uuid)
        return DespesaConciliacaoSerializer(despesa_conciliada, many=False).data


def desconciliar_transacao(conta_associacao, transacao, tipo_transacao):
    from sme_ptrf_apps.despesas.api.serializers.despesa_serializer import DespesaConciliacaoSerializer
    from sme_ptrf_apps.receitas.api.serializers.receita_serializer import ReceitaConciliacaoSerializer

    if tipo_transacao == "CREDITO" and isinstance(transacao, Receita):
        receita_desconciliada = transacao.desmarcar_conferido()
        return ReceitaConciliacaoSerializer(receita_desconciliada, many=False).data

    if tipo_transacao == "GASTO" and isinstance(transacao, Despesa):
        rateios = transacao.rateios.filter(status=STATUS_COMPLETO).filter(conta_associacao=conta_associacao).filter(conferido=True)
        for rateio in rateios:
            rateio.desmarcar_conferido()
        despesa_desconciliada = Despesa.by_uuid(transacao.uuid)
        return DespesaConciliacaoSerializer(despesa_desconciliada, many=False).data


def salva_conciliacao_bancaria(texto_observacao, periodo, conta_associacao,
                               data_extrato, saldo_extrato, comprovante_extrato,
                               data_atualizacao_comprovante_extrato,
                               observacao_conciliacao):
    if texto_observacao:
        observacao_conciliacao.criar_atualizar_justificativa(
            periodo=periodo,
            conta_associacao=conta_associacao,
            texto_observacao=texto_observacao,
        )
    else:
        observacao_conciliacao.criar_atualizar_extrato_bancario(
            periodo=periodo,
            conta_associacao=conta_associacao,
            data_extrato=data_extrato,
            saldo_extrato=saldo_extrato,
            comprovante_extrato=comprovante_extrato,
            data_atualizacao_comprovante_extrato=data_atualizacao_comprovante_extrato,
        )
