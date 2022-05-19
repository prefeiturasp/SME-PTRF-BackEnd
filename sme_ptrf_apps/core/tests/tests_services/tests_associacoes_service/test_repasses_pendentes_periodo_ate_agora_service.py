import pytest

from sme_ptrf_apps.core.services.associacoes_service import retorna_repasses_pendentes_periodos_ate_agora

pytestmark = pytest.mark.django_db


def test_retorna_repasses_pendentes_periodos_ate_agora(jwt_authenticated_client_a, associacao, periodo, repasse):
    result = retorna_repasses_pendentes_periodos_ate_agora(associacao=associacao, periodo=periodo)
    assert len(result) == 1
    assert result[0]['repasse_periodo'] == repasse.periodo.referencia
    assert result[0]['repasse_acao'] == repasse.acao_associacao.acao.nome
    assert float(result[0]['repasse_total']) == round(repasse.valor_capital + repasse.valor_custeio + repasse.valor_livre, 2)
