from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class VerificacaoRegularidadeAssociacao(ModeloBase):
    history = AuditlogHistoryField()

    analise_regularidade = models.ForeignKey(
        'AnaliseRegularidadeAssociacao',
        on_delete=models.CASCADE,
        related_name='verificacoes_da_analise',
        null=True,
    )

    item_verificacao = models.ForeignKey(
        'ItemVerificacaoRegularidade',
        on_delete=models.PROTECT,
        related_name="itens_de_verificacao"
    )

    regular = models.BooleanField('Regular?', default=True)

    def __str__(self):
        verificacao_id = f'Verificação:{self.id}'
        verificacao_nome = f'{self.item_verificacao.descricao if self.item_verificacao else "?"}'
        return f'{verificacao_id}-{verificacao_nome}'

    class Meta:
        verbose_name = 'Verificação de regularidade de associação'
        verbose_name_plural = 'Verificações de regularidade de associações'


auditlog.register(VerificacaoRegularidadeAssociacao)
