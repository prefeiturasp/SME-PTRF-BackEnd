from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.core.models import AcaoAssociacao


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
        return self.texto[:30]

    @classmethod
    def criar_atualizar(cls, prestacao_conta, lista_observacoes=None):
        if lista_observacoes:
            for obs_data in lista_observacoes:
                observacao = cls.objects.filter(
                    acao_associacao__uuid=obs_data['acao_associacao_uuid'], 
                    prestacao_conta=prestacao_conta).first()
                if observacao:
                    if obs_data['observacao']:
                        observacao.texto = obs_data['observacao']
                        observacao.save()
                    else:
                        observacao.delete()
                elif obs_data['observacao']:
                    cls.objects.create(
                        prestacao_conta=prestacao_conta,
                        acao_associacao=AcaoAssociacao.objects.filter(
                            uuid=obs_data['acao_associacao_uuid']).first(),
                        texto=obs_data['observacao']
                    )
