"""Modelo para representar uma fonte de recurso do PAA."""
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class FonteRecursoPaa(ModeloIdNome):
    """
    Modelo para representar uma fonte de recurso do PAA.
    """
    history = AuditlogHistoryField()

    def __str__(self) -> str:
        """Retorna o nome da fonte de recurso PAA para representação textual."""
        return self.nome

    class Meta:
        verbose_name = "Fonte Recursos PAA"
        verbose_name_plural = "Fonte Recursos PAA"


auditlog.register(FonteRecursoPaa)
