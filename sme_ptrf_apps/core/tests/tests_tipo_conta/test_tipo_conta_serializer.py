import pytest
from rest_framework import serializers as drf_serializers

from sme_ptrf_apps.core.api.serializers.tipo_conta_serializer import TipoContaSerializer

pytestmark = pytest.mark.django_db


def test_serializer(tipo_conta):

    serializer = TipoContaSerializer(tipo_conta)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['id']
    assert serializer.data['nome']
    assert not serializer.data['apenas_leitura']


def test_serializer_exibe_recurso_completo(tipo_conta):
    data = TipoContaSerializer(tipo_conta).data

    assert 'recurso_completo' in data
    assert data['recurso_completo']['id'] == tipo_conta.recurso.id


def test_serializer_exibe_recurso_como_uuid(tipo_conta):
    data = TipoContaSerializer(tipo_conta).data

    assert str(data['recurso']) == str(tipo_conta.recurso.uuid)


def test_create_normaliza_nome_com_espacos_extras(recurso_legado):
    data = {
        'nome': '  Conta   Corrente  ',
        'banco_nome': 'Banco X',
        'agencia': '1234',
        'numero_conta': '12345-6',
        'numero_cartao': '',
        'recurso': str(recurso_legado.uuid),
    }
    serializer = TipoContaSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    instance = serializer.save()

    assert instance.nome == 'Conta Corrente'


def test_create_sucesso(recurso_legado):
    data = {
        'nome': 'Poupança',
        'banco_nome': 'Banco Y',
        'agencia': '0001',
        'numero_conta': '00001-1',
        'numero_cartao': '',
        'recurso': str(recurso_legado.uuid),
    }
    serializer = TipoContaSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    instance = serializer.save()

    assert instance.pk is not None
    assert instance.nome == 'Poupança'


def test_create_erro_duplicado_case_insensitive(tipo_conta_factory, recurso_legado):
    tipo_conta_factory(nome='Cheque', recurso=recurso_legado)

    data = {
        'nome': 'CHEQUE',
        'banco_nome': 'Banco Z',
        'agencia': '0002',
        'numero_conta': '00002-2',
        'numero_cartao': '',
        'recurso': str(recurso_legado.uuid),
    }
    serializer = TipoContaSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    with pytest.raises(drf_serializers.ValidationError) as exc_info:
        serializer.save()

    assert 'non_field_errors' in exc_info.value.detail


def test_update_normaliza_nome_com_espacos_extras(tipo_conta_factory, recurso_legado):
    instance = tipo_conta_factory(nome='Corrente Antigo', recurso=recurso_legado)

    data = {
        'nome': '  Conta   Poupança  ',
        'banco_nome': instance.banco_nome,
        'agencia': instance.agencia,
        'numero_conta': instance.numero_conta,
        'numero_cartao': instance.numero_cartao,
        'recurso': str(recurso_legado.uuid),
    }
    serializer = TipoContaSerializer(instance, data=data)
    assert serializer.is_valid(), serializer.errors

    updated = serializer.save()

    assert updated.nome == 'Conta Poupança'


def test_update_sucesso(tipo_conta_factory, recurso_legado):
    instance = tipo_conta_factory(nome='Original', recurso=recurso_legado)

    data = {
        'nome': 'Atualizado',
        'banco_nome': 'Banco W',
        'agencia': '9999',
        'numero_conta': '99999-9',
        'numero_cartao': '',
        'recurso': str(recurso_legado.uuid),
    }
    serializer = TipoContaSerializer(instance, data=data)
    assert serializer.is_valid(), serializer.errors

    updated = serializer.save()

    assert updated.nome == 'Atualizado'
    assert updated.banco_nome == 'Banco W'


def test_update_erro_duplicado_case_insensitive(tipo_conta_factory, recurso_legado):
    tipo_conta_factory(nome='Cheque', recurso=recurso_legado)
    instance = tipo_conta_factory(nome='Poupança', recurso=recurso_legado)

    data = {
        'nome': 'cheque',
        'banco_nome': instance.banco_nome,
        'agencia': instance.agencia,
        'numero_conta': instance.numero_conta,
        'numero_cartao': instance.numero_cartao,
        'recurso': str(recurso_legado.uuid),
    }
    serializer = TipoContaSerializer(instance, data=data)
    assert serializer.is_valid(), serializer.errors

    with pytest.raises(drf_serializers.ValidationError) as exc_info:
        serializer.save()

    assert 'non_field_errors' in exc_info.value.detail


def test_update_nao_conflita_consigo_mesmo(tipo_conta_factory, recurso_legado):
    instance = tipo_conta_factory(nome='Cheque', recurso=recurso_legado)

    data = {
        'nome': 'Cheque',
        'banco_nome': 'Banco Novo',
        'agencia': instance.agencia,
        'numero_conta': instance.numero_conta,
        'numero_cartao': instance.numero_cartao,
        'recurso': str(recurso_legado.uuid),
    }
    serializer = TipoContaSerializer(instance, data=data)
    assert serializer.is_valid(), serializer.errors

    updated = serializer.save()

    assert updated.banco_nome == 'Banco Novo'
