import os
from django.db import models
from django.dispatch import receiver
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class RelacaoBens(ModeloBase):
    arquivo = models.FileField(blank=True, null=True)
    
    conta_associacao = models.ForeignKey('ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='relacoes_de_bens', blank=True, null=True)
    
    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE,
                                        related_name='relacoes_de_bens_da_prestacao', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Relação de bens'
        verbose_name_plural = 'Relações de bens'

    def __str__(self):
        return f"Documento gerado dia {self.criado_em.strftime('%d/%m/%Y %H:%M')}"


@receiver(models.signals.post_delete, sender=RelacaoBens)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deleta o arquivo do sistema de arquivos quando
    o correspondente objeto 'MediaFile' é deletado.
    """
    if instance.arquivo:
        if os.path.isfile(instance.arquivo.path):
            os.remove(instance.arquivo.path)


@receiver(models.signals.pre_save, sender=RelacaoBens)
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
