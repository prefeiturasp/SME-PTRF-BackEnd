import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r18_boletim_ocorrencia import BoletimOcorrenciaValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return BoletimOcorrenciaValidator()


def test_valida_ok_despesa_reconhecida_sem_boletim(validator):
    ctx = make_ctx(
        eh_despesa_reconhecida_pela_associacao=True,
        numero_boletim_de_ocorrencia="",
    )
    assert validator.validate(ctx) is ctx


def test_valida_ok_nao_reconhecida_com_boletim(validator):
    ctx = make_ctx(
        eh_despesa_reconhecida_pela_associacao=False,
        numero_boletim_de_ocorrencia="BO-123",
    )
    assert validator.validate(ctx) is ctx


def test_valida_erro_nao_reconhecida_sem_boletim(validator):
    ctx = make_ctx(
        eh_despesa_reconhecida_pela_associacao=False,
        numero_boletim_de_ocorrencia="",
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "numero_boletim_de_ocorrencia" in exc_info.value.detail


def test_valida_erro_nao_reconhecida_boletim_so_espacos(validator):
    ctx = make_ctx(
        eh_despesa_reconhecida_pela_associacao=False,
        numero_boletim_de_ocorrencia="   ",
    )
    with pytest.raises(DespesaValidationError):
        validator.validate(ctx)
