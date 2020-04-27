from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class AcaoAssociacao(ModeloBase):
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

    associacao = models.ForeignKey('Associacao', on_delete=models.CASCADE, related_name='acoes', blank=True, null=True)
    acao = models.ForeignKey('Acao', on_delete=models.PROTECT, blank=True, null=True)
    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_ATIVA
    )

    def __str__(self):
        associacao = self.associacao.nome if self.associacao else 'ACM indefinida'
        acao = self.acao.nome if self.acao else 'Ação indefinida'
        status = AcaoAssociacao.STATUS_NOMES[self.status]
        return f"{associacao} - Ação {acao} - {status}"

    @classmethod
    def get_valores(cls, user=None):
        query = cls.objects.filter(status=cls.STATUS_ATIVA)
        if user:
            query = query.filter(associacao__uuid=user.associacao.uuid)
        return query.all()

    class Meta:
        verbose_name = "Ação de Associação"
        verbose_name_plural = "Ações de Associações"
