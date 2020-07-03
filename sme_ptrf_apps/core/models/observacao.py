from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class Observacao(ModeloBase):
    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE,
                                        related_name='observacoes_da_prestacao', blank=True, null=True)

    acao_associacao = models.ForeignKey('AcaoAssociacao', on_delete=models.PROTECT,
                                        related_name='observacoes_da_acao', blank=True, null=True)

    texto = models.TextField('Texto', max_length=600, blank=True, null=True)

    class Meta:
        verbose_name = 'observação'
        verbose_name_plural = 'observações'

    def __str__(self):
        return text[:30]
