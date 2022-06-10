import pytest
from django.contrib import admin

from ...models import (
    AnaliseLancamentoPrestacaoConta,
    SolicitacaoAcertoLancamento,
    TipoAcertoLancamento,
    DevolucaoAoTesouro
)

pytestmark = pytest.mark.django_db


def test_instance_model(solicitacao_acerto_lancamento_devolucao):
    model = solicitacao_acerto_lancamento_devolucao
    assert isinstance(model, SolicitacaoAcertoLancamento)
    assert isinstance(model.analise_lancamento, AnaliseLancamentoPrestacaoConta)
    assert isinstance(model.tipo_acerto, TipoAcertoLancamento)
    assert isinstance(model.devolucao_ao_tesouro, DevolucaoAoTesouro)
    assert model.detalhamento


def test_srt_model(solicitacao_acerto_lancamento_devolucao):
    assert solicitacao_acerto_lancamento_devolucao.__str__() == 'Devolução - teste'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[SolicitacaoAcertoLancamento]


def test_audit_log(solicitacao_acerto_lancamento_devolucao):
    assert solicitacao_acerto_lancamento_devolucao.history.count() == 1  # Um log de inclusão
    assert solicitacao_acerto_lancamento_devolucao.history.latest().action == 0  # 0-Inclusão

    solicitacao_acerto_lancamento_devolucao.detalhamento = "TESTE"
    solicitacao_acerto_lancamento_devolucao.save()
    assert solicitacao_acerto_lancamento_devolucao.history.count() == 2  # Um log de inclusão e outro de edição
    assert solicitacao_acerto_lancamento_devolucao.history.latest().action == 1  # 1-Edição

