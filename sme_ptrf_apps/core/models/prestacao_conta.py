from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase

# Status Choice
STATUS_FECHADO = 'FECHADO'
STATUS_ABERTO = 'ABERTO'

STATUS_NOMES = {
    STATUS_ABERTO: 'Aberta',
    STATUS_FECHADO: 'Fechada',
}

STATUS_CHOICES = (
    (STATUS_ABERTO, STATUS_NOMES[STATUS_ABERTO]),
    (STATUS_FECHADO, STATUS_NOMES[STATUS_FECHADO]),
)


class PrestacaoConta(ModeloBase):
    periodo = models.ForeignKey('Periodo', on_delete=models.PROTECT, related_name='prestacoes_de_conta')

    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT,
                                   related_name='prestacoes_de_conta_da_associacao',
                                   blank=True, null=True)

    conta_associacao = models.ForeignKey('ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='prestacoes_de_conta_da_conta', blank=True, null=True)

    prestacao_de_conta_anterior = models.ForeignKey('PrestacaoConta', on_delete=models.PROTECT,
                                                    related_name='proxima_prestacao_de_conta', null=True, blank=True)

    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_ABERTO
    )

    conciliado = models.BooleanField('Período Conciliado?', default=False)

    conciliado_em = models.DateTimeField('Última conciliação feita em', blank=True, null=True)

    observacoes = models.TextField('observacoes', blank=True, default='')

    motivo_reabertura = models.TextField('Motivo de reabrir a conciliação', blank=True, default='')

    def __str__(self):
        nome_conta = self.conta_associacao.tipo_conta.nome if self.conta_associacao else ''
        return f"{self.periodo} - {nome_conta}  - {self.status}"

    @classmethod
    def iniciar(cls, conta_associacao, periodo):
        return PrestacaoConta.objects.create(
            conta_associacao=conta_associacao,
            periodo=periodo,
            associacao=conta_associacao.associacao,
        )

    class Meta:
        verbose_name = "Prestação de conta"
        verbose_name_plural = "Prestações de contas"
        unique_together = ['conta_associacao', 'periodo']
