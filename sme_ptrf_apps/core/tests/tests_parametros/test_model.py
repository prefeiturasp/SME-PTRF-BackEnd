import pytest

from ...models import Parametros

pytestmark = pytest.mark.django_db


def test_parametros_model(parametros):
    assert isinstance(parametros, Parametros)
    assert parametros.permite_saldo_conta_negativo
    assert parametros.fique_de_olho == ''
    assert parametros.tempo_notificar_nao_demonstrados == 0
    assert parametros.fique_de_olho_relatorio_dre == ''
    assert parametros.dias_antes_inicio_periodo_pc_para_notificacao == 5

