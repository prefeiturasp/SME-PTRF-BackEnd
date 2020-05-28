from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class DemonstrativoFinanceiro(ModeloBase):

    acao_associacao = models.ForeignKey('core.AcaoAssociacao', on_delete=models.PROTECT,
                                        related_name='demonstrativo_financeiro', blank=True, null=True)
    class Meta:
        verbose_name = 'Demonstrativo Financeiro'
        verbose_name_plural = 'Demonstrativos Financeiros'

    def __str__(self):
        return f"Documento gerado dia {self.criado_em.strftime('%d/%m/%Y %H:%S')}"
