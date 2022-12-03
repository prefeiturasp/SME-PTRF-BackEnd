from django.db import models
from ...core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class AnaliseDocumentoConsolidadoDre(ModeloBase):
    history = AuditlogHistoryField()

    # Status Choice
    RESULTADO_CORRETO = 'CORRETO'
    RESULTADO_AJUSTE = 'AJUSTE'

    RESULTADO_NOMES = {
        RESULTADO_CORRETO: 'Documento Correto',
        RESULTADO_AJUSTE: 'Ajuste necessário',
    }

    RESULTADO_CHOICES = (
        (RESULTADO_CORRETO, RESULTADO_NOMES[RESULTADO_CORRETO]),
        (RESULTADO_AJUSTE, RESULTADO_NOMES[RESULTADO_AJUSTE]),
    )

    analise_consolidado_dre = models.ForeignKey(
        'AnaliseConsolidadoDre',
        on_delete=models.CASCADE,
        related_name='analises_de_documentos_da_analise_do_consolidado'
    )

    documento_adicional = models.ForeignKey(
        'DocumentoAdicional',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='analises_de_documentos_do_documento_adicional'
    )

    relatorio_consolidao_dre = models.ForeignKey(
        'RelatorioConsolidadoDRE',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='analises_de_documentos_do_relatorio_consolidao_dre'
    )

    ata_parecer_tecnico = models.ForeignKey(
        'AtaParecerTecnico',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='analises_de_documentos_da_ata_parecer_tecnico'
    )

    detalhamento = models.TextField('Motivo', max_length=600, blank=True, default="")

    resultado = models.CharField(
        'status',
        max_length=20,
        choices=RESULTADO_CHOICES,
        default=RESULTADO_CORRETO
    )
    documento_devolvido = models.BooleanField('Já foi devolvido?', default=False)

    def __str__(self):
        return f"{self.analise_consolidado_dre.consolidado_dre.dre} - {self.analise_consolidado_dre.consolidado_dre.periodo} - Análise documento #{self.pk}"

    class Meta:
        verbose_name = "Análise de documento do consolidado DRE"
        verbose_name_plural = "Análises de documentos dos consolidados DRE"


auditlog.register(AnaliseDocumentoConsolidadoDre)
