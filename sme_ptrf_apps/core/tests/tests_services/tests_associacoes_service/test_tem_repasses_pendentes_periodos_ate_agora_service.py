import pytest

from sme_ptrf_apps.core.services.associacoes_service import tem_repasses_pendentes_periodos_ate_agora

pytestmark = pytest.mark.django_db


def test_tem_repasses_pendentes_periodos_ate_agora_quando_tem(jwt_authenticated_client_a, associacao, periodo, repasse):

    result = tem_repasses_pendentes_periodos_ate_agora(associacao=associacao, periodo=periodo)

    assert result, "Deveria retornar True"


def test_tem_repasses_pendentes_periodos_ate_agora_quando_nao_tem(jwt_authenticated_client_a, associacao, periodo):

    result = tem_repasses_pendentes_periodos_ate_agora(associacao=associacao, periodo=periodo)

    assert not result, "Deveria retornar False"
