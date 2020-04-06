from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from ..status_cadastro_completo import STATUS_CHOICES, STATUS_COMPLETO, STATUS_INCOMPLETO
from ..tipos_aplicacao_recurso import APLICACAO_CHOICES, APLICACAO_CUSTEIO, APLICACAO_CAPITAL


class RateioDespesa(ModeloBase):
    despesa = models.ForeignKey('Despesa', on_delete=models.CASCADE, related_name='rateios', blank=True, null=True)

    associacao = models.ForeignKey('core.Associacao', on_delete=models.PROTECT, related_name='rateios_associacao',
                                   blank=True, null=True)

    conta_associacao = models.ForeignKey('core.ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='rateios_da_conta', blank=True, null=True)

    acao_associacao = models.ForeignKey('core.AcaoAssociacao', on_delete=models.PROTECT,
                                        related_name='rateios_da_associacao', blank=True, null=True)

    aplicacao_recurso = models.CharField(
        'Tipo de aplicação do recurso',
        max_length=15,
        choices=APLICACAO_CHOICES,
        default=APLICACAO_CUSTEIO,
        null=True,
    )

    tipo_custeio = models.ForeignKey('TipoCusteio', on_delete=models.PROTECT, blank=True, null=True)

    especificacao_material_servico = models.ForeignKey('EspecificacaoMaterialServico', on_delete=models.PROTECT,
                                                       blank=True, null=True)

    valor_rateio = models.DecimalField('Valor', max_digits=8, decimal_places=2, default=0)

    quantidade_itens_capital = models.PositiveSmallIntegerField('Quantidade de itens', default=0)
    valor_item_capital = models.DecimalField('Valor unitário ', max_digits=8, decimal_places=2, default=0)
    numero_processo_incorporacao_capital = models.CharField('Nº processo incorporação', max_length=100, default='',
                                                            blank=True)

    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_INCOMPLETO
    )

    def __str__(self):
        documento = self.despesa.numero_documento if self.despesa else 'Despesa indefinida'
        return f"{documento} - {self.valor_rateio:.2f}"

    def cadastro_completo(self):
        completo = self.conta_associacao and \
                   self.acao_associacao and \
                   self.aplicacao_recurso and \
                   self.especificacao_material_servico and \
                   self.valor_rateio

        if self.aplicacao_recurso == APLICACAO_CUSTEIO:
            completo = completo and self.tipo_custeio

        if self.aplicacao_recurso == APLICACAO_CAPITAL:
            completo = completo and \
                       self.quantidade_itens_capital > 0 and \
                       self.valor_item_capital > 0 and self.numero_processo_incorporacao_capital

        return completo

    class Meta:
        verbose_name = "Rateio de despesa"
        verbose_name_plural = "Rateios de despesas"


@receiver(pre_save, sender=RateioDespesa)
def rateio_pre_save(instance, **kwargs):
    instance.status = STATUS_COMPLETO if instance.cadastro_completo() else STATUS_INCOMPLETO


@receiver(post_save, sender=RateioDespesa)
def rateio_post_save(instance, created, **kwargs):
    if instance and instance.despesa:
        instance.despesa.atualiza_status()
