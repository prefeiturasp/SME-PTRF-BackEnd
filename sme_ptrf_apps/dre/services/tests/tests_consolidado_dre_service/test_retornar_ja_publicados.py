
import pytest

from sme_ptrf_apps.dre.services.consolidado_dre_service import retornar_ja_publicadas

pytestmark = pytest.mark.django_db


def test_retorna_ja_publicados_publicados_no_diario_oficial(
    jwt_authenticated_client_dre,
    consolidado_dre_publicado_no_diario_oficial
):
    result = retornar_ja_publicadas(consolidado_dre_publicado_no_diario_oficial.dre, consolidado_dre_publicado_no_diario_oficial.periodo)

    assert len(result) == 1
    assert result[0]['status_sme'] == 'PUBLICADO'
    assert result[0]['exibe_botao_retificar'] is True


def test_retorna_ja_publicados_nao_publicados_no_diario_oficial(
    jwt_authenticated_client_dre,
    consolidado_dre_nao_publicado_no_diario_oficial
):
    result = retornar_ja_publicadas(consolidado_dre_nao_publicado_no_diario_oficial.dre, consolidado_dre_nao_publicado_no_diario_oficial.periodo)

    assert len(result) == 1
    assert result[0]['status_sme'] == 'NAO_PUBLICADO'
    assert result[0]['exibe_botao_retificar'] is False


def test_retorna_ja_publicados_nao_publicados_no_diario_oficial_com_retificacao(
    jwt_authenticated_client_dre,
    consolidado_dre_publicado_no_diario_oficial,
    retificacao_dre
):
    result = retornar_ja_publicadas(consolidado_dre_publicado_no_diario_oficial.dre, consolidado_dre_publicado_no_diario_oficial.periodo)
    lista_ordenada = sorted(result, key=lambda item: item['eh_retificacao'])

    assert len(lista_ordenada) == 2
    assert lista_ordenada[0]['status_sme'] == 'PUBLICADO'
    assert lista_ordenada[1]['status_sme'] == 'NAO_PUBLICADO'
    assert lista_ordenada[0]['exibe_botao_retificar'] is True
    assert lista_ordenada[1]['exibe_botao_retificar'] is False

