from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class AnaliseDocumentoPrestacaoConta(ModeloBase):
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

    analise_prestacao_conta = models.ForeignKey('AnalisePrestacaoConta', on_delete=models.CASCADE,
                                                related_name='analises_de_documento')

    tipo_documento_prestacao_conta = models.ForeignKey('TipoDocumentoPrestacaoConta', on_delete=models.PROTECT,
                                                       related_name='analises_do_documento', blank=True, null=True)

    conta_associacao = models.ForeignKey('ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='analises_de_documento_da_conta', blank=True, null=True)

    resultado = models.CharField(
        'status',
        max_length=20,
        choices=RESULTADO_CHOICES,
        default=RESULTADO_CORRETO
    )

    def __str__(self):
        return f"Análise de documento {self.uuid} - Resultado:{self.resultado}"

    class Meta:
        verbose_name = "Análise de documentos de PC"
        verbose_name_plural = "16.6) Análises de documentos de PC"


auditlog.register(AnaliseDocumentoPrestacaoConta)
