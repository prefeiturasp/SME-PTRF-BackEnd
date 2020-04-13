import re

from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError

from brazilnum.cnpj import validate_cnpj

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
