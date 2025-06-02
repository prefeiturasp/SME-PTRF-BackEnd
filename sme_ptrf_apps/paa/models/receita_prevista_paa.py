from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.core.models.acao_associacao import AcaoAssociacao
from sme_ptrf_apps.paa.models import Paa


class ReceitaPrevistaPaa(ModeloBase):
    history = AuditlogHistoryField()
    paa = models.ForeignKey(Paa, on_delete=models.PROTECT,
                            verbose_name="PAA", blank=False, null=True)
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

    class Meta:
        verbose_name = "Receita Prevista do PAA"
        verbose_name_plural = "Receitas Previstas do PAA"


auditlog.register(ReceitaPrevistaPaa)
