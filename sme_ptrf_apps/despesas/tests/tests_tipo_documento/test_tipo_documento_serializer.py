import pytest

from ...api.serializers.tipo_documento_serializer import (TipoDocumentoSerializer, TipoDocumentoListSerializer)
from ...models import TipoDocumento
from rest_framework.exceptions import ValidationError

pytestmark = pytest.mark.django_db

def test_serializer(tipo_documento):

    serializer = TipoDocumentoSerializer(tipo_documento)
    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']
    assert serializer.data['apenas_digitos'] is not None
    assert serializer.data['pode_reter_imposto'] is not None
    assert serializer.data['numero_documento_digitado'] is not None
    assert serializer.data['eh_documento_de_retencao_de_imposto'] is not None


def test_create_tipo_documento_success():
    """
    Testa a criação de um TipoDocumento com dados válidos.
    """
    data = {
        "nome": "Documento Teste",
        "apenas_digitos": True,
        "numero_documento_digitado": False,
        "pode_reter_imposto": False,
        "eh_documento_de_retencao_de_imposto": False,
        "documento_comprobatorio_de_despesa": False,
    }

    serializer = TipoDocumentoSerializer(data=data)
    assert serializer.is_valid(), f"Erros: {serializer.errors}"

    tipo_documento = serializer.save()
    assert tipo_documento.nome == data["nome"]
    assert TipoDocumento.objects.count() == 1


def test_update_tipo_documento_success():
    """
    Testa a atualização de um TipoDocumento com um nome novo.
    """
    tipo_documento = TipoDocumento.objects.create(nome="Documento Antigo")
    data = {
        "nome": "Documento Atualizado",
        "apenas_digitos": False,
        "numero_documento_digitado": True,
        "pode_reter_imposto": True,
        "eh_documento_de_retencao_de_imposto": False,
        "documento_comprobatorio_de_despesa": True,
    }

    serializer = TipoDocumentoSerializer(instance=tipo_documento, data=data, partial=True)
    assert serializer.is_valid(), f"Erros: {serializer.errors}"

    tipo_documento_atualizado = serializer.save()
    assert tipo_documento_atualizado.nome == "Documento Atualizado"


def test_Listserializer(tipo_documento):

    serializer = TipoDocumentoSerializer(tipo_documento)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['nome']

def test_create_tipo_documento_duplicate_nome():
    """
    Testa a criação de um TipoDocumento com um nome duplicado.
    """
    TipoDocumento.objects.create(nome="Documento Teste")
    data = {
        "nome": "Documento Teste",
        "apenas_digitos": True,
        "numero_documento_digitado": False,
        "pode_reter_imposto": False,
        "eh_documento_de_retencao_de_imposto": False,
        "documento_comprobatorio_de_despesa": False,
    }

    serializer = TipoDocumentoSerializer(data=data)
    with pytest.raises(ValidationError) as exc:
        serializer.is_valid(raise_exception=True)

    assert "non_field_errors" in str(exc.value), exc.value
    error = ValidationError
    assert isinstance(exc.value, error)

def test_update_tipo_documento_duplicate_nome():
    """
    Testa a atualização de um TipoDocumento para um nome já existente.
    """
    TipoDocumento.objects.create(nome="Documento Existente")
    tipo_documento = TipoDocumento.objects.create(nome="Documento Original")
    data = {
        "nome": "Documento Existente"
    }

    serializer = TipoDocumentoSerializer(instance=tipo_documento, data=data, partial=True)
    with pytest.raises(ValidationError) as exc:
        serializer.is_valid(raise_exception=True)

    assert "non_field_errors" in str(exc.value)
    error = ValidationError
    assert isinstance(exc.value, error)
