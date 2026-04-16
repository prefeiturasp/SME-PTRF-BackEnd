from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class ReplicaPaa(ModeloBase):
    history = AuditlogHistoryField()

    paa = models.OneToOneField(
        'paa.Paa',
        on_delete=models.CASCADE,
        related_name='replica',
        verbose_name='PAA'
    )

    historico = models.JSONField(
        'Histórico do PAA',
        help_text=(
            "Snapshot serializado do PAA no momento da retificação. "
            "Estrutura: {texto_introducao, texto_conclusao, objetivos, "
            "receitas_ptrf, receitas_pdde, receitas_outros_recursos, prioridades}"
        )
    )

    def __str__(self):
        return f"Réplica do PAA {self.paa.periodo_paa.referencia} ({self.paa.associacao})"

    def formatted_json_replica(self):
        import json
        from django.utils.html import format_html
        if not self.historico:
            return "-"
        formatted = json.dumps(
            self.historico,
            indent=4,
            ensure_ascii=False
        )
        return format_html("<pre>{}</pre>", formatted)
    formatted_json_replica.short_description = 'Snapshot'

    class Meta:
        verbose_name = "Réplica PAA"
        verbose_name_plural = "Réplicas PAA"


auditlog.register(ReplicaPaa)
