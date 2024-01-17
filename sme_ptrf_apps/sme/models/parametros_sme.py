from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase, SingletonModel
from django.core.exceptions import ValidationError
import re

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


def validate_tipos_unidade(value):
    # Verifica se o valor corresponde ao padrão: dígito, vírgula, dígito, vírgula, ...

    if not re.match(r'^\d+(\,\d+)*$', value):
        raise ValidationError('O campo deve seguir o padrão "0, 00, 00" ou ser um único dígito.')


class ParametrosSme(SingletonModel, ModeloBase):
    history = AuditlogHistoryField()

    valida_unidades_login = models.BooleanField('Valida unidades ao logar', default=False)

    def __str__(self):
        return 'Parâmetros SME do PTRF'

    class Meta:
        verbose_name = "Parâmetro SME"
        verbose_name_plural = "01.0) Parâmetros SME"


auditlog.register(ParametrosSme)
