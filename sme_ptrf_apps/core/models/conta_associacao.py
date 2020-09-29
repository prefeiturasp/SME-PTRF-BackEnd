from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class ContaAssociacao(ModeloBase):
    # Status Choice
    STATUS_ATIVA = 'ATIVA'
    STATUS_INATIVA = 'INATIVA'

    STATUS_NOMES = {
        STATUS_ATIVA: 'Ativa',
        STATUS_INATIVA: 'Inativa',
    }

    STATUS_CHOICES = (
        (STATUS_ATIVA, STATUS_NOMES[STATUS_ATIVA]),
        (STATUS_INATIVA, STATUS_NOMES[STATUS_INATIVA]),
    )

    associacao = models.ForeignKey('Associacao', on_delete=models.CASCADE, related_name='contas', blank=True, null=True)
    tipo_conta = models.ForeignKey('TipoConta', on_delete=models.PROTECT, blank=True, null=True)
    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_ATIVA
    )
    banco_nome = models.CharField('Nome do banco', max_length=50, blank=True, default='')
    agencia = models.CharField('Nº agência',  max_length=15, blank=True, default='')
    numero_conta = models.CharField('Nº conta', max_length=30, blank=True, default='')
    numero_cartao = models.CharField('Nº do cartão', max_length=80, blank=True, default='')


    def __str__(self):
        associacao = self.associacao.nome if self.associacao else 'ACM indefinida'
        tipo_conta = self.tipo_conta.nome if self.tipo_conta else 'Tipo de conta indefinido'
        status = ContaAssociacao.STATUS_NOMES[self.status]
        return f"{associacao} - Conta {tipo_conta} - {status}"

    @classmethod
    def get_valores(cls, user=None, associacao_uuid=None):
        query = cls.objects.filter(status=cls.STATUS_ATIVA)
        if user:
            query = query.filter(associacao__uuid=associacao_uuid)
        return query.all()

    class Meta:
        verbose_name = "Conta de Associação"
        verbose_name_plural = "07.1) Contas de Associações"
