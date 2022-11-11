import pytest
from datetime import date
from ...models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


def test_pode_devolver_consolidado(consolidado_dre_em_analise, parametros_dre_comissoes):
    import ipdb; ipdb.set_trace();
    assert consolidado_dre_em_analise.status_sme != ConsolidadoDRE.STATUS_SME_DEVOLVIDO
    consolidado = consolidado_dre_em_analise.devolver_consolidado(data_limite=date(2022, 12, 30))
    assert consolidado.status_sme == ConsolidadoDRE.STATUS_SME_DEVOLVIDO
