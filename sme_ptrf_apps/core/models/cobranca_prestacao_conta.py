from django.db import models

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

    def __str__(self):
        return f"{self.data} - {self.tipo}"

    class Meta:
        verbose_name = "Cobrança de prestação de contas"
        verbose_name_plural = "Cobranças de prestações de contas"
