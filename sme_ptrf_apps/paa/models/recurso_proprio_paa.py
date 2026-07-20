"""
Módulo de modelos do recurso próprio  do PAA (Plano Anual de Ação).

Este módulo define a entidade responsável por
representar os recurso próprio  do PAA e seus atributos de negócio.
"""
from datetime import date

from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.paa.models import FonteRecursoPaa, Paa
from sme_ptrf_apps.core.models import Associacao


class RecursoProprioPaa(ModeloBase):
    """
    Representa um recurso próprio do paa.

    Essa model registra armazena os dados do recurso próprio do paa,
    informações sobre o paa, a fonte do recurso e a associação.
    """
    history = AuditlogHistoryField()
    paa = models.ForeignKey(Paa, on_delete=models.PROTECT, verbose_name="PAA", blank=False, null=True)
    fonte_recurso = models.ForeignKey(FonteRecursoPaa, on_delete=models.PROTECT, related_name='recurso_proprio')
    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, related_name='associacao')
    data_prevista = models.DateField(default=date.today)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField('Valor', max_digits=20, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Recurso Próprio do PAA"
        verbose_name_plural = "Recursos Próprios do PAA"


auditlog.register(RecursoProprioPaa)
