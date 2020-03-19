from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class RateioDespesa(ModeloBase):
    despesa = models.ForeignKey('Despesa', on_delete=models.CASCADE, related_name='rateios', blank=True, null=True)

    associacao = models.ForeignKey('core.Associacao', on_delete=models.PROTECT, related_name='rateios_associacao',
                                   blank=True, null=True)

    conta_associacao = models.ForeignKey('core.ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='rateios_da_conta', blank=True, null=True)

    acao = models.ForeignKey('core.Acao', on_delete=models.PROTECT, blank=True, null=True)

    tipo_aplicacao_recurso = models.ForeignKey('TipoAplicacaoRecurso', on_delete=models.PROTECT, blank=True, null=True)

    tipo_custeio = models.ForeignKey('TipoCusteio', on_delete=models.PROTECT, blank=True, null=True)

    especificacao_material_servico = models.ForeignKey('EspecificacaoMaterialServico', on_delete=models.PROTECT,
                                                       blank=True, null=True)

    valor_rateio = models.DecimalField('Valor', max_digits=8, decimal_places=2, default=0)

    quantidade_itens_capital = models.PositiveSmallIntegerField('Quantidade de itens', default=0)
    valor_item_capital = models.DecimalField('Valor unitário ', max_digits=8, decimal_places=2, default=0)
    numero_processo_incorporacao_capital = models.CharField('Nº processo incorporação', max_length=100, default='', blank=True)

    def __str__(self):
        documento = self.despesa.numero_documento if self.despesa else 'Despesa indefinida'
        return f"{documento} - {self.valor_rateio:.2f}"

    class Meta:
        verbose_name = "Rateio de despesa"
        verbose_name_plural = "Rateios de despesas"
