"""
Modelo para representar um documento do PAA.

Este módulo define a entidade responsável por armazenar informações sobre os documentos
gerados para o Plano Anual de Ações (PAA), incluindo o status de geração.
"""
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class DocumentoPaa(ModeloBase):
    """
    Modelo para representar um documento do PAA.
    """
    class StatusChoices(models.TextChoices):
        """
        Escolhas para o status de geração do documento.
        """
        NAO_GERADO = 'NAO_GERADO', 'Não gerado'
        EM_PROCESSAMENTO = 'EM_PROCESSAMENTO', 'Em processamento'
        CONCLUIDO = 'CONCLUIDO', 'Geração concluída'
        ERRO_PROCESSAMENTO = 'ERRO_PROCESSAMENTO', 'Erro no processamento'

    class VersaoChoices(models.TextChoices):
        """
        Escolhas para a versão do documento.
        """
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

    def __str__(self) -> str:
        """Retorna uma representação textual da atividade com a label do
        documento e a label da geração do documento."""
        return f"{self.label_documento()} {self.status_label_geracao()}"

    def label_nome(self) -> str:
        """Retorna a label do plano anual, considerando se é retificado."""
        return f"Plano Anual{' Retificado' if self.retificacao else ''}"

    def label_documento(self) -> str:
        """Retorna a label do documento, considerando a versão e se é retificado."""
        versao_label = DocumentoPaa.VersaoChoices(self.versao).label
        return f"Documento {versao_label}{' retificado' if self.retificacao else ''}"

    def status_label_geracao(self) -> str:
        """
        Retorna a label do status de geração do documento.
        """
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
    def concluido(self) -> bool:
        """ Indica se o documento foi gerado com sucesso """
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

    def arquivo_concluido(self) -> None:
        """Marca o documento como concluído, indicando que a geração foi finalizada com sucesso."""
        self.status_geracao = DocumentoPaa.StatusChoices.CONCLUIDO
        self.save()

    def arquivo_em_processamento(self) -> None:
        """Marca o documento como em processamento, indicando que a geração está em andamento."""
        self.status_geracao = DocumentoPaa.StatusChoices.EM_PROCESSAMENTO
        self.save()

    def arquivo_em_erro_processamento(self) -> None:
        """Marca o documento como com erro no processamento, indicando que a geração falhou."""
        self.status_geracao = DocumentoPaa.StatusChoices.ERRO_PROCESSAMENTO
        self.save()


def obter_documento_final_por_retificacao(paa, retificacao: bool) -> DocumentoPaa | None:
    """Retorna o documento final do PAA, considerando se é uma retificação ou não."""
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


@receiver(post_delete, sender=DocumentoPaa)
def documento_paa_post_delete(instance, **kwargs) -> None:
    """
    Remove o arquivo físico do storage ao apagar o registro. Necessário porque
    o Django não apaga arquivos de FileField automaticamente, nem em
    instance.delete() nem em queryset.delete().
    """
    if instance.arquivo_pdf:
        instance.arquivo_pdf.delete(save=False)


auditlog.register(DocumentoPaa)
