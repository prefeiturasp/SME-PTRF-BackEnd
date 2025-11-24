import pytest

from django.db import IntegrityError, transaction

from sme_ptrf_apps.paa.models import AtividadeEstatutaria
from sme_ptrf_apps.paa.choices import StatusChoices, Mes
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum


@pytest.mark.django_db
def test_criacao(atividade_estatutaria_factory):
    atividade_estatutaria_factory.create(
        status=StatusChoices.ATIVO,
        mes=Mes.JANEIRO,
        tipo=TipoAtividadeEstatutariaEnum.ORDINARIA.name,
        paa=None)
    atividade_estatutaria_factory.create(
        status=StatusChoices.INATIVO,
        mes=Mes.FEVEREIRO,
        tipo=TipoAtividadeEstatutariaEnum.EXTRAORDINARIA.name,
        paa=None
    )
    assert AtividadeEstatutaria.objects.filter(
        status=True,
        mes=Mes.JANEIRO,
        tipo=TipoAtividadeEstatutariaEnum.ORDINARIA.name
    ).exists()
    assert AtividadeEstatutaria.objects.filter(
        status=False,
        mes=Mes.FEVEREIRO,
        tipo=TipoAtividadeEstatutariaEnum.EXTRAORDINARIA.name
    ).exists()


def test_simnao_choices_values():
    assert StatusChoices.ATIVO == 1
    assert StatusChoices.INATIVO == 0
    assert StatusChoices(1).label == "Ativo"
    assert StatusChoices(0).label == "Inativo"


def test_simnao_choices_to_dict():
    dict_esperado = [
        {"key": 1, "value": "Ativo"},
        {"key": 0, "value": "Inativo"}
    ]
    assert StatusChoices.to_dict() == dict_esperado


def test_mes_choices_values():
    assert Mes.JANEIRO == 1 and Mes(1).label == "Janeiro"
    assert Mes.FEVEREIRO == 2 and Mes(2).label == "Fevereiro"
    assert Mes.MARCO == 3 and Mes(3).label == "Março"
    assert Mes.ABRIL == 4 and Mes(4).label == "Abril"
    assert Mes.MAIO == 5 and Mes(5).label == "Maio"
    assert Mes.JUNHO == 6 and Mes(6).label == "Junho"
    assert Mes.JULHO == 7 and Mes(7).label == "Julho"
    assert Mes.AGOSTO == 8 and Mes(8).label == "Agosto"
    assert Mes.SETEMBRO == 9 and Mes(9).label == "Setembro"
    assert Mes.OUTUBRO == 10 and Mes(10).label == "Outubro"
    assert Mes.NOVEMBRO == 11 and Mes(11).label == "Novembro"
    assert Mes.DEZEMBRO == 12 and Mes(12).label == "Dezembro"


def test_mes_choices_to_dict():
    dict_esperado = [
        {"key": 1, "value": "Janeiro"},
        {"key": 2, "value": "Fevereiro"},
        {"key": 3, "value": "Março"},
        {"key": 4, "value": "Abril"},
        {"key": 5, "value": "Maio"},
        {"key": 6, "value": "Junho"},
        {"key": 7, "value": "Julho"},
        {"key": 8, "value": "Agosto"},
        {"key": 9, "value": "Setembro"},
        {"key": 10, "value": "Outubro"},
        {"key": 11, "value": "Novembro"},
        {"key": 12, "value": "Dezembro"},
    ]
    assert Mes.to_dict() == dict_esperado


def test_tipo_choices_values():
    assert TipoAtividadeEstatutariaEnum.ORDINARIA.name == "ORDINARIA" and \
        TipoAtividadeEstatutariaEnum.ORDINARIA.value == "Reuniões Ordinárias"

    assert TipoAtividadeEstatutariaEnum.EXTRAORDINARIA.name == "EXTRAORDINARIA" and \
        TipoAtividadeEstatutariaEnum.EXTRAORDINARIA.value == "Reuniões Extraordinárias"


def test_tipo_choices_to_dict():
    dict_esperado = [
        {"key": "ORDINARIA", "value": "Reuniões Ordinárias"},
        {"key": "EXTRAORDINARIA", "value": "Reuniões Extraordinárias"},
    ]
    assert TipoAtividadeEstatutariaEnum.to_dict() == dict_esperado


@pytest.mark.django_db
def test_status_pode_ser_ativo_inativo(atividade_estatutaria_factory):
    atividade_ativo = atividade_estatutaria_factory.create(
        nome="atividade ATIVO",
        status=StatusChoices.ATIVO,
        paa=None
    )
    atividade_inativo = atividade_estatutaria_factory.create(
        nome="atividade INATIVO",
        status=StatusChoices.INATIVO,
        paa=None
    )

    assert atividade_ativo.status == StatusChoices.ATIVO
    assert atividade_inativo.status == StatusChoices.INATIVO


@pytest.mark.django_db
def test_mes_pode_ser_1_a_12(atividade_estatutaria_factory):
    atividades = []
    for mes in range(1, 13):
        atividades.append(atividade_estatutaria_factory.create(
            nome=f"atividade {mes}",
            status=StatusChoices.ATIVO,
            mes=mes,
            paa=None
        ))
    for atividade in atividades:
        assert atividade.mes in range(1, 13)

    assert len(atividades) == 12


@pytest.mark.django_db
def test_nome_mes_tipo_devem_ser_unico(atividade_estatutaria_factory):
    atividade_estatutaria_factory.create(
        nome="Único",
        mes=Mes.JANEIRO,
        tipo=TipoAtividadeEstatutariaEnum.ORDINARIA.name,
        paa=None),

    atividade_estatutaria_factory.create(
        nome="Único",
        mes=Mes.FEVEREIRO,
        tipo=TipoAtividadeEstatutariaEnum.EXTRAORDINARIA.name,
        paa=None)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            atividade_estatutaria_factory.create(
                nome="Único",
                mes=Mes.JANEIRO,
                tipo=TipoAtividadeEstatutariaEnum.ORDINARIA.name,
                paa=None)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            atividade_estatutaria_factory.create(
                nome="Único",
                mes=Mes.FEVEREIRO,
                tipo=TipoAtividadeEstatutariaEnum.EXTRAORDINARIA.name,
                paa=None)

    assert AtividadeEstatutaria.objects.filter(tipo=TipoAtividadeEstatutariaEnum.ORDINARIA.name).count() == 1
    assert AtividadeEstatutaria.objects.filter(tipo=TipoAtividadeEstatutariaEnum.EXTRAORDINARIA.name).count() == 1
