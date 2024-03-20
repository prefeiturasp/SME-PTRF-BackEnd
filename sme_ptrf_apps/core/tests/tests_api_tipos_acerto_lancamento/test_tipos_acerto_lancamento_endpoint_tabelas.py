import pytest
from rest_framework import status
from sme_ptrf_apps.core.models.tipo_acerto_lancamento import TipoAcertoLancamento
pytestmark = pytest.mark.django_db


def test_api_tabelas(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(f'/api/tipos-acerto-lancamento/tabelas/', content_type='application/json')
    assert response.status_code == status.HTTP_200_OK


def test_api_tabelas_com_filtro_aplicavel_despesas_periodos_anteriores(jwt_authenticated_client_a, tipo_acerto_lancamento_factory):
    tipo_acerto_lancamento_factory(
        categoria=TipoAcertoLancamento.CATEGORIA_CONCILIACAO_LANCAMENTO)
    tipo_acerto_lancamento_factory(
        categoria=TipoAcertoLancamento.CATEGORIA_DESCONCILIACAO_LANCAMENTO)

    response = jwt_authenticated_client_a.get(
        f'/api/tipos-acerto-lancamento/tabelas/?aplicavel_despesas_periodos_anteriores=true', content_type='application/json')

    assert len(response.json()['agrupado_por_categorias']) == 2
    assert response.status_code == status.HTTP_200_OK
