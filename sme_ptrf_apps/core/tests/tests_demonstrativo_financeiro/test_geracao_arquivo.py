import pytest
from sme_ptrf_apps.core.services.demonstrativo_financeiro import gerar

pytestmark = pytest.mark.django_db


def test_gerar_arquivo(periodo, acao_associacao, conta_associacao, rateio_despesa_demonstrativo, rateio_despesa_demonstrativo2, prestacao_conta):
    assert gerar(periodo, acao_associacao, conta_associacao, prestacao_conta)


