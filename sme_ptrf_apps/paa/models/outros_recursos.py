"""Modelo para representar recursos adicionais disponíveis para uso no PAA."""
from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


def gerar_cor() -> str:
    """
    Gera uma cor aleatória.

    Retorna uma string com a cor no formato hexadecimal.
    """
    import random
    r = random.randint(50, 100)
    g = random.randint(100, 160)
    b = random.randint(0, 180)
    return f"#{r:02x}{g:02x}{b:02x}"


class OutroRecurso(ModeloIdNome):
    """
    Representa um recurso adicional disponível para uso no PAA.

    Essa model armazena informações sobre recursos adicionais, incluindo o nome do recurso,
    os tipos de aplicação aceitos e a cor associada ao recurso.
    """
    history = AuditlogHistoryField()

    aceita_capital = models.BooleanField('Aceita capital?', default=False)
    aceita_custeio = models.BooleanField('Aceita custeio?', default=False)
    aceita_livre_aplicacao = models.BooleanField('Aceita livre aplicação?', default=False)

    cor = models.CharField(max_length=10, blank=True, null=True, default=gerar_cor)

    def __str__(self) -> str:
        """Retorna o nome do recurso para representação textual."""
        return self.nome

    class Meta:
        verbose_name = "Outro Recurso"
        verbose_name_plural = "Outros Recursos"
        unique_together = ['nome',]


auditlog.register(OutroRecurso)
