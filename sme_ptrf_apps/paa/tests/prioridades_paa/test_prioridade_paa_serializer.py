import pytest

from sme_ptrf_apps.paa.api.serializers import PrioridadePaaCreateUpdateSerializer, PrioridadePaaListSerializer
from sme_ptrf_apps.paa.fixtures.factories import PrioridadePaaFactory
from rest_framework.exceptions import ValidationError
from sme_ptrf_apps.paa.models.prioridade_paa import SimNaoChoices
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum

pytestmark = pytest.mark.django_db


def test_prioridade_paa_list_default_serializer(paa):
    prioridade = PrioridadePaaFactory(paa=paa)
    serializer = PrioridadePaaListSerializer(prioridade)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'paa' in serializer.data
    assert 'prioridade' in serializer.data
    assert 'recurso' in serializer.data
    assert 'acao_associacao' in serializer.data
    assert 'programa_pdde' in serializer.data
    assert 'acao_pdde' in serializer.data
    assert 'tipo_aplicacao' in serializer.data
    assert 'tipo_despesa_custeio' in serializer.data
    assert 'especificacao_material' in serializer.data
    assert 'valor_total' in serializer.data


def test_prioridade_paa_create_sem_paa():
    prioridade = {}
    with pytest.raises(ValidationError):
        PrioridadePaaCreateUpdateSerializer().validate(prioridade)


def test_prioridade_paa_com_recurso_ptrf_capital(paa):
    prioridade = {
        "paa": str(paa.uuid),
        "prioridade": SimNaoChoices.SIM,
        "recurso": RecursoOpcoesEnum.PTRF.name,
        "tipo_aplicacao": TipoAplicacaoOpcoesEnum.CAPITAL.name,
        # "acao_associacao": "9b3a5413-de6c-4c0d-bfb0-5e2215d16b69",
        "valor_total": 20
    }
    with pytest.raises(ValidationError):
        # PTRF/CAPITAL requer acao_associacao
        PrioridadePaaCreateUpdateSerializer().validate(prioridade)


def test_prioridade_paa_sem_valor(paa):
    """
        Validação inicial aceita valor None para avaliações de próximas features
        relacionadas a duplicação e importação de prioridades que não possuírão valor por padrao
    """
    prioridade = {
        "paa": str(paa.uuid),
        "prioridade": SimNaoChoices.SIM,
        "recurso": RecursoOpcoesEnum.RECURSO_PROPRIO.name,
        "tipo_aplicacao": TipoAplicacaoOpcoesEnum.CAPITAL.name,
        "valor_total": None
    }
    with pytest.raises(ValidationError):
        # requer valor
        PrioridadePaaCreateUpdateSerializer().validate(prioridade)


def test_prioridade_paa_com_recurso_ptrf_custeio(paa):
    prioridade = {
        "paa": str(paa.uuid),
        "prioridade": SimNaoChoices.SIM,
        "recurso": RecursoOpcoesEnum.PTRF.name,
        "tipo_aplicacao": TipoAplicacaoOpcoesEnum.CUSTEIO.name,
        "acao_associacao": "9b3a5413-de6c-4c0d-bfb0-5e2215d16b69",
        # "tipo_despesa_custeio": "14d11302-226e-4f8c-9fc4-be6a48ec0728",
        "valor_total": 20
    }
    with pytest.raises(ValidationError):
        # CUSTEIO requer tipo_despesa_custeio
        PrioridadePaaCreateUpdateSerializer().validate(prioridade)


def test_prioridade_paa_com_recurso_pdde_custeio_sem_programa_pdde(paa):
    prioridade = {
        "paa": str(paa.uuid),
        "prioridade": SimNaoChoices.SIM,
        "recurso": RecursoOpcoesEnum.PDDE.name,
        "tipo_aplicacao": TipoAplicacaoOpcoesEnum.CUSTEIO.name,
        "acao_associacao": "9b3a5413-de6c-4c0d-bfb0-5e2215d16b69",
        "tipo_despesa_custeio": "14d11302-226e-4f8c-9fc4-be6a48ec0728",
        # "programa_pdde": "1de0c2ac-8468-48a6-89e8-14ffa0d78133",
        "acao_pdde": "ea1b7457-93dd-4abe-aa21-95744921bb59",
        "especificacao_material": "93ac0bdd-5bda-4fc8-a409-3a8ff38a9f74",
        "valor_total": 20
    }
    with pytest.raises(ValidationError):
        # PDDE/CUSTEIO requer programa_pdde
        PrioridadePaaCreateUpdateSerializer().validate(prioridade)


def test_prioridade_paa_com_recurso_pdde_custeio_sem_acao_pdde(paa):
    prioridade = {
        "paa": str(paa.uuid),
        "prioridade": SimNaoChoices.SIM,
        "recurso": RecursoOpcoesEnum.PDDE.name,
        "tipo_aplicacao": TipoAplicacaoOpcoesEnum.CUSTEIO.name,
        "acao_associacao": "9b3a5413-de6c-4c0d-bfb0-5e2215d16b69",
        "tipo_despesa_custeio": "14d11302-226e-4f8c-9fc4-be6a48ec0728",
        "programa_pdde": "1de0c2ac-8468-48a6-89e8-14ffa0d78133",
        # "acao_pdde": "ea1b7457-93dd-4abe-aa21-95744921bb59",
        "especificacao_material": "93ac0bdd-5bda-4fc8-a409-3a8ff38a9f74",
        "valor_total": 20
    }
    with pytest.raises(ValidationError):
        # PDDE/CUSTEIO requer acao_pdde
        PrioridadePaaCreateUpdateSerializer().validate(prioridade)


def test_prioridade_paa_com_recurso_pdde_capital_sem_material_servico(paa):
    prioridade = {
        "paa": str(paa.uuid),
        "prioridade": SimNaoChoices.SIM,
        "recurso": RecursoOpcoesEnum.PDDE.name,
        "tipo_aplicacao": TipoAplicacaoOpcoesEnum.CAPITAL.name,
        "programa_pdde": "1de0c2ac-8468-48a6-89e8-14ffa0d78133",
        "acao_pdde": "ea1b7457-93dd-4abe-aa21-95744921bb59",
        # "especificacao_material": "93ac0bdd-5bda-4fc8-a409-3a8ff38a9f74",
        "valor_total": 20
    }
    with pytest.raises(ValidationError):
        # PDDE/CUSTEIO requer acao_pdde
        PrioridadePaaCreateUpdateSerializer().validate(prioridade)


def test_prioridade_paa_com_recurso_proprio_capital_sem_saldo(paa):
    try:
        prioridade = {
            "paa": paa,
            "prioridade": SimNaoChoices.SIM,
            "recurso": RecursoOpcoesEnum.RECURSO_PROPRIO.name,
            "tipo_aplicacao": TipoAplicacaoOpcoesEnum.CAPITAL.name,
            "especificacao_material": "93ac0bdd-5bda-4fc8-a409-3a8ff38a9f74",
            "valor_total": 20
        }
        PrioridadePaaCreateUpdateSerializer().validate(prioridade)
    except Exception as ex:
        assert 'O valor indicado para a prioridade excede o valor disponível de receita prevista.' in str(ex)
