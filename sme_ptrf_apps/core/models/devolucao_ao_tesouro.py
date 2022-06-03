from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class DevolucaoAoTesouro(ModeloBase):
    history = AuditlogHistoryField()

    # visao_criacao Choice
    VISAO_DRE = 'DRE'
    VISAO_UE = 'UE'

    VISAO_NOMES = {
        VISAO_DRE: 'Diretoria Regional',
        VISAO_UE: 'Unidade Escolar',
    }

    VISAO_CHOICES = (
        (VISAO_DRE, VISAO_NOMES[VISAO_DRE]),
        (VISAO_UE, VISAO_NOMES[VISAO_UE]),
    )

    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE,
                                        related_name='devolucoes_ao_tesouro_da_prestacao')

    tipo = models.ForeignKey('TipoDevolucaoAoTesouro', on_delete=models.PROTECT,
                             related_name='devolucoes_ao_tesouro_do_tipo')

    data = models.DateField('data da devolução ao tesouro', blank=True, null=True)

    despesa = models.ForeignKey('despesas.Despesa', on_delete=models.PROTECT,
                                related_name='devolucoes_ao_tesouro_da_despesa', blank=True, null=True)

    devolucao_total = models.BooleanField('Devolução total?', default=True)

    valor = models.DecimalField('Valor', max_digits=8, decimal_places=2, default=0)

    motivo = models.TextField('Motivo', max_length=600, blank=True, null=True)

    visao_criacao = models.CharField(
        'Criado pela',
        max_length=20,
        choices=VISAO_CHOICES,
        default=VISAO_DRE
    )

    def __str__(self):
        return f"{self.data} - {self.tipo}"

    class Meta:
        verbose_name = "Devolução ao tesouro prestação de contas"
        verbose_name_plural = "09.9) Devoluções ao tesouro prestações de contas"


auditlog.register(DevolucaoAoTesouro)
