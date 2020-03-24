from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from ..tipos_aplicacao_recurso import APLICACAO_CHOICES, APLICACAO_CUSTEIO


class RateioDespesa(ModeloBase):
    # Status Choice
    STATUS_COMPLETO = 'COMPLETO'
    STATUS_INCOMPLETO = 'INCOMPLETO'

    STATUS_NOMES = {
        STATUS_COMPLETO: 'Completo',
        STATUS_INCOMPLETO: 'Incompleto',
    }

    STATUS_CHOICES = (
        (STATUS_COMPLETO, STATUS_NOMES[STATUS_COMPLETO]),
        (STATUS_INCOMPLETO, STATUS_NOMES[STATUS_INCOMPLETO]),
    )

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
        default=APLICACAO_CUSTEIO
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

    @classmethod
    def aplicacoes_recurso_to_json(cls):
        result = []
        for aplicacao in APLICACAO_CHOICES:
            choice = {
                'id': aplicacao[0],
                'nome': aplicacao[1]
            }
            result.append(choice)
        return result

    def cadastro_completo(self):
        completo = self.conta_associacao and \
                   self.acao_associacao and \
                   self.aplicacao_recurso and \
                   self.tipo_custeio and \
                   self.especificacao_material_servico and \
                   self.valor_rateio

        return completo

    class Meta:
        verbose_name = "Rateio de despesa"
        verbose_name_plural = "Rateios de despesas"


@receiver(pre_save, sender=RateioDespesa)
def proponente_pre_save(instance, **kwargs):
    ...
    # if instance.status == Proponente.STATUS_INSCRITO and instance.cnpj and cnpj_esta_bloqueado(instance.cnpj):
    #     instance.status = Proponente.STATUS_BLOQUEADO
    #
    # elif instance.status == Proponente.STATUS_BLOQUEADO and instance.cnpj and not cnpj_esta_bloqueado(instance.cnpj):
    #     instance.status = Proponente.STATUS_INSCRITO
