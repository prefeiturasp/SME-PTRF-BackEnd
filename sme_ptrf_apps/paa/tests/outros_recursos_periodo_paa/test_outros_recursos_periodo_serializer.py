import pytest

from ...api.serializers import OutrosRecursosPeriodoPaaSerializer

pytestmark = pytest.mark.django_db


def test_outros_recursos_list_serializer(outros_recursos_periodo):
    serializer = OutrosRecursosPeriodoPaaSerializer(outros_recursos_periodo)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'periodo_paa' in serializer.data
    assert 'outro_recurso' in serializer.data
    assert 'outro_recurso_objeto' in serializer.data
    assert 'ativo' in serializer.data
    assert 'uso_associacao' in serializer.data
    assert 'unidades' in serializer.data


@pytest.mark.django_db
def test_serializer_erro_periodo_obrigatorio(outro_recurso):
    payload = {
        "outro_recurso": outro_recurso.uuid,
        "ativo": True
    }

    serializer = OutrosRecursosPeriodoPaaSerializer(data=payload)
    assert not serializer.is_valid()

    assert "periodo_paa" in serializer.errors
    assert serializer.errors["periodo_paa"][0] == "Período não foi informado."


@pytest.mark.django_db
def test_serializer_erro_recurso_obrigatorio(periodo_paa):
    payload = {
        "periodo_paa": periodo_paa.uuid,
        "ativo": True
    }

    serializer = OutrosRecursosPeriodoPaaSerializer(data=payload)
    assert not serializer.is_valid()

    assert "outro_recurso" in serializer.errors
    assert serializer.errors["outro_recurso"][0] == "Outro Recurso não foi informado."


@pytest.mark.django_db
def test_serializer_unique_together_validator(outros_recursos_periodo):
    payload = {
        "periodo_paa": outros_recursos_periodo.periodo_paa.uuid,
        "outro_recurso": outros_recursos_periodo.outro_recurso.uuid,
    }

    serializer = OutrosRecursosPeriodoPaaSerializer(data=payload)
    assert not serializer.is_valid()

    assert "non_field_errors" in serializer.errors
    assert serializer.errors["non_field_errors"][0] == \
           "Já existe um Recurso cadastrado para o período informado."


@pytest.mark.django_db
def test_serializer_unidades_optional(periodo_paa, outro_recurso):
    payload = {
        "periodo_paa": periodo_paa.uuid,
        "outro_recurso": outro_recurso.uuid,
        "ativo": True,
        "unidades": []  # opcional
    }

    serializer = OutrosRecursosPeriodoPaaSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors

    instance = serializer.save()
    assert instance.unidades.count() == 0


def test_campos_read_only_nao_podem_ser_setados(periodo_paa, outro_recurso):
    payload = {
        "periodo_paa": str(periodo_paa.uuid),
        "outro_recurso": str(outro_recurso.uuid),
        "ativo": True,
        "uuid": "valor-indevido",
        "id": 999,
        "uso_associacao": "Outro valor"
    }

    serializer = OutrosRecursosPeriodoPaaSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors

    instance = serializer.save()

    assert instance.id != 999
    assert instance.uuid != "valor-indevido"
    assert instance.uso_associacao != "Outro valor"


def test_serializer_unidades_many(periodo_paa, outro_recurso, unidade):
    payload = {
        "periodo_paa": str(periodo_paa.uuid),
        "outro_recurso": str(outro_recurso.uuid),
        "ativo": True,
        "unidades": [str(unidade.uuid)]
    }

    serializer = OutrosRecursosPeriodoPaaSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors

    inst = serializer.save()
    unidades = list(inst.unidades.all())

    assert len(unidades) == 1
    assert unidades[0] == unidade
