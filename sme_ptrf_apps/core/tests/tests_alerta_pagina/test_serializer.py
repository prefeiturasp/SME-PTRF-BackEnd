import pytest
from uuid import uuid4

from rest_framework.exceptions import ValidationError

from sme_ptrf_apps.core.api.serializers.alerta_pagina_serializer import AlertaPaginaQueryParamsSerializer
from sme_ptrf_apps.core.fixtures.factories.unidade_factory import UnidadeFactory

pytestmark = pytest.mark.django_db


def test_parametros_validos_resolvem_objetos_e_categoria_padrao(recurso_legado):
    unidade = UnidadeFactory()
    serializer = AlertaPaginaQueryParamsSerializer(
        data={'recurso': str(recurso_legado.uuid), 'unidade': str(unidade.uuid)})

    assert serializer.is_valid(raise_exception=True)
    assert serializer.validated_data['recurso'] == recurso_legado
    assert serializer.validated_data['unidade'] == unidade
    assert serializer.validated_data['categoria'] == 'AVISO_REMOCAO_PRESIDENTE'


def test_recurso_inexistente_levanta_validation_error():
    unidade = UnidadeFactory()
    serializer = AlertaPaginaQueryParamsSerializer(data={'recurso': str(uuid4()), 'unidade': str(unidade.uuid)})

    with pytest.raises(ValidationError) as erro:
        serializer.is_valid(raise_exception=True)

    assert 'recurso' in erro.value.detail


@pytest.mark.parametrize('dados', [
    {'recurso': 'invalido', 'unidade': 'invalido'},
    {},
])
def test_uuid_invalido_ou_ausente_levanta_validation_error(dados):
    with pytest.raises(ValidationError):
        AlertaPaginaQueryParamsSerializer(data=dados).is_valid(raise_exception=True)


def test_categoria_invalida_levanta_validation_error(recurso_legado):
    unidade = UnidadeFactory()
    serializer = AlertaPaginaQueryParamsSerializer(
        data={'recurso': str(recurso_legado.uuid), 'unidade': str(unidade.uuid), 'categoria': 'X'})

    with pytest.raises(ValidationError) as erro:
        serializer.is_valid(raise_exception=True)

    assert 'categoria' in erro.value.detail
