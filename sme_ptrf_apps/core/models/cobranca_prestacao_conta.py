from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase

# Tipo Choice
TIPO_RECEBIMENTO = 'RECEBIMENTO'
TIPO_DEVOLUCAO = 'DEVOLUCAO'

TIPOS_NOMES = {
    TIPO_RECEBIMENTO: 'Cobrança de recebimento',
    TIPO_DEVOLUCAO: 'Cobrança de devolução',
}

TIPOS_CHOICES = (
    (TIPO_RECEBIMENTO, TIPOS_NOMES[TIPO_RECEBIMENTO]),
    (TIPO_DEVOLUCAO, TIPOS_NOMES[TIPO_DEVOLUCAO]),
)


class CobrancaPrestacaoConta(ModeloBase):
    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE,
                                        related_name='cobrancas_da_prestacao')

    data = models.DateField('data da cobrança')

    tipo = models.CharField(
        'tipo de cobrança',
        max_length=15,
        choices=TIPOS_CHOICES,
        default=TIPO_RECEBIMENTO
    )

    devolucao_prestacao = models.ForeignKey('DevolucaoPrestacaoConta', on_delete=models.CASCADE,
                                            related_name='cobrancas_da_devolucao', null=True, blank=True)

    def __str__(self):
        return f"{self.data} - {self.tipo}"

    class Meta:
        verbose_name = "Cobrança de prestação de contas"
        verbose_name_plural = "09.6) Cobranças de prestações de contas"


@receiver(pre_save, sender=CobrancaPrestacaoConta)
def cobranca_pre_save(instance, **kwargs):
    if instance.tipo == TIPO_DEVOLUCAO and instance.prestacao_conta:
        ultima_devolucao = instance.prestacao_conta.devolucoes_da_prestacao.order_by('-id').first()
        instance.devolucao_prestacao = ultima_devolucao
