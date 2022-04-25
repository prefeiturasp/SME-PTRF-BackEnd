from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class TipoDocumento(ModeloIdNome):
    history = AuditlogHistoryField()
    apenas_digitos = models.BooleanField("Apenas dígitos?", default=False)
    numero_documento_digitado = models.BooleanField("Solicitar a digitação do número do documento?", default=False)
    pode_reter_imposto = models.BooleanField('Habilita o preenchimento do imposto', default=False)
    eh_documento_de_retencao_de_imposto = models.BooleanField('Documento relativo ao imposto recolhido', default=False)
    documento_comprobatorio_de_despesa = models.BooleanField('Documento comprobatório de despesa', default=True)

    class Meta:
        verbose_name = "Tipo de documento"
        verbose_name_plural = "Tipos de documento"


auditlog.register(TipoDocumento)
