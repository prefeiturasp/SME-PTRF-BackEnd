from datetime import date
from django.db import models
from ...core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class AnaliseConsolidadoDre(ModeloBase):
    history = AuditlogHistoryField()

    # Versao Choice
    VERSAO_NAO_GERADO = '-'
    VERSAO_FINAL = 'FINAL'
    VERSAO_RASCUNHO = 'RASCUNHO'

    VERSAO_NOMES = {
        VERSAO_NAO_GERADO: '-',
        VERSAO_FINAL: 'final',
        VERSAO_RASCUNHO: 'rascunho',
    }

    VERSAO_CHOICES = (
        (VERSAO_NAO_GERADO, VERSAO_NOMES[VERSAO_NAO_GERADO]),
        (VERSAO_FINAL, VERSAO_NOMES[VERSAO_FINAL]),
        (VERSAO_RASCUNHO, VERSAO_NOMES[VERSAO_RASCUNHO]),
    )

    # Status Choice
    STATUS_NAO_GERADO = 'NAO_GERADO'
    STATUS_EM_PROCESSAMENTO = 'EM_PROCESSAMENTO'
    STATUS_CONCLUIDO = 'CONCLUIDO'

    STATUS_NOMES_CHOICES = {
        STATUS_NAO_GERADO: 'Não gerado',
        STATUS_EM_PROCESSAMENTO: 'Em processamento',
        STATUS_CONCLUIDO: 'Geração concluída',
    }

    STATUS_CHOICES_VERSAO = (
        (STATUS_NAO_GERADO, STATUS_NOMES_CHOICES[STATUS_NAO_GERADO]),
        (STATUS_EM_PROCESSAMENTO, STATUS_NOMES_CHOICES[STATUS_EM_PROCESSAMENTO]),
        (STATUS_CONCLUIDO, STATUS_NOMES_CHOICES[STATUS_CONCLUIDO]),
    )

    consolidado_dre = models.ForeignKey(
        'ConsolidadoDRE', on_delete=models.CASCADE,
        related_name='analises_do_consolidado_dre',
    )
    data_devolucao = models.DateField('data da devolução pela SME', blank=True, null=True)
    data_limite = models.DateField('data para reenvio para SME após acertos', blank=True, null=True)
    data_retorno_analise = models.DateField('data para retorno da análise para SME', blank=True, null=True)

    relatorio_acertos_pdf = models.FileField(
        blank=True, null=True, verbose_name='Relatório em PDF de apresentação após acertos')

    relatorio_acertos_versao = models.CharField(
        'Versão do documento de apresentação após acertos',
        max_length=20,
        choices=VERSAO_CHOICES,
        default=VERSAO_NAO_GERADO
    )
    relatorio_acertos_status = models.CharField(
        'Status da geração do documento de apresentação após acertos',
        max_length=20,
        choices=STATUS_CHOICES_VERSAO,
        default=STATUS_NAO_GERADO
    )
    relatorio_acertos_gerado_em = models.DateTimeField("Arquivo pdf de solicitação de acertos gerado em", null=True)

    def devolucao(self, data_limite=None, data_devolucao=date.today()):
        self.data_limite = data_limite
        self.data_devolucao = data_devolucao
        self.save()

        return self

    def __str__(self):
        return f"{self.consolidado_dre.dre} - {self.consolidado_dre.periodo} - Análise #{self.pk}"

    class Meta:
        verbose_name = "Análise consolidado DRE"
        verbose_name_plural = "Análises consolidados DRE"


auditlog.register(AnaliseConsolidadoDre)
