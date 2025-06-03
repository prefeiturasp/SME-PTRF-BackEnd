from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.paa.models import Paa, AcaoPdde


class ReceitaPrevistaPdde(ModeloBase):
    history = AuditlogHistoryField()
    paa = models.ForeignKey(Paa, on_delete=models.PROTECT, verbose_name="PAA", blank=False, null=True)

    acao_pdde = models.ForeignKey(AcaoPdde, on_delete=models.PROTECT,
                                  verbose_name="Ação PDDE", blank=False, null=True)

    previsao_valor_custeio = models.DecimalField('Previsão Valor Custeio', max_digits=20, decimal_places=2, default=0)

    previsao_valor_capital = models.DecimalField('Previsão Valor Capital', max_digits=20, decimal_places=2, default=0)

    previsao_valor_livre = models.DecimalField('Previsão Valor Livre Aplicação',
                                               max_digits=20, decimal_places=2, default=0)

    saldo_custeio = models.DecimalField('Saldo Custeio', max_digits=20, decimal_places=2, default=0)

    saldo_capital = models.DecimalField('Saldo Capital', max_digits=20, decimal_places=2, default=0)

    saldo_livre = models.DecimalField('Saldo Livre Aplicação', max_digits=20, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Receita Prevista PDDE"
        verbose_name_plural = "Receitas Previstas PDDE"


auditlog.register(ReceitaPrevistaPdde)
