import pytest
from django.forms import ValidationError

from sme_ptrf_apps.core.models.validators import (
    cnpj_validation,
    format_cnpj,
    is_cnpj_valid,
)
from sme_ptrf_apps.despesas.models.validators import cpf_cnpj_validation

pytestmark = pytest.mark.django_db

CNPJ_NUMERICO_VALIDO = '12.345.678/0001-95'
CNPJ_NUMERICO_VALIDO_SEM_MASCARA = '12345678000195'
CNPJ_ALFANUMERICO_VALIDO = 'AB.12C.D34/EF56-02'
CNPJ_ALFANUMERICO_VALIDO_SEM_MASCARA = 'AB12CD34EF5602'
CPF_VALIDO = '123.456.789-09'


@pytest.mark.parametrize(
    'cnpj',
    [
        CNPJ_NUMERICO_VALIDO,
        CNPJ_NUMERICO_VALIDO_SEM_MASCARA,
        CNPJ_ALFANUMERICO_VALIDO,
        CNPJ_ALFANUMERICO_VALIDO_SEM_MASCARA,
        'ab.12c.d34/ef56-02',
    ],
)
def test_is_cnpj_valid_aceita_cnpj_numerico_e_alfanumerico(cnpj: str) -> None:
    assert is_cnpj_valid(cnpj) is True


@pytest.mark.parametrize(
    'cnpj',
    [
        '',
        '00000000000000',
        '11.111.111/1111-11',
        'AB.12C.D34/EF56-99',
        '123',
        '12.345.678/0001-00',
    ],
)
def test_is_cnpj_valid_rejeita_cnpj_invalido(cnpj: str) -> None:
    assert is_cnpj_valid(cnpj) is False


def test_format_cnpj_aplica_mascara_e_uppercase() -> None:
    assert format_cnpj(CNPJ_ALFANUMERICO_VALIDO_SEM_MASCARA) == CNPJ_ALFANUMERICO_VALIDO
    assert format_cnpj('12345678000195') == CNPJ_NUMERICO_VALIDO


def test_cnpj_validation_retorna_valor_em_maiusculo() -> None:
    assert cnpj_validation('ab.12c.d34/ef56-02') == CNPJ_ALFANUMERICO_VALIDO


def test_cnpj_validation_rejeita_formato_invalido() -> None:
    with pytest.raises(ValidationError, match='Digite CNPJ no formato'):
        cnpj_validation('123')


def test_cnpj_validation_rejeita_dv_invalido() -> None:
    with pytest.raises(ValidationError, match='Número de CNPJ inválido'):
        cnpj_validation('AB.12C.D34/EF56-99')


def test_cpf_cnpj_validation_aceita_cpf_e_cnpj() -> None:
    assert cpf_cnpj_validation(CPF_VALIDO) == CPF_VALIDO
    assert cpf_cnpj_validation(CNPJ_NUMERICO_VALIDO) == CNPJ_NUMERICO_VALIDO
    assert cpf_cnpj_validation('ab.12c.d34/ef56-02') == CNPJ_ALFANUMERICO_VALIDO


def test_cpf_cnpj_validation_rejeita_valor_invalido() -> None:
    with pytest.raises(ValidationError):
        cpf_cnpj_validation('valor-invalido')
