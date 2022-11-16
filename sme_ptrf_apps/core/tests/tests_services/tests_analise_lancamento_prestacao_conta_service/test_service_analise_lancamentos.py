import pytest

from sme_ptrf_apps.core.services import AnaliseLancamentoPrestacaoContaService

pytestmark = pytest.mark.django_db


def test_marcar_devolucao_tesouro_atualizada(
    analise_lancamento_despesa_prestacao_conta_2020_1,
    tipo_acerto_lancamento_devolucao,
    devolucao_ao_tesouro_parcial,
    solicitacao_acerto_lancamento_devolucao
):
    assert not analise_lancamento_despesa_prestacao_conta_2020_1.devolucao_tesouro_atualizada

    result = AnaliseLancamentoPrestacaoContaService.marcar_devolucao_tesouro_como_atualizada(
        analise_lancamento_despesa_prestacao_conta_2020_1
    )

    assert result.devolucao_tesouro_atualizada


def test_marcar_lancamento_atualizado(
    analise_lancamento_despesa_prestacao_conta_2020_1,
    tipo_acerto_edicao_de_lancamento,
    solicitacao_acerto_edicao_lancamento
):
    assert not analise_lancamento_despesa_prestacao_conta_2020_1.lancamento_atualizado

    result = AnaliseLancamentoPrestacaoContaService.marcar_lancamento_como_atualizado(
        analise_lancamento_despesa_prestacao_conta_2020_1
    )

    assert result.lancamento_atualizado


def test_marcar_lancamento_excluido(
    analise_lancamento_despesa_prestacao_conta_2020_1,
    tipo_acerto_exclusao_de_lancamento,
    solicitacao_acerto_exclusao_lancamento
):
    assert not analise_lancamento_despesa_prestacao_conta_2020_1.lancamento_excluido

    result = AnaliseLancamentoPrestacaoContaService.marcar_lancamento_como_excluido(
        analise_lancamento_despesa_prestacao_conta_2020_1
    )

    assert result.lancamento_excluido

