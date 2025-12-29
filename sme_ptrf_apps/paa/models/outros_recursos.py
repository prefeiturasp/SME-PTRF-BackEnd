from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


def gerar_cor():
    """
    Gera uma cor aleatória no formato '#rrggbb', tendendo às cores em tonalidades frias.

    Retorna uma string com a cor no formato hexadecimal.
    """
    import random
    r = random.randint(50, 100)
    g = random.randint(100, 160)
    b = random.randint(0, 180)
    return f"#{r:02x}{g:02x}{b:02x}"


class OutroRecurso(ModeloIdNome):
    history = AuditlogHistoryField()

    aceita_capital = models.BooleanField('Aceita capital?', default=False)
    aceita_custeio = models.BooleanField('Aceita custeio?', default=False)
    aceita_livre_aplicacao = models.BooleanField('Aceita livre aplicação?', default=False)

    cor = models.CharField(max_length=10, blank=True, null=True, default=gerar_cor)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Outro Recurso"
        verbose_name_plural = "Outros Recursos"
        unique_together = ['nome',]


auditlog.register(OutroRecurso)
