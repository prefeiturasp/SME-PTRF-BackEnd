from django.db import models

from sme_ptrf_apps.core.models import Associacao, Periodo
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class Repasse(ModeloBase):
    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, related_name='repasses', 
                                   blank=True, null=True)

    valor_capital = models.DecimalField('Valor Capital', max_digits=20, decimal_places=2, default=0)

    valor_custeio = models.DecimalField('Valor Custeio', max_digits=20, decimal_places=2, default=0)

    conta_associacao = models.ForeignKey('core.ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='repasses_da_conta', blank=True, null=True)

    acao_associacao = models.ForeignKey('core.AcaoAssociacao', on_delete=models.PROTECT,
                                        related_name='repasses_da_associacao', blank=True, null=True)

    periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, 
                                related_name='+', blank=True, null=True)

    class Meta:
        verbose_name = 'Repasse'
        verbose_name_plural = 'Repasses'

    def __str__(self):
        return f'Repasse<val_capital: {self.valor_capital}, val_custeio: {self.valor_custeio}>'
