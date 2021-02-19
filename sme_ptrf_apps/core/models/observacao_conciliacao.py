from django.db import models

from sme_ptrf_apps.core.models import AcaoAssociacao
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class ObservacaoConciliacao(ModeloBase):
    periodo = models.ForeignKey('Periodo', on_delete=models.PROTECT, related_name='observacoes_conciliacao_do_periodo')

    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT,
                                   related_name='observacoes_conciliacao_da_associacao',
                                   blank=True, null=True)

    conta_associacao = models.ForeignKey('ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='observacoes_conciliacao_da_conta', blank=True, null=True)

    texto = models.TextField('Observações da conciliação', max_length=600, blank=True, null=True)

    data_extrato = models.DateField('data do extrato', blank=True, null=True)

    saldo_extrato = models.DecimalField('saldo do extrato', max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'informação de conciliação'
        verbose_name_plural = '09.5) Informações de conciliação'

    def __str__(self):
        return self.texto[:30]

    @classmethod
    def criar_atualizar(cls, periodo, conta_associacao, texto_observacao="", data_extrato=None, saldo_extrato=0.0):

        observacao = cls.objects.filter(periodo=periodo, conta_associacao=conta_associacao).first()
        if observacao:
            if texto_observacao or data_extrato or saldo_extrato:
                observacao.texto = texto_observacao
                observacao.data_extrato = data_extrato
                observacao.saldo_extrato = saldo_extrato
                observacao.save()
            else:
                observacao.delete()
        elif texto_observacao or data_extrato or saldo_extrato:
            cls.objects.create(
                periodo=periodo,
                conta_associacao=conta_associacao,
                associacao=conta_associacao.associacao,
                texto=texto_observacao,
                data_extrato=data_extrato,
                saldo_extrato=saldo_extrato
            )
