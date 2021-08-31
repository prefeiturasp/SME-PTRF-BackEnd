import os
from django.db import models
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class DemonstrativoFinanceiro(ModeloBase):
    history = AuditlogHistoryField()

    # Status Choice
    STATUS_EM_PROCESSAMENTO = 'EM_PROCESSAMENTO'
    STATUS_CONCLUIDO = 'CONCLUIDO'

    STATUS_NOMES = {
        STATUS_EM_PROCESSAMENTO: 'Em processamento',
        STATUS_CONCLUIDO: 'Geração concluída',
    }

    STATUS_CHOICES = (
        (STATUS_EM_PROCESSAMENTO, STATUS_NOMES[STATUS_EM_PROCESSAMENTO]),
        (STATUS_CONCLUIDO, STATUS_NOMES[STATUS_CONCLUIDO]),
    )

    # Versao Choice
    VERSAO_FINAL = 'FINAL'
    VERSAO_PREVIA = 'PREVIA'

    VERSAO_NOMES = {
        VERSAO_FINAL: 'final',
        VERSAO_PREVIA: 'prévio',
    }

    VERSAO_CHOICES = (
        (VERSAO_FINAL, VERSAO_NOMES[VERSAO_FINAL]),
        (VERSAO_PREVIA, VERSAO_NOMES[VERSAO_PREVIA]),
    )

    arquivo = models.FileField(blank=True, null=True, verbose_name='Relatório em XLSX')

    arquivo_pdf = models.FileField(blank=True, null=True, verbose_name='Relatório em PDF')

    conta_associacao = models.ForeignKey('ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='demonstrativos_financeiros', blank=True, null=True)

    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE,
                                        related_name='demonstrativos_da_prestacao', blank=True, null=True)

    periodo_previa = models.ForeignKey('Periodo', on_delete=models.PROTECT,
                                       related_name='demonstrativos_previos_do_periodo', blank=True, null=True,
                                       verbose_name='Período da prévia')

    status = models.CharField(
        'status',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CONCLUIDO
    )

    versao = models.CharField(
        'versão',
        max_length=20,
        choices=VERSAO_CHOICES,
        default=VERSAO_FINAL
    )

    class Meta:
        verbose_name = 'Demonstrativo Financeiro'
        verbose_name_plural = '09.2) Demonstrativos Financeiros'

    def __str__(self):
        if self.status == self.STATUS_CONCLUIDO:
            return f"Documento {self.VERSAO_NOMES[self.versao]} gerado dia {self.criado_em.strftime('%d/%m/%Y %H:%M')}"
        else:
            return f"Documento {self.VERSAO_NOMES[self.versao]} sendo gerado. Aguarde."

    def arquivo_concluido(self):
        self.status = self.STATUS_CONCLUIDO
        self.save()


@receiver(models.signals.post_delete, sender=DemonstrativoFinanceiro)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deleta o arquivo do sistema de arquivos quando
    o correspondente objeto 'MediaFile' é deletado.
    """
    if instance.arquivo:
        if os.path.isfile(instance.arquivo.path):
            os.remove(instance.arquivo.path)


@receiver(models.signals.pre_save, sender=DemonstrativoFinanceiro)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deleta o arquivo antigo do sistema de arquivos quando
    o correspondente objeti 'MediaFile' é atualizado com um
    novo arquivo.
    """

    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).arquivo
    except sender.DoesNotExist:
        return False

    new_file = instance.arquivo
    if old_file and not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


auditlog.register(DemonstrativoFinanceiro)
