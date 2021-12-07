from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class AnaliseRegularidadeAssociacao(ModeloBase):
    # Status de Regularidade
    STATUS_REGULARIDADE_PENDENTE = 'PENDENTE'
    STATUS_REGULARIDADE_REGULAR = 'REGULAR'

    STATUS_REGULARIDADE_NOMES = {
        STATUS_REGULARIDADE_PENDENTE: 'Pendente',
        STATUS_REGULARIDADE_REGULAR: 'Regular',
    }

    STATUS_REGULARIDADE_CHOICES = (
        (STATUS_REGULARIDADE_PENDENTE, STATUS_REGULARIDADE_NOMES[STATUS_REGULARIDADE_PENDENTE]),
        (STATUS_REGULARIDADE_REGULAR, STATUS_REGULARIDADE_NOMES[STATUS_REGULARIDADE_REGULAR]),
    )

    history = AuditlogHistoryField()

    ano_analise = models.ForeignKey('AnoAnaliseRegularidade', on_delete=models.PROTECT, related_name='analises_regularidade_no_ano')
    associacao = models.ForeignKey('core.Associacao', on_delete=models.PROTECT, related_name='analises_regularidade_da_associacao')

    status_regularidade = models.CharField(
        'Status de Regularidade',
        max_length=15,
        choices=STATUS_REGULARIDADE_CHOICES,
        default=STATUS_REGULARIDADE_PENDENTE,
    )

    def __str__(self):
        codigo_eol = self.associacao.unidade.codigo_eol if self.associacao and self.associacao.unidade else "?"
        ano_ref = self.ano_analise.ano if self.ano_analise else "?"
        return f'Análise:{self.id} EOL:{codigo_eol} Ano:{ano_ref}'

    class Meta:
        verbose_name = 'Análise de regularidade de associação'
        verbose_name_plural = 'Análises de regularidade de associações'


auditlog.register(AnaliseRegularidadeAssociacao)
