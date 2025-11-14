import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from sme_ptrf_apps.paa.api.views.ata_paa_viewset import AtaPaaViewSet

pytestmark = pytest.mark.django_db


def test_view_set_retrieve(ata_paa, usuario_permissao_sme, flag_paa):
    request = APIRequestFactory().get("")
    detalhe = AtaPaaViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=usuario_permissao_sme)
    response = detalhe(request, uuid=ata_paa.uuid)

    assert response.status_code == status.HTTP_200_OK


def test_view_set_tabelas(usuario_permissao_sme, flag_paa):
    request = APIRequestFactory().get("/api/atas-paa/tabelas/")
    tabelas = AtaPaaViewSet.as_view({'get': 'tabelas'})
    force_authenticate(request, user=usuario_permissao_sme)
    response = tabelas(request)

    assert response.status_code == status.HTTP_200_OK
    assert 'tipos_ata' in response.data
    assert 'tipos_reuniao' in response.data
    assert 'convocacoes' in response.data
    assert 'pareceres' in response.data

