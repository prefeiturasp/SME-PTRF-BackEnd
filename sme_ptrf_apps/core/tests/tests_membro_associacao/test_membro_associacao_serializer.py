import pytest

from sme_ptrf_apps.core.api.serializers import MembroAssociacaoListSerializer, MembroAssociacaoCreateSerializer

pytestmark = pytest.mark.django_db


def test_membro_associacao_list_serializer(membro_associacao):
    membro = MembroAssociacaoListSerializer(membro_associacao)
    assert membro.data is not None
    assert membro.data['uuid']
    assert membro.data['nome']
    assert membro.data['associacao']
    assert membro.data['cargo_associacao']
    assert membro.data['cargo_educacao']
    assert membro.data['representacao']
    assert membro.data['codigo_identificacao']
    assert membro.data['email']
    assert membro.data['cpf']
    assert membro.data['telefone']
    assert membro.data['cep']
    assert membro.data['bairro']
    assert membro.data['endereco']


def test_membro_associacao_create_serializer(membro_associacao):
    membro = MembroAssociacaoCreateSerializer(membro_associacao)
    assert membro.data is not None
    assert membro.data['uuid']
    assert membro.data['nome']
    assert membro.data['associacao']
    assert membro.data['cargo_associacao']
    assert membro.data['cargo_educacao']
    assert membro.data['representacao']
    assert membro.data['codigo_identificacao']
    assert membro.data['email']
    assert membro.data['cpf']
    assert membro.data['telefone']
    assert membro.data['cep']
    assert membro.data['bairro']
    assert membro.data['endereco']
