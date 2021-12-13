from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from sme_ptrf_apps.core.models_abstracts import TemCriadoEm, TemAlteradoEm
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class AnoAnaliseRegularidade(TemCriadoEm, TemAlteradoEm):
    history = AuditlogHistoryField()
    lookup_field = 'ano'
    ano = models.PositiveSmallIntegerField(
        'Ano de análise de regularidade',
        default=2020,
        validators=[MaxValueValidator(2099), MinValueValidator(2000)],
        unique=True
    )

    class Meta:
        verbose_name = 'Ano de análise de regularidade'
        verbose_name_plural = 'Anos de análise de regularidade'

    def __str__(self):
        return f'{self.ano}'


auditlog.register(AnoAnaliseRegularidade)
