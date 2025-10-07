import pytest

from django.db import IntegrityError, transaction

from sme_ptrf_apps.paa.models import ObjetivoPaa
from sme_ptrf_apps.paa.models.objetivo_paa import StatusChoices


@pytest.mark.django_db
def test_criacao_objetivo_paa(objetivo_paa_factory):
    objetivo_paa_factory.create(status=1)
    objetivo_paa_factory.create(status=0)
    assert ObjetivoPaa.objects.filter(status=True).count() == 1
    assert ObjetivoPaa.objects.filter(status=False).count() == 1


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


@pytest.mark.django_db
def test_status_pode_ser_sim_ou_nao(objetivo_paa_factory):
    objetivo_sim = objetivo_paa_factory.create(
        nome="Objetivo ATIVO",
        status=StatusChoices.ATIVO,
    )
    objetivo_nao = objetivo_paa_factory.create(
        nome="Objetivo INATIVO",
        status=StatusChoices.INATIVO,
    )

    assert objetivo_sim.status == StatusChoices.ATIVO
    assert objetivo_nao.status == StatusChoices.INATIVO


@pytest.mark.django_db
def test_nome_deve_ser_unico(objetivo_paa_factory):
    objetivo_paa_factory.create(nome="Único")
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            objetivo_paa_factory.create(nome="Único")

    assert ObjetivoPaa.objects.filter(nome="Único").count() == 1
