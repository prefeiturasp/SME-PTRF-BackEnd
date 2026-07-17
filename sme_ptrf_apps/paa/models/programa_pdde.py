"""
Módulo de modelos do programas PDDE.

Este módulo define a entidade responsável por
representar os programas PDDE seus atributos de negócio.
"""
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class ProgramaPdde(ModeloIdNome):
    """
    Representa um programa PDDE.

    Essa model registra armazena os dados do programa PDDE.
    """
    history = AuditlogHistoryField()

    class Meta:
        verbose_name = "Programa PDDE"
        verbose_name_plural = "Programas PDDE"
        unique_together = ['nome',]


auditlog.register(ProgramaPdde)
