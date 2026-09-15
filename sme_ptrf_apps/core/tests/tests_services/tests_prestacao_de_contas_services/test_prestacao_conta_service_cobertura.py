import uuid
from datetime import date
from unittest.mock import Mock, PropertyMock, patch

import pytest
from waffle.testutils import override_flag

from sme_ptrf_apps.core.models import AnalisePrestacaoConta, TaskCelery
from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta
from sme_ptrf_apps.core.services.prestacao_conta_service import PrestacaoContaService

pytestmark = pytest.mark.django_db

MODULE = 'sme_ptrf_apps.core.services.prestacao_conta_service'


def _servico(associacao, periodo, logger=None, username=""):
    return PrestacaoContaService(
        associacao_uuid=associacao.uuid,
        periodo_uuid=periodo.uuid,
        username=username,
        logger=logger or Mock(),
    )


# __init__

def test_init_periodo_nao_encontrado(associacao):
    with pytest.raises(Exception, match='não encontrado'):
        PrestacaoContaService(
            associacao_uuid=associacao.uuid,
            periodo_uuid=uuid.uuid4(),
            logger=Mock(),
        )


def test_init_associacao_nao_encontrada(periodo_2020_1):
    with pytest.raises(Exception, match='não encontrada'):
        PrestacaoContaService(
            associacao_uuid=uuid.uuid4(),
            periodo_uuid=periodo_2020_1.uuid,
            logger=Mock(),
        )


def test_init_sem_logger_valido(associacao, periodo_2020_1):
    with pytest.raises(Exception, match='ContextualLogger'):
        PrestacaoContaService(
            associacao_uuid=associacao.uuid,
            periodo_uuid=periodo_2020_1.uuid,
            logger=None,
        )


def test_init_com_username_define_usuario(associacao, periodo_2020_1, django_user_model):
    usuario = django_user_model.objects.create_user(username='7654321', password='Sgp0418')

    servico = _servico(associacao, periodo_2020_1, username='7654321')

    assert servico.usuario == usuario


# properties simples

def test_properties_basicas(associacao, periodo_2020_1):
    servico = _servico(associacao, periodo_2020_1)

    assert servico.periodo == periodo_2020_1
    assert servico.associacao == associacao
    assert servico.usuario is None
    assert list(servico.acoes) == list(associacao.acoes.filter(status='ATIVA'))
    assert servico.contas is None
    assert servico.prestacao is None


# propriedades dependentes de devolução/análise

def test_propriedades_devolucao_quando_nao_e_devolucao(
    associacao, periodo_2020_1, prestacao_conta_factory,
):
    prestacao_conta_factory(associacao=associacao, periodo=periodo_2020_1, data_recebimento=None)
    servico = _servico(associacao, periodo_2020_1)

    assert servico.e_retorno_devolucao is False
    assert servico.pc_e_devolucao_com_solicitacoes_mudanca is False
    assert servico.pc_e_devolucao_com_solicitacoes_mudanca_realizadas is False
    assert servico.pc_e_devolucao_com_solicitacao_acerto_em_extrato is False
    assert servico.requer_criar_fechamentos is True
    assert servico.requer_gerar_documentos is True
    assert servico.requer_apagar_fechamentos is False
    assert servico.requer_apagar_documentos is False
    assert servico.analise_atual_id == 0


def test_propriedades_devolucao_sem_analise(
    associacao, periodo_2020_1, prestacao_conta_factory,
):
    prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1, data_recebimento=date(2020, 7, 2),
    )
    servico = _servico(associacao, periodo_2020_1)

    assert servico.e_retorno_devolucao is True
    assert servico.pc_e_devolucao_com_solicitacoes_mudanca is False
    assert servico.requer_criar_fechamentos is False
    assert servico.requer_gerar_documentos is False


def test_propriedades_devolucao_com_analise_requer_alteracao(
    associacao, periodo_2020_1, prestacao_conta_factory, analise_prestacao_conta_factory,
):
    pc = prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1, data_recebimento=date(2020, 7, 2),
    )
    analise_prestacao_conta_factory(prestacao_conta=pc)

    with patch.object(
        AnalisePrestacaoConta, 'verifica_se_requer_alteracao_em_lancamentos', return_value=True,
    ), patch.object(
        AnalisePrestacaoConta, 'acertos_em_extrato_requer_gerar_documentos', new_callable=PropertyMock,
    ) as mock_acerto_extrato:
        mock_acerto_extrato.return_value = False

        servico = _servico(associacao, periodo_2020_1)

        assert servico.pc_e_devolucao_com_solicitacoes_mudanca is True
        assert servico.pc_e_devolucao_com_solicitacoes_mudanca_realizadas is True
        assert servico.requer_apagar_fechamentos is True
        assert servico.requer_criar_fechamentos is True
        assert servico.requer_apagar_documentos is True
        assert servico.requer_gerar_documentos is True
        assert servico.analise_atual_id > 0


def test_propriedades_devolucao_com_analise_acerto_extrato(
    associacao, periodo_2020_1, prestacao_conta_factory, analise_prestacao_conta_factory,
):
    pc = prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1, data_recebimento=date(2020, 7, 2),
    )
    analise_prestacao_conta_factory(prestacao_conta=pc)

    with patch.object(
        AnalisePrestacaoConta, 'verifica_se_requer_alteracao_em_lancamentos', return_value=False,
    ), patch.object(
        AnalisePrestacaoConta, 'acertos_em_extrato_requer_gerar_documentos', new_callable=PropertyMock,
    ) as mock_acerto_extrato:
        mock_acerto_extrato.return_value = True

        servico = _servico(associacao, periodo_2020_1)

        assert servico.pc_e_devolucao_com_solicitacao_acerto_em_extrato is True
        assert servico.requer_apagar_documentos is True
        assert servico.requer_gerar_documentos is True
        assert servico.requer_apagar_fechamentos is False
        assert servico.requer_criar_fechamentos is False


# from_prestacao_conta_uuid

def test_from_prestacao_conta_uuid_nao_encontrada():
    with pytest.raises(Exception, match='não encontrada'):
        PrestacaoContaService.from_prestacao_conta_uuid(uuid.uuid4(), logger=Mock())


def test_from_prestacao_conta_uuid_encontrada(associacao, periodo_2020_1, prestacao_conta_factory):
    pc = prestacao_conta_factory(associacao=associacao, periodo=periodo_2020_1)

    servico = PrestacaoContaService.from_prestacao_conta_uuid(pc.uuid, logger=Mock())

    assert servico.prestacao.id == pc.id
    assert servico.associacao == associacao
    assert servico.periodo == periodo_2020_1


# _set_pc — ramo de criação (nenhuma PC existente ainda)

def test_set_pc_cria_pc_quando_nao_existe(associacao, periodo_2020_1):
    assert not PrestacaoConta.objects.filter(associacao=associacao, periodo=periodo_2020_1).exists()

    servico = _servico(associacao, periodo_2020_1)
    servico._set_pc()

    pc = PrestacaoConta.objects.get(associacao=associacao, periodo=periodo_2020_1)
    assert servico.prestacao.id == pc.id
    assert pc.status == PrestacaoConta.STATUS_A_PROCESSAR


# _reabrir_prestacao_de_contas

def test_reabrir_prestacao_de_contas(associacao, periodo_2020_1, prestacao_conta_factory):
    pc = prestacao_conta_factory(associacao=associacao, periodo=periodo_2020_1)
    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    resultado = servico._reabrir_prestacao_de_contas()

    assert resultado is True
    assert not PrestacaoConta.objects.filter(pk=pc.pk).exists()


# set_despesa_anterior_ao_uso_do_sistema_pc_concluida

def test_set_despesa_anterior_ao_uso_do_sistema_pc_concluida(
    associacao, periodo_2020_1, despesa_factory,
):
    despesa = despesa_factory(
        associacao=associacao,
        despesa_anterior_ao_uso_do_sistema=True,
        despesa_anterior_ao_uso_do_sistema_pc_concluida=False,
    )

    servico = _servico(associacao, periodo_2020_1)
    with override_flag('ajustes-despesas-anteriores', active=True):
        servico.set_despesa_anterior_ao_uso_do_sistema_pc_concluida()

    despesa.refresh_from_db()
    assert despesa.despesa_anterior_ao_uso_do_sistema_pc_concluida is True


# atualiza_justificativa_conciliacao_original

def test_atualiza_justificativa_conciliacao_original(
    associacao, periodo_2020_1, prestacao_conta_factory, conta_associacao_factory,
):
    conta = conta_associacao_factory(associacao=associacao)
    pc = prestacao_conta_factory(associacao=associacao, periodo=periodo_2020_1)

    from sme_ptrf_apps.core.models import ObservacaoConciliacao
    observacao = ObservacaoConciliacao.objects.create(
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta,
        texto='Texto atual',
        justificativa_original='',
    )

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc
    servico._contas = [conta]
    servico.atualiza_justificativa_conciliacao_original()

    observacao.refresh_from_db()
    assert observacao.justificativa_original == 'Texto atual'


def test_atualiza_justificativa_conciliacao_original_sem_observacao(
    associacao, periodo_2020_1, conta_associacao_factory,
):
    conta = conta_associacao_factory(associacao=associacao)

    servico = _servico(associacao, periodo_2020_1)
    servico._contas = [conta]

    # não deve levantar exceção quando não há observação de conciliação
    servico.atualiza_justificativa_conciliacao_original()


# validar_geracao_pc_periodo_anterior

def test_validar_geracao_pc_periodo_anterior_true_quando_ja_existe_pc_do_periodo_anterior(
    associacao, periodo_2020_1, prestacao_conta_factory,
):
    prestacao_conta_factory(associacao=associacao, periodo=periodo_2020_1.periodo_anterior)

    servico = _servico(associacao, periodo_2020_1)

    with patch.object(associacao.__class__, 'primeiro_periodo_ativo_por_recurso', return_value=None):
        assert servico.validar_geracao_pc_periodo_anterior() is True


def test_validar_geracao_pc_periodo_anterior_false_quando_nao_existe_pc_do_periodo_anterior(
    associacao, periodo_2020_1,
):
    servico = _servico(associacao, periodo_2020_1)

    with patch.object(associacao.__class__, 'primeiro_periodo_ativo_por_recurso', return_value=None):
        assert servico.validar_geracao_pc_periodo_anterior() is False


def test_validar_geracao_pc_periodo_anterior_true_quando_e_primeiro_periodo_ativo(
    associacao, periodo_2020_1,
):
    servico = _servico(associacao, periodo_2020_1)

    with patch.object(associacao.__class__, 'primeiro_periodo_ativo_por_recurso', return_value=periodo_2020_1):
        assert servico.validar_geracao_pc_periodo_anterior() is True


# resolve_registros_falha

def test_resolve_registros_falha(associacao, periodo_2020_1):
    servico = _servico(associacao, periodo_2020_1)

    with patch('sme_ptrf_apps.core.services.FalhaGeracaoPcService') as mock_service:
        servico.resolve_registros_falha()

    mock_service.return_value.marcar_como_resolvido.assert_called_once()


# apagar_previas_documentos

def test_apagar_previas_documentos(associacao, periodo_2020_1, conta_associacao_factory):
    conta = conta_associacao_factory(associacao=associacao)
    servico = _servico(associacao, periodo_2020_1)
    servico._contas = [conta]

    with patch('sme_ptrf_apps.core.services.relacao_bens.apagar_previas_relacao_de_bens') as mock_apagar:
        servico.apagar_previas_documentos()

    mock_apagar.assert_called_once_with(periodo=periodo_2020_1, conta_associacao=conta)


# _persiste_dados_demonstrativo_financeiro / _persiste_dados_relacao_de_bens / persiste_dados_docs

def test_persiste_dados_demonstrativo_financeiro(
    associacao, periodo_2020_1, prestacao_conta_factory, conta_associacao_factory,
):
    conta = conta_associacao_factory(associacao=associacao)
    pc = prestacao_conta_factory(associacao=associacao, periodo=periodo_2020_1)

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    with patch(f'{MODULE}.gerar_dados_demonstrativo_financeiro', return_value={'a': 1}) as mock_gerar, \
            patch(f'{MODULE}.PersistenciaDadosDemoFinanceiro') as mock_persistencia:
        demonstrativo = servico._persiste_dados_demonstrativo_financeiro(conta_associacao=conta)

    mock_gerar.assert_called_once()
    mock_persistencia.assert_called_once()
    assert demonstrativo.conta_associacao == conta
    assert demonstrativo.prestacao_conta == pc


def test_persiste_dados_relacao_de_bens_com_compras_de_capital(
    associacao, periodo_2020_1, conta_associacao_factory,
):
    conta = conta_associacao_factory(associacao=associacao)
    servico = _servico(associacao, periodo_2020_1)

    mock_qs = Mock()
    mock_qs.exists.return_value = True

    with patch(f'{MODULE}.RateioDespesa.rateios_da_conta_associacao_no_periodo', return_value=mock_qs), \
            patch(f'{MODULE}._persistir_arquivo_relacao_de_bens', return_value='relacao-bens') as mock_persistir:
        resultado = servico._persiste_dados_relacao_de_bens(conta_associacao=conta)

    mock_persistir.assert_called_once()
    assert resultado == 'relacao-bens'


def test_persiste_dados_relacao_de_bens_sem_compras_de_capital(
    associacao, periodo_2020_1, conta_associacao_factory,
):
    conta = conta_associacao_factory(associacao=associacao)
    servico = _servico(associacao, periodo_2020_1)

    mock_qs = Mock()
    mock_qs.exists.return_value = False

    with patch(f'{MODULE}.RateioDespesa.rateios_da_conta_associacao_no_periodo', return_value=mock_qs):
        resultado = servico._persiste_dados_relacao_de_bens(conta_associacao=conta)

    assert resultado is None


def test_persiste_dados_docs(
    associacao, periodo_2020_1, prestacao_conta_factory, conta_associacao_factory,
):
    conta = conta_associacao_factory(associacao=associacao)
    pc = prestacao_conta_factory(associacao=associacao, periodo=periodo_2020_1)

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc
    servico._contas = [conta]

    with patch.object(servico, '_persiste_dados_demonstrativo_financeiro') as mock_demo, \
            patch.object(servico, '_persiste_dados_relacao_de_bens') as mock_bens:
        servico.persiste_dados_docs()

    mock_demo.assert_called_once_with(conta_associacao=conta)
    mock_bens.assert_called_once_with(conta_associacao=conta)


# criar_fechamentos

def test_criar_fechamentos(
    associacao, periodo_2020_1, prestacao_conta_factory, conta_associacao_factory, acao_associacao,
):
    conta = conta_associacao_factory(associacao=associacao)
    pc = prestacao_conta_factory(associacao=associacao, periodo=periodo_2020_1)

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc
    servico._contas = [conta]
    servico._acoes = associacao.acoes.filter(status='ATIVA')

    totais_receitas = {
        'total_receitas_capital': 0, 'total_receitas_devolucao_capital': 0, 'total_repasses_capital': 0,
        'total_receitas_custeio': 0, 'total_receitas_devolucao_custeio': 0, 'total_receitas_devolucao_livre': 0,
        'total_repasses_custeio': 0, 'total_receitas_livre': 0, 'total_repasses_livre': 0,
        'total_receitas_nao_conciliadas_capital': 0, 'total_receitas_nao_conciliadas_custeio': 0,
        'total_receitas_nao_conciliadas_livre': 0,
    }
    totais_despesas = {
        'total_despesas_capital': 0, 'total_despesas_custeio': 0,
        'total_despesas_nao_conciliadas_capital': 0, 'total_despesas_nao_conciliadas_custeio': 0,
    }

    with patch(f'{MODULE}.Receita.totais_por_acao_associacao_no_periodo', return_value=totais_receitas), \
            patch(f'{MODULE}.RateioDespesa.totais_por_acao_associacao_no_periodo', return_value=totais_despesas), \
            patch(f'{MODULE}.RateioDespesa.especificacoes_dos_rateios_da_acao_associacao_no_periodo',
                  return_value=[]), \
            patch(f'{MODULE}.FechamentoPeriodo.criar') as mock_criar:
        servico.criar_fechamentos()

    mock_criar.assert_called_once()
    assert mock_criar.call_args.kwargs['prestacao_conta'] == pc
    assert mock_criar.call_args.kwargs['conta_associacao'] == conta


# contas_com_saldo_alterado_sem_solicitacao — ramos adicionais

def test_contas_com_saldo_alterado_sem_solicitacao_sem_fechamento_e_sem_movimento(
    associacao, periodo_2020_1, prestacao_conta_factory, conta_associacao_factory, analise_prestacao_conta_factory,
):
    conta_associacao_factory(associacao=associacao, data_inicio=date(2019, 1, 1))
    pc = prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1,
        status=PrestacaoConta.STATUS_DEVOLVIDA, data_recebimento=periodo_2020_1.data_inicio_realizacao_despesas,
    )
    analise_prestacao_conta_factory(status='DEVOLVIDA', prestacao_conta=pc)

    servico = _servico(associacao, periodo_2020_1)

    mock_resumo = Mock()
    mock_resumo.saldo_posterior = None

    with patch(
        'sme_ptrf_apps.core.services.resumo_rescursos_service.ResumoRecursosService.resumo_recursos',
        return_value=mock_resumo,
    ), \
            patch.object(AnalisePrestacaoConta, 'requer_acertos_em_saldo_na_conta_associacao', return_value=False):
        resultado = servico.contas_com_saldo_alterado_sem_solicitacao()

    # A validação real está desativada (HISTÓRIA #134189), sempre retorna [].
    assert resultado == []


def test_persiste_dados_demonstrativo_financeiro_erro_ao_buscar_observacao_conciliacao(
    associacao, periodo_2020_1, prestacao_conta_factory, conta_associacao_factory,
):
    conta = conta_associacao_factory(associacao=associacao)
    pc = prestacao_conta_factory(associacao=associacao, periodo=periodo_2020_1)

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    with patch(f'{MODULE}.ObservacaoConciliacao.objects.filter', side_effect=Exception('erro de banco')), \
            patch(f'{MODULE}.gerar_dados_demonstrativo_financeiro', return_value={'a': 1}), \
            patch(f'{MODULE}.PersistenciaDadosDemoFinanceiro'):
        # não deve levantar exceção - o erro na busca da observação é silenciado
        servico._persiste_dados_demonstrativo_financeiro(conta_associacao=conta)


# _revoke_tasks_by_id

def test_revoke_tasks_by_id(associacao, periodo_2020_1, prestacao_conta_factory):
    pc = prestacao_conta_factory(associacao=associacao, periodo=periodo_2020_1)
    task = TaskCelery.objects.create(
        nome_task='concluir_prestacao_de_contas_async',
        associacao=associacao,
        periodo=periodo_2020_1,
        prestacao_conta=pc,
        finalizada=False,
        id_task_assincrona='abc-123',
    )

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    with patch.object(servico.app.control, 'revoke') as mock_revoke:
        servico._revoke_tasks_by_id()

    mock_revoke.assert_called_once_with(task_id='abc-123', terminate=True)
    task.refresh_from_db()
    assert task.finalizada is True


def test_revoke_tasks_by_id_sem_tasks_ativas(associacao, periodo_2020_1, prestacao_conta_factory):
    pc = prestacao_conta_factory(associacao=associacao, periodo=periodo_2020_1)
    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    with patch.object(servico.app.control, 'revoke') as mock_revoke:
        servico._revoke_tasks_by_id()

    mock_revoke.assert_not_called()


# trata_falha_processo_pc

def test_trata_falha_processo_pc_com_analise_requer_alteracao(
    associacao, periodo_2020_1, prestacao_conta_factory, analise_prestacao_conta_factory,
):
    pc = prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1, status=PrestacaoConta.STATUS_EM_PROCESSAMENTO,
    )
    analise_prestacao_conta_factory(prestacao_conta=pc)

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    with patch('sme_ptrf_apps.core.services.FalhaGeracaoPcService') as mock_falha_service, \
            patch.object(servico, '_revoke_tasks_by_id'), \
            patch.object(PrestacaoConta, 'apaga_fechamentos') as mock_apaga_fechamentos, \
            patch.object(
                AnalisePrestacaoConta, 'verifica_se_requer_alteracao_em_lancamentos', return_value=True,):
        servico.trata_falha_processo_pc()

    mock_falha_service.return_value.registra_falha_geracao_pc.assert_called_once()
    pc.refresh_from_db()
    assert pc.status == PrestacaoConta.STATUS_DEVOLVIDA
    mock_apaga_fechamentos.assert_called_once()


def test_trata_falha_processo_pc_com_analise_sem_requerer_alteracao(
    associacao, periodo_2020_1, prestacao_conta_factory, analise_prestacao_conta_factory,
):
    pc = prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1, status=PrestacaoConta.STATUS_EM_PROCESSAMENTO,
    )
    analise_prestacao_conta_factory(prestacao_conta=pc)

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    with patch('sme_ptrf_apps.core.services.FalhaGeracaoPcService'), \
            patch.object(servico, '_revoke_tasks_by_id'), \
            patch.object(PrestacaoConta, 'apaga_fechamentos') as mock_apaga_fechamentos, \
            patch.object(
                AnalisePrestacaoConta, 'verifica_se_requer_alteracao_em_lancamentos', return_value=False,
    ):
        servico.trata_falha_processo_pc()

    mock_apaga_fechamentos.assert_not_called()


def test_trata_falha_processo_pc_sem_analise_reabre_com_sucesso(
    associacao, periodo_2020_1, prestacao_conta_factory,
):
    pc = prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1, status=PrestacaoConta.STATUS_EM_PROCESSAMENTO,
    )

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    with patch('sme_ptrf_apps.core.services.FalhaGeracaoPcService'), \
            patch.object(servico, '_revoke_tasks_by_id'), \
            patch.object(servico, '_reabrir_prestacao_de_contas', return_value=True) as mock_reabrir:
        servico.trata_falha_processo_pc()

    mock_reabrir.assert_called_once()


def test_trata_falha_processo_pc_sem_analise_falha_ao_reabrir(
    associacao, periodo_2020_1, prestacao_conta_factory,
):
    pc = prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1, status=PrestacaoConta.STATUS_EM_PROCESSAMENTO,
    )

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    with patch('sme_ptrf_apps.core.services.FalhaGeracaoPcService'), \
            patch.object(servico, '_revoke_tasks_by_id'), \
            patch.object(servico, '_reabrir_prestacao_de_contas', return_value=False) as mock_reabrir:
        servico.trata_falha_processo_pc()

    mock_reabrir.assert_called_once()


def test_trata_falha_processo_pc_captura_excecao(
    associacao, periodo_2020_1, prestacao_conta_factory,
):
    pc = prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1, status=PrestacaoConta.STATUS_EM_PROCESSAMENTO,
    )

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    with patch('sme_ptrf_apps.core.services.FalhaGeracaoPcService', side_effect=Exception('erro inesperado')):
        # não deve propagar a exceção
        servico.trata_falha_processo_pc()


# terminar_processo_pc

def test_terminar_processo_pc_sem_prestacao_levanta_excecao(associacao, periodo_2020_1):
    servico = _servico(associacao, periodo_2020_1)

    with pytest.raises(Exception, match='Não existe PC'):
        servico.terminar_processo_pc()


def test_terminar_processo_pc_com_sucesso(
    associacao, periodo_2020_1, prestacao_conta_factory, conta_associacao_factory,
):
    conta = conta_associacao_factory(associacao=associacao)
    pc = prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1, status=PrestacaoConta.STATUS_CALCULADA,
    )

    from sme_ptrf_apps.core.models import DemonstrativoFinanceiro
    DemonstrativoFinanceiro.objects.create(
        prestacao_conta=pc,
        conta_associacao=conta,
        status=DemonstrativoFinanceiro.STATUS_CONCLUIDO,
    )

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    with patch.object(servico, 'resolve_registros_falha') as mock_resolve, \
            patch.object(servico, 'trata_falha_processo_pc') as mock_trata_falha:
        servico.terminar_processo_pc()

    pc.refresh_from_db()
    assert pc.status == PrestacaoConta.STATUS_NAO_RECEBIDA
    mock_resolve.assert_called_once()
    mock_trata_falha.assert_not_called()


def test_terminar_processo_pc_sucesso_retorno_devolucao(
    associacao, periodo_2020_1, prestacao_conta_factory, conta_associacao_factory,
):
    conta = conta_associacao_factory(associacao=associacao)
    pc = prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1, status=PrestacaoConta.STATUS_DEVOLVIDA_CALCULADA,
        data_recebimento=periodo_2020_1.data_inicio_realizacao_despesas,
    )

    from sme_ptrf_apps.core.models import DemonstrativoFinanceiro, RelacaoBens
    DemonstrativoFinanceiro.objects.create(
        prestacao_conta=pc,
        conta_associacao=conta,
        status=DemonstrativoFinanceiro.STATUS_CONCLUIDO,
    )
    RelacaoBens.objects.create(
        prestacao_conta=pc,
        conta_associacao=conta,
        status=RelacaoBens.STATUS_CONCLUIDO,
    )

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    with patch.object(servico, 'resolve_registros_falha'), \
            patch.object(servico, 'trata_falha_processo_pc') as mock_trata_falha:
        servico.terminar_processo_pc()

    pc.refresh_from_db()
    assert pc.status == PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA
    mock_trata_falha.assert_not_called()


def test_terminar_processo_pc_falha_demonstrativo_nao_concluido(
    associacao, periodo_2020_1, prestacao_conta_factory, conta_associacao_factory,
):
    conta = conta_associacao_factory(associacao=associacao)
    pc = prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1, status=PrestacaoConta.STATUS_CALCULADA,
    )

    from sme_ptrf_apps.core.models import DemonstrativoFinanceiro
    DemonstrativoFinanceiro.objects.create(
        prestacao_conta=pc,
        conta_associacao=conta,
        status=DemonstrativoFinanceiro.STATUS_EM_PROCESSAMENTO,
    )

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    with patch.object(servico, 'trata_falha_processo_pc') as mock_trata_falha:
        servico.terminar_processo_pc()

    mock_trata_falha.assert_called_once()


def test_terminar_processo_pc_falha_relatorio_bens_nao_concluido(
    associacao, periodo_2020_1, prestacao_conta_factory, conta_associacao_factory,
):
    conta = conta_associacao_factory(associacao=associacao)
    pc = prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1, status=PrestacaoConta.STATUS_CALCULADA,
    )

    from sme_ptrf_apps.core.models import DemonstrativoFinanceiro, RelacaoBens
    DemonstrativoFinanceiro.objects.create(
        prestacao_conta=pc,
        conta_associacao=conta,
        status=DemonstrativoFinanceiro.STATUS_CONCLUIDO,
    )
    RelacaoBens.objects.create(
        prestacao_conta=pc,
        conta_associacao=conta,
        status=RelacaoBens.STATUS_EM_PROCESSAMENTO,
    )

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    with patch.object(servico, 'trata_falha_processo_pc') as mock_trata_falha:
        servico.terminar_processo_pc()

    mock_trata_falha.assert_called_once()


def test_terminar_processo_pc_falha_calculo_nao_concluido(
    associacao, periodo_2020_1, prestacao_conta_factory,
):
    pc = prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1, status=PrestacaoConta.STATUS_EM_PROCESSAMENTO,
    )

    servico = _servico(associacao, periodo_2020_1)
    servico._prestacao = pc

    with patch.object(servico, 'trata_falha_processo_pc') as mock_trata_falha:
        servico.terminar_processo_pc()

    mock_trata_falha.assert_called_once()


# iniciar_tasks_de_conclusao_de_pc

def test_iniciar_tasks_de_conclusao_de_pc(
    associacao, periodo_2020_1, django_user_model,
):
    usuario = django_user_model.objects.create_user(username='9998887', password='Sgp0418')
    servico = _servico(associacao, periodo_2020_1)

    resultado = servico.iniciar_tasks_de_conclusao_de_pc(usuario, justificativa_acertos_pendentes='')

    assert resultado.id == servico.prestacao.id
    assert TaskCelery.objects.filter(nome_task='calcular_prestacao_de_contas_async').exists()
    assert TaskCelery.objects.filter(nome_task='gerar_demonstrativo_financeiro_async').exists()
    assert TaskCelery.objects.filter(nome_task='gerar_relacao_bens_async').exists()
    assert TaskCelery.objects.filter(nome_task='terminar_processo_pc_async').exists()
    assert not TaskCelery.objects.filter(nome_task='gerar_relatorio_apos_acertos_v2_async').exists()


def test_iniciar_tasks_de_conclusao_de_pc_retorno_devolucao(
    associacao, periodo_2020_1, prestacao_conta_factory, django_user_model,
):
    prestacao_conta_factory(
        associacao=associacao, periodo=periodo_2020_1, status=PrestacaoConta.STATUS_DEVOLVIDA,
        data_recebimento=periodo_2020_1.data_inicio_realizacao_despesas,
    )
    usuario = django_user_model.objects.create_user(username='9998886', password='Sgp0418')
    servico = _servico(associacao, periodo_2020_1)

    servico.iniciar_tasks_de_conclusao_de_pc(usuario, justificativa_acertos_pendentes='')

    assert TaskCelery.objects.filter(nome_task='gerar_relatorio_apos_acertos_v2_async').exists()
