from unittest.mock import MagicMock, patch

import pytest
from django.contrib.admin.sites import AdminSite

from sme_ptrf_apps.core import admin as core_admin
from sme_ptrf_apps.core.models import (
    Acao,
    Associacao,
    PrestacaoConta,
    AnaliseContaPrestacaoConta,
    Arquivo,
    DemonstrativoFinanceiro,
    RelacaoBens,
    SolicitacaoAcertoLancamento,
    TransferenciaEol,
    ValoresReprogramados,
    DevolucaoAoTesouro,
    ProcessoAssociacao,
)
from sme_ptrf_apps.dre.fixtures.factories.consolidado_dre_factory import ConsolidadoDREFactory

pytestmark = pytest.mark.django_db

site = AdminSite()


# AcaoAdmin.save_model
acao_admin = core_admin.AcaoAdmin(Acao, site)


def test_acao_admin_save_model_create_nao_verifica_exibir_paa():
    request = MagicMock()
    obj = MagicMock()
    form = MagicMock(cleaned_data={})

    with patch('sme_ptrf_apps.core.services.acoes_desabilitadas_paa.desabilitar_acao_ptrf_paa') as mock_desabilitar:
        acao_admin.save_model(request, obj, form, change=False)

    mock_desabilitar.assert_not_called()
    obj.save.assert_called_once()


def test_acao_admin_save_model_change_mantendo_exibir_paa_nao_desabilita():
    request = MagicMock()
    obj = MagicMock()
    form = MagicMock(cleaned_data={'exibir_paa': True})

    with patch('sme_ptrf_apps.core.services.acoes_desabilitadas_paa.desabilitar_acao_ptrf_paa') as mock_desabilitar:
        acao_admin.save_model(request, obj, form, change=True)

    mock_desabilitar.assert_not_called()
    obj.save.assert_called_once()


def test_acao_admin_save_model_desabilitando_exibir_paa_notifica_prioridades_e_receitas():
    request = MagicMock()
    obj = MagicMock()
    obj.nome = 'Ação Teste'

    prioridades_qs = MagicMock()
    prioridades_qs.values_list.return_value.distinct.return_value = ['Assoc 1', 'Assoc 2']
    prioridades_qs.count.return_value = 2
    obj.prioridades_paa_em_elaboracao_acao_ptrf.return_value = prioridades_qs

    receitas_qs = MagicMock()
    receitas_qs.values_list.return_value.distinct.return_value = ['Assoc 3']
    receitas_qs.count.return_value = 1
    obj.receitas_previstas_paa_em_elaboracao_acao_ptrf.return_value = receitas_qs

    form = MagicMock(cleaned_data={'exibir_paa': False})

    acao_admin.message_user = MagicMock()
    with patch('sme_ptrf_apps.core.services.acoes_desabilitadas_paa.desabilitar_acao_ptrf_paa') as mock_desabilitar:
        acao_admin.save_model(request, obj, form, change=True)

    mock_desabilitar.assert_called_once_with(obj)
    assert acao_admin.message_user.call_count == 2
    obj.save.assert_called_once()


def test_acao_admin_save_model_desabilitando_exibir_paa_sem_prioridades_nem_receitas():
    request = MagicMock()
    obj = MagicMock()

    prioridades_qs = MagicMock()
    prioridades_qs.values_list.return_value.distinct.return_value = []
    prioridades_qs.count.return_value = 0
    obj.prioridades_paa_em_elaboracao_acao_ptrf.return_value = prioridades_qs

    receitas_qs = MagicMock()
    receitas_qs.values_list.return_value.distinct.return_value = []
    receitas_qs.count.return_value = 0
    obj.receitas_previstas_paa_em_elaboracao_acao_ptrf.return_value = receitas_qs

    form = MagicMock(cleaned_data={'exibir_paa': False})

    acao_admin.message_user = MagicMock()
    with patch('sme_ptrf_apps.core.services.acoes_desabilitadas_paa.desabilitar_acao_ptrf_paa') as mock_desabilitar:
        acao_admin.save_model(request, obj, form, change=True)

    mock_desabilitar.assert_called_once_with(obj)
    acao_admin.message_user.assert_not_called()


# AssociacaoAdmin: define_status_nao_finalizado_valores_reprogramados
associacao_admin = core_admin.AssociacaoAdmin(Associacao, site)


def test_define_status_nao_finalizado_altera_quando_permite_implantacao(
    associacao_factory, periodo_inicial_associacao_factory, recurso_factory
):
    recurso = recurso_factory()
    assoc = associacao_factory()
    pia = periodo_inicial_associacao_factory(associacao=assoc, recurso=recurso)

    request = MagicMock()
    queryset = Associacao.objects.filter(pk=assoc.pk)

    with patch(
        'sme_ptrf_apps.core.admin.associacao_pode_implantar_saldo',
        return_value={'permite_implantacao': True},
    ):
        associacao_admin.message_user = MagicMock()
        associacao_admin.define_status_nao_finalizado_valores_reprogramados(request, queryset)

    pia.refresh_from_db()
    assert pia.status_valores_reprogramados == Associacao.STATUS_VALORES_REPROGRAMADOS_NAO_FINALIZADO
    associacao_admin.message_user.assert_called_once()


def test_define_status_nao_finalizado_nao_altera_quando_nao_permite_implantacao(
    associacao_factory, periodo_inicial_associacao_factory, recurso_factory
):
    recurso = recurso_factory()
    assoc = associacao_factory()
    periodo_inicial_associacao_factory(associacao=assoc, recurso=recurso)
    status_original = assoc.status_valores_reprogramados

    request = MagicMock()
    queryset = Associacao.objects.filter(pk=assoc.pk)

    with patch(
        'sme_ptrf_apps.core.admin.associacao_pode_implantar_saldo',
        return_value={'permite_implantacao': False},
    ):
        associacao_admin.message_user = MagicMock()
        associacao_admin.define_status_nao_finalizado_valores_reprogramados(request, queryset)

    assoc.refresh_from_db()
    assert assoc.status_valores_reprogramados == status_original


# AssociacaoAdmin: migrar_valores_reprogramados
def test_migrar_valores_reprogramados_cria_valores_custeio_capital_e_livre(
    associacao_factory, periodo_inicial_associacao_factory, conta_associacao_factory,
    tipo_conta_factory, acao_factory, acao_associacao_factory, recurso_factory, periodo_factory
):
    recurso = recurso_factory()
    periodo = periodo_factory()
    assoc = associacao_factory(periodo_inicial=periodo)
    periodo_inicial_associacao_factory(
        associacao=assoc,
        recurso=recurso,
        periodo_inicial=periodo,
        status_valores_reprogramados=Associacao.STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS,
    )
    tipo_conta = tipo_conta_factory(recurso=recurso)
    conta_associacao_factory(associacao=assoc, tipo_conta=tipo_conta)
    acao = acao_factory(recurso=recurso, aceita_custeio=True, aceita_capital=True, aceita_livre=True)
    acao_associacao_factory(associacao=assoc, acao=acao)

    request = MagicMock()
    queryset = Associacao.objects.filter(pk=assoc.pk)

    associacao_admin.message_user = MagicMock()
    associacao_admin.migrar_valores_reprogramados(request, queryset)

    valores = ValoresReprogramados.objects.filter(associacao=assoc)
    assert valores.count() == 3
    aplicacoes = set(valores.values_list('aplicacao_recurso', flat=True))
    assert aplicacoes == {'CUSTEIO', 'CAPITAL', 'LIVRE'}
    associacao_admin.message_user.assert_called_once()


def test_migrar_valores_reprogramados_ignora_periodo_nao_finalizado(
    associacao_factory, periodo_inicial_associacao_factory, conta_associacao_factory,
    tipo_conta_factory, acao_factory, acao_associacao_factory, recurso_factory
):
    recurso = recurso_factory()
    assoc = associacao_factory()
    periodo_inicial_associacao_factory(
        associacao=assoc,
        recurso=recurso,
        status_valores_reprogramados=Associacao.STATUS_VALORES_REPROGRAMADOS_NAO_FINALIZADO,
    )
    tipo_conta = tipo_conta_factory(recurso=recurso)
    conta_associacao_factory(associacao=assoc, tipo_conta=tipo_conta)
    acao = acao_factory(recurso=recurso, aceita_custeio=True)
    acao_associacao_factory(associacao=assoc, acao=acao)

    request = MagicMock()
    queryset = Associacao.objects.filter(pk=assoc.pk)

    associacao_admin.message_user = MagicMock()
    associacao_admin.migrar_valores_reprogramados(request, queryset)

    assert ValoresReprogramados.objects.filter(associacao=assoc).count() == 0


def test_migrar_valores_reprogramados_ignora_quando_ja_existe_valor_migrado(
    associacao_factory, periodo_inicial_associacao_factory, conta_associacao_factory,
    tipo_conta_factory, acao_factory, acao_associacao_factory, recurso_factory, periodo_factory
):
    recurso = recurso_factory()
    periodo = periodo_factory()
    assoc = associacao_factory(periodo_inicial=periodo)
    periodo_inicial_associacao_factory(
        associacao=assoc,
        recurso=recurso,
        periodo_inicial=periodo,
        status_valores_reprogramados=Associacao.STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS,
    )
    tipo_conta = tipo_conta_factory(recurso=recurso)
    conta_associacao = conta_associacao_factory(associacao=assoc, tipo_conta=tipo_conta)
    acao = acao_factory(recurso=recurso, aceita_custeio=True)
    acao_associacao = acao_associacao_factory(associacao=assoc, acao=acao)

    ValoresReprogramados.criar_valor_reprogramado_custeio(assoc, conta_associacao, acao_associacao, None)

    request = MagicMock()
    queryset = Associacao.objects.filter(pk=assoc.pk)

    associacao_admin.message_user = MagicMock()
    associacao_admin.migrar_valores_reprogramados(request, queryset)

    assert ValoresReprogramados.objects.filter(associacao=assoc).count() == 1


# ProcessoAssociacaoAdmin.periodos_str
processo_associacao_admin = core_admin.ProcessoAssociacaoAdmin(ProcessoAssociacao, site)


def test_processo_associacao_admin_periodos_str(processo_associacao_factory, periodo_factory):
    periodo_1 = periodo_factory(referencia='2024.1')
    periodo_2 = periodo_factory(referencia='2024.2')
    processo = processo_associacao_factory()
    processo.periodos.add(periodo_1, periodo_2)

    assert processo_associacao_admin.periodos_str(processo) == '2024.1, 2024.2'


# PrestacaoContaAdmin: actions
prestacao_conta_admin_actions = core_admin.PrestacaoContaAdmin(PrestacaoConta, site)


def test_desvincular_pcs_do_consolidado(prestacao_conta_factory):
    consolidado = ConsolidadoDREFactory()
    pc = prestacao_conta_factory(consolidado_dre=consolidado, publicada=False)

    request = MagicMock()
    queryset = PrestacaoConta.objects.filter(pk=pc.pk)

    prestacao_conta_admin_actions.message_user = MagicMock()
    prestacao_conta_admin_actions.desvincular_pcs_do_consolidado(request, queryset)

    pc.refresh_from_db()
    assert pc.consolidado_dre is None
    prestacao_conta_admin_actions.message_user.assert_called_once_with(request, '1 PC(s) desvinculada(s)')


def test_desvincular_pcs_do_consolidado_nao_desvincula_publicada(prestacao_conta_factory):
    consolidado = ConsolidadoDREFactory()
    pc = prestacao_conta_factory(consolidado_dre=consolidado, publicada=True)

    request = MagicMock()
    queryset = PrestacaoConta.objects.filter(pk=pc.pk)

    prestacao_conta_admin_actions.message_user = MagicMock()
    prestacao_conta_admin_actions.desvincular_pcs_do_consolidado(request, queryset)

    pc.refresh_from_db()
    assert pc.consolidado_dre_id == consolidado.pk


def test_marcar_como_nao_publicada(prestacao_conta_factory):
    pc = prestacao_conta_factory(publicada=True, consolidado_dre=None)

    request = MagicMock()
    queryset = PrestacaoConta.objects.filter(pk=pc.pk)

    prestacao_conta_admin_actions.message_user = MagicMock()
    prestacao_conta_admin_actions.marcar_como_nao_publicada(request, queryset)

    pc.refresh_from_db()
    assert pc.publicada is False


def test_setar_status_anterior_a_retificacao(prestacao_conta_factory):
    pc = prestacao_conta_factory(
        status=PrestacaoConta.STATUS_DEVOLVIDA,
        status_anterior_a_retificacao=PrestacaoConta.STATUS_APROVADA,
    )

    request = MagicMock()
    queryset = PrestacaoConta.objects.filter(pk=pc.pk)

    prestacao_conta_admin_actions.message_user = MagicMock()
    prestacao_conta_admin_actions.setar_status_anterior_a_retificacao(request, queryset)

    pc.refresh_from_db()
    assert pc.status == PrestacaoConta.STATUS_APROVADA


# AnaliseContaPrestacaoContaAdmin: vincula_analise_prestacao_contas
analise_conta_prestacao_conta_admin_actions = core_admin.AnaliseContaPrestacaoContaAdmin(
    AnaliseContaPrestacaoConta, site)


def test_vincula_analise_prestacao_contas(
    analise_conta_prestacao_conta_factory, analise_prestacao_conta_factory, prestacao_conta_factory
):
    pc = prestacao_conta_factory()
    analise_pc = analise_prestacao_conta_factory(prestacao_conta=pc)
    analise_conta = analise_conta_prestacao_conta_factory(prestacao_conta=pc, analise_prestacao_conta=None)

    request = MagicMock()
    queryset = AnaliseContaPrestacaoConta.objects.filter(pk=analise_conta.pk)

    analise_conta_prestacao_conta_admin_actions.message_user = MagicMock()
    analise_conta_prestacao_conta_admin_actions.vincula_analise_prestacao_contas(request, queryset)

    analise_conta.refresh_from_db()
    assert analise_conta.analise_prestacao_conta_id == analise_pc.pk
    analise_conta_prestacao_conta_admin_actions.message_user.assert_called_once_with(
        request, 'Vinculação Concluída.')


def test_vincula_analise_prestacao_contas_nao_altera_quando_ja_vinculada(
    analise_conta_prestacao_conta_factory, analise_prestacao_conta_factory, prestacao_conta_factory
):
    pc = prestacao_conta_factory()
    analise_pc = analise_prestacao_conta_factory(prestacao_conta=pc)
    analise_conta = analise_conta_prestacao_conta_factory(prestacao_conta=pc, analise_prestacao_conta=analise_pc)

    request = MagicMock()
    queryset = AnaliseContaPrestacaoConta.objects.filter(pk=analise_conta.pk)

    analise_conta_prestacao_conta_admin_actions.message_user = MagicMock()
    analise_conta_prestacao_conta_admin_actions.vincula_analise_prestacao_contas(request, queryset)

    analise_conta.refresh_from_db()
    assert analise_conta.analise_prestacao_conta_id == analise_pc.pk


# ArquivoAdmin.processa_carga
arquivo_admin = core_admin.ArquivoAdmin(Arquivo, site)


def test_arquivo_admin_processa_carga():
    request = MagicMock()
    queryset = MagicMock()

    arquivo_admin.message_user = MagicMock()
    with patch('sme_ptrf_apps.core.admin.processa_cargas') as mock_processa:
        arquivo_admin.processa_carga(request, queryset)

    mock_processa.assert_called_once_with(queryset)
    arquivo_admin.message_user.assert_called_once_with(
        request, 'Processo Terminado. Verifique o status do processo.')


# DemonstrativoFinanceiroAdmin: gerar_pdf_dados_persistidos / regerar_pdf
demonstrativo_financeiro_admin_actions = core_admin.DemonstrativoFinanceiroAdmin(DemonstrativoFinanceiro, site)


def test_gerar_pdf_dados_persistidos_gera_quando_ha_dados():
    item_mock = MagicMock()
    item_mock.dados.exists.return_value = True

    request = MagicMock()
    queryset = [item_mock]

    with patch(
        'sme_ptrf_apps.core.services.recuperacao_dados_persistindos_demo_financeiro_service.RecuperaDadosDemoFinanceiro'
    ) as mock_recupera, patch(
        'sme_ptrf_apps.core.services.demonstrativo_financeiro_pdf_service.gerar_arquivo_demonstrativo_financeiro_pdf'
    ) as mock_gerar_pdf:
        mock_recupera.return_value.dados_formatados = {'algum': 'dado'}
        demonstrativo_financeiro_admin_actions.gerar_pdf_dados_persistidos(request, queryset)

    mock_gerar_pdf.assert_called_once_with({'algum': 'dado'}, item_mock)


def test_gerar_pdf_dados_persistidos_nao_gera_sem_dados():
    item_mock = MagicMock()
    item_mock.dados.exists.return_value = False

    request = MagicMock()
    queryset = [item_mock]

    with patch(
        'sme_ptrf_apps.core.services.demonstrativo_financeiro_pdf_service.gerar_arquivo_demonstrativo_financeiro_pdf'
    ) as mock_gerar_pdf:
        demonstrativo_financeiro_admin_actions.gerar_pdf_dados_persistidos(request, queryset)

    mock_gerar_pdf.assert_not_called()


def test_regerar_pdf_usuario_existe():
    from django.contrib.auth import get_user_model

    request = MagicMock()
    queryset = MagicMock()

    demonstrativo_financeiro_admin_actions.message_user = MagicMock()
    with patch.object(get_user_model().objects, 'get', return_value=MagicMock()), \
            patch('sme_ptrf_apps.core.admin.regerar_demonstrativo_financeiro_async') as mock_task:
        demonstrativo_financeiro_admin_actions.regerar_pdf(request, queryset)

    mock_task.apply_async.assert_called_once()
    demonstrativo_financeiro_admin_actions.message_user.assert_called_once()


def test_regerar_pdf_usuario_nao_existe():
    from django.contrib.auth import get_user_model

    request = MagicMock()
    queryset = MagicMock()

    demonstrativo_financeiro_admin_actions.message_user = MagicMock()
    with patch.object(get_user_model().objects, 'get', side_effect=get_user_model().DoesNotExist), \
            patch('sme_ptrf_apps.core.admin.regerar_demonstrativo_financeiro_async') as mock_task:
        demonstrativo_financeiro_admin_actions.regerar_pdf(request, queryset)

    mock_task.apply_async.assert_called_once()
    demonstrativo_financeiro_admin_actions.message_user.assert_called_once()


# RelacaoBensAdmin.gerar_pdf
relacao_bens_admin_actions = core_admin.RelacaoBensAdmin(RelacaoBens, site)


def test_relacao_bens_admin_gerar_pdf(
    relacao_bens_factory, tipo_conta_factory, conta_associacao_factory, recurso_factory
):
    recurso = recurso_factory(nome='PTRF', nome_exibicao='PTRF Exibição')
    tipo_conta = tipo_conta_factory(recurso=recurso)
    conta_associacao = conta_associacao_factory(tipo_conta=tipo_conta)
    item = relacao_bens_factory(conta_associacao=conta_associacao)

    request = MagicMock()
    queryset = RelacaoBens.objects.filter(pk=item.pk)

    with patch(
        'sme_ptrf_apps.core.services.relacao_bens.gerar_arquivo_relacao_de_bens_dados_persistidos'
    ) as mock_gerar:
        relacao_bens_admin_actions.gerar_pdf(request, queryset)

    mock_gerar.assert_called_once_with(item, 'PTRF', 'PTRF Exibição')


# SolicitacaoAcertoLancamentoAdmin.buscar_e_vincular_devolucao_ao_tesouro
solicitacao_acerto_lancamento_admin_actions = core_admin.SolicitacaoAcertoLancamentoAdmin(
    SolicitacaoAcertoLancamento, site)


def test_buscar_e_vincular_devolucao_ao_tesouro_vincula(
    solicitacao_acerto_lancamento_factory, analise_lancamento_prestacao_conta_factory,
    tipo_acerto_lancamento_factory, tipo_devolucao_ao_tesouro_factory, prestacao_conta_factory, despesa_factory
):
    pc = prestacao_conta_factory()
    despesa = despesa_factory()
    from sme_ptrf_apps.core.fixtures.factories import AnalisePrestacaoContaFactory
    analise_prestacao_conta = AnalisePrestacaoContaFactory(prestacao_conta=pc)
    analise_lancamento = analise_lancamento_prestacao_conta_factory(
        analise_prestacao_conta=analise_prestacao_conta, despesa=despesa)
    tipo_acerto = tipo_acerto_lancamento_factory(categoria='DEVOLUCAO')
    solicitacao = solicitacao_acerto_lancamento_factory(
        analise_lancamento=analise_lancamento, tipo_acerto=tipo_acerto, devolucao_ao_tesouro=None,
        detalhamento='obs')

    devolucao = DevolucaoAoTesouro.objects.create(
        prestacao_conta=pc, tipo=tipo_devolucao_ao_tesouro_factory(), despesa=despesa)

    request = MagicMock()
    queryset = SolicitacaoAcertoLancamento.objects.filter(pk=solicitacao.pk)

    solicitacao_acerto_lancamento_admin_actions.message_user = MagicMock()
    solicitacao_acerto_lancamento_admin_actions.buscar_e_vincular_devolucao_ao_tesouro(request, queryset)

    solicitacao.refresh_from_db()
    assert solicitacao.devolucao_ao_tesouro_id == devolucao.pk
    assert '(**vinculada a dvt)' in solicitacao.detalhamento
    solicitacao_acerto_lancamento_admin_actions.message_user.assert_called_once_with(
        request, 'Processo realizado com sucesso!')


def test_buscar_e_vincular_devolucao_ao_tesouro_ignora_quando_categoria_diferente(
    solicitacao_acerto_lancamento_factory, tipo_acerto_lancamento_factory
):
    tipo_acerto = tipo_acerto_lancamento_factory(categoria='ACERTO')
    solicitacao = solicitacao_acerto_lancamento_factory(tipo_acerto=tipo_acerto, devolucao_ao_tesouro=None)

    request = MagicMock()
    queryset = SolicitacaoAcertoLancamento.objects.filter(pk=solicitacao.pk)

    solicitacao_acerto_lancamento_admin_actions.message_user = MagicMock()
    solicitacao_acerto_lancamento_admin_actions.buscar_e_vincular_devolucao_ao_tesouro(request, queryset)

    solicitacao.refresh_from_db()
    assert solicitacao.devolucao_ao_tesouro is None


# TransferenciaEolAdmin.transfere_codigo_eol
transferencia_eol_admin = core_admin.TransferenciaEolAdmin(TransferenciaEol, site)


def test_transferencia_eol_admin_transfere_codigo_eol():
    transferencia_mock = MagicMock()
    request = MagicMock()
    queryset = MagicMock()
    queryset.all.return_value = [transferencia_mock]

    transferencia_eol_admin.message_user = MagicMock()
    transferencia_eol_admin.transfere_codigo_eol(request, queryset)

    transferencia_mock.transferir.assert_called_once()
    transferencia_eol_admin.message_user.assert_called_once_with(request, 'Transferência concluida.')
