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

    prestacao_de_conta_anterior = models.ForeignKey('PrestacaoConta', on_delete=models.PROTECT,
                                                    related_name='proxima_prestacao_de_conta', null=True, blank=True)

    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_ABERTO
    )

    def __str__(self):
        return f"{self.periodo} - {self.status}"

    @classmethod
    def iniciar(cls, periodo, associacao):
        return PrestacaoConta.objects.create(
            periodo=periodo,
            associacao=associacao,
        )

    def apaga_fechamentos(self):
        for fechamento in self.fechamentos_da_prestacao.all():
            fechamento.delete()

    def apaga_relacao_bens(self):
        for relacao in self.relacoes_de_bens_da_prestacao.all():
            relacao.delete()

    def apaga_demonstrativos_financeiros(self):
        for demonstrativo in self.demonstrativos_da_prestacao.all():
            demonstrativo.delete()

    def ultima_ata(self):
        return self.atas_da_prestacao.last()

    @classmethod
    def revisar(cls, uuid, motivo):
        #TODO Rever o parâmetro motivo
        prestacao_de_conta = cls.by_uuid(uuid=uuid)
        prestacao_de_conta.save()
        prestacao_de_conta.apaga_fechamentos()
        prestacao_de_conta.apaga_relacao_bens()
        prestacao_de_conta.apaga_demonstrativos_financeiros()
        return prestacao_de_conta

    @classmethod
    def salvar(cls, uuid):
        #TODO Rever o salvamento de PC
        prestacao_de_conta = cls.by_uuid(uuid=uuid)
        prestacao_de_conta.save()
        return prestacao_de_conta

    @classmethod
    def concluir(cls, uuid):
        #TODO Rever a conclusão de PC
        prestacao_de_conta = cls.by_uuid(uuid=uuid)
        prestacao_de_conta.save()
        return prestacao_de_conta

    class Meta:
        verbose_name = "Prestação de conta"
        verbose_name_plural = "Prestações de contas"
        #TODO Retornar com Unique Together após migração inicial da nova PC
        #unique_together = ['associacao', 'periodo']
