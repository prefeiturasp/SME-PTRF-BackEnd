import pytest

pytestmark = pytest.mark.django_db


def test_consulta_visoes(
        jwt_authenticated_client_u2,
        usuario_2,
        visao_ue,
        visao_dre,
        visao_sme,
        permissao1,
        permissao2,
        grupo_1,
        grupo_2,
        grupo_3):

    response = jwt_authenticated_client_u2.get("/api/usuarios/visoes/", content_type='application/json')
    result = response.json()
    esperado = [

        {
            "id": str(visao_dre.id),
            "nome": visao_dre.nome,
        },
        {
            "id": str(visao_sme.id),
            "nome": visao_sme.nome,
        },
        {
            "id": str(visao_ue.id),
            "nome": visao_ue.nome,
        },
    ]

    assert result == esperado
