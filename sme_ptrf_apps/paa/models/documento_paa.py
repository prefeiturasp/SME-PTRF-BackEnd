from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class DocumentoPaa(ModeloBase):

    class StatusChoices(models.TextChoices):
        NAO_GERADO = 'NAO_GERADO', 'Não gerado'
        EM_PROCESSAMENTO = 'EM_PROCESSAMENTO', 'Em processamento'
        CONCLUIDO = 'CONCLUIDO', 'Geração concluída'
        ERRO_PROCESSAMENTO = 'ERRO_PROCESSAMENTO', 'Erro no processamento'

    class VersaoChoices(models.TextChoices):
        FINAL = 'FINAL', 'final'
        PREVIA = 'PREVIA', 'prévia'

    history = AuditlogHistoryField()

    paa = models.ForeignKey('paa.Paa', on_delete=models.PROTECT, verbose_name="PAA", blank=True, null=True)

    arquivo_pdf = models.FileField(blank=True, null=True, verbose_name='Documento em PDF')

    status_geracao = models.CharField(
        'Status geração',
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.NAO_GERADO
    )
    versao = models.CharField(
        'Versão',
        max_length=20,
        choices=VersaoChoices.choices,
        default=VersaoChoices.FINAL
    )

    versao_documento = models.IntegerField(
        'Versão do documento',
        default=1
    )

    retificacao = models.BooleanField(
        'Retificação',
        default=False,
        help_text="Identifica se o documento é gerado por uma retificação"
    )

    def __str__(self):
        return f"{self.label_documento()} {self.status_label_geracao()}"

    def label_nome(self):
        return f"Plano Anual{' Retificado' if self.retificacao else ''}"

    def label_documento(self):
        versao_label = DocumentoPaa.VersaoChoices(self.versao).label
        return f"Documento {versao_label}{' retificado' if self.retificacao else ''}"

    def status_label_geracao(self):
        if self.status_geracao == DocumentoPaa.StatusChoices.CONCLUIDO:
            return f"gerado em {self.criado_em.strftime('%d/%m/%Y às %H:%M')}"
        elif self.status_geracao == DocumentoPaa.StatusChoices.EM_PROCESSAMENTO:
            return "sendo gerado. Aguarde."
        elif self.status_geracao == DocumentoPaa.StatusChoices.ERRO_PROCESSAMENTO:
            return "interrompido com erro no processamento. Tente novamente."
        else:
            return "aguardando início da geração."

    class Meta:
        verbose_name = "Documento PAA"
        verbose_name_plural = "Documentos PAA"

    @property
    def concluido(self):
        return self.status_geracao == DocumentoPaa.StatusChoices.CONCLUIDO

    @property
    def status_nao_gerado(self) -> bool:
        """ Indica se o documento ainda não foi gerado """
        return self.status_geracao == DocumentoPaa.StatusChoices.NAO_GERADO

    @property
    def status_em_processamento(self) -> bool:
        """ Indica se o documento ainda está em processamento """
        return self.status_geracao == DocumentoPaa.StatusChoices.EM_PROCESSAMENTO

    @property
    def status_erro_processamento(self) -> bool:
        """ Indica se o documento gerado apresentou erro no processamento """
        return self.status_geracao == DocumentoPaa.StatusChoices.ERRO_PROCESSAMENTO

    def arquivo_concluido(self):
        self.status_geracao = DocumentoPaa.StatusChoices.CONCLUIDO
        self.save()

    def arquivo_em_processamento(self):
        self.status_geracao = DocumentoPaa.StatusChoices.EM_PROCESSAMENTO
        self.save()

    def arquivo_em_erro_processamento(self):
        self.status_geracao = DocumentoPaa.StatusChoices.ERRO_PROCESSAMENTO
        self.save()


def obter_documento_final_por_retificacao(paa, retificacao: bool):
    if paa is None or not getattr(paa, 'pk', None):
        return None
    return (
        DocumentoPaa.objects.filter(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            retificacao=retificacao,
        )
        .order_by('-pk')
        .first()
    )


auditlog.register(DocumentoPaa)
