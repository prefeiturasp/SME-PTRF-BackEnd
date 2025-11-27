from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class DocumentoPaa(ModeloBase):

    class StatusChoices(models.TextChoices):
        NAO_GERADO = 'NAO_GERADO', 'Não gerado'
        EM_PROCESSAMENTO = 'EM_PROCESSAMENTO', 'Em processamento'
        CONCLUIDO = 'CONCLUIDO', 'Geração concluída'

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
        if self.status_geracao == DocumentoPaa.StatusChoices.CONCLUIDO:
            return f"Documento PAA {DocumentoPaa.VersaoChoices[self.versao]} gerado dia {self.criado_em.strftime('%d/%m/%Y %H:%M')}"
        else:
            return f"Documento PAA {DocumentoPaa.VersaoChoices[self.versao]} sendo gerado. Aguarde."

    class Meta:
        verbose_name = "Documento PAA"
        verbose_name_plural = "Documentos PAA"

    def arquivo_concluido(self):
        self.status_geracao = DocumentoPaa.StatusChoices.CONCLUIDO
        self.save()

    def arquivo_em_processamento(self):
        self.status_geracao = DocumentoPaa.StatusChoices.EM_PROCESSAMENTO
        self.save()


auditlog.register(DocumentoPaa)
