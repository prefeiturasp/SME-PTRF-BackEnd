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

    acao_associacao = models.ForeignKey('AcaoAssociacao', on_delete=models.PROTECT,
                                        related_name='observacoes_conciliacao_da_acao', blank=True, null=True)

    texto = models.TextField('Texto', max_length=600, blank=True, null=True)

    class Meta:
        verbose_name = 'observação de conciliação'
        verbose_name_plural = 'observações de conciliação'

    def __str__(self):
        return self.texto[:30]

    @classmethod
    def criar_atualizar(cls, periodo, conta_associacao, lista_observacoes=None):
        if lista_observacoes:
            for obs_data in lista_observacoes:
                observacao = cls.objects.filter(
                    acao_associacao__uuid=obs_data['acao_associacao_uuid'],
                    periodo=periodo, conta_associacao=conta_associacao).first()
                if observacao:
                    if obs_data['observacao']:
                        observacao.texto = obs_data['observacao']
                        observacao.save()
                    else:
                        observacao.delete()
                elif obs_data['observacao']:
                    cls.objects.create(
                        periodo=periodo,
                        conta_associacao=conta_associacao,
                        associacao=conta_associacao.associacao,
                        acao_associacao=AcaoAssociacao.by_uuid(obs_data['acao_associacao_uuid']),
                        texto=obs_data['observacao']
                    )
