from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome


class TipoAcertoLancamento(ModeloIdNome):
    history = AuditlogHistoryField()

    # Categoria Choices
    CATEGORIA_DEVOLUCAO = 'DEVOLUCAO'
    CATEGORIA_EDICAO_LANCAMENTO = 'EDICAO_LANCAMENTO'
    CATEGORIA_EXCLUSAO_LANCAMENTO = 'EXCLUSAO_LANCAMENTO'
    CATEGORIA_AJUSTES_EXTERNOS = 'AJUSTES_EXTERNOS'
    CATEGORIA_SOLICITACAO_ESCLARECIMENTO = 'SOLICITACAO_ESCLARECIMENTO'

    CATEGORIA_NOMES = {
        CATEGORIA_DEVOLUCAO: 'Devolução ao tesouro',
        CATEGORIA_EDICAO_LANCAMENTO: 'Edição do lançamento',
        CATEGORIA_EXCLUSAO_LANCAMENTO: 'Exclusão do lançamento',
        CATEGORIA_AJUSTES_EXTERNOS: 'Ajustes externos',
        CATEGORIA_SOLICITACAO_ESCLARECIMENTO: 'Solicitação de esclarecimento'
    }

    CATEGORIA_CHOICES = (
        (CATEGORIA_DEVOLUCAO, CATEGORIA_NOMES[CATEGORIA_DEVOLUCAO]),
        (CATEGORIA_EDICAO_LANCAMENTO, CATEGORIA_NOMES[CATEGORIA_EDICAO_LANCAMENTO]),
        (CATEGORIA_EXCLUSAO_LANCAMENTO, CATEGORIA_NOMES[CATEGORIA_EXCLUSAO_LANCAMENTO]),
        (CATEGORIA_AJUSTES_EXTERNOS, CATEGORIA_NOMES[CATEGORIA_AJUSTES_EXTERNOS]),
        (CATEGORIA_SOLICITACAO_ESCLARECIMENTO, CATEGORIA_NOMES[CATEGORIA_SOLICITACAO_ESCLARECIMENTO])
    )

    categoria = models.CharField(
        'Categoria',
        max_length=35,
        choices=CATEGORIA_CHOICES,
    )

    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = "Tipo de acerto em lançamentos"
        verbose_name_plural = "16.2) Tipos de acerto em lançamentos"


auditlog.register(TipoAcertoLancamento)
