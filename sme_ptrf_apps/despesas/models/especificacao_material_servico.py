from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from ..tipos_aplicacao_recurso import APLICACAO_CHOICES, APLICACAO_CUSTEIO

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class EspecificacaoMaterialServico(ModeloBase):
    history = AuditlogHistoryField()
    descricao = models.CharField('Descrição', max_length=200)

    aplicacao_recurso = models.CharField(
        'Tipo de aplicação do recurso',
        max_length=15,
        choices=APLICACAO_CHOICES,
        default=APLICACAO_CUSTEIO
    )
    tipo_custeio = models.ForeignKey('TipoCusteio', on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return f"{self.descricao}"

    class Meta:
        verbose_name = "Especificação de material ou serviço"
        verbose_name_plural = "Especificações de materiais ou serviços"


auditlog.register(EspecificacaoMaterialServico)
