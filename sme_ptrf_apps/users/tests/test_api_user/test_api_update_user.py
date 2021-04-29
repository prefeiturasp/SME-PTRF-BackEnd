import json
import pytest

pytestmark = pytest.mark.django_db

def test_atualizar_usuario_servidor(
        jwt_authenticated_client_u,
        usuario_3,
        usuario_2,
        visao_ue,
        visao_dre,
        visao_sme,
        grupo_1,
        grupo_2,
        unidade_ue_271170,
        unidade_diferente,
        dre
):

    assert not usuario_2.visoes.filter(nome='UE').first(), "Não deveria estar vinculado à UE antes do teste."
    assert not usuario_2.unidades.filter(codigo_eol='271170').first(), "Não deveria estar vinculado à unidade 271170 antes do teste."

    payload = {
        'e_servidor': True,
        'username': usuario_2.username,
        'name': usuario_2.name,
        'email': 'novoEmail@gmail.com',
        'visao': "UE",
        'unidade': "271170",
        'groups': [
            grupo_1.id
        ]
    }

    response = jwt_authenticated_client_u.put(
        f"/api/usuarios/{usuario_2.id}/", data=json.dumps(payload), content_type='application/json')
    result = response.json()

    esperado = {
        'username': usuario_2.username,
        'email': 'novoEmail@gmail.com',
        'name': usuario_2.name,
        'e_servidor': True,
        'groups': [grupo_1.id]
    }

    assert usuario_2.visoes.filter(nome='UE').first(), "Deveria ter sido vinculado à visão UE."
    assert usuario_2.unidades.filter(codigo_eol='271170').first(), "Deveria ter sido vinculado à unidade 271170."
    assert result == esperado
