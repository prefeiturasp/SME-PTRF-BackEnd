import re
from typing import Any

from django.core import validators
from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError

PESOS_DV_CNPJ: list[int] = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
CNPJ_ZERADO: str = '00000000000000'
CNPJ_REGEX_SEM_MASCARA: re.Pattern[str] = re.compile(r'^[A-Z0-9]{12}\d{2}$')
CNPJ_REGEX_COM_MASCARA: re.Pattern[str] = re.compile(
    r'^[A-Z0-9]{2}\.[A-Z0-9]{3}\.[A-Z0-9]{3}/[A-Z0-9]{4}-\d{2}$',
    re.IGNORECASE,
)


def _char_value_cnpj(caractere: str) -> int:
    return ord(caractere.upper()) - 48


def _remove_mascara_cnpj(value: str) -> str:
    return re.sub(r'[.\-/]', '', value).upper()


def _calcula_dv_cnpj(base_12: str) -> str:
    somatorio_dv1 = sum(
        _char_value_cnpj(caractere) * PESOS_DV_CNPJ[indice + 1]
        for indice, caractere in enumerate(base_12)
    )
    dv1 = 0 if somatorio_dv1 % 11 < 2 else 11 - (somatorio_dv1 % 11)

    somatorio_dv2 = sum(
        _char_value_cnpj(caractere) * PESOS_DV_CNPJ[indice]
        for indice, caractere in enumerate(base_12)
    )
    somatorio_dv2 += dv1 * PESOS_DV_CNPJ[12]
    dv2 = 0 if somatorio_dv2 % 11 < 2 else 11 - (somatorio_dv2 % 11)

    return f'{dv1}{dv2}'


def is_cnpj_valid(value: str | None) -> bool:
    if not value:
        return False

    cnpj = _remove_mascara_cnpj(value)

    if cnpj == CNPJ_ZERADO:
        return False

    if not CNPJ_REGEX_SEM_MASCARA.match(cnpj):
        return False

    return cnpj[-2:] == _calcula_dv_cnpj(cnpj[:12])


def format_cnpj(value: str) -> str:
    cnpj = _remove_mascara_cnpj(value)
    return f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}'


def cnpj_validation(value: Any) -> str:
    """
    CNPJ válido no formato XX.XXX.XXX/XXXX-XX (numérico ou alfanumérico).
    """

    if value in EMPTY_VALUES:
        return ''

    value = str(value).upper()

    if not CNPJ_REGEX_COM_MASCARA.match(value):
        raise ValidationError("Digite CNPJ no formato XX.XXX.XXX/XXXX-XX.")

    if not is_cnpj_valid(value):
        raise ValidationError("Número de CNPJ inválido.")

    return value


cep_validation = validators.RegexValidator(
    regex=r"^\d{5}-\d{3}$", message="Digite o CEP no formato XXXXX-XXX. Com 8 digitos"
)

phone_validation = validators.RegexValidator(
    regex=r"^\(\d{2}\) [\d\-]{9,10}$",
    message="Digite o telefone no formato (XX) 12345-6789. Entre 8 ou 9 digitos",
)
