import json
import pytest
from unittest.mock import patch
from rest_framework import status

from sme_ptrf_apps.dre.models import MembroComissao, Comissao
from sme_ptrf_apps.core.services import TerceirizadasService

pytestmark = pytest.mark.django_db


def test_create_membro_comissao(jwt_authenticated_client_dre, dre_x, comissao_a, comissao_b):
    mock_dados_servidor = [
        {
            'nm_pessoa': 'ELOIR JOSE DA SILVA',
            'cd_cpf_pessoa': '15143960843',
            'cargo': 'DIRETOR DE ESCOLA',
            'cd_divisao': '095401',
            'divisao': 'PRUDENTE DE MORAIS, PRES.',
            'cd_coord': '108600',
            'coord': 'DIRETORIA REGIONAL DE EDUCACAO IPIRANGA'
        }
    ]

    payload = {
        'rf': '6605656',
        'nome': 'Pedro Antunes',
        'email': 'tecnico.sobrenome@sme.prefeitura.sp.gov.br',
        'dre': f'{dre_x.uuid}',
        'telefone': '1259275127',
        'comissoes': [f'{comissao_a.id}', f'{comissao_b.id}']
    }

    with patch.object(TerceirizadasService, 'get_informacao_servidor', return_value=mock_dados_servidor):
        response = jwt_authenticated_client_dre.post(
            f'/api/membros-comissoes/',
            data=json.dumps(payload),
            content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert MembroComissao.objects.filter(uuid=result['uuid']).exists()

    assert Comissao.objects.get(id=comissao_b.id).membros.filter(uuid=result['uuid']).exists()


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


def test_create_membro_comissao_contador_com_crc(
    jwt_authenticated_client_dre, dre_x, comissao_a
):
    payload = {
        'rf': '9988001',
        'nome': 'Pedro Antunes',
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
        response = jwt_authenticated_client_dre.post(
            '/api/membros-comissoes/',
            data=payload,
            format='json'
        )

    assert response.status_code == status.HTTP_201_CREATED

    membro = MembroComissao.objects.get(
        uuid=response.data['uuid']
    )

    assert membro.eh_contador is True
    assert membro.contador_crc == 'SP-123456'


@pytest.mark.parametrize('crc', [None, '', '   '])
def test_create_membro_comissao_contador_sem_crc(
    jwt_authenticated_client_dre, dre_x, comissao_a, crc
):
    payload = {
        'rf': '9988002',
        'nome': 'Pedro Antunes',
        'dre': str(dre_x.uuid),
        'comissoes': [comissao_a.id],
        'eh_contador': True
    }

    if crc is not None:
        payload['contador_crc'] = crc

    response = jwt_authenticated_client_dre.post(
        '/api/membros-comissoes/',
        data=payload,
        format='json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'contador_crc' in response.data
    assert not MembroComissao.objects.filter(
        rf='9988002', dre=dre_x
    ).exists()


def test_create_membro_comissao_crc_duplicado_mesma_dre(
    jwt_authenticated_client_dre,
    dre_x,
    comissao_a,
    membro_alex_comissao_a_dre_x
):
    MembroComissao.objects.filter(
        pk=membro_alex_comissao_a_dre_x.pk
    ).update(
        eh_contador=True,
        contador_crc='SP-123456'
    )

    payload = {
        'rf': '9988003',
        'nome': 'Pedro Antunes',
        'dre': str(dre_x.uuid),
        'comissoes': [comissao_a.id],
        'eh_contador': True,
        'contador_crc': 'SP-123456'
    }

    response = jwt_authenticated_client_dre.post(
        '/api/membros-comissoes/',
        data=payload,
        format='json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'contador_crc' in response.data

    assert MembroComissao.objects.filter(
        dre=dre_x,
        contador_crc='SP-123456'
    ).count() == 1


def test_create_membro_comissao_mesmo_crc_dres_diferentes(
    jwt_authenticated_client_dre,
    dre_x,
    dre_y,
    comissao_a,
    membro_alex_comissao_a_dre_x
):
    MembroComissao.objects.filter(
        pk=membro_alex_comissao_a_dre_x.pk
    ).update(
        eh_contador=True,
        contador_crc='SP-123456'
    )

    payload = {
        'rf': '9988004',
        'nome': 'Pedro Antunes',
        'dre': str(dre_y.uuid),
        'comissoes': [comissao_a.id],
        'eh_contador': True,
        'contador_crc': 'SP-123456'
    }

    with patch.object(
        TerceirizadasService,
        'get_informacao_servidor',
        return_value=[]
    ):
        response = jwt_authenticated_client_dre.post(
            '/api/membros-comissoes/',
            data=payload,
            format='json'
        )

    assert response.status_code == status.HTTP_201_CREATED

    assert MembroComissao.objects.filter(
        contador_crc='SP-123456'
    ).count() == 2


def test_create_membro_comissao_nao_contador_descarta_crc(
    jwt_authenticated_client_dre, dre_x, comissao_a
):
    payload = {
        'rf': '9988005',
        'nome': 'Pedro Antunes',
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
        response = jwt_authenticated_client_dre.post(
            '/api/membros-comissoes/',
            data=payload,
            format='json'
        )

    assert response.status_code == status.HTTP_201_CREATED

    membro = MembroComissao.objects.get(
        uuid=response.data['uuid']
    )

    assert membro.eh_contador is False
    assert membro.contador_crc is None
