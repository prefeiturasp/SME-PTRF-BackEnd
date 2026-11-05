import pytest
from datetime import date
from django.contrib import admin

from sme_ptrf_apps.core.models import Ata, Participante


pytestmark = pytest.mark.django_db


def test_instance_model(presente_ata_membro_com_data_inicio_no_cargo):
    model = presente_ata_membro_com_data_inicio_no_cargo
    assert isinstance(model, Participante)
    assert isinstance(model.ata, Ata)
    assert model.identificacao
    assert model.nome
    assert model.cargo
    assert model.membro is True
    assert model.data_inicio_no_cargo == date(2023, 1, 10)
    assert model.vago is False
    assert model.conselho_fiscal is False
    assert model.presente is True
    assert model.professor_gremio is False
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_admin():
    assert admin.site._registry[Participante]


def test_valores_padrao_data_inicio_no_cargo_e_vago(presente_ata_membro_arnaldo):
    """Sem informar os campos, data_inicio_no_cargo é None e vago é False."""
    assert presente_ata_membro_arnaldo.data_inicio_no_cargo is None
    assert presente_ata_membro_arnaldo.vago is False


def test_cargo_vago_tem_data_inicio_no_cargo(presente_ata_membro_cargo_vago):
    """Quando o cargo está vago, a data de início no cargo é informada."""
    participante = Participante.objects.get(id=presente_ata_membro_cargo_vago.id)
    assert participante.vago is True
    assert participante.data_inicio_no_cargo == date(2024, 3, 25)


def test_cargo_ocupado_com_data_inicio_no_cargo(presente_ata_membro_com_data_inicio_no_cargo):
    """Cargo ocupado (vago=False) pode ter data de início no cargo."""
    participante = Participante.objects.get(id=presente_ata_membro_com_data_inicio_no_cargo.id)
    assert participante.vago is False
    assert participante.data_inicio_no_cargo == date(2023, 1, 10)


def test_cargo_ocupado_sem_data_inicio_no_cargo(presente_ata_membro_sem_data_inicio_no_cargo):
    """Cargo ocupado (vago=False) nem sempre tem data de início no cargo."""
    participante = Participante.objects.get(id=presente_ata_membro_sem_data_inicio_no_cargo.id)
    assert participante.vago is False
    assert participante.data_inicio_no_cargo is None


def test_atualiza_data_inicio_no_cargo_e_vago(presente_ata_membro_sem_data_inicio_no_cargo):
    """Os campos data_inicio_no_cargo e vago são persistidos ao salvar."""
    presente_ata_membro_sem_data_inicio_no_cargo.vago = True
    presente_ata_membro_sem_data_inicio_no_cargo.data_inicio_no_cargo = date(2024, 5, 2)
    presente_ata_membro_sem_data_inicio_no_cargo.save()

    participante = Participante.objects.get(id=presente_ata_membro_sem_data_inicio_no_cargo.id)
    assert participante.vago is True
    assert participante.data_inicio_no_cargo == date(2024, 5, 2)
