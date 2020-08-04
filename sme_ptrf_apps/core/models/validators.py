import re

from brazilnum.cnpj import validate_cnpj
from django.core import validators
from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError


def cnpj_validation(value):
    """
    CNPJ válido no formato XX.XXX.XXX/XXXX-XX
    :type value: object
    """

    if value in EMPTY_VALUES:
        return u''

    pattern = re.compile("(^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$)")
    if not pattern.match(value):
        raise ValidationError("Digite CNPJ no formato XX.XXX.XXX/XXXX-XX.")

    if not validate_cnpj(value):
        raise ValidationError("Número de CNPJ inválido.")

    return value


cep_validation = validators.RegexValidator(
    regex=r"^\d{5}-\d{3}$", message="Digite o CEP no formato XXXXX-XXX. Com 8 digitos"
)

phone_validation = validators.RegexValidator(
    regex=r"^\(\d{2}\) [\d\-]{9,10}$",
    message="Digite o telefone no formato (XX) 12345-6789. Entre 8 ou 9 digitos",
)
