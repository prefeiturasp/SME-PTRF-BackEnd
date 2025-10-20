import pytest

from sme_ptrf_apps.paa.api.serializers import AtividadeEstatutariaSerializer
from sme_ptrf_apps.paa.choices import StatusChoices, Mes
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum

pytestmark = pytest.mark.django_db


def test_list_atividade_estatutaria_default_serializer(atividade_estatutaria_ativo):
    serializer = AtividadeEstatutariaSerializer(atividade_estatutaria_ativo)

    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'status' in serializer.data
    assert 'nome' in serializer.data
    assert 'tipo' in serializer.data
    assert 'mes' in serializer.data


def test_create_atividade_estatutaria_sem_nome():
    atividade = {'nome': None}
    serializer = AtividadeEstatutariaSerializer(data=atividade)
    assert not serializer.is_valid()


def test_create_com_nome_duplicado(atividade_estatutaria_factory):
    atividade_estatutaria_factory.create(
        nome="Duplicado",
        status=StatusChoices.ATIVO,
        tipo=TipoAtividadeEstatutariaEnum.ORDINARIA.name,
        mes=Mes.JANEIRO
    )
    data = {
        "nome": "Duplicado",
        "status": StatusChoices.ATIVO,
        "tipo": TipoAtividadeEstatutariaEnum.ORDINARIA.name,
        "mes": Mes.JANEIRO
    }
    serializer = AtividadeEstatutariaSerializer(data=data)
    with pytest.raises(Exception):
        assert serializer.is_valid()


def test_update_mantendo_os_dados(atividade_estatutaria_factory):
    obj = atividade_estatutaria_factory.create(
        nome="atividade Antiga",
        status=StatusChoices.ATIVO,
        tipo=TipoAtividadeEstatutariaEnum.ORDINARIA.name,
        mes=Mes.JANEIRO
    )
    serializer = AtividadeEstatutariaSerializer(
        instance=obj,
        data={
            "nome": "atividade Antiga",
            "status": StatusChoices.ATIVO,
            "tipo": TipoAtividadeEstatutariaEnum.ORDINARIA.name,
            "mes": Mes.JANEIRO
        }, partial=True)
    assert serializer.is_valid()
    updated = serializer.save()
    assert updated.nome == "atividade Antiga"
    assert updated.status == StatusChoices.ATIVO
    assert updated.mes == Mes.JANEIRO
    assert updated.tipo == TipoAtividadeEstatutariaEnum.ORDINARIA.name


def test_update_com_novo_nome_valido(atividade_estatutaria_factory):
    atividade_estatutaria_factory.create(nome="atividade A")
    obj2 = atividade_estatutaria_factory.create(nome="atividade B")
    serializer = AtividadeEstatutariaSerializer(instance=obj2, data={"nome": "Novo nome da atividade"}, partial=True)
    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()
    assert updated.nome == "Novo nome da atividade"


def test_update_com_nome_duplicado(atividade_estatutaria_factory):
    atividade_estatutaria_factory.create(
        nome="atividade X",
        mes=Mes.JANEIRO,
        tipo=TipoAtividadeEstatutariaEnum.ORDINARIA.name,
        status=StatusChoices.ATIVO
    )
    obj2 = atividade_estatutaria_factory.create(
        nome="atividade Y",
        mes=Mes.JANEIRO,
        tipo=TipoAtividadeEstatutariaEnum.ORDINARIA.name,
        status=StatusChoices.ATIVO
    )
    serializer = AtividadeEstatutariaSerializer(instance=obj2, data={"nome": "atividade X"}, partial=True)
    assert not serializer.is_valid()


def test_update_com_nome_vazio(atividade_estatutaria_factory):
    obj1 = atividade_estatutaria_factory.create(
        nome="atividade X",
        mes=Mes.JANEIRO,
        tipo=TipoAtividadeEstatutariaEnum.ORDINARIA.name,
        status=StatusChoices.ATIVO
    )
    serializer = AtividadeEstatutariaSerializer(instance=obj1, data={"nome": ""}, partial=True)
    assert not serializer.is_valid()
