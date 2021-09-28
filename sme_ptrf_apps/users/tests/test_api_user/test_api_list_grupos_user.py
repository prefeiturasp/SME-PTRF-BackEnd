import pytest

pytestmark = pytest.mark.django_db

def test_consulta_grupos(
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

    response = jwt_authenticated_client_u2.get("/api/usuarios/grupos/?visao=DRE", content_type='application/json')
    result = response.json()
    esperado = [
        {
            "id": str(grupo_1.id),
            "nome": grupo_1.name,
            "descricao": grupo_1.descricao,
            "visao": 'DRE'
        },
        {
            "id": str(grupo_2.id),
            "nome": grupo_2.name,
            "descricao": grupo_2.descricao,
            "visao": 'DRE'
        },
        {
            "id": str(grupo_3.id),
            "nome": grupo_3.name,
            "descricao": grupo_3.descricao,
            "visao": 'DRE'
        },
    ]

    assert result == esperado
