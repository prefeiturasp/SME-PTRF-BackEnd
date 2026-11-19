import json

import pytest
from rest_framework import status
from unittest.mock import patch
from sme_ptrf_apps.dre.models import MembroComissao
from sme_ptrf_apps.core.services import TerceirizadasService

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
    assert membro_comissao.comissoes.filter(uuid=comissao_b.uuid).exists()


def test_update_membro_comissao_nome_igual(
    jwt_authenticated_client_dre,
    dre_x, dre_y,
    comissao_a, comissao_b,
    membro_alex_comissao_a_dre_x,
    membro_jose_comissao_a_b_dre_y
):
    payload = {
        'rf': '123458',
        'nome': 'José',
        'email': 'jose@teste.com',
        'dre': f'{dre_y.uuid}',
        'comissoes': [comissao_b.id]
    }

    response = jwt_authenticated_client_dre.put(
        f'/api/membros-comissoes/{membro_alex_comissao_a_dre_x.uuid}/',
        data=json.dumps(payload),
        content_type='application/json')

    result = json.loads(response.content)
    resultado_esperado = {
        'detail': 'Já existe um membro de comissão com esse Registro Funcional.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(MembroComissao.objects.filter(rf='123458').all()) == 1
    assert resultado_esperado == result


def test_update_membro_comissao_contador_com_crc(
    jwt_authenticated_client_dre,
    dre_x, comissao_a,
    membro_alex_comissao_a_dre_x
):
    membro = membro_alex_comissao_a_dre_x

    payload = {
        'rf': membro.rf,
        'nome': 'Pedro',
        'dre': str(dre_x.uuid),
        'comissoes': [comissao_a.id],
        'eh_contador': True,
        'contador_crc': 'SP-123456'
    }

    with patch.object(
        TerceirizadasService,
        'get_informacao_servidor',
        return_value=[]
    ):
        response = jwt_authenticated_client_dre.put(
            f'/api/membros-comissoes/{membro.uuid}/',
            data=payload,
            format='json'
        )

    assert response.status_code == status.HTTP_200_OK

    membro.refresh_from_db()

    assert membro.eh_contador is True
    assert membro.contador_crc == 'SP-123456'


@pytest.mark.parametrize('crc', [None, '', '   '])
def test_update_membro_comissao_contador_sem_crc(
    jwt_authenticated_client_dre,
    dre_x, comissao_a,
    membro_alex_comissao_a_dre_x,
    crc
):
    membro = membro_alex_comissao_a_dre_x

    payload = {
        'rf': membro.rf,
        'nome': 'Pedro',
        'dre': str(dre_x.uuid),
        'comissoes': [comissao_a.id],
        'eh_contador': True
    }

    if crc is not None:
        payload['contador_crc'] = crc

    response = jwt_authenticated_client_dre.put(
        f'/api/membros-comissoes/{membro.uuid}/',
        data=payload,
        format='json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'contador_crc' in response.data

    membro.refresh_from_db()
    assert membro.eh_contador is False
    assert membro.contador_crc is None


def test_update_membro_comissao_crc_duplicado_mesma_dre(
    jwt_authenticated_client_dre,
    dre_x, dre_y, comissao_b,
    membro_alex_comissao_a_dre_x,
    membro_jose_comissao_a_b_dre_y
):
    membro = membro_alex_comissao_a_dre_x

    MembroComissao.objects.filter(
        pk=membro_jose_comissao_a_b_dre_y.pk
    ).update(
        eh_contador=True,
        contador_crc='SP-123456'
    )

    payload = {
        'rf': membro.rf,
        'nome': 'Pedro',
        'dre': str(dre_y.uuid),
        'comissoes': [comissao_b.id],
        'eh_contador': True,
        'contador_crc': 'SP-123456'
    }

    response = jwt_authenticated_client_dre.put(
        f'/api/membros-comissoes/{membro.uuid}/',
        data=payload,
        format='json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'contador_crc' in response.data

    membro.refresh_from_db()
    assert membro.dre == dre_x


def test_update_membro_comissao_mantem_proprio_crc(
    jwt_authenticated_client_dre,
    dre_x, comissao_a,
    membro_alex_comissao_a_dre_x
):
    membro = membro_alex_comissao_a_dre_x

    MembroComissao.objects.filter(pk=membro.pk).update(
        eh_contador=True,
        contador_crc='SP-123456'
    )
    membro.refresh_from_db()

    payload = {
        'rf': membro.rf,
        'nome': 'Pedro Atualizado',
        'dre': str(dre_x.uuid),
        'comissoes': [comissao_a.id],
        'eh_contador': True,
        'contador_crc': 'SP-123456'
    }

    with patch.object(
        TerceirizadasService,
        'get_informacao_servidor',
        return_value=[]
    ):
        response = jwt_authenticated_client_dre.put(
            f'/api/membros-comissoes/{membro.uuid}/',
            data=payload,
            format='json'
        )

    assert response.status_code == status.HTTP_200_OK

    membro.refresh_from_db()

    assert membro.nome == 'Pedro Atualizado'
    assert membro.eh_contador is True
    assert membro.contador_crc == 'SP-123456'


def test_update_membro_comissao_remove_crc_ao_desmarcar_contador(
    jwt_authenticated_client_dre,
    dre_x, comissao_a,
    membro_alex_comissao_a_dre_x
):
    membro = membro_alex_comissao_a_dre_x

    MembroComissao.objects.filter(pk=membro.pk).update(
        eh_contador=True,
        contador_crc='SP-123456'
    )
    membro.refresh_from_db()

    payload = {
        'rf': membro.rf,
        'nome': membro.nome,
        'dre': str(dre_x.uuid),
        'comissoes': [comissao_a.id],
        'eh_contador': False,
        'contador_crc': 'SP-123456'
    }

    with patch.object(
        TerceirizadasService,
        'get_informacao_servidor',
        return_value=[]
    ):
        response = jwt_authenticated_client_dre.put(
            f'/api/membros-comissoes/{membro.uuid}/',
            data=payload,
            format='json'
        )

    assert response.status_code == status.HTTP_200_OK

    membro.refresh_from_db()

    assert membro.eh_contador is False
    assert membro.contador_crc is None
