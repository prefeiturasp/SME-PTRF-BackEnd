from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.paa.enums import TipoCargaPaaEnum


class ModeloCargaPaa(ModeloBase):
    history = AuditlogHistoryField()

    tipo_carga = models.CharField(
        'tipo de carga',
        max_length=35,
        choices=TipoCargaPaaEnum.choices(),
        default=TipoCargaPaaEnum.MODELO_PLANO_ANUAL.name,
        unique=True,
    )
    arquivo = models.FileField(blank=True, null=True)

    class Meta:
        verbose_name = "modelo de carga"
        verbose_name_plural = "Modelos de carga"

    def __str__(self):
        try:
            return TipoCargaPaaEnum[self.tipo_carga].value if self.tipo_carga else ""
        except Exception:
            return "Modelo desconhecido"

    @classmethod
    def tipos_cargas_to_json(cls):
        return TipoCargaPaaEnum.to_dict()


auditlog.register(ModeloCargaPaa)
