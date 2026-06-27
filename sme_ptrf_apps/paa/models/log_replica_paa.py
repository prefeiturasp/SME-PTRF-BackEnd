from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class LogReplicaPaa(ModeloBase):
    history = AuditlogHistoryField()

    CANCELAMENTO = 'CANCELAMENTO'
    CONCLUSAO = 'CONCLUSAO'

    ORIGEM_NOMES = {
        CANCELAMENTO: 'Ao Cancelar Retificação',
        CONCLUSAO: 'Ao Concluir Retificação',
    }

    ORIGEM_CHOICES = (
        (CANCELAMENTO, ORIGEM_NOMES[CANCELAMENTO]),
        (CONCLUSAO, ORIGEM_NOMES[CONCLUSAO]),
    )

    paa = models.ForeignKey(
        'paa.Paa',
        on_delete=models.CASCADE,
        related_name='logs_replica',
        verbose_name='PAA'
    )

    origem = models.CharField(
        'origem',
        max_length=30,
        choices=ORIGEM_CHOICES,
        default=CANCELAMENTO
    )

    numero_versao_documento = models.IntegerField(
        'Número da versão do documento gerado',
        null=True,
        blank=True
    )

    replica = models.JSONField(
        'Log Réplica do PAA',
        help_text=("Snapshot serializado do PAA")
    )

    def __str__(self):
        return "Log Réplica do PAA %s (%s) originado por %s" % (
            self.paa.periodo_paa.referencia,
            self.paa.associacao,
            self.origem
        )

    def formatted_json_replica(self):
        import json
        from django.utils.html import format_html
        if not self.replica:
            return "-"
        formatted = json.dumps(
            self.replica,
            indent=4,
            ensure_ascii=False
        )
        return format_html("<pre>{}</pre>", formatted)
    formatted_json_replica.short_description = 'Snapshot'

    class Meta:
        verbose_name = "Log da Réplica PAA"
        verbose_name_plural = "Logs das Réplicas PAA"


auditlog.register(LogReplicaPaa)
