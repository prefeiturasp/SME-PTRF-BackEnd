from django.db import models

from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class Receita(ModeloBase):
    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, related_name='receitas', 
                                   blank=True, null=True)

    data = models.DateField('Data Receita', blank=True, null=True)

    valor = models.DecimalField('Valor Receita', max_digits=8, decimal_places=2, default=0)

    descricao = models.TextField('Descrição', max_length=400, blank=True, null=True)

    conta_associacao = models.ForeignKey('core.ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='receitas_da_conta', blank=True, null=True)

    acao_associacao = models.ForeignKey('core.AcaoAssociacao', on_delete=models.PROTECT,
                                        related_name='receitas_da_associacao', blank=True, null=True)

    tipo_receita = models.ForeignKey('TipoReceita', on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return f'{self.descricao} - {self.data} - {self.valor}'
