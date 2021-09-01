from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class TecnicoDre(ModeloBase):
    history = AuditlogHistoryField()
    dre = models.ForeignKey('core.Unidade', on_delete=models.PROTECT, related_name='tecnicos_da_dre', to_field="codigo_eol",
                            blank=True, null=True, limit_choices_to={'tipo_unidade': 'DRE'})

    nome = models.CharField('Nome', max_length=160)

    rf = models.CharField('RF', max_length=10, blank=True, null=True, default="", unique=True)

    email = models.EmailField("E-mail", max_length=254, blank=True, default='')

    telefone = models.CharField('Telefone', max_length=20, blank=True, default='')

    class Meta:
        verbose_name = "Técnico de DRE"
        verbose_name_plural = "Técnicos de DREs"

    def __str__(self):
        return f"Nome: {self.nome}, RF: {self.rf}"


auditlog.register(TecnicoDre)
