import pytest

from sme_ptrf_apps.receitas.services.carga_repasses_realizados import get_conta_associacao as get_conta_realizado
from sme_ptrf_apps.receitas.services.carga_repasses_previstos import get_conta_associacao as get_conta_previstos

pytestmark = pytest.mark.django_db


def test_criacao_conta_associacao_na_carga_repasses_realizados_com_valor_default(tipo_conta, associacao):
    conta = get_conta_realizado(tipo_conta, associacao)

    assert conta.banco_nome == "Banco do Inter"
    assert conta.agencia == '67945'
    assert conta.numero_conta == '935556-x'
    assert conta.numero_cartao == '987644164221'


def test_criacao_conta_associacao_na_carga_repasses_previstos_com_valor_default(tipo_conta, associacao):
    conta = get_conta_previstos(tipo_conta, associacao)

    assert conta.banco_nome == "Banco do Inter"
    assert conta.agencia == '67945'
    assert conta.numero_conta == '935556-x'
    assert conta.numero_cartao == '987644164221'
