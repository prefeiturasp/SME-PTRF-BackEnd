import pytest

pytestmark = pytest.mark.django_db


def test_retrieve_usuarios(
        jwt_authenticated_client_u,
        usuario_para_teste,
        usuario_3,
        visao_ue,
        visao_dre,
        visao_sme,
        permissao1,
        permissao2,
        grupo_1,
        grupo_2,
        unidade
):

    response = jwt_authenticated_client_u.get(f"/api/usuarios/{usuario_3.id}/", content_type='application/json')
    result = response.json()
    esperado = {
        'id': usuario_3.id,
        'username': usuario_3.username,
        'email': usuario_3.email,
        'name': usuario_3.name,
        'url': f'http://testserver/api/esqueci-minha-senha/{usuario_3.username}/',
        'e_servidor': usuario_3.e_servidor,
        'groups': [
            {
                'id': grupo_2.id,
                'name': grupo_2.name,
                'descricao': grupo_2.descricao,
                'visoes': [{'id': visao_dre.id, 'nome': 'DRE'}, ]
            }
        ],
        'unidades': [
            {
                'uuid': f'{unidade.uuid}',
                'nome': unidade.nome,
                'codigo_eol': unidade.codigo_eol,
                'tipo_unidade': unidade.tipo_unidade
            }
        ],
        'visoes': [
            {
                'nome': visao_ue.nome,
                'id': visao_ue.id,
            },
            {
                'nome': visao_dre.nome,
                'id': visao_dre.id,
            },
        ]
    }
    assert result == esperado
