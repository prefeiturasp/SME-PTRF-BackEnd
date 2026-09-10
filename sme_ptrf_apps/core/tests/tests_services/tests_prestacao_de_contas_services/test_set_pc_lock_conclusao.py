from unittest.mock import Mock

import pytest

from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta
from sme_ptrf_apps.core.services.prestacao_conta_service import PrestacaoContaService

pytestmark = pytest.mark.django_db


def _servico(associacao, periodo, logger):
    return PrestacaoContaService(
        associacao_uuid=associacao.uuid,
        periodo_uuid=periodo.uuid,
        logger=logger,
    )


def test_set_pc_marca_a_processar_quando_pc_esta_devolvida(
    associacao_factory,
    periodo_factory,
    prestacao_conta_factory,
):
    associacao = associacao_factory()
    periodo = periodo_factory(referencia='2026.1')
    pc = prestacao_conta_factory(
        associacao=associacao,
        periodo=periodo,
        status=PrestacaoConta.STATUS_DEVOLVIDA,
    )
    logger = Mock()

    servico = _servico(associacao, periodo, logger)
    servico._set_pc()

    pc.refresh_from_db()
    assert pc.status == PrestacaoConta.STATUS_A_PROCESSAR
    assert servico.e_retorno_devolucao is True
    assert servico.prestacao.id == pc.id


def test_set_pc_bloqueia_segunda_chamada_na_mesma_pc(
    associacao_factory,
    periodo_factory,
    prestacao_conta_factory,
):
    associacao = associacao_factory()
    periodo = periodo_factory(referencia='2026.1')
    prestacao_conta_factory(
        associacao=associacao,
        periodo=periodo,
        status=PrestacaoConta.STATUS_DEVOLVIDA,
    )
    logger = Mock()

    primeiro = _servico(associacao, periodo, logger)
    primeiro._set_pc()

    segundo = _servico(associacao, periodo, logger)
    with pytest.raises(Exception, match='já está em processamento'):
        segundo._set_pc()

    assert PrestacaoConta.objects.filter(associacao=associacao, periodo=periodo).count() == 1
    pc = PrestacaoConta.objects.get(associacao=associacao, periodo=periodo)
    assert pc.status == PrestacaoConta.STATUS_A_PROCESSAR


@pytest.mark.parametrize('status_bloqueado', [
    PrestacaoConta.STATUS_A_PROCESSAR,
    PrestacaoConta.STATUS_EM_PROCESSAMENTO,
    PrestacaoConta.STATUS_CALCULADA,
    PrestacaoConta.STATUS_DEVOLVIDA_CALCULADA,
])
def test_set_pc_bloqueia_pc_ja_em_andamento(
    associacao_factory,
    periodo_factory,
    prestacao_conta_factory,
    status_bloqueado,
):
    associacao = associacao_factory()
    periodo = periodo_factory(referencia='2026.1')
    prestacao_conta_factory(
        associacao=associacao,
        periodo=periodo,
        status=status_bloqueado,
    )
    logger = Mock()

    servico = _servico(associacao, periodo, logger)
    with pytest.raises(Exception, match='já está em processamento'):
        servico._set_pc()

    pc = PrestacaoConta.objects.get(associacao=associacao, periodo=periodo)
    assert pc.status == status_bloqueado
