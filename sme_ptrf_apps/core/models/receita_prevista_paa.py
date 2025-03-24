from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from .acao_associacao import AcaoAssociacao


class ReceitaPrevistaPaa(ModeloBase):
    history = AuditlogHistoryField()
    acao_associacao = models.ForeignKey(AcaoAssociacao, on_delete=models.PROTECT,
                                        verbose_name="Ação de Associação", blank=False, null=True)

    previsao_valor_custeio = models.DecimalField('Previsão Valor Custeio',
                                                 max_digits=20, decimal_places=2, default=0)

    previsao_valor_capital = models.DecimalField('Previsão Valor Capital',
                                                 max_digits=20, decimal_places=2, default=0)

    previsao_valor_livre = models.DecimalField('Previsão Valor Livre Aplicação',
                                               max_digits=20, decimal_places=2, default=0)

    def acao_associacao_objeto(self):
        return self.acao_associacao
    
    # def __str__(self):
    #     return self.acao_associacao or ''

    class Meta:
        verbose_name = "Receita Prevista PAA"
        verbose_name_plural = "21.0) Receitas Previstas PAA"


auditlog.register(ReceitaPrevistaPaa)
