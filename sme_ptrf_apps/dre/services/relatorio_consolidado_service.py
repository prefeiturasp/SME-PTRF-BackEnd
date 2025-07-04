import logging

from django.db.models import Count, Sum, Q

from sme_ptrf_apps.core.models import (
    PrestacaoConta,
    FechamentoPeriodo,
    PrevisaoRepasseSme,
    DevolucaoAoTesouro, TipoConta,
    ContaAssociacao,
    SolicitacaoEncerramentoContaAssociacao
)
from sme_ptrf_apps.dre.models import RelatorioConsolidadoDRE, ObsDevolucaoRelatorioConsolidadoDRE, \
    JustificativaRelatorioConsolidadoDRE, ConsolidadoDRE
from sme_ptrf_apps.receitas.models import Receita

from ..services.dados_demo_execucao_fisico_financeira_service import gerar_dados_demo_execucao_fisico_financeira
from .demo_execucao_fisico_financeiro_pdf_service import gerar_arquivo_demonstrativo_execucao_fisico_financeiro_pdf

logger = logging.getLogger(__name__)


def status_de_geracao_do_relatorio(dre, periodo, tipo_conta):
    """
    Calcula o status de geração do relatório da DRE em determinado período e tipo de conta conforme tabela:

    PCs em análise?	Relatório gerado?	Texto status	                                                                            Cor
    Sim	            Não	                Ainda constam prestações de contas das associações em análise. Relatório não gerado.	    0
    Sim	            Sim (parcial)	    Ainda constam prestações de contas das associações em análise. Relatório parcial gerado.	1
    Não	            Não	                Análise de prestações de contas das associações completa. Relatório não gerado.	            2
    Não	            Sim (parcial)	    Análise de prestações de contas das associações completa. Relatório parcial gerado.	        2
    Não	            Sim (final)	        Análise de prestações de contas das associações completa. Relatório final gerado.	        3
    """

    LEGENDA_COR = {
        'NAO_GERADO': {'com_pcs_em_analise': 0, 'sem_pcs_em_analise': 2},
        'GERADO_PARCIAL': {'com_pcs_em_analise': 1, 'sem_pcs_em_analise': 2},
        'GERADO_TOTAL': {'com_pcs_em_analise': 0, 'sem_pcs_em_analise': 3},
        'EM_PROCESSAMENTO': {'com_pcs_em_analise': 0, 'sem_pcs_em_analise': 3},
    }

    pcs_em_analise = PrestacaoConta.objects.filter(periodo=periodo,
                                                   status__in=['EM_ANALISE', 'RECEBIDA', 'NAO_RECEBIDA', 'DEVOLVIDA'],
                                                   associacao__unidade__dre=dre).exists()

    relatorio = RelatorioConsolidadoDRE.objects.filter(dre=dre, periodo=periodo, tipo_conta=tipo_conta).first()

    status_relatorio = relatorio.status if relatorio else 'NAO_GERADO'

    status_txt_relatorio = f'{RelatorioConsolidadoDRE.STATUS_NOMES[status_relatorio]}.'

    versao_relatorio = relatorio.versao if relatorio else None

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
        'status_arquivo': 'Documento pendente de geração' if status_relatorio == 'NAO_GERADO' else relatorio.__str__(),
        'versao': versao_relatorio
    }
    return status


def retorna_informacoes_execucao_financeira_todas_as_contas(dre, periodo, consolidado_dre=None):
    from .consolidado_dre_service import verificar_se_status_parcial_ou_total_e_retornar_sequencia_de_publicacao
    eh_retificacao = True if consolidado_dre and consolidado_dre.eh_retificacao else False

    dre_uuid = dre.uuid
    periodo_uuid = periodo.uuid

    if eh_retificacao:
        eh_parcial = consolidado_dre.eh_parcial
        qtde_unidades = consolidado_dre.pcs_do_consolidado.all().count()

        associacoes_do_consolidado = consolidado_dre.pcs_do_consolidado.values_list("associacao_id", flat=True).distinct()

        if consolidado_dre.consolidado_retificado and consolidado_dre.consolidado_retificado.data_publicacao:
            titulo_parcial = f"Retificação da Publicação de {consolidado_dre.consolidado_retificado.data_publicacao.strftime('%d/%m/%Y')} - {qtde_unidades} unidade(s)"
        else:
            titulo_parcial = ""
    else:
        parcial = verificar_se_status_parcial_ou_total_e_retornar_sequencia_de_publicacao(dre_uuid, periodo_uuid)
        eh_parcial = parcial['parcial']
        sequencia_de_publicacao = parcial['sequencia_de_publicacao_atual']

        # TODO Tratativa dos Bugs: 91797, 93549 e 93018 da Sprint 65
        # Gerava divergência em Tela do Relatório Consolidado em Tela
        # Quando uma prévia era gerada com um número X de PCS e depois concluisse mais PCS sempre olhava para o numero
        # Que já estava na Prévia, não levava em consideração as novas PCs concluídas
        # Não considera mais as PCs do Consolidado
        # Foi adicionado and consolidado_dre.versao == "FINAL" para verificar se passa ou não o consolidado

        if consolidado_dre and consolidado_dre.versao == "FINAL":
            qtde_unidades = consolidado_dre.pcs_do_consolidado.all().count()

            associacoes_do_consolidado = consolidado_dre.pcs_do_consolidado.values_list("associacao_id", flat=True).distinct()

            sequencia_de_publicacao_do_consolidado = consolidado_dre.sequencia_de_publicacao

            if sequencia_de_publicacao_do_consolidado > 0:
                titulo_parcial = f"Publicação Parcial #{sequencia_de_publicacao_do_consolidado} - {qtde_unidades} unidade(s)" if eh_parcial else f"Publicação Única {qtde_unidades} unidade(s)"
            else:
                titulo_parcial = "Publicação Única"
        else:
            pcs = PrestacaoConta.objects.filter(
                periodo=periodo,
                status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA'],
                associacao__unidade__dre=dre,
                publicada=False
            )

            qtde_unidades = pcs.count()

            associacoes_do_consolidado = pcs.values_list("associacao_id", flat=True).distinct()

            if sequencia_de_publicacao > 0:
                titulo_parcial = f"Publicação Parcial #{sequencia_de_publicacao} - {qtde_unidades} unidade(s)" if eh_parcial else f"Publicação Única {qtde_unidades} unidade(s)"
            else:
                titulo_parcial = "Publicação Única"


    dados = {
        "periodo_referencia": periodo.referencia if periodo.referencia else "",
        "periodo_data_inicio_realizacao_despesas": periodo.data_inicio_realizacao_despesas if periodo.data_inicio_realizacao_despesas else "",
        "periodo_data_fim_realizacao_despesas": periodo.data_fim_realizacao_despesas if periodo.data_fim_realizacao_despesas else "",
        "titulo_parcial": titulo_parcial,
        "eh_parcial": eh_parcial,
    }

    tipos_de_conta = TipoConta.objects.all()

    objeto_tipo_de_conta = []
    dados['por_tipo_de_conta'] = []

    for tipo_conta in tipos_de_conta:
        # TODO Tratativa dos Bugs: 91797, 93549 e 93018 da Sprint 65
        # totais = informacoes_execucao_financeira(dre, periodo, tipo_conta, apenas_nao_publicadas=True, consolidado_dre=consolidado_dre)
        # Foi adicionado and consolidado_dre.versao == "FINAL" para verificar se passa ou não o consolidado
        contas_inativas_com_solicitacao_de_encerramento =  {Q(status=ContaAssociacao.STATUS_INATIVA) & Q(solicitacao_encerramento__isnull=False)}
        contas_encerradas_em_periodos_anteriores = {Q(*contas_inativas_com_solicitacao_de_encerramento) &
                                                    Q(solicitacao_encerramento__status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA) &
                                                    Q(solicitacao_encerramento__data_de_encerramento_na_agencia__lt=periodo.data_inicio_realizacao_despesas)}
        if periodo.data_fim_realizacao_despesas:
            contas_criadas_no_periodo_ou_anterior = {Q(data_inicio__isnull=True) | Q(data_inicio__lte=periodo.data_fim_realizacao_despesas)}
        else:
            contas_criadas_no_periodo_ou_anterior = {}

        contas_validas = ContaAssociacao.objects.filter(Q(*contas_criadas_no_periodo_ou_anterior),
                                                        associacao__in=associacoes_do_consolidado,
                                                        tipo_conta=tipo_conta).exclude(
                                                            Q(*contas_encerradas_em_periodos_anteriores)
                                                        )

        if contas_validas.exists():
            if consolidado_dre and consolidado_dre.versao == "FINAL":
                totais = informacoes_execucao_financeira(dre, periodo, tipo_conta, apenas_nao_publicadas=True,
                                                        consolidado_dre=consolidado_dre)
            else:
                totais = informacoes_execucao_financeira(dre, periodo, tipo_conta, apenas_nao_publicadas=True)

            if consolidado_dre and consolidado_dre.eh_retificacao:
                if consolidado_dre.laudas_do_consolidado_dre.all():
                    # foi gerado

                    justificativa = JustificativaRelatorioConsolidadoDRE.objects.filter(
                        dre=dre,
                        tipo_conta=tipo_conta,
                        periodo=periodo,
                        consolidado_dre=consolidado_dre,
                        eh_retificacao=True
                    ).last()

                else:
                    justificativa = JustificativaRelatorioConsolidadoDRE.objects.filter(
                        dre=dre,
                        tipo_conta=tipo_conta,
                        periodo=periodo,
                        consolidado_dre__isnull=True,
                        eh_retificacao=True
                    ).last()

            elif consolidado_dre and consolidado_dre.versao == 'FINAL':
                # Justificativa
                justificativa = JustificativaRelatorioConsolidadoDRE.objects.filter(
                    dre=dre,
                    tipo_conta=tipo_conta,
                    periodo=periodo,
                    consolidado_dre=consolidado_dre,
                    eh_retificacao=False
                ).last()
            else:
                justificativa = JustificativaRelatorioConsolidadoDRE.objects.filter(
                    dre=dre,
                    tipo_conta=tipo_conta,
                    periodo=periodo,
                    consolidado_dre__isnull=True,
                    eh_retificacao=False
                ).last()

            objeto_tipo_de_conta.append({
                'tipo_conta': tipo_conta.nome if tipo_conta.nome else '',
                'valores': totais,
                'justificativa_texto': justificativa.texto if justificativa else '',
                'justificativa_uuid': justificativa.uuid if justificativa else None,
                'consolidado_dre': consolidado_dre.uuid if justificativa and justificativa.consolidado_dre and justificativa.consolidado_dre.uuid else None,
                'tipo_conta_uuid': tipo_conta.uuid,
                'eh_retificacao': consolidado_dre.eh_retificacao if consolidado_dre else False
            })

            dados['por_tipo_de_conta'] = objeto_tipo_de_conta

    return dados


def informacoes_execucao_financeira(dre, periodo, tipo_conta, apenas_nao_publicadas=False, consolidado_dre=None):
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

        if consolidado_dre:
            fechamentos = FechamentoPeriodo.objects.filter(
                prestacao_conta__consolidados_dre_da_prestacao_de_contas=consolidado_dre,
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
                associacao__unidade__dre=dre,
            )
        elif not apenas_nao_publicadas:
            fechamentos = FechamentoPeriodo.objects.filter(
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
                associacao__unidade__dre=dre,
                prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']
            )
        else:
            fechamentos = FechamentoPeriodo.objects.filter(
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
                associacao__unidade__dre=dre,
                prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA'],
                prestacao_conta__publicada=False,
            )

        for fechamento in fechamentos:
            conta_associacao = fechamento.conta_associacao

            if not conta_associacao.conta_criada_no_periodo_ou_periodo_anteriores(periodo=periodo):
                continue

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

        if consolidado_dre:
            previsoes = PrevisaoRepasseSme.objects.filter(
                Q(associacao__prestacoes_de_conta_da_associacao__consolidados_dre_da_prestacao_de_contas=consolidado_dre) &
                (
                    Q(associacao__prestacoes_de_conta_da_associacao__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']) |
                    Q(associacao__prestacoes_de_conta_da_associacao__status_anterior_a_retificacao__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA'])
                ) &
                Q(periodo=periodo) &
                Q(conta_associacao__tipo_conta=tipo_conta) &
                Q(associacao__unidade__dre=dre)
            ).distinct()
        elif not apenas_nao_publicadas:
            previsoes = PrevisaoRepasseSme.objects.filter(
                associacao__prestacoes_de_conta_da_associacao__periodo=periodo,
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
                associacao__unidade__dre=dre,
                associacao__prestacoes_de_conta_da_associacao__status__in=['APROVADA', 'APROVADA_RESSALVA',
                                                                           'REPROVADA'],
            ).distinct()
        else:
            previsoes = PrevisaoRepasseSme.objects.filter(
                associacao__prestacoes_de_conta_da_associacao__periodo=periodo,
                associacao__prestacoes_de_conta_da_associacao__publicada=False,
                associacao__prestacoes_de_conta_da_associacao__status__in=['APROVADA', 'APROVADA_RESSALVA',
                                                                           'REPROVADA'],
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
                associacao__unidade__dre=dre,
            ).distinct()

        for previsao in previsoes:
            conta_associacao = previsao.conta_associacao
            if not conta_associacao.conta_criada_no_periodo_ou_periodo_anteriores(periodo=periodo):
                continue

            totais['repasses_previstos_sme_custeio'] += previsao.valor_custeio
            totais['repasses_previstos_sme_capital'] += previsao.valor_capital
            totais['repasses_previstos_sme_livre'] += previsao.valor_livre
            totais['repasses_previstos_sme_total'] += previsao.valor_total

        return totais

    def _totaliza_devolucoes_ao_tesouro(dre, periodo, totais, tipo_conta):
        # Devoluções ao tesouro de PCs de Associações da DRE, no período e concluídas

        if consolidado_dre:
            devolucoes = DevolucaoAoTesouro.objects.filter(
                prestacao_conta__consolidado_dre=consolidado_dre,
                prestacao_conta__periodo=periodo,
                prestacao_conta__associacao__unidade__dre=dre,
                prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA'],
                despesa__rateios__conta_associacao__tipo_conta=tipo_conta
            ).distinct("pk")
        elif not apenas_nao_publicadas:
            devolucoes = DevolucaoAoTesouro.objects.filter(
                prestacao_conta__periodo=periodo,
                prestacao_conta__associacao__unidade__dre=dre,
                prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA'],
                despesa__rateios__conta_associacao__tipo_conta=tipo_conta
            ).distinct("pk")
        else:
            devolucoes = DevolucaoAoTesouro.objects.filter(
                prestacao_conta__periodo=periodo,
                prestacao_conta__associacao__unidade__dre=dre,
                prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA'],
                despesa__rateios__conta_associacao__tipo_conta=tipo_conta,
                prestacao_conta__publicada=False,
            ).distinct("pk")

        for devolucao in devolucoes:
            rateio = devolucao.despesa.rateios.filter(conta_associacao__tipo_conta=tipo_conta).first()
            conta_associacao = rateio.conta_associacao if rateio else None
            if conta_associacao and not conta_associacao.conta_criada_no_periodo_ou_periodo_anteriores(periodo=periodo):
                continue

            totais['devolucoes_ao_tesouro_no_periodo_total'] += devolucao.valor

        return totais

    totais = _totalizador_zerado()

    totais = _totaliza_fechamentos(dre, periodo, tipo_conta, totais)

    totais = _atualiza_demais_creditos(totais)

    totais = _totaliza_previsoes_repasses_sme(dre, periodo, tipo_conta, totais)

    totais = _totaliza_devolucoes_ao_tesouro(dre, periodo, totais, tipo_conta)

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

    # Necessário realizar as duas querys para usar o distinct e annotate
    distinct_devolucoes = DevolucaoAoTesouro.objects.filter(
        prestacao_conta__periodo=periodo,
        prestacao_conta__associacao__unidade__dre=dre,
        prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA'],
        despesa__rateios__conta_associacao__tipo_conta=tipo_conta
    ).distinct("uuid")

    devolucoes = DevolucaoAoTesouro.objects.values('tipo__nome', 'tipo__uuid').filter(
        id__in=distinct_devolucoes).annotate(ocorrencias=Count('uuid'), valor=Sum('valor'))

    return add_obs_devolucoes_dre(devolucoes, 'TESOURO', dre=dre, periodo=periodo,
                                  tipo_conta=tipo_conta)


def get_status_label(status):
    if status == 'APROVADA':
        status_label = 'Aprovada'
    elif status == 'APROVADA_RESSALVA':
        status_label = 'Aprovada com ressalvas'
    elif status == 'REPROVADA':
        status_label = 'Reprovada'
    elif status == 'NAO_RECEBIDA':
        status_label = 'Não recebida'
    elif status == 'RECEBIDA':
        status_label = 'Recebida'
    elif status == 'EM_ANALISE':
        status_label = 'Em análise'
    elif status == 'NAO_APRESENTADA':
        status_label = 'Não apresentada'
    elif status == 'DEVOLVIDA':
        status_label = 'Devolvida para acertos'
    elif status == 'DEVOLVIDA_RETORNADA':
        status_label = 'Apresentada após acertos'
    elif status == 'DEVOLVIDA_RECEBIDA':
        status_label = 'Recebida após acertos'
    elif status == 'EM_PROCESSAMENTO':
        status_label = 'Em processamento'
    else:
        status_label = 'Sem status'

    return status_label


def informacoes_execucao_financeira_unidades(
    dre,
    periodo,
    tipo_conta,
    apenas_nao_publicadas=False,
    filtro_nome=None,
    filtro_tipo_unidade=None,
    filtro_status=None,
    consolidado_dre=None
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

        if consolidado_dre:
            # Quando é uma retificação, as informações são resgatadas filtrando pelo consolidado

            fechamentos = associacao.fechamentos_associacao.filter(
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
                prestacao_conta__consolidado_dre=consolidado_dre
            )

        elif not apenas_nao_publicadas:
            fechamentos = associacao.fechamentos_associacao.filter(
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
                prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']
            )
        else:
            fechamentos = associacao.fechamentos_associacao.filter(
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
                prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA'],
                prestacao_conta__publicada=False
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

        if not apenas_nao_publicadas:
            previsoes = associacao.previsoes_de_repasse_sme_para_a_associacao.filter(
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
            )
        else:
            previsoes = associacao.previsoes_de_repasse_sme_para_a_associacao.filter(
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
                associacao__prestacoes_de_conta_da_associacao__publicada=False,
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
    resultado_nao_apresentada = []

    if consolidado_dre:
        # Quando é uma retificação, as informações são resgatadas filtrando pelo consolidado

        associacoes_da_dre = Associacao.objects.filter(unidade__dre=dre).filter(
            contas__tipo_conta__nome=tipo_conta).exclude(cnpj__exact='').order_by('unidade__tipo_unidade',
                                                                                  'unidade__nome')
        associacoes_da_dre = associacoes_da_dre.filter(
            prestacoes_de_conta_da_associacao__consolidado_dre=consolidado_dre)

    elif not apenas_nao_publicadas:
        associacoes_da_dre = Associacao.objects.filter(unidade__dre=dre).filter(
            contas__tipo_conta__nome=tipo_conta).exclude(cnpj__exact='').order_by('unidade__tipo_unidade',
                                                                                  'unidade__nome')
    else:
        associacoes_da_dre = Associacao.objects.filter(unidade__dre=dre).filter(
            contas__tipo_conta__nome=tipo_conta).exclude(cnpj__exact='').order_by('unidade__tipo_unidade',
                                                                                  'unidade__nome')
        associacoes_da_dre = associacoes_da_dre.filter(prestacoes_de_conta_da_associacao__periodo=periodo,
                                                       prestacoes_de_conta_da_associacao__publicada=False)

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

        if status_prestacao_conta == 'NAO_APRESENTADA':
            resultado_nao_apresentada.append(
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
        else:

            dado = {
                'unidade': {
                    'uuid': f'{associacao.unidade.uuid}',
                    'codigo_eol': associacao.unidade.codigo_eol,
                    'tipo_unidade': associacao.unidade.tipo_unidade,
                    'nome': associacao.unidade.nome,
                    'sigla': associacao.unidade.sigla,
                },

                'status_prestacao_contas': status_prestacao_conta,
                'valores': totais,
                'uuid_pc': prestacao_conta.uuid,
            }

            if status_prestacao_conta == "REPROVADA":
                dado["motivos_reprovacao"] = get_teste_motivos_reprovacao(prestacao_conta)
            elif status_prestacao_conta == "APROVADA_RESSALVA":
                dado["motivos_aprovada_ressalva"] = get_motivos_aprovacao_ressalva(prestacao_conta)
                dado["recomendacoes"] = prestacao_conta.recomendacoes

            resultado.append(dado)

    resultado = sorted(resultado, key=lambda row: row['status_prestacao_contas'])
    resultado.extend(resultado_nao_apresentada)

    return resultado


def informacoes_execucao_financeira_unidades_do_consolidado_dre(
    dre,
    periodo,
    apenas_nao_publicadas=False,
    eh_consolidado_de_publicacoes_parciais=False,
    consolidado_dre=None
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

        if consolidado_dre:
            # Quando é uma retificação, as informações são resgatadas filtrando pelo consolidado

            fechamentos = associacao.fechamentos_associacao.filter(
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
                prestacao_conta__consolidado_dre=consolidado_dre
            )

        elif not apenas_nao_publicadas:
            fechamentos = associacao.fechamentos_associacao.filter(
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
                prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA'],
            )
        else:
            fechamentos = associacao.fechamentos_associacao.filter(
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
                prestacao_conta__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA'],
                prestacao_conta__publicada=False
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

        if not apenas_nao_publicadas:
            previsoes = associacao.previsoes_de_repasse_sme_para_a_associacao.filter(
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
            )
        else:
            previsoes = associacao.previsoes_de_repasse_sme_para_a_associacao.filter(
                periodo=periodo,
                conta_associacao__tipo_conta=tipo_conta,
                associacao__prestacoes_de_conta_da_associacao__publicada=False,
            )

        for previsao in previsoes:
            totais['repasses_previstos_sme_custeio'] += previsao.valor_custeio
            totais['repasses_previstos_sme_capital'] += previsao.valor_capital
            totais['repasses_previstos_sme_livre'] += previsao.valor_livre
            totais['repasses_previstos_sme_total'] += previsao.valor_total

        return totais

    def _totaliza_devolucoes_ao_tesouro(prestacao_conta, periodo, totais, tipo_conta):
        # Devoluções ao tesouro de PCs de Associações da DRE, no período e concluídas
        devolucoes = prestacao_conta.devolucoes_ao_tesouro_da_prestacao.all()

        for devolucao in devolucoes:
            totais['devolucoes_ao_tesouro_no_periodo_total'] += devolucao.valor

        return totais

    resultado = []

    associacoes_da_dre = Associacao.objects.filter(unidade__dre=dre).exclude(cnpj__exact='').order_by('unidade__tipo_unidade', 'unidade__nome')

    if consolidado_dre:
        # Quando é uma retificação, as informações são resgatadas filtrando pelo consolidado

        associacoes_da_dre = associacoes_da_dre.filter(
            prestacoes_de_conta_da_associacao__periodo=periodo,
            prestacoes_de_conta_da_associacao__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']
        )

        associacoes_da_dre = associacoes_da_dre.filter(
            prestacoes_de_conta_da_associacao__consolidado_dre=consolidado_dre)

    elif not apenas_nao_publicadas:
        associacoes_da_dre = associacoes_da_dre.filter(
            prestacoes_de_conta_da_associacao__periodo=periodo,
            prestacoes_de_conta_da_associacao__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']
        )
    else:
        associacoes_da_dre = associacoes_da_dre.filter(
            prestacoes_de_conta_da_associacao__periodo=periodo,
            prestacoes_de_conta_da_associacao__publicada=False,
            prestacoes_de_conta_da_associacao__status__in=['APROVADA', 'APROVADA_RESSALVA', 'REPROVADA']
        )

    for associacao in associacoes_da_dre.all():

        prestacao_conta = associacao.prestacoes_de_conta_da_associacao.filter(periodo=periodo).first()

        status_prestacao_conta = prestacao_conta.status if prestacao_conta else 'NAO_APRESENTADA'

        referencia_consolidado = ""
        if(prestacao_conta.consolidado_dre.eh_parcial and prestacao_conta.consolidado_dre.consolidado_retificado_id):
            consolidado_origem_retificacao = ConsolidadoDRE.objects.filter(pk=prestacao_conta.consolidado_dre.consolidado_retificado_id)

            if(consolidado_origem_retificacao.count() > 0 and consolidado_origem_retificacao[0].data_publicacao):
                data_publicacao_consolidado_origem_retificacao = consolidado_origem_retificacao[0].data_publicacao.strftime("%d/%m/%Y")
                referencia_consolidado = f"Retificação da publicação de {data_publicacao_consolidado_origem_retificacao}"

        elif(not prestacao_conta.consolidado_dre.eh_parcial):
            referencia_consolidado = f"Única"

        else:
            referencia_consolidado = f"Parcial #{prestacao_conta.consolidado_dre.sequencia_de_publicacao}"

        dado = []
        objeto_tipo_de_conta = []

        for conta_associacao in associacao.contas.all():

            if not conta_associacao.conta_criada_no_periodo_ou_periodo_anteriores(periodo=periodo):
                continue

            totais = _totalizador_zerado()

            tipo_conta = conta_associacao.tipo_conta

            if prestacao_conta:
                totais = _totaliza_fechamentos(associacao, periodo, tipo_conta, totais)
                totais = _atualiza_demais_creditos(totais)
                totais = _totaliza_devolucoes_ao_tesouro(prestacao_conta, periodo, totais, tipo_conta)

            totais = _totaliza_previsoes_repasses_sme(associacao, periodo, tipo_conta, totais)

            dado = {
                'unidade': {
                    'uuid': f'{associacao.unidade.uuid}',
                    'codigo_eol': associacao.unidade.codigo_eol,
                    'tipo_unidade': associacao.unidade.tipo_unidade,
                    'nome': associacao.unidade.nome,
                    'sigla': associacao.unidade.sigla,
                },
                'status_prestacao_contas': status_prestacao_conta,
                'uuid_pc': prestacao_conta.uuid,
                'referencia_consolidado': referencia_consolidado,
            }

            data_encerramento = conta_associacao.conta_encerrada_em(periodo=periodo, adiciona_prefixo=False, origem_relatorio_consolidado=True) if conta_associacao.conta_encerrada_em(periodo=periodo, adiciona_prefixo=False, origem_relatorio_consolidado=True) else ''

            conta_encerrada_em_periodos_anteriores = conta_associacao.conta_encerrada_em_periodos_anteriores(periodo=periodo)

            if not conta_encerrada_em_periodos_anteriores:
                objeto_tipo_de_conta.append({
                    'tipo_conta': tipo_conta.nome if tipo_conta.nome else '',
                    'encerrada_em': data_encerramento,
                    'valores': totais,
                })

            dado['por_tipo_de_conta'] = objeto_tipo_de_conta

            if status_prestacao_conta == "REPROVADA":
                dado["motivos_reprovacao"] = get_teste_motivos_reprovacao(prestacao_conta)
            elif status_prestacao_conta == "APROVADA_RESSALVA":
                dado["motivos_aprovada_ressalva"] = get_motivos_aprovacao_ressalva(prestacao_conta)
                dado["recomendacoes"] = prestacao_conta.recomendacoes

        # Verificando se pelo menos um objeto do tipo dado foi criado, se sim existe o index status_prestacao_contas no dict dado
        _status_prestacao_contas = any('status_prestacao_contas' in d for d in dado)

        if _status_prestacao_contas:
            resultado.append(dado)
            # resultado = sorted(resultado, key=lambda row: row['status_prestacao_contas'])

    return resultado


def get_motivos_aprovacao_ressalva(prestacao_conta):
    lista_motivos_e_outros = []

    motivos = prestacao_conta.motivos_aprovacao_ressalva.values("motivo")
    for motivo in motivos:
        lista_motivos_e_outros.append(motivo["motivo"])

    outros_motivos = prestacao_conta.outros_motivos_aprovacao_ressalva
    if outros_motivos:
        lista_motivos_e_outros.append(outros_motivos)

    return lista_motivos_e_outros


def get_teste_motivos_reprovacao(prestacao_conta):
    lista_motivos_e_outros = []

    motivos = prestacao_conta.motivos_reprovacao.values("motivo")
    for motivo in motivos:
        lista_motivos_e_outros.append(motivo["motivo"])

    outros_motivos = prestacao_conta.outros_motivos_reprovacao
    if outros_motivos:
        lista_motivos_e_outros.append(outros_motivos)

    return lista_motivos_e_outros


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


def dashboard_sme(periodo, unificar_pcs_apresentadas_nao_recebidas = False):
    def add_card_dashboard(dashboard, status, quantidade):
        titulos_por_status = {
            PrestacaoConta.STATUS_NAO_APRESENTADA: "Prestações de contas não apresentadas",
            PrestacaoConta.STATUS_NAO_RECEBIDA: "Prestações de contas não recebidas",
            PrestacaoConta.STATUS_RECEBIDA: "Prestações de contas aguardando análise",
            PrestacaoConta.STATUS_EM_ANALISE: "Prestações de contas em análise",
            PrestacaoConta.STATUS_DEVOLVIDA: "Prestações de conta devolvidas para acertos",
            PrestacaoConta.STATUS_APROVADA: "Prestações de contas aprovadas",
            PrestacaoConta.STATUS_APROVADA_RESSALVA: "Prestações de contas aprovadas com ressalvas",
            PrestacaoConta.STATUS_REPROVADA: "Prestações de contas reprovadas",
            'TOTAL_UNIDADES': "Total de unidades educacionais",
        }
        dashboard.append(
            {
                "titulo": titulos_por_status[status],
                "quantidade_prestacoes": quantidade,
                "status": status
            }
        )

    qtd_status = PrestacaoConta.quantidade_por_status_sme(periodo_uuid=periodo.uuid, numero_bruto_nao_apresentadas=unificar_pcs_apresentadas_nao_recebidas)

    cards_dashboard = []

    add_card_dashboard(cards_dashboard, 'TOTAL_UNIDADES', qtd_status['TOTAL_UNIDADES'])

    if (
        qtd_status[PrestacaoConta.STATUS_NAO_RECEBIDA] > 0
        or qtd_status[PrestacaoConta.STATUS_RECEBIDA] > 0
        or qtd_status[PrestacaoConta.STATUS_EM_ANALISE] > 0
        or qtd_status[PrestacaoConta.STATUS_DEVOLVIDA] > 0
    ):

        if unificar_pcs_apresentadas_nao_recebidas:

            add_card_dashboard(
                cards_dashboard,
                PrestacaoConta.STATUS_NAO_APRESENTADA,
                qtd_status[PrestacaoConta.STATUS_NAO_APRESENTADA]
            )

            add_card_dashboard(
                cards_dashboard,
                PrestacaoConta.STATUS_NAO_RECEBIDA,
                qtd_status[PrestacaoConta.STATUS_NAO_RECEBIDA]
            )

        else:

            add_card_dashboard(
                cards_dashboard,
                PrestacaoConta.STATUS_NAO_RECEBIDA,
                qtd_status[PrestacaoConta.STATUS_NAO_RECEBIDA] + qtd_status[PrestacaoConta.STATUS_NAO_APRESENTADA]
            )

        add_card_dashboard(
            cards_dashboard,
            PrestacaoConta.STATUS_RECEBIDA,
            qtd_status[PrestacaoConta.STATUS_RECEBIDA]
        )

        add_card_dashboard(
            cards_dashboard,
            PrestacaoConta.STATUS_EM_ANALISE,
            qtd_status[PrestacaoConta.STATUS_EM_ANALISE]
        )

        add_card_dashboard(
            cards_dashboard,
            PrestacaoConta.STATUS_DEVOLVIDA,
            qtd_status[PrestacaoConta.STATUS_DEVOLVIDA]
        )

        status_periodo = {
            'status_txt': 'Período de análise das prestações de contas pelas DREs em andamento.',
            'cor_idx': 1,
            'status': 'EM_ANDAMENTO'
        }
    else:
        add_card_dashboard(
            cards_dashboard,
            PrestacaoConta.STATUS_NAO_APRESENTADA,
            qtd_status[PrestacaoConta.STATUS_NAO_APRESENTADA]
        )

        status_periodo = {
            'status_txt': 'Período de análise das prestações de contas pelas DREs concluído.',
            'cor_idx': 2,
            'status': 'CONCLUIDO'
        }

    add_card_dashboard(
        cards_dashboard,
        PrestacaoConta.STATUS_APROVADA,
        qtd_status[PrestacaoConta.STATUS_APROVADA]
    )

    add_card_dashboard(
        cards_dashboard,
        PrestacaoConta.STATUS_APROVADA_RESSALVA,
        qtd_status[PrestacaoConta.STATUS_APROVADA_RESSALVA]
    )

    add_card_dashboard(
        cards_dashboard,
        PrestacaoConta.STATUS_REPROVADA,
        qtd_status[PrestacaoConta.STATUS_REPROVADA]
    )

    resumo_por_dre = PrestacaoConta.quantidade_por_status_por_dre(periodo_uuid=periodo.uuid, numero_bruto_nao_apresentadas=unificar_pcs_apresentadas_nao_recebidas)

    dashboard = {
        "status": status_periodo,
        "cards": cards_dashboard,
        "resumo_por_dre": resumo_por_dre
    }

    return dashboard


def _criar_previa_demonstrativo_execucao_fisico_financeiro(dre, periodo, usuario, consolidado_dre, parcial,
                                                           apenas_nao_publicadas=False):
    logger.info("Prévia relatório consolidado em processamento...")

    relatorio_consolidado = _gerar_arquivos_demonstrativo_execucao_fisico_financeiro(
        dre=dre,
        periodo=periodo,
        parcial=parcial,
        usuario=usuario,
        previa=True,
        consolidado_dre=consolidado_dre,
        apenas_nao_publicadas=apenas_nao_publicadas,
    )

    logger.info("Prévia relatório Consolidado Gerado: uuid: %s, status: %s",
                relatorio_consolidado.uuid, relatorio_consolidado.status)


def _criar_demonstrativo_execucao_fisico_financeiro(
    dre,
    periodo,
    usuario,
    parcial,
    consolidado_dre=None,
    apenas_nao_publicadas=False,
    eh_consolidado_de_publicacoes_parciais=False,
):
    logger.info("Relatório consolidado em processamento...")

    relatorio_consolidado = _gerar_arquivos_demonstrativo_execucao_fisico_financeiro(
        dre=dre,
        periodo=periodo,
        usuario=usuario,
        parcial=parcial,
        consolidado_dre=consolidado_dre,
        previa=False,
        apenas_nao_publicadas=apenas_nao_publicadas,
        eh_consolidado_de_publicacoes_parciais=eh_consolidado_de_publicacoes_parciais

    )

    logger.info("Relatório Consolidado Gerado: uuid: %s, status: %s",
                relatorio_consolidado.uuid, relatorio_consolidado.status)


def _gerar_arquivos_demonstrativo_execucao_fisico_financeiro(
    dre,
    periodo,
    usuario,
    parcial,
    previa,
    consolidado_dre,
    apenas_nao_publicadas,
    eh_consolidado_de_publicacoes_parciais=False,
):
    logger.info(f'Criando registro do demonstrativo execução fisico financeiro')

    relatorio_consolidado, _ = RelatorioConsolidadoDRE.objects.update_or_create(
        dre=dre,
        periodo=periodo,
        tipo_conta=None,
        defaults={'status': RelatorioConsolidadoDRE.STATUS_EM_PROCESSAMENTO},
        consolidado_dre=consolidado_dre,
    )

    relatorio_consolidado.versao = RelatorioConsolidadoDRE.VERSAO_CONSOLIDADA if eh_consolidado_de_publicacoes_parciais else RelatorioConsolidadoDRE.VERSAO_PREVIA if previa else RelatorioConsolidadoDRE.VERSAO_FINAL
    relatorio_consolidado.save()

    logger.info(f'Gerando arquivos do demonstrativo financeiro em PDF')

    dados_demonstrativo = gerar_dados_demo_execucao_fisico_financeira(
        dre,
        periodo,
        usuario,
        parcial,
        previa,
        apenas_nao_publicadas,
        eh_consolidado_de_publicacoes_parciais,
        consolidado_dre,
    )

    gerar_arquivo_demonstrativo_execucao_fisico_financeiro_pdf(dados_demonstrativo, relatorio_consolidado)

    eh_parcial = parcial['parcial']

    relatorio_consolidado.status = (
        RelatorioConsolidadoDRE.STATUS_GERADO_PARCIAL if eh_parcial else RelatorioConsolidadoDRE.STATUS_GERADO_TOTAL)
    relatorio_consolidado.save()

    return relatorio_consolidado
