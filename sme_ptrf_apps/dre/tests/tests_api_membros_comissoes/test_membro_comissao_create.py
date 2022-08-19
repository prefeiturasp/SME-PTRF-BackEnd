import json

import pytest
from rest_framework import status

from sme_ptrf_apps.dre.models import MembroComissao, Comissao

pytestmark = pytest.mark.django_db


# TODO
# Será necessário refatorar esse teste, pois atualmente ele esta quebrando quando a API terceirizada esta indisponivel

# def test_create_membro_comissao(jwt_authenticated_client_dre, dre_x, comissao_a, comissao_b):
#     payload = {
#         'rf': '6605656',
#         'nome': 'Pedro Antunes',
#         'email': 'tecnico.sobrenome@sme.prefeitura.sp.gov.br',
#         'dre': f'{dre_x.uuid}',
#         'telefone': '1259275127',
#         'comissoes': [f'{comissao_a.id}', f'{comissao_b.id}']
#     }
#     response = jwt_authenticated_client_dre.post(
#         '/api/membros-comissoes/', data=json.dumps(payload), content_type='application/json')
#
#     assert response.status_code == status.HTTP_201_CREATED
#
#     result = json.loads(response.content)
#
#     assert MembroComissao.objects.filter(uuid=result['uuid']).exists()
#
#     assert Comissao.objects.get(id=comissao_b.id).membros.filter(uuid=result['uuid']).exists()

def test_create_membro_comissao_nome_igual(
    jwt_authenticated_client_dre, dre_x, dre_y, comissao_a, comissao_b, membro_jose_comissao_a_b_dre_y
):
    payload = {
        'rf': '123458',
        'nome': 'Pedro Antunes',
        'email': 'tecnico.sobrenome@sme.prefeitura.sp.gov.br',
        'dre': f'{dre_y.uuid}',
        'telefone': '1259275127',
        'comissoes': [f'{comissao_a.id}', f'{comissao_b.id}']
    }

    response = jwt_authenticated_client_dre.post(
            '/api/membros-comissoes/', data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)
    resultado_esperado = {
        'detail': 'Já existe um membro de comissão com esse Registro Funcional.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(MembroComissao.objects.filter(rf='123458').all()) == 1
    assert resultado_esperado == result

