import uuid as uuid
from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class TipoCusteio(ModeloIdNome):
    history = AuditlogHistoryField()
    eh_tributos_e_tarifas = models.BooleanField('Impostos de serviço', default=False)
    unidades = models.ManyToManyField('core.Unidade', blank=True)

    class Meta:
        verbose_name = "Tipo de despesa de custeio"
        verbose_name_plural = "Tipos de despesa de custeio"
        unique_together = ['nome', ]

    def pode_vincular(self, unidades_uuid):
        unidades_uuid_set = {uuid.UUID(u) for u in unidades_uuid}

        unidades_permitidas = unidades_uuid_set | set(self.unidades.values_list('uuid', flat=True))

        unidades_com_rateio = set(self.rateiodespesa_set.values_list('despesa__associacao__unidade__uuid', flat=True))

        return unidades_com_rateio.issubset(unidades_permitidas)

    def pode_desvincular(self, unidades_uuid):
        unidades_uuid_set = {uuid.UUID(u) for u in unidades_uuid}

        unidades_com_rateio = set(self.rateiodespesa_set.values_list('despesa__associacao__unidade__uuid', flat=True))

        return unidades_com_rateio.isdisjoint(unidades_uuid_set)


auditlog.register(TipoCusteio)
