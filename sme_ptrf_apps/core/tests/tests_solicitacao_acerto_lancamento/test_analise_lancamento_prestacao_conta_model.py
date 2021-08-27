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
