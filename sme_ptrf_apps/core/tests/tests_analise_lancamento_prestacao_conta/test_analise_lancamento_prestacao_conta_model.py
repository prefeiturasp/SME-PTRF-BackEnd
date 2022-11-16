import pytest
from django.contrib import admin

from ...models import AnalisePrestacaoConta, AnaliseLancamentoPrestacaoConta

pytestmark = pytest.mark.django_db


def test_instance_model(analise_lancamento_receita_prestacao_conta_2020_1):
    model = analise_lancamento_receita_prestacao_conta_2020_1
    assert isinstance(model, AnaliseLancamentoPrestacaoConta)
    assert isinstance(model.analise_prestacao_conta, AnalisePrestacaoConta)
    assert model.tipo_lancamento == AnaliseLancamentoPrestacaoConta.TIPO_LANCAMENTO_CREDITO
    assert model.receita is not None
    assert model.despesa is None
    assert model.resultado == AnaliseLancamentoPrestacaoConta.RESULTADO_CORRETO
    assert model.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE


def test_srt_model(analise_lancamento_receita_prestacao_conta_2020_1):
    assert analise_lancamento_receita_prestacao_conta_2020_1.__str__() == f'2020.1 - 2020-01-01 a 2020-06-30 - Análise #{analise_lancamento_receita_prestacao_conta_2020_1.analise_prestacao_conta.id} - Resultado:CORRETO'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[AnaliseLancamentoPrestacaoConta]


def test_audit_log(analise_lancamento_receita_prestacao_conta_2020_1):
    assert analise_lancamento_receita_prestacao_conta_2020_1.history.count() == 1  # Um log de inclusão
    assert analise_lancamento_receita_prestacao_conta_2020_1.history.latest().action == 0  # 0-Inclusão

    analise_lancamento_receita_prestacao_conta_2020_1.resultado = "AJUSTE"
    analise_lancamento_receita_prestacao_conta_2020_1.save()
    assert analise_lancamento_receita_prestacao_conta_2020_1.history.count() == 2  # Um log de inclusão e outro de edição
    assert analise_lancamento_receita_prestacao_conta_2020_1.history.latest().action == 1  # 1-Edição

