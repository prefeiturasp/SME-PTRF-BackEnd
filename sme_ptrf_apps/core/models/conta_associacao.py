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

    def __str__(self):
        associacao = self.associacao.nome if self.associacao else 'ACM indefinida'
        tipo_conta = self.tipo_conta.nome if self.tipo_conta else 'Tipo de conta indefinido'
        status = ContaAssociacao.STATUS_NOMES[self.status]
        return f"{associacao} - Conta {tipo_conta} - {status}"

    @classmethod
    def get_valores(cls, user=None):
        query = cls.objects.filter(status=cls.STATUS_ATIVA)
        if user:
            query = query.filter(associacao__usuario=user)
        return query.all()

    class Meta:
        verbose_name = "Conta de Associação"
        verbose_name_plural = "Contas de Associações"
