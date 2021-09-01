import os
from django.db import models
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class RelatorioConsolidadoDRE(ModeloBase):
    history = AuditlogHistoryField()

    # Status Choice
    STATUS_NAO_GERADO = 'NAO_GERADO'
    STATUS_GERADO_PARCIAL = 'GERADO_PARCIAL'
    STATUS_GERADO_TOTAL = 'GERADO_TOTAL'
    STATUS_EM_PROCESSAMENTO = 'EM_PROCESSAMENTO'

    STATUS_NOMES = {
        STATUS_NAO_GERADO: 'Relatório não gerado',
        STATUS_GERADO_PARCIAL: 'Relatório parcial gerado',
        STATUS_GERADO_TOTAL: 'Relatório final gerado',
        STATUS_EM_PROCESSAMENTO: 'Relatório em processamento',
    }

    STATUS_CHOICES = (
        (STATUS_NAO_GERADO, STATUS_NOMES[STATUS_NAO_GERADO]),
        (STATUS_GERADO_PARCIAL, STATUS_NOMES[STATUS_GERADO_PARCIAL]),
        (STATUS_GERADO_TOTAL, STATUS_NOMES[STATUS_GERADO_TOTAL]),
        (STATUS_EM_PROCESSAMENTO, STATUS_NOMES[STATUS_EM_PROCESSAMENTO]),
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

    arquivo = models.FileField(blank=True, null=True)

    dre = models.ForeignKey('core.Unidade', on_delete=models.PROTECT, related_name='relatorios_consolidados_da_dre',
                            to_field="codigo_eol", blank=True, null=True, limit_choices_to={'tipo_unidade': 'DRE'})

    tipo_conta = models.ForeignKey('core.TipoConta', on_delete=models.PROTECT, blank=True, null=True)

    periodo = models.ForeignKey('core.Periodo', on_delete=models.PROTECT,
                                related_name='relatorios_consolidados_dre_do_periodo')

    status = models.CharField(
        'status',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NAO_GERADO
    )

    versao = models.CharField(
        'versão',
        max_length=20,
        choices=VERSAO_CHOICES,
        default=VERSAO_FINAL
    )

    class Meta:
        verbose_name = 'Relatório consolidado DRE'
        verbose_name_plural = 'Relatórios consolidados DREs'

    def __str__(self):
        if self.versao == self.VERSAO_PREVIA:
            if self.status == self.STATUS_EM_PROCESSAMENTO:
                status_str = "Previa do relatório sendo gerada. Aguarde."
            elif self.status == self.STATUS_NAO_GERADO:
                status_str = "Documento não gerado"
            else:
                status_str = f"Prévia do documento {'final' if self.status == 'GERADO_TOTAL' else 'parcial'} " \
                             f"gerada dia {self.criado_em.strftime('%d/%m/%Y %H:%M')}"
        elif self.versao == self.VERSAO_FINAL:
            if self.status == self.STATUS_EM_PROCESSAMENTO:
                status_str = "Relatório sendo gerado. Aguarde."
            elif self.status == self.STATUS_NAO_GERADO:
                status_str = "Documento não gerado"
            else:
                status_str = f"Documento {'final' if self.status == 'GERADO_TOTAL' else 'parcial'} " \
                             f"gerado dia {self.criado_em.strftime('%d/%m/%Y %H:%M')}"

        return status_str


@receiver(models.signals.post_delete, sender=RelatorioConsolidadoDRE)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deleta o arquivo do sistema de arquivos quando
    o correspondente objeto 'MediaFile' é deletado.
    """
    if instance.arquivo:
        if os.path.isfile(instance.arquivo.path):
            os.remove(instance.arquivo.path)


@receiver(models.signals.pre_save, sender=RelatorioConsolidadoDRE)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deleta o arquivo antigo do sistema de arquivos quando
    o correspondente objeto 'MediaFile' é atualizado com um
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


auditlog.register(RelatorioConsolidadoDRE)
