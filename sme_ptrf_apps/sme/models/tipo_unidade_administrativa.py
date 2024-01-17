from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class TipoUnidadeAdministrativa(ModeloBase):
    history = AuditlogHistoryField()

    tipo_unidade_administrativa = models.PositiveIntegerField(verbose_name='Tipo unidade administrativa')
    inicio_codigo_eol = models.CharField(
        verbose_name='Inicio do código eol que deve ser validado',
        max_length=6,
        blank=True,
        help_text='Deixe vazio para considerar qualquer código eol'
    )

    class Meta:
        verbose_name = 'Tipo unidade administrativa'
        verbose_name_plural = '02.0) Tipos unidades administrativas'
        unique_together = ('tipo_unidade_administrativa',)

    def __str__(self):
        return f'Tipo unidade: {self.tipo_unidade_administrativa} - codigol eol: {self.inicio_codigo_eol}'

    @property
    def possui_codigo_eol(self):
        return True if self.inicio_codigo_eol else False


auditlog.register(TipoUnidadeAdministrativa)
