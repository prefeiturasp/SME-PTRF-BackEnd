"""
Módulo de modelos de uma replica do PAA.

Este módulo define a entidade responsável por representar a uma replica do PAA
e seus atributos de negócio.
"""
from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class ReplicaPaa(ModeloBase):
    """
    Representa uma replica do PAA.

    Essa model registra os dados do PAA, e o histórico do PAA.
    """
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

    def __str__(self) -> str:
        """Retorna uma representação textual do PAA com o período e a associação."""
        return f"Réplica do PAA {self.paa.periodo_paa.referencia} ({self.paa.associacao})"

    def formatted_json_replica(self) -> str:
        """
        Retorna o conteúdo do campo ``historico`` formatado como JSON para
        exibição no Django Admin.

        Returns:
            str: O JSON formatado envolvido na tag ``<pre>`` ou ``"-"`` quando
            não houver histórico disponível.
        """
        import json
        from django.utils.html import format_html
        if self.historico is None:
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
