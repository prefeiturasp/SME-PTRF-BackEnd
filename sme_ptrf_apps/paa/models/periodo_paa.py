from django.db import models
from django.core.exceptions import ValidationError

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class PeriodoPaa(ModeloBase):
    history = AuditlogHistoryField()
    referencia = models.CharField('Referência do período', max_length=150)
    data_inicial = models.DateField(verbose_name='Data de início do período')
    data_final = models.DateField(verbose_name='Data de término do período')

    class Meta:
        verbose_name = 'Período PAA'
        verbose_name_plural = 'Períodos PAA'

    def __str__(self):
        return self.referencia


    def clean(self):
        super().clean()

        # Verificar se a data final é menor que a data inicial
        if self.data_final < self.data_inicial:
            raise ValidationError('A data final não pode ser menor que a data inicial')

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)


auditlog.register(PeriodoPaa)
