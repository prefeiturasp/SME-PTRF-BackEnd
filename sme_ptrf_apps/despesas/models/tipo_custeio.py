import uuid as uuid
from django.db import models
from django.db.models import Q
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

    @classmethod
    def get_valores(cls, user=None, associacao_uuid=None):
        from sme_ptrf_apps.core.models.associacao import Associacao

        query = cls.objects.all()

        if associacao_uuid:
            try:
                associacao = Associacao.objects.get(uuid=associacao_uuid)
            except Associacao.DoesNotExist:
                associacao = None

            if associacao:
                query = query.filter(Q(unidades__isnull=True) | Q(unidades__in=[associacao.unidade]))

        return query.order_by('nome')

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
