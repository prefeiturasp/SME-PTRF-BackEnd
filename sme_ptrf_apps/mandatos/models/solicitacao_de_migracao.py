from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.core.exceptions import ValidationError


class StatusProcessamento(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    PROCESSANDO = "PROCESSANDO", "Processando..."
    SUCESSO = "SUCESSO", "Sucesso"
    ERRO = "ERRO", "Erro"


class SolicitacaoDeMigracao(ModeloBase):
    history = AuditlogHistoryField()

    eol_unidade = models.ForeignKey(
        'core.Unidade',
        on_delete=models.PROTECT,
        related_name='migracoes_da_unidade',
        to_field="codigo_eol",
        blank=True,
        null=True,
        verbose_name="Migrar apenas uma unidade",
        help_text="Busque pelo código EOL da Unidade",
    )

    dre = models.ForeignKey(
        'core.Unidade',
        on_delete=models.PROTECT,
        related_name='migracoes_da_dre',
        to_field="codigo_eol",
        blank=True,
        null=True,
        verbose_name="Migrar as unidades da DRE",
        help_text="Escolha a DRE que você deseja migrar",
        limit_choices_to={'tipo_unidade': 'DRE'}
    )

    todas_as_unidades = models.BooleanField(
        'Migrar todas as unidades',
        help_text="Selecione esta opção se você deseja migrar todas as unidades de uma vez",
        default=False
    )

    status_processamento = models.CharField(
        "Status do processamento",
        max_length=20,
        choices=StatusProcessamento.choices,
        default=StatusProcessamento.PENDENTE,
        help_text="Status do processamento da migração.",
    )

    log_execucao = models.TextField(
        "Log de migração",
        blank=True,
        null=True,
        help_text="Log de execução da migração.",
    )

    class Meta:
        verbose_name = 'Solicitação de migração'
        verbose_name_plural = 'Solicitações de migração'

    def __str__(self):
        if self.eol_unidade:
            return f"Migração da Unidade: {self.eol_unidade}"
        elif self.dre:
            return f"Migração das Unidades da DRE: {self.dre}"
        else:
            return f"Migração de todas as Unidades"

    def inicia_processamento(self):
        self.status_processamento = StatusProcessamento.PROCESSANDO
        self.save()

    def clean(self):
        super().clean()

        if self.eol_unidade is None and self.dre is None and not self.todas_as_unidades:
            raise ValidationError("Você deve escolher uma das opções: "
                                  "Migrar apenas uma unidade, Migrar as unidades da DRE ou Migrar todas as unidades")

        if sum(1 for field in [self.eol_unidade, self.dre, self.todas_as_unidades] if field) > 1:
            raise ValidationError("Escolha apenas uma das opções: "
                                  "Migrar apenas uma unidade, Migrar as unidades da DRE ou Migrar todas as unidades")

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)


auditlog.register(SolicitacaoDeMigracao)
