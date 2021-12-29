import json

import pytest
from rest_framework import status

from sme_ptrf_apps.dre.models import MembroComissao

pytestmark = pytest.mark.django_db


def test_update_membro_comissao(
    jwt_authenticated_client_dre,
    dre_x, dre_y,
    comissao_a, comissao_b,
    membro_alex_comissao_a_dre_x
):
    payload = {
        'rf': '555444',
        'nome': 'Pedro',
        'email': 'pedro@teste.com',
        'dre': f'{dre_y.uuid}',
        'comissoes': [comissao_b.id]
    }

    response = jwt_authenticated_client_dre.put(
        f'/api/membros-comissoes/{membro_alex_comissao_a_dre_x.uuid}/',
        data=json.dumps(payload),
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)
    membro_comissao = MembroComissao.objects.get(uuid=result['uuid'])

    assert membro_comissao.rf == '555444'
    assert membro_comissao.nome == 'Pedro'
    assert membro_comissao.email == 'pedro@teste.com'
    assert membro_comissao.dre == dre_y
    assert membro_comissao.comissoes.filter(uuid=comissao_b.uuid)
