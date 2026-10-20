"""Modelo para representar um objetivo do PAA."""
from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class StatusChoices(models.IntegerChoices):
    """Enumeração para representar os status de ativação de uma entidade."""
    ATIVO = 1, "Ativo"
    INATIVO = 0, "Inativo"

    @classmethod
    def to_dict(cls) -> list[dict[str, str]]:
        """
        Retorna uma lista de dicionários representando os status disponíveis.
        Cada dicionário contém a chave 'key' com o valor do status e a chave
        'value' com o rótulo do status.
        """
        return [dict(key=key.value, value=key.label) for key in cls]


class ObjetivoPaa(ModeloBase):
    """
    Modelo para representar um objetivo do PAA.

    Este modelo armazena informações sobre os objetivos do PAA, incluindo o nome do objetivo,
    o PAA ao qual está associado e o status de ativação da entidade.
    """
    history = AuditlogHistoryField()
    nome = models.CharField('Objetivo', max_length=160, blank=False)
    paa = models.ForeignKey('paa.Paa', on_delete=models.PROTECT, verbose_name="PAA", blank=True, null=True)
    status = models.BooleanField(choices=StatusChoices.choices, default=StatusChoices.ATIVO)

    def __str__(self) -> str:
        """Retorna uma representação textual do objetivo com o nome."""
        return self.nome

    class Meta:
        verbose_name = "Objetivo do PAA"
        verbose_name_plural = "Objetivos do PAA"


auditlog.register(ObjetivoPaa)
