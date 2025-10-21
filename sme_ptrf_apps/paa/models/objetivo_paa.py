from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class StatusChoices(models.IntegerChoices):
    ATIVO = 1, "Ativo"
    INATIVO = 0, "Inativo"

    @classmethod
    def to_dict(cls):
        return [dict(key=key.value, value=key.label) for key in cls]


class ObjetivoPaa(ModeloBase):
    history = AuditlogHistoryField()
    nome = models.CharField('Objetivo', max_length=160, unique=True, blank=False)
    paa = models.ForeignKey('paa.Paa', on_delete=models.PROTECT, verbose_name="PAA", blank=True, null=True)
    status = models.BooleanField(choices=StatusChoices.choices, default=StatusChoices.ATIVO)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Objetivo do PAA"
        verbose_name_plural = "Objetivos do PAA"


auditlog.register(ObjetivoPaa)
