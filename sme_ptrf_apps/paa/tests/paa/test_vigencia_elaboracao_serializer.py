from types import SimpleNamespace
from uuid import uuid4

import pytest
from rest_framework.exceptions import NotFound

from sme_ptrf_apps.paa.api.serializers import VigenciaElaboracaoQuerySerializer

pytestmark = pytest.mark.django_db


def _serializer(usuario, associacao_uuid):
    request = SimpleNamespace(user=usuario)
    return VigenciaElaboracaoQuerySerializer(
        data={'associacao_uuid': associacao_uuid}, context={'request': request})


@pytest.fixture
def usuario_ue(usuario_factory, unidade_factory):
    unidade = unidade_factory.create(tipo_unidade='CEU')
    return usuario_factory.create(unidades=[unidade]), unidade


@pytest.fixture
def associacao_da_unidade(associacao_factory):
    def _cria(unidade):
        return associacao_factory.create(unidade=unidade)
    return _cria


def test_uuid_ausente_ou_malformado_e_invalido(usuario_ue):
    usuario, _ = usuario_ue

    ausente = VigenciaElaboracaoQuerySerializer(data={}, context={'request': SimpleNamespace(user=usuario)})
    malformado = _serializer(usuario, 'nao-e-uuid')

    assert not ausente.is_valid()
    assert 'associacao_uuid' in ausente.errors
    assert not malformado.is_valid()
    assert 'associacao_uuid' in malformado.errors


def test_usuario_ue_acessa_associacao_da_sua_unidade(usuario_ue, associacao_da_unidade):
    usuario, unidade = usuario_ue
    associacao = associacao_da_unidade(unidade)
    serializer = _serializer(usuario, associacao.uuid)

    assert serializer.is_valid(raise_exception=True)
    assert serializer.validated_data['associacao'] == associacao


def test_associacao_inexistente_e_de_outra_unidade_respondem_igual(
        usuario_ue, unidade_factory, associacao_da_unidade):
    usuario, _ = usuario_ue
    associacao_de_outra_unidade = associacao_da_unidade(unidade_factory.create(tipo_unidade='CEU'))

    with pytest.raises(NotFound) as inexistente:
        _serializer(usuario, uuid4()).is_valid(raise_exception=True)
    with pytest.raises(NotFound) as inacessivel:
        _serializer(usuario, associacao_de_outra_unidade.uuid).is_valid(raise_exception=True)

    assert str(inexistente.value.detail) == str(inacessivel.value.detail) == 'Associação não encontrada.'


def test_usuario_sem_unidade_nao_acessa(usuario_factory, unidade_factory, associacao_da_unidade):
    usuario = usuario_factory.create()
    associacao = associacao_da_unidade(unidade_factory.create(tipo_unidade='CEU'))

    with pytest.raises(NotFound):
        _serializer(usuario, associacao.uuid).is_valid(raise_exception=True)


def test_usuario_dre_acessa_ues_da_propria_dre_e_nao_de_outra(
        usuario_factory, unidade_factory, dre_factory, associacao_da_unidade):
    dre = dre_factory.create()
    outra_dre = dre_factory.create()
    usuario = usuario_factory.create(unidades=[dre])
    da_dre = associacao_da_unidade(unidade_factory.create(tipo_unidade='CEU', dre=dre))
    de_outra_dre = associacao_da_unidade(unidade_factory.create(tipo_unidade='CEU', dre=outra_dre))

    assert _serializer(usuario, da_dre.uuid).is_valid(raise_exception=True)
    with pytest.raises(NotFound):
        _serializer(usuario, de_outra_dre.uuid).is_valid(raise_exception=True)


def test_usuario_sme_acessa_qualquer_associacao(
        usuario_factory, visao_factory, unidade_factory, associacao_da_unidade):
    usuario = usuario_factory.create()
    usuario.visoes.add(visao_factory.create(nome='SME'))
    associacao = associacao_da_unidade(unidade_factory.create(tipo_unidade='CEU'))

    assert _serializer(usuario, associacao.uuid).is_valid(raise_exception=True)
