from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from .tipo_documento_prestacao_conta import TipoDocumentoPrestacaoConta


class TipoAcertoDocumento(ModeloIdNome):
    history = AuditlogHistoryField()

    # Categoria Choices
    CATEGORIA_INCLUSAO_CREDITO = 'INCLUSAO_CREDITO'
    CATEGORIA_INCLUSAO_GASTO = 'INCLUSAO_GASTO'
    CATEGORIA_AJUSTES_EXTERNOS = 'AJUSTES_EXTERNOS'
    CATEGORIA_SOLICITACAO_ESCLARECIMENTO = 'SOLICITACAO_ESCLARECIMENTO'

    CATEGORIA_NOMES = {
        CATEGORIA_INCLUSAO_CREDITO: 'Inclusão de crédito',
        CATEGORIA_INCLUSAO_GASTO: 'Inclusão de gasto',
        CATEGORIA_AJUSTES_EXTERNOS: 'Ajustes externos',
        CATEGORIA_SOLICITACAO_ESCLARECIMENTO: 'Solicitação de esclarecimento'
    }

    CATEGORIA_CHOICES = (
        (CATEGORIA_INCLUSAO_CREDITO, CATEGORIA_NOMES[CATEGORIA_INCLUSAO_CREDITO]),
        (CATEGORIA_INCLUSAO_GASTO, CATEGORIA_NOMES[CATEGORIA_INCLUSAO_GASTO]),
        (CATEGORIA_AJUSTES_EXTERNOS, CATEGORIA_NOMES[CATEGORIA_AJUSTES_EXTERNOS]),
        (CATEGORIA_SOLICITACAO_ESCLARECIMENTO, CATEGORIA_NOMES[CATEGORIA_SOLICITACAO_ESCLARECIMENTO])
    )

    tipos_documento_prestacao = models.ManyToManyField(TipoDocumentoPrestacaoConta, blank=True)

    categoria = models.CharField(
        'Categoria',
        max_length=35,
        choices=CATEGORIA_CHOICES,
        default=CATEGORIA_SOLICITACAO_ESCLARECIMENTO
    )

    ativo = models.BooleanField('Ativo', default=True)

    def adiciona_tipos_documentos_prestacao(self, tipos_documentos_prestacao):
        self.tipos_documento_prestacao.set(tipos_documentos_prestacao)
        self.save()

    class Meta:
        verbose_name = "Tipo de acerto em documentos"
        verbose_name_plural = "16.5) Tipos de acerto em documentos"


auditlog.register(TipoAcertoDocumento)
