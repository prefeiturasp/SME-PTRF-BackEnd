import os
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome, TemAtivo

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class Recurso(ModeloIdNome, TemAtivo):
    history = AuditlogHistoryField()

    class CorChoices(models.TextChoices):
        AZUL = "#3982AC", "Azul"
        VERDE = "#01585E", "Verde"
        AZUL_MARINHO = "#0D3B66", "Azul Marinho"
        LARANJA = "#C65A1E", "Laranja"
        ROXO = "#4B2E83", "Roxo Profundo"

    nome_exibicao = models.CharField(
        verbose_name='Nome exibição', help_text='Será usado no seletor de recursos do site.', max_length=160)

    icone = models.FileField(
        verbose_name='Ícone', help_text='Será usado no menu lateral e modal de escolha de recurso.', blank=True, null=True)

    cor = models.CharField(
        max_length=7,
        help_text='Será usada na estilização do site.',
        choices=CorChoices.choices,
    )

    legado = models.BooleanField(verbose_name="Legado?",
                                 help_text='Em caso de flag inativa, esse recurso será utilizado nos filtros. '
                                           'No caso da SME/SP, o recurso legado refere-se ao PTRF.',
                                 default=False
                                )

    exibe_valores_reprogramados = models.BooleanField(
        verbose_name="Exibir valores reprogramados?",
        default=False,
        null=False,
        blank=False
    )

    habilita_aprovacao_com_ressalvas = models.BooleanField(
        verbose_name="Habilitar Aprovação com ressalvas",
        help_text="Define se o recurso exibe a opção de aprovação com ressalvas.",
        default=False,
    )

    permite_saldo_conta_negativo = models.BooleanField('Permite saldo negativo em contas?', default=False)

    permite_saldo_acoes_negativo = models.BooleanField('Permite saldo negativo em ações?', default=False)

    tipo_conta_um = models.ForeignKey(
        "core.TipoConta",
        on_delete=models.CASCADE,
        related_name="recurso_tipo_conta_um",
        null=True,
        blank=True,
        default=None,
    )

    tipo_conta_dois = models.ForeignKey(
        "core.TipoConta",
        on_delete=models.CASCADE,
        related_name="recurso_tipo_conta_dois",
        null=True,
        blank=True,
        default=None,
    )

    class Meta:
        verbose_name = 'Recurso'
        verbose_name_plural = '20.0) Recursos'
        constraints = [
            models.UniqueConstraint(
                fields=["legado"],
                condition=Q(legado=True),
                name="unique_recurso_legado",
                violation_error_message="Já existe um recurso marcado como legado."
            )
        ]

    def __str__(self):
        return self.nome


@receiver(models.signals.post_delete, sender=Recurso)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deleta o arquivo do sistema de arquivos quando
    o correspondente objeto 'MediaFile' é deletado.
    """

    if instance.icone:
        if os.path.isfile(instance.icone.path):
            os.remove(instance.icone.path)


@receiver(models.signals.pre_save, sender=Recurso)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deleta o arquivo antigo do sistema de arquivos quando
    o correspondente objeti 'MediaFile' é atualizado com um
    novo arquivo.
    """

    if not instance.pk:
        return False

    try:
        old_icone_file = sender.objects.get(pk=instance.pk).icone
    except sender.DoesNotExist:
        return False

    new_icone_file = instance.icone
    if old_icone_file and not old_icone_file == new_icone_file:
        if os.path.isfile(old_icone_file.path):
            os.remove(old_icone_file.path)


auditlog.register(Recurso)
