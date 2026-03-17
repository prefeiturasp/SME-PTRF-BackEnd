import pytest

from sme_ptrf_apps.paa.api.serializers import ObjetivoPaaSerializer
from sme_ptrf_apps.paa.models.objetivo_paa import StatusChoices

pytestmark = pytest.mark.django_db


def test_list_objetivo_paa_default_serializer(objetivo_paa_ativo):
    serializer = ObjetivoPaaSerializer(objetivo_paa_ativo)

    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'paa' in serializer.data
    assert 'status' in serializer.data
    assert 'nome' in serializer.data


def test_create_objetivo_paa_sem_nome():
    objetivo = {'nome': None}
    serializer = ObjetivoPaaSerializer(data=objetivo)
    assert not serializer.is_valid()


def test_crete_objetivo_paa_com_nome():
    objetivo = {'nome': 'Objetivo 1'}
    assert ObjetivoPaaSerializer().validate(objetivo)


def test_create_com_nome_paa_duplicado(objetivo_paa_factory, paa):
    objetivo_paa_factory.create(nome="Duplicado", paa=paa)
    data = {"nome": "Duplicado", "paa": paa.id}
    serializer = ObjetivoPaaSerializer(data=data)
    assert not serializer.is_valid()


def test_update_mantendo_nome(objetivo_paa_factory):
    obj = objetivo_paa_factory.create(nome="Objetivo Antigo")
    serializer = ObjetivoPaaSerializer(instance=obj, data={"nome": "Objetivo Antigo"}, partial=True)
    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()
    assert updated.nome == "Objetivo Antigo"


def test_update_com_nome_valido(objetivo_paa_factory):
    objetivo_paa_factory.create(nome="Objetivo A")
    obj2 = objetivo_paa_factory.create(nome="Objetivo B")
    serializer = ObjetivoPaaSerializer(instance=obj2, data={"nome": "Novo Objetivo"}, partial=True)
    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()
    assert updated.nome == "Novo Objetivo"


def test_update_com_nome_paa_duplicado(objetivo_paa_factory, paa):
    objetivo_paa_factory.create(nome="Objetivo X", paa=paa)
    obj2 = objetivo_paa_factory.create(nome="Objetivo Y", paa=paa)
    serializer = ObjetivoPaaSerializer(instance=obj2, data={"nome": "Objetivo X", "paa": str(paa.uuid)}, partial=True)
    assert serializer.is_valid()


def test_update_com_nome_vazio(objetivo_paa_factory):
    obj1 = objetivo_paa_factory.create(nome="Objetivo X")
    serializer = ObjetivoPaaSerializer(instance=obj1, data={"nome": ""}, partial=True)
    assert not serializer.is_valid()


def test_get_status_objeto_sim(objetivo_paa_factory):
    obj = objetivo_paa_factory.create(nome="Objetivo ATIVO", status=StatusChoices.ATIVO)
    serializer = ObjetivoPaaSerializer()
    result = serializer.get_status_objeto(obj)

    assert result == {"key": StatusChoices.ATIVO, "value": "Ativo"}


def test_get_status_objeto_nao(objetivo_paa_factory):
    obj = objetivo_paa_factory.create(nome="Objetivo INATIVO", status=StatusChoices.INATIVO)
    serializer = ObjetivoPaaSerializer()
    result = serializer.get_status_objeto(obj)

    assert result == {"key": StatusChoices.INATIVO, "value": "Inativo"}
