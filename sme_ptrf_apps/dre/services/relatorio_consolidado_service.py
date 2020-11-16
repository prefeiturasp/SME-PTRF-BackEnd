import logging

from django.db.models import Count, Sum, F, Q

from sme_ptrf_apps.core.models import (
    PrestacaoConta,
    FechamentoPeriodo,
    PrevisaoRepasseSme,
    DevolucaoAoTesouro,
)
from sme_ptrf_apps.dre.models import RelatorioConsolidadoDRE, ObsDevolucaoRelatorioConsolidadoDRE
from sme_ptrf_apps.receitas.models import Receita

logger = logging.getLogger(__name__)


def status_de_geracao_do_relatorio(dre, periodo, tipo_conta):
    '''
    Calcula o status de geração do relatório da DRE em determinado período e tipo de conta conforme tabela:

    PCs em análise?	Relatório gerado?	Texto status	                                                                            Cor
    Sim	            Não	                Ainda constam prestações de contas das associações em análise. Relatório não gerado.	    0
    Sim	            Sim (parcial)	    Ainda constam prestações de contas das associações em análise. Relatório parcial gerado.	1
    Não	            Não	                Análise de prestações de contas das associações completa. Relatório não gerado.	            2
    Não	            Sim (parcial)	    Análise de prestações de contas das associações completa. Relatório parcial gerado.	        2
    Não	            Sim (final)	        Análise de prestações de contas das associações completa. Relatório final gerado.	        3
    '''
    LEGENDA_COR = {
        'NAO_GERADO': {'com_pcs_em_analise': 0, 'sem_pcs_em_analise': 2},
        'GERADO_PARCIAL': {'com_pcs_em_analise': 1, 'sem_pcs_em_analise': 2},
        'GERADO_TOTAL': {'com_pcs_em_analise': 0, 'sem_pcs_em_analise': 3},
    }

    pcs_em_analise = PrestacaoConta.objects.filter(periodo=periodo,
                                                   status__in=['EM_ANALISE', 'RECEBIDA', 'NAO_RECEBIDA', 'DEVOLVIDA'],
                                                   associacao__unidade__dre=dre).exists()

    relatorio = RelatorioConsolidadoDRE.objects.filter(dre=dre, periodo=periodo, tipo_conta=tipo_conta).first()

    status_relatorio = relatorio.status if relatorio else 'NAO_GERADO'

    status_txt_relatorio = f'{RelatorioConsolidadoDRE.STATUS_NOMES[status_relatorio]}.'

    if pcs_em_analise:
        status_txt_analise = 'Ainda constam prestações de contas das associações em análise.'
    else:
        status_txt_analise = 'Análise de prestações de contas das associações completa.'

    status_txt_geracao = f'{status_txt_analise} {status_txt_relatorio}'

    cor_idx = LEGENDA_COR[status_relatorio]['com_pcs_em_analise' if pcs_em_analise else 'sem_pcs_em_analise']

    status = {
        'pcs_em_analise': pcs_em_analise,
        'status_geracao': status_relatorio,
        'status_txt': status_txt_geracao,
        'cor_idx': cor_idx,
        'status_arquivo': 'Documento pendente de geração' if status_relatorio == 'NAO_GERADO' else relatorio.__str__()
    }
    return status


def informacoes_execucao_financeira(dre, periodo, tipo_conta):
    def _totalizador_zerado():
        return {
            'saldo_reprogramado_periodo_anterior_custeio': 0,
            'saldo_reprogramado_periodo_anterior_capital': 0,
            'saldo_reprogramado_periodo_anterior_livre': 0,
            'saldo_reprogramado_periodo_anterior_total': 0,

            'repasses_previstos_sme_custeio': 0,
            'repasses_previstos_sme_capital': 0,
            'repasses_previstos_sme_livre': 0,
            'repasses_previstos_sme_total': 0,

            'repasses_no_periodo_custeio': 0,
            'repasses_no_periodo_capital': 0,
            'repasses_no_periodo_livre': 0,
            'repasses_no_periodo_total': 0,

            'receitas_rendimento_no_periodo_custeio': 0,
            'receitas_rendimento_no_periodo_capital': 0,
            'receitas_rendimento_no_periodo_livre': 0,
            'receitas_rendimento_no_periodo_total': 0,

            'receitas_devolucao_no_periodo_custeio': 0,
            'receitas_devolucao_no_periodo_capital': 0,
            'receitas_devolucao_no_periodo_livre': 0,
            'receitas_devolucao_no_periodo_total': 0,

            'demais_creditos_no_periodo_custeio': 0,
            'demais_creditos_no_periodo_capital': 0,
            'demais_creditos_no_periodo_livre': 0,
            'demais_creditos_no_periodo_total': 0,

            'receitas_totais_no_periodo_custeio': 0,
            'receitas_totais_no_periodo_capital': 0,
            'receitas_totais_no_periodo_livre': 0,
            'receitas_totais_no_periodo_total': 0,

            'despesas_no_periodo_custeio': 0,
            'despesas_no_periodo_capital': 0,
            'despesas_no_periodo_total': 0,

            'saldo_reprogramado_proximo_periodo_custeio': 0,
            'saldo_reprogramado_proximo_periodo_capital': 0,
            'saldo_reprogramado_proximo_periodo_livre': 0,
            'saldo_reprogramado_proximo_periodo_total': 0,

            'devolucoes_ao_tesouro_no_periodo_total': 0,
        }

    def _soma_fechamento(totalizador, fechamento):
        # Saldo Anterior
        totalizador['saldo_reprogramado_periodo_anterior_custeio'] += fechamento.saldo_anterior_custeio
        totalizador['saldo_reprogramado_periodo_anterior_capital'] += fechamento.saldo_anterior_capital
        totalizador['saldo_reprogramado_periodo_anterior_livre'] += fechamento.saldo_anterior_livre
        totalizador['saldo_reprogramado_periodo_anterior_total'] += fechamento.saldo_anterior

        # Repasses no período
        totalizador['repasses_no_periodo_custeio'] += fechamento.total_repasses_custeio
        totalizador['repasses_no_periodo_capital'] += fechamento.total_repasses_capital
        totalizador['repasses_no_periodo_livre'] += fechamento.total_repasses_livre
        totalizador['repasses_no_periodo_total'] += fechamento.total_repasses

        # Receitas Tipo Devolução no período
        totalizador['receitas_devolucao_no_periodo_custeio'] += fechamento.total_receitas_devolucao_custeio
        totalizador['receitas_devolucao_no_periodo_capital'] += fechamento.total_receitas_devolucao_capital
        totalizador['receitas_devolucao_no_periodo_livre'] += fechamento.total_receitas_devolucao_livre
        totalizador['receitas_devolucao_no_periodo_total'] += fechamento.total_receitas_devolucao

        # Receitas Totais no período
        totalizador['receitas_totais_no_periodo_custeio'] += fechamento.total_receitas_custeio
        totalizador['receitas_totais_no_periodo_capital'] += fechamento.total_receitas_capital
        totalizador['receitas_totais_no_periodo_livre'] += fechamento.total_receitas_livre
        totalizador['receitas_totais_no_periodo_total'] += fechamento.total_receitas

        # Despesas Totais no período
        totalizador['despesas_no_periodo_custeio'] += fechamento.total_despesas_custeio
        totalizador['despesas_no_periodo_capital'] += fechamento.total_despesas_capital
        totalizador['despesas_no_periodo_total'] += fechamento.total_despesas

        # Saldos Reprogramados Totais para o próximo período
        totalizador['saldo_reprogramado_proximo_periodo_custeio'] += fechamento.saldo_reprogramado_custeio
        totalizador['saldo_reprogramado_proximo_periodo_capital'] += fechamento.saldo_reprogramado_capital
        totalizador['saldo_reprogramado_proximo_periodo_livre'] += fechamento.saldo_reprogramado_livre
        totalizador['saldo_reprogramado_proximo_periodo_total'] += fechamento.saldo_reprogramado

        return totalizador

    def _soma_receitas_tipo_rendimento(totais, periodo, conta_associacao, acao_associacao):

        receitas = Receita.receitas_da_acao_associacao_no_periodo(acao_associacao=acao_associacao, periodo=periodo,
                                                                  conta_associacao=conta_associacao)
        for receita in receitas:
            if receita.tipo_receita.e_rendimento:
                totais['receitas_rendimento_no_periodo_total'] += receita.valor

                if receita.categoria_receita == 'CAPITAL':
                    totais['receitas_rendimento_no_periodo_capital'] += receita.valor
                elif receita.categoria_receita == 'CUSTEIO':
                    totais['receitas_rendimento_no_periodo_custeio'] += receita.valor
                else:
                    totais['receitas_rendimento_no_periodo_livre'] += receita.valor

        return totais

    def _atualiza_demais_creditos(totais):
        totais['demais_creditos_no_periodo_custeio'] += totais['receitas_totais_no_periodo_custeio'] - \
                                                        totais['repasses_no_periodo_custeio'] - \
                                                        totais['receitas_devolucao_no_periodo_custeio'] - \
                                                        totais['receitas_rendimento_no_periodo_custeio']

        totais['demais_creditos_no_periodo_capital'] += totais['receitas_totais_no_periodo_capital'] - \
                                                        totais['repasses_no_periodo_capital'] - \
                                                        totais['receitas_devolucao_no_periodo_capital'] - \
                                                        totais['receitas_rendimento_no_periodo_capital']

        totais['demais_creditos_no_periodo_livre'] += totais['receitas_totais_no_periodo_livre'] - \
                                                      totais['repasses_no_periodo_livre'] - \
                                                      totais['receitas_devolucao_no_periodo_livre'] - \
                                                      totais['receitas_rendimento_no_periodo_livre']

        totais['demais_creditos_no_periodo_total'] += totais['receitas_totais_no_periodo_total'] - \
                                                      totais['repasses_no_periodo_total'] - \
                                                      totais['receitas_devolucao_no_periodo_total'] - \
                                                      totais['receitas_rendimento_no_periodo_total']

        return totais

    def _totaliza_fechamentos(dre, periodo, tipo_conta, totais):
        # Fechamentos no período da conta de PCs de Associações da DRE, concluídas
        fechamentos = FechamentoPeriodo.objects.filter(
            periodo=periodo,
            conta_associacao__tipo_conta=tipo_conta,
            associacao__unidade__dre=dre,
            prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']
        )
        for fechamento in fechamentos:
            totais = _soma_fechamento(totais, fechamento)
            totais = _soma_receitas_tipo_rendimento(
                periodo=periodo,
                conta_associacao=fechamento.conta_associacao,
                acao_associacao=fechamento.acao_associacao,
                totais=totais
            )
        return totais

    def _totaliza_previsoes_repasses_sme(dre, periodo, tipo_conta, totais):
        # Previsões para o período e conta com o tipo de conta para Associações da DRE
        previsoes = PrevisaoRepasseSme.objects.filter(
            periodo=periodo,
            conta_associacao__tipo_conta=tipo_conta,
            associacao__unidade__dre=dre
        )
        for previsao in previsoes:
            totais['repasses_previstos_sme_custeio'] += previsao.valor_custeio
            totais['repasses_previstos_sme_capital'] += previsao.valor_capital
            totais['repasses_previstos_sme_livre'] += previsao.valor_livre
            totais['repasses_previstos_sme_total'] += previsao.valor_total

        return totais

    def _totaliza_devolucoes_ao_tesouro(dre, periodo, totais):
        # Devoluções ao tesouro de PCs de Associações da DRE, no período e concluídas
        devolucoes = DevolucaoAoTesouro.objects.filter(
            prestacao_conta__periodo=periodo,
            prestacao_conta__associacao__unidade__dre=dre,
            prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']
        )
        for devolucao in devolucoes:
            totais['devolucoes_ao_tesouro_no_periodo_total'] += devolucao.valor

        return totais

    totais = _totalizador_zerado()

    totais = _totaliza_fechamentos(dre, periodo, tipo_conta, totais)

    totais = _atualiza_demais_creditos(totais)

    totais = _totaliza_previsoes_repasses_sme(dre, periodo, tipo_conta, totais)

    totais = _totaliza_devolucoes_ao_tesouro(dre, periodo, totais)

    return totais


def add_obs_devolucoes_dre(devolucoes, tipo_devolucao, dre, periodo, tipo_conta):
    result = []
    for dev in devolucoes:

        if tipo_devolucao == 'CONTA':
            registro_obs = ObsDevolucaoRelatorioConsolidadoDRE.objects.filter(
                dre=dre,
                periodo=periodo,
                tipo_conta=tipo_conta,
                tipo_devolucao=tipo_devolucao,
                tipo_devolucao_a_conta__uuid=dev['detalhe_tipo_receita__uuid']
            ).first()
        else:

            registro_obs = ObsDevolucaoRelatorioConsolidadoDRE.objects.filter(
                dre=dre,
                periodo=periodo,
                tipo_conta=tipo_conta,
                tipo_devolucao=tipo_devolucao,
                tipo_devolucao_ao_tesouro__uuid=dev['tipo__uuid']
            ).first()

        result.append(
            {
                'tipo_nome': dev['detalhe_tipo_receita__nome'] if tipo_devolucao == 'CONTA' else dev['tipo__nome'],
                'tipo_uuid': dev['detalhe_tipo_receita__uuid'] if tipo_devolucao == 'CONTA' else dev['tipo__uuid'],
                'ocorrencias': dev['ocorrencias'],
                'valor': dev['valor'],
                'observacao': registro_obs.observacao if registro_obs else '',
            }
        )
    return result


def informacoes_devolucoes_a_conta_ptrf(dre, periodo, tipo_conta):
    # Devoluções à conta referente ao período e tipo_conta de Associações da DRE concluídas
    associacoes_com_pc_concluidas = PrestacaoConta.objects.filter(
        periodo=periodo,
        associacao__unidade__dre=dre,
        status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']
    ).values_list('associacao__uuid')

    if periodo.data_fim_realizacao_despesas:
        receitas_periodo = Receita.objects.filter(
            data__range=(periodo.data_inicio_realizacao_despesas, periodo.data_fim_realizacao_despesas))
    else:
        receitas_periodo = Receita.objects.filter(
            data__gte=periodo.data_inicio_realizacao_despesas)

    devolucoes = receitas_periodo.filter(
        tipo_receita__e_devolucao=True,
        conta_associacao__tipo_conta=tipo_conta,
        associacao__uuid__in=associacoes_com_pc_concluidas,
    ).values('detalhe_tipo_receita__nome', 'detalhe_tipo_receita__uuid').annotate(ocorrencias=Count('uuid'),
                                                                                  valor=Sum('valor'))

    return add_obs_devolucoes_dre(devolucoes=devolucoes, tipo_devolucao='CONTA', dre=dre, periodo=periodo,
                                  tipo_conta=tipo_conta)


def informacoes_devolucoes_ao_tesouro(dre, periodo, tipo_conta):
    # Devoluções ao tesouro de PCs de Associações da DRE, no período da conta e concluídas
    devolucoes = DevolucaoAoTesouro.objects.filter(
        prestacao_conta__periodo=periodo,
        prestacao_conta__associacao__unidade__dre=dre,
        prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']
    ).values('tipo__nome', 'tipo__uuid').annotate(ocorrencias=Count('uuid'), valor=Sum('valor'))

    return add_obs_devolucoes_dre(devolucoes, 'TESOURO', dre=dre, periodo=periodo,
                                  tipo_conta=tipo_conta)


def informacoes_execucao_financeira_unidades(
    dre,
    periodo,
    tipo_conta,
    filtro_nome=None, filtro_tipo_unidade=None, filtro_status=None
):
    from sme_ptrf_apps.core.models import Associacao

    def _totalizador_zerado():
        return {
            'saldo_reprogramado_periodo_anterior_custeio': 0,
            'saldo_reprogramado_periodo_anterior_capital': 0,
            'saldo_reprogramado_periodo_anterior_livre': 0,
            'saldo_reprogramado_periodo_anterior_total': 0,

            'repasses_previstos_sme_custeio': 0,
            'repasses_previstos_sme_capital': 0,
            'repasses_previstos_sme_livre': 0,
            'repasses_previstos_sme_total': 0,

            'repasses_no_periodo_custeio': 0,
            'repasses_no_periodo_capital': 0,
            'repasses_no_periodo_livre': 0,
            'repasses_no_periodo_total': 0,

            'receitas_rendimento_no_periodo_custeio': 0,
            'receitas_rendimento_no_periodo_capital': 0,
            'receitas_rendimento_no_periodo_livre': 0,
            'receitas_rendimento_no_periodo_total': 0,

            'receitas_devolucao_no_periodo_custeio': 0,
            'receitas_devolucao_no_periodo_capital': 0,
            'receitas_devolucao_no_periodo_livre': 0,
            'receitas_devolucao_no_periodo_total': 0,

            'demais_creditos_no_periodo_custeio': 0,
            'demais_creditos_no_periodo_capital': 0,
            'demais_creditos_no_periodo_livre': 0,
            'demais_creditos_no_periodo_total': 0,

            'receitas_totais_no_periodo_custeio': 0,
            'receitas_totais_no_periodo_capital': 0,
            'receitas_totais_no_periodo_livre': 0,
            'receitas_totais_no_periodo_total': 0,

            'despesas_no_periodo_custeio': 0,
            'despesas_no_periodo_capital': 0,
            'despesas_no_periodo_total': 0,

            'saldo_reprogramado_proximo_periodo_custeio': 0,
            'saldo_reprogramado_proximo_periodo_capital': 0,
            'saldo_reprogramado_proximo_periodo_livre': 0,
            'saldo_reprogramado_proximo_periodo_total': 0,

            'devolucoes_ao_tesouro_no_periodo_total': 0,
        }

    def _soma_fechamento(totalizador, fechamento):
        # Saldo Anterior
        totalizador['saldo_reprogramado_periodo_anterior_custeio'] += fechamento.saldo_anterior_custeio
        totalizador['saldo_reprogramado_periodo_anterior_capital'] += fechamento.saldo_anterior_capital
        totalizador['saldo_reprogramado_periodo_anterior_livre'] += fechamento.saldo_anterior_livre
        totalizador['saldo_reprogramado_periodo_anterior_total'] += fechamento.saldo_anterior

        # Repasses no período
        totalizador['repasses_no_periodo_custeio'] += fechamento.total_repasses_custeio
        totalizador['repasses_no_periodo_capital'] += fechamento.total_repasses_capital
        totalizador['repasses_no_periodo_livre'] += fechamento.total_repasses_livre
        totalizador['repasses_no_periodo_total'] += fechamento.total_repasses

        # Receitas Tipo Devolução no período
        totalizador['receitas_devolucao_no_periodo_custeio'] += fechamento.total_receitas_devolucao_custeio
        totalizador['receitas_devolucao_no_periodo_capital'] += fechamento.total_receitas_devolucao_capital
        totalizador['receitas_devolucao_no_periodo_livre'] += fechamento.total_receitas_devolucao_livre
        totalizador['receitas_devolucao_no_periodo_total'] += fechamento.total_receitas_devolucao

        # Receitas Totais no período
        totalizador['receitas_totais_no_periodo_custeio'] += fechamento.total_receitas_custeio
        totalizador['receitas_totais_no_periodo_capital'] += fechamento.total_receitas_capital
        totalizador['receitas_totais_no_periodo_livre'] += fechamento.total_receitas_livre
        totalizador['receitas_totais_no_periodo_total'] += fechamento.total_receitas

        # Despesas Totais no período
        totalizador['despesas_no_periodo_custeio'] += fechamento.total_despesas_custeio
        totalizador['despesas_no_periodo_capital'] += fechamento.total_despesas_capital
        totalizador['despesas_no_periodo_total'] += fechamento.total_despesas

        # Saldos Reprogramados Totais para o próximo período
        totalizador['saldo_reprogramado_proximo_periodo_custeio'] += fechamento.saldo_reprogramado_custeio
        totalizador['saldo_reprogramado_proximo_periodo_capital'] += fechamento.saldo_reprogramado_capital
        totalizador['saldo_reprogramado_proximo_periodo_livre'] += fechamento.saldo_reprogramado_livre
        totalizador['saldo_reprogramado_proximo_periodo_total'] += fechamento.saldo_reprogramado

        return totalizador

    def _soma_receitas_tipo_rendimento(totais, periodo, conta_associacao, acao_associacao):

        receitas = Receita.receitas_da_acao_associacao_no_periodo(acao_associacao=acao_associacao, periodo=periodo,
                                                                  conta_associacao=conta_associacao)
        for receita in receitas:
            if receita.tipo_receita.e_rendimento:
                totais['receitas_rendimento_no_periodo_total'] += receita.valor

                if receita.categoria_receita == 'CAPITAL':
                    totais['receitas_rendimento_no_periodo_capital'] += receita.valor
                elif receita.categoria_receita == 'CUSTEIO':
                    totais['receitas_rendimento_no_periodo_custeio'] += receita.valor
                else:
                    totais['receitas_rendimento_no_periodo_livre'] += receita.valor

        return totais

    def _atualiza_demais_creditos(totais):
        totais['demais_creditos_no_periodo_custeio'] += totais['receitas_totais_no_periodo_custeio'] - \
                                                        totais['repasses_no_periodo_custeio'] - \
                                                        totais['receitas_devolucao_no_periodo_custeio'] - \
                                                        totais['receitas_rendimento_no_periodo_custeio']

        totais['demais_creditos_no_periodo_capital'] += totais['receitas_totais_no_periodo_capital'] - \
                                                        totais['repasses_no_periodo_capital'] - \
                                                        totais['receitas_devolucao_no_periodo_capital'] - \
                                                        totais['receitas_rendimento_no_periodo_capital']

        totais['demais_creditos_no_periodo_livre'] += totais['receitas_totais_no_periodo_livre'] - \
                                                      totais['repasses_no_periodo_livre'] - \
                                                      totais['receitas_devolucao_no_periodo_livre'] - \
                                                      totais['receitas_rendimento_no_periodo_livre']

        totais['demais_creditos_no_periodo_total'] += totais['receitas_totais_no_periodo_total'] - \
                                                      totais['repasses_no_periodo_total'] - \
                                                      totais['receitas_devolucao_no_periodo_total'] - \
                                                      totais['receitas_rendimento_no_periodo_total']

        return totais

    def _totaliza_fechamentos(associacao, periodo, tipo_conta, totais):
        # Fechamentos no período da conta de PCs de Associações da DRE, concluídas
        fechamentos = associacao.fechamentos_associacao.filter(
            periodo=periodo,
            conta_associacao__tipo_conta=tipo_conta,
            prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']
        )
        for fechamento in fechamentos:
            totais = _soma_fechamento(totais, fechamento)
            totais = _soma_receitas_tipo_rendimento(
                periodo=periodo,
                conta_associacao=fechamento.conta_associacao,
                acao_associacao=fechamento.acao_associacao,
                totais=totais
            )
        return totais

    def _totaliza_previsoes_repasses_sme(associacao, periodo, tipo_conta, totais):
        # Previsões para o período e conta com o tipo de conta para Associações da DRE
        previsoes = associacao.previsoes_de_repasse_sme_para_a_associacao.filter(
            periodo=periodo,
            conta_associacao__tipo_conta=tipo_conta,
        )
        for previsao in previsoes:
            totais['repasses_previstos_sme_custeio'] += previsao.valor_custeio
            totais['repasses_previstos_sme_capital'] += previsao.valor_capital
            totais['repasses_previstos_sme_livre'] += previsao.valor_livre
            totais['repasses_previstos_sme_total'] += previsao.valor_total

        return totais

    def _totaliza_devolucoes_ao_tesouro(prestacao_conta, periodo, totais):
        # Devoluções ao tesouro de PCs de Associações da DRE, no período e concluídas
        devolucoes = prestacao_conta.devolucoes_ao_tesouro_da_prestacao.all()
        for devolucao in devolucoes:
            totais['devolucoes_ao_tesouro_no_periodo_total'] += devolucao.valor

        return totais

    resultado = []

    associacoes_da_dre = Associacao.objects.filter(unidade__dre=dre).exclude(cnpj__exact='').order_by('nome')

    if filtro_nome is not None:
        associacoes_da_dre = associacoes_da_dre.filter(Q(nome__unaccent__icontains=filtro_nome) | Q(
            unidade__nome__unaccent__icontains=filtro_nome))

    if filtro_tipo_unidade is not None:
        associacoes_da_dre = associacoes_da_dre.filter(unidade__tipo_unidade=filtro_tipo_unidade)

    for associacao in associacoes_da_dre.all():

        prestacao_conta = associacao.prestacoes_de_conta_da_associacao.filter(periodo=periodo).first()

        status_prestacao_conta = prestacao_conta.status if prestacao_conta else 'NAO_APRESENTADA'

        if filtro_status and status_prestacao_conta != filtro_status:
            continue

        totais = _totalizador_zerado()

        if prestacao_conta:
            totais = _totaliza_fechamentos(associacao, periodo, tipo_conta, totais)
            totais = _atualiza_demais_creditos(totais)
            totais = _totaliza_devolucoes_ao_tesouro(prestacao_conta, periodo, totais)

        totais = _totaliza_previsoes_repasses_sme(associacao, periodo, tipo_conta, totais)

        resultado.append(
            {
                'unidade': {
                    'uuid': f'{associacao.unidade.uuid}',
                    'codigo_eol': associacao.unidade.codigo_eol,
                    'tipo_unidade': associacao.unidade.tipo_unidade,
                    'nome': associacao.unidade.nome,
                    'sigla': associacao.unidade.sigla,
                },

                'status_prestacao_contas': status_prestacao_conta,
                'valores': totais,
            }
        )

    return resultado


def update_observacao_devolucao(dre, tipo_conta, periodo, tipo_devolucao, subtipo_devolucao, observacao):
    if not observacao:
        ObsDevolucaoRelatorioConsolidadoDRE.objects.filter(
            dre=dre,
            tipo_conta=tipo_conta,
            periodo=periodo,
            tipo_devolucao=tipo_devolucao,
            tipo_devolucao_a_conta=subtipo_devolucao if tipo_devolucao == 'CONTA' else None,
            tipo_devolucao_ao_tesouro=subtipo_devolucao if tipo_devolucao == 'TESOURO' else None,
        ).delete()

        return {
            'tipo_nome': f'{subtipo_devolucao.nome}',
            'tipo_uuid': f'{subtipo_devolucao.uuid}',
            'observacao': '',
            'mensagem': 'Observação apagada com sucesso.'
        }

    obj, created = ObsDevolucaoRelatorioConsolidadoDRE.objects.update_or_create(
        dre=dre,
        tipo_conta=tipo_conta,
        periodo=periodo,
        tipo_devolucao=tipo_devolucao,
        tipo_devolucao_a_conta=subtipo_devolucao if tipo_devolucao == 'CONTA' else None,
        tipo_devolucao_ao_tesouro=subtipo_devolucao if tipo_devolucao == 'TESOURO' else None,
        defaults={'observacao': observacao},
    )

    resultado = {
        'tipo_nome': f'{subtipo_devolucao.nome}',
        'tipo_uuid': f'{subtipo_devolucao.uuid}',
        'observacao': observacao,
        'mensagem': 'Observação criada com sucesso.' if created else 'Observação atualizada com sucesso.'
    }

    return resultado
