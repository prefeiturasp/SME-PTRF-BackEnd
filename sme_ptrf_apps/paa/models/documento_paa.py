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

    def __str__(self):
        versao_label = DocumentoPaa.VersaoChoices(self.versao).label
        if self.status_geracao == DocumentoPaa.StatusChoices.CONCLUIDO:
            return f"Documento PAA {versao_label} gerado dia {self.criado_em.strftime('%d/%m/%Y %H:%M')}"
        elif self.status_geracao == DocumentoPaa.StatusChoices.EM_PROCESSAMENTO:
            return f"Documento PAA {versao_label} sendo gerado. Aguarde."
        elif self.status_geracao == DocumentoPaa.StatusChoices.ERRO_PROCESSAMENTO:
            return f"Documento PAA {versao_label} interrompido com erro no processamento. Tente novamente."
        else:
            return f"Documento PAA {versao_label} aguardando início da geração."

    class Meta:
        verbose_name = "Documento PAA"
        verbose_name_plural = "Documentos PAA"

    @property
    def concluido(self):
        return self.status_geracao == DocumentoPaa.StatusChoices.CONCLUIDO

    def arquivo_concluido(self):
        self.status_geracao = DocumentoPaa.StatusChoices.CONCLUIDO
        self.save()

    def arquivo_em_processamento(self):
        self.status_geracao = DocumentoPaa.StatusChoices.EM_PROCESSAMENTO
        self.save()

    def arquivo_em_erro_processamento(self):
        self.status_geracao = DocumentoPaa.StatusChoices.ERRO_PROCESSAMENTO
        self.save()


auditlog.register(DocumentoPaa)
