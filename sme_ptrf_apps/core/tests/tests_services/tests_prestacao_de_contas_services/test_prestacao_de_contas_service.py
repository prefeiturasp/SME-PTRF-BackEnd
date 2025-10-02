import pytest
from datetime import date
from unittest.mock import patch, Mock
from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta
from sme_ptrf_apps.core.services.prestacao_conta_service import PrestacaoContaService
pytestmark = pytest.mark.django_db


# [HISTÓRIA #134189] DESCONSIDERA VALIDAÇÃO TEMPORARIAMENTE DEVIDO A INSCONSISTÊNCIAS NO FLUXO DE ANÁLISE DRE
def test_contas_com_saldo_alterado_sem_solicitacao(
    associacao_factory,
    periodo_factory,
    prestacao_conta_factory,
    analise_prestacao_conta_factory,
    conta_associacao_factory,
    despesa_factory,
    rateio_despesa_factory
):

    associacao = associacao_factory()
    periodo_2024_1 = periodo_factory(
        data_inicio_realizacao_despesas=date(2024, 1, 1),
        data_fim_realizacao_despesas=date(2024, 6, 1),
        referencia='2024.1',
    )
    conta_associacao = conta_associacao_factory(associacao=associacao, data_inicio=date(2019, 2, 2))
    pc = prestacao_conta_factory(
        associacao=associacao,
        periodo=periodo_2024_1,
        status=PrestacaoConta.STATUS_DEVOLVIDA,
        data_recebimento=periodo_2024_1.data_inicio_realizacao_despesas
    )
    analise_prestacao_conta_factory(status='DEVOLVIDA', prestacao_conta=pc)
    despesa = despesa_factory(data_transacao=periodo_2024_1.data_inicio_realizacao_despesas,
                              valor_total=100, associacao=associacao)
    rateio_despesa_factory(
        conta_associacao=conta_associacao,
        despesa=despesa,
        associacao=associacao,
        valor_rateio=100,
        conferido=False,
        update_conferido=False,
        aplicacao_recurso='CUSTEIO'
    )

    fake_logger = Mock()

    with patch(
        "sme_ptrf_apps.logging.loggers.ContextualLogger.get_logger",
        return_value=fake_logger,
    ):

        pc_service = PrestacaoContaService(
            associacao_uuid=associacao.uuid,
            periodo_uuid=periodo_2024_1.uuid,
            logger=fake_logger
        )
        # assert pc_service.contas_com_saldo_alterado_sem_solicitacao() == [conta_associacao]
        assert pc_service.contas_com_saldo_alterado_sem_solicitacao() == []
