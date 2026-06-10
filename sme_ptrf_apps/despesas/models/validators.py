import re
from typing import Any

from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError

from sme_ptrf_apps.core.models.validators import is_cnpj_valid

CPF_REGEX: re.Pattern[str] = re.compile(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
CNPJ_REGEX: re.Pattern[str] = re.compile(
    r'^[A-Z0-9]{2}\.[A-Z0-9]{3}\.[A-Z0-9]{3}/[A-Z0-9]{4}-\d{2}$',
    re.IGNORECASE,
)


def cpf_cnpj_validation(value: Any) -> str:
    if value in EMPTY_VALUES:
        return ''

    value = str(value)
    value_cnpj = value.upper()

    if CPF_REGEX.match(value):
        return value

    if CNPJ_REGEX.match(value_cnpj):
        if not is_cnpj_valid(value_cnpj):
            raise ValidationError("Número de CNPJ inválido.")
        return value_cnpj

    raise ValidationError(
        "Digite o CPF ou CNPJ no formato XX.XXX.XXX/XXXX-XX ou XXX.XXX.XXX-XX."
    )
