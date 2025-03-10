from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from .categoria_pdde import CategoriaPdde


class AcaoPdde(ModeloIdNome):
    history = AuditlogHistoryField()
    categoria = models.ForeignKey(CategoriaPdde, on_delete=models.PROTECT)
    aceita_capital = models.BooleanField('Aceita capital?', default=False)
    aceita_custeio = models.BooleanField('Aceita custeio?', default=False)
    aceita_livre_aplicacao = models.BooleanField('Aceita livre aplicação?', default=False)

    def categoria_objeto(self):
        return self.categoria

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Ação PDDE"
        verbose_name_plural = "20.0) Ações PDDE"
        unique_together = ('nome', 'categoria')


auditlog.register(AcaoPdde)
