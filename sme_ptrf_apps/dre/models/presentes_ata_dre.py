from sme_ptrf_apps.core.models_abstracts import ModeloBase
from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class PresenteAtaDre(ModeloBase):
    history = AuditlogHistoryField()

    ata = models.ForeignKey('AtaParecerTecnico', on_delete=models.CASCADE, related_name='presentes_na_ata')
    rf = models.CharField('RF', max_length=10)
    nome = models.CharField('Nome', max_length=200, blank=True, default='')
    cargo = models.CharField('Cargo', max_length=200, blank=True, default='', null=True)

    @property
    def editavel(self):
        return False

    def __str__(self):
        return f"RF: {self.rf} Nome: {self.nome} Ata: {self.ata}>"

    class Meta:
        verbose_name = "Presente da ata DRE"
        verbose_name_plural = "Presentes das atas DRE"


auditlog.register(PresenteAtaDre)
