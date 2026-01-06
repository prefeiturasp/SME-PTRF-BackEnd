from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.paa.models import Paa, OutroRecursoPeriodoPaa


class ReceitaPrevistaOutroRecursoPeriodo(ModeloBase):
    history = AuditlogHistoryField()
    paa = models.ForeignKey(Paa, on_delete=models.PROTECT,
                            verbose_name="PAA", blank=False, null=True)
    outro_recurso_periodo = models.ForeignKey(OutroRecursoPeriodoPaa, on_delete=models.PROTECT,
                                              verbose_name="Outro Recurso Período", blank=False, null=True)
    saldo_custeio = models.DecimalField('Saldo Custeio', max_digits=20, decimal_places=2, blank=False, null=True)
    saldo_capital = models.DecimalField('Saldo Capital', max_digits=20, decimal_places=2, blank=False, null=True)
    saldo_livre = models.DecimalField('Saldo Livre Aplicação', max_digits=20, decimal_places=2, blank=False, null=True)
    previsao_valor_custeio = models.DecimalField('Previsão Valor Custeio',
                                                 max_digits=20, decimal_places=2, default=0)
    previsao_valor_capital = models.DecimalField('Previsão Valor Capital',
                                                 max_digits=20, decimal_places=2, default=0)
    previsao_valor_livre = models.DecimalField('Previsão Valor Livre Aplicação',
                                               max_digits=20, decimal_places=2, default=0)

    def unidade_nome(self):
        return self.paa.associacao.unidade.nome
    unidade_nome.short_description = "Unidade"

    def outro_recurso_objeto(self):
        return self.outro_recurso_periodo.outro_recurso

    class Meta:
        verbose_name = "Receita Prevista Outro Recurso Período"
        verbose_name_plural = "Receitas Previstas Outros Recursos Períodos"
        constraints = [
            models.UniqueConstraint(
                fields=['paa', 'outro_recurso_periodo'],
                name='unique_receita_prevista_por_outro_recurso_periodo'
            )
        ]
        ordering = ('outro_recurso_periodo__outro_recurso__nome',)


auditlog.register(ReceitaPrevistaOutroRecursoPeriodo)
