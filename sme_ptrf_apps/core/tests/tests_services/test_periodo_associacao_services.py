import pytest
from freezegun import freeze_time

from ...services import status_periodo_associacao
from ...status_periodo_associacao import (STATUS_PERIODO_ASSOCIACAO_EM_ANDAMENTO, STATUS_PERIODO_ASSOCIACAO_PENDENTE)

pytestmark = pytest.mark.django_db


def test_status_periodo_em_andamento(associacao, periodo_fim_em_aberto):
    status = status_periodo_associacao(associacao_uuid=associacao.uuid, periodo_uuid=periodo_fim_em_aberto.uuid)
    status_esperado = STATUS_PERIODO_ASSOCIACAO_EM_ANDAMENTO
    assert status == status_esperado


@freeze_time('2020-07-10 10:20:00')
def test_status_periodo_pentente(associacao, periodo_fim_em_2020_06_30):
    status = status_periodo_associacao(associacao_uuid=associacao.uuid, periodo_uuid=periodo_fim_em_2020_06_30.uuid)
    status_esperado = STATUS_PERIODO_ASSOCIACAO_PENDENTE
    assert status == status_esperado


@freeze_time('2020-12-1 10:00:00')
def test_status_periodo_nao_conciliado(associacao, periodo_2020_1, prestacao_conta_2020_1_nao_conciliada):
    status = status_periodo_associacao(associacao_uuid=associacao.uuid, periodo_uuid=periodo_2020_1.uuid)
    status_esperado = STATUS_PERIODO_ASSOCIACAO_PENDENTE
    assert status == status_esperado, 'períodos com prestações não conciliadas devem ter status pendente.'


@freeze_time('2020-12-1 10:00:00')
def test_status_periodo_nao_conciliado_integralmente(associacao, periodo_2020_1, prestacao_conta_2020_1_nao_conciliada,
                                                     prestacao_conta_2020_1_conciliada):
    status = status_periodo_associacao(associacao_uuid=associacao.uuid, periodo_uuid=periodo_2020_1.uuid)
    status_esperado = STATUS_PERIODO_ASSOCIACAO_PENDENTE
    assert status == status_esperado, 'períodos com ao menos uma prestação não conciliada devem ter status pendente.'
