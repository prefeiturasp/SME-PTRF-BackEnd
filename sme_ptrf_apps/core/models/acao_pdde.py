from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from .categoria_pdde import CategoriaPdde


class AcaoPdde(ModeloIdNome):
    history = AuditlogHistoryField()
    categoria = models.ForeignKey(CategoriaPdde, on_delete=models.SET_NULL, null=True, blank=True)
    aceita_capital = models.BooleanField('Aceita capital?', default=False)
    aceita_custeio = models.BooleanField('Aceita custeio?', default=False)
    aceita_livre_aplicacao = models.BooleanField('Aceita livre aplicação?', default=False)
    saldo_valor_custeio = models.DecimalField('Saldo Valor Custeio', max_digits=20, decimal_places=2, null=True, blank=True)
    saldo_valor_capital = models.DecimalField('Saldo Valor Capital', max_digits=20, decimal_places=2, null=True, blank=True)
    saldo_valor_livre_aplicacao = models.DecimalField('Saldo Valor Livre Aplicação', max_digits=20, decimal_places=2, null=True, blank=True)
    previsao_valor_custeio = models.DecimalField('Previsão Valor Custeio', max_digits=20, decimal_places=2, null=True, blank=True)
    previsao_valor_capital = models.DecimalField('Previsão Valor Capital', max_digits=20, decimal_places=2, null=True, blank=True)
    previsao_valor_livre_aplicacao = models.DecimalField('Previsão Valor Livre Aplicação', max_digits=20, decimal_places=2, null=True, blank=True)

    def categoria_objeto(self):
        return self.categoria

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Ação PDDE"
        verbose_name_plural = "20.0) Ações PDDE"
        unique_together = ('nome', 'categoria')


auditlog.register(AcaoPdde)
