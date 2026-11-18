import pytest

from sme_ptrf_apps.paa.api.serializers import ProgramaPddeSerializer
from sme_ptrf_apps.paa.fixtures.factories.prioridade_paa_factory import PrioridadePaaFactory

pytestmark = pytest.mark.django_db


def test_programa_pdde_list_serializer(programa_pdde):
    serializer = ProgramaPddeSerializer(programa_pdde)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'nome' in serializer.data
    assert 'pode_ser_excluida' in serializer.data


def test_pode_ser_excluida_sem_vinculos(programa_pdde_3):
    assert ProgramaPddeSerializer(programa_pdde_3).data['pode_ser_excluida'] is True


def test_pode_ser_excluida_com_acao(acao_pdde):
    assert ProgramaPddeSerializer(acao_pdde.programa).data['pode_ser_excluida'] is False


def test_pode_ser_excluida_com_prioridade_paa(programa_pdde_3):
    PrioridadePaaFactory(programa_pdde=programa_pdde_3, acao_pdde=None)
    assert ProgramaPddeSerializer(programa_pdde_3).data['pode_ser_excluida'] is False
