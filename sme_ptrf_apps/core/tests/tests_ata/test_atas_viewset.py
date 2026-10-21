from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.atas_viewset import AtasViewSet
from ...api.serializers import AtaSerializer, AtaCreateSerializer

pytestmark = pytest.mark.django_db


def test_view_set(ata_2020_1_cheque_aprovada, usuario_permissao_associacao):
    request = APIRequestFactory().get("")
    detalhe = AtasViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_associacao)
    response = detalhe(request, uuid=ata_2020_1_cheque_aprovada.uuid)

    assert response.status_code == status.HTTP_200_OK


def test_get_serializer_class_partial_update():
    view = AtasViewSet()
    view.action = 'partial_update'
    assert view.get_serializer_class() is AtaCreateSerializer


def test_get_serializer_class_outras_actions():
    view = AtasViewSet()
    view.action = 'retrieve'
    assert view.get_serializer_class() is AtaSerializer


# ata_despesas_com_pagamento_antecipado
def _ata_despesas_pagamento_antecipado(usuario, **query_params):
    querystring = '&'.join(f'{chave}={valor}' for chave, valor in query_params.items())
    request = APIRequestFactory().get(f'/?{querystring}')
    force_authenticate(request, user=usuario)
    view = AtasViewSet.as_view({'get': 'ata_despesas_com_pagamento_antecipado'})
    return view(request)


def test_ata_despesas_pagamento_antecipado_sem_uuid(usuario_permissao_associacao):
    response = _ata_despesas_pagamento_antecipado(usuario_permissao_associacao)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_ata_despesas_pagamento_antecipado_uuid_invalido(usuario_permissao_associacao):
    response = _ata_despesas_pagamento_antecipado(usuario_permissao_associacao, **{'ata-uuid': 'nao-e-um-uuid'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'Objeto não encontrado.'


def test_ata_despesas_pagamento_antecipado_sucesso(usuario_permissao_associacao, ata_factory):
    ata = ata_factory()

    response = _ata_despesas_pagamento_antecipado(usuario_permissao_associacao, **{'ata-uuid': ata.uuid})

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


# gerar_arquivo_ata
def _gerar_arquivo_ata(usuario, **query_params):
    querystring = '&'.join(f'{chave}={valor}' for chave, valor in query_params.items())
    request = APIRequestFactory().get(f'/?{querystring}')
    force_authenticate(request, user=usuario)
    view = AtasViewSet.as_view({'get': 'gerar_arquivo_ata'})
    return view(request)


def test_gerar_arquivo_ata_sem_parametros(usuario_permissao_associacao):
    response = _gerar_arquivo_ata(usuario_permissao_associacao)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_gerar_arquivo_ata_prestacao_de_contas_invalida(usuario_permissao_associacao, ata_factory):
    ata = ata_factory()

    response = _gerar_arquivo_ata(
        usuario_permissao_associacao, **{'prestacao-de-conta-uuid': 'nao-e-um-uuid', 'ata-uuid': ata.uuid})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'Objeto não encontrado.'
    assert 'prestação de contas' in response.data['mensagem']


def test_gerar_arquivo_ata_ata_invalida(usuario_permissao_associacao, prestacao_conta_factory):
    pc = prestacao_conta_factory()

    response = _gerar_arquivo_ata(
        usuario_permissao_associacao, **{'prestacao-de-conta-uuid': pc.uuid, 'ata-uuid': 'nao-e-um-uuid'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'Objeto não encontrado.'
    assert 'ata' in response.data['mensagem']


def test_gerar_arquivo_ata_campos_invalidos(usuario_permissao_associacao, prestacao_conta_factory, ata_factory):
    pc = prestacao_conta_factory()
    ata = ata_factory()

    with patch(
        'sme_ptrf_apps.core.api.views.atas_viewset.validar_campos_ata',
        return_value={'is_valid': False, 'campos': ['presidente_reuniao']},
    ):
        response = _gerar_arquivo_ata(
            usuario_permissao_associacao, **{'prestacao-de-conta-uuid': pc.uuid, 'ata-uuid': ata.uuid})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.data['campos_invalidos'] == ['presidente_reuniao']


def test_gerar_arquivo_ata_sucesso(usuario_permissao_associacao, prestacao_conta_factory, ata_factory):
    pc = prestacao_conta_factory()
    ata = ata_factory()

    with patch(
        'sme_ptrf_apps.core.api.views.atas_viewset.validar_campos_ata',
        return_value={'is_valid': True, 'campos': []},
    ), patch('sme_ptrf_apps.core.api.views.atas_viewset.gerar_arquivo_ata_async') as mock_task:
        response = _gerar_arquivo_ata(
            usuario_permissao_associacao, **{'prestacao-de-conta-uuid': pc.uuid, 'ata-uuid': ata.uuid})

    assert response.status_code == status.HTTP_200_OK
    assert response.data['mensagem'] == 'Arquivo na fila para processamento.'
    mock_task.delay.assert_called_once_with(
        prestacao_de_contas_uuid=str(pc.uuid),
        ata_uuid=str(ata.uuid),
        usuario=usuario_permissao_associacao.username,
    )


# download_arquivo_ata
def _download_arquivo_ata(usuario, **query_params):
    querystring = '&'.join(f'{chave}={valor}' for chave, valor in query_params.items())
    request = APIRequestFactory().get(f'/?{querystring}')
    force_authenticate(request, user=usuario)
    view = AtasViewSet.as_view({'get': 'download_arquivo_ata'})
    return view(request)


def test_download_arquivo_ata_sem_uuid(usuario_permissao_associacao):
    response = _download_arquivo_ata(usuario_permissao_associacao)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_download_arquivo_ata_uuid_invalido(usuario_permissao_associacao):
    response = _download_arquivo_ata(usuario_permissao_associacao, **{'ata-uuid': 'nao-e-um-uuid'})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'Objeto não encontrado.'


def test_download_arquivo_ata_arquivo_nao_gerado(usuario_permissao_associacao, ata_factory):
    ata = ata_factory()

    response = _download_arquivo_ata(usuario_permissao_associacao, **{'ata-uuid': ata.uuid})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['erro'] == 'arquivo_nao_gerado'


def test_download_arquivo_ata_sucesso(usuario_permissao_associacao, ata_factory):
    ata = ata_factory()
    ata.arquivo_pdf.save('ata_teste.pdf', SimpleUploadedFile('ata_teste.pdf', b'%PDF-1.4 conteudo'), save=True)

    try:
        response = _download_arquivo_ata(usuario_permissao_associacao, **{'ata-uuid': ata.uuid})

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/pdf'
        assert response['Content-Disposition'] == 'attachment; filename=ata.pdf'
    finally:
        ata.arquivo_pdf.delete(save=True)


# tabelas
def test_tabelas(usuario_permissao_associacao):
    request = APIRequestFactory().get('')
    force_authenticate(request, user=usuario_permissao_associacao)
    view = AtasViewSet.as_view({'get': 'tabelas'})

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert set(response.data.keys()) == {'tipos_ata', 'tipos_reuniao', 'convocacoes', 'pareceres'}
    assert len(response.data['tipos_ata']) > 0
