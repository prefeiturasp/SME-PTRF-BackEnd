from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class AnaliseValorReprogramadoPrestacaoConta(ModeloBase):
    analise_prestacao_conta = models.ForeignKey('AnalisePrestacaoConta', on_delete=models.CASCADE,
                                                related_name='analises_de_valores_reprogramados')

    conta_associacao = models.ForeignKey('ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='analises_de_valores_reprogramados_da_conta')

    acao_associacao = models.ForeignKey('AcaoAssociacao', on_delete=models.PROTECT,
                                        related_name='analises_de_valores_reprogramados_da_acao')

    valor_saldo_reprogramado_correto = models.BooleanField("O valor de saldo reprogramado inicial está correto?",
                                                           default=True)

    novo_saldo_reprogramado_custeio = models.DecimalField('Novo Saldo Reprogramado (Custeio)', max_digits=12,
                                                          decimal_places=2, null=True, default=None)

    novo_saldo_reprogramado_capital = models.DecimalField('Novo Saldo Reprogramado (Capital)', max_digits=12,
                                                          decimal_places=2, null=True, default=None)

    novo_saldo_reprogramado_livre = models.DecimalField('Novo Saldo Reprogramado (livre)', max_digits=12,
                                                        decimal_places=2, null=True, default=None)

    def __str__(self):
        return f"Análise de valores reprogramados Conta {self.conta_associacao} - Ação {self.acao_associacao}"

    class Meta:
        verbose_name = "Análise de valor reprogramado de PC"
        verbose_name_plural = "16.8) Análises de valores reprogramados de PC"
        unique_together = ['analise_prestacao_conta', 'conta_associacao', 'acao_associacao', ]
