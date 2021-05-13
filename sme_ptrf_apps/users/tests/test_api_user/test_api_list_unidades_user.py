import pytest

pytestmark = pytest.mark.django_db


def test_list_unidades_e_permissoes_na_visao(
        jwt_authenticated_client_u2,
        usuario_2,
        visao_ue,
        visao_dre,
        visao_sme,
        permissao1,
        permissao2,
        grupo_1,
        grupo_2,
        grupo_3,
        unidade,
        unidade_diferente
):
    visao = "UE"
    url = f"/api/usuarios/{usuario_2.id}/unidades-e-permissoes-na-visao/{visao}/?unidade_logada_uuid={unidade_diferente.uuid}"
    response = jwt_authenticated_client_u2.get(url, content_type='application/json')
    result = response.json()
    esperado = [
        {
            'uuid': f'{unidade_diferente.uuid}',
            'nome': unidade_diferente.nome,
            'codigo_eol': unidade_diferente.codigo_eol,
            'tipo_unidade': unidade_diferente.tipo_unidade,
            'pode_excluir': True
        }
    ]

    assert result == esperado
