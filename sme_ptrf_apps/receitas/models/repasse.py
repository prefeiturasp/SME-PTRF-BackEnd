from enum import Enum

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models import Associacao, Periodo
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class StatusRepasse(Enum):
    PENDENTE = 'Pendente'
    REALIZADO = 'Realizado'

STATUS_CHOICES = (
    (StatusRepasse.PENDENTE.name, StatusRepasse.PENDENTE.value),
    (StatusRepasse.REALIZADO.name, StatusRepasse.REALIZADO.value),
)


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

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=StatusRepasse.PENDENTE.value
    )

    realizado_capital = models.BooleanField('Realizado Capital?', default=False)

    realizado_custeio = models.BooleanField('Realizado Custeio?', default=False)

    class Meta:
        verbose_name = 'Repasse'
        verbose_name_plural = 'Repasses'

    def __str__(self):
        return f'Repasse<val_capital: {self.valor_capital}, val_custeio: {self.valor_custeio}>'

    @property
    def valor_total(self):
        return self.valor_capital + self.valor_custeio

