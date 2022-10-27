import pytest
from ...models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


def test_pode_devolver_consolidado(consolidado_dre_em_analise, parametros_dre_comissoes):
    assert consolidado_dre_em_analise.status_sme != ConsolidadoDRE.STATUS_SME_DEVOLVIDO
    consolidado = consolidado_dre_em_analise.devolver_consolidado()
    assert consolidado.status_sme == ConsolidadoDRE.STATUS_SME_DEVOLVIDO



