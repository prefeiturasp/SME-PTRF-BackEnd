from django.db import models
from django.db.models import Q
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from sme_ptrf_apps.core.models import TipoConta, Associacao

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class TipoReceita(ModeloIdNome):
    history = AuditlogHistoryField()
    e_repasse = models.BooleanField("É repasse?", default=False)
    e_rendimento = models.BooleanField("É rendimento?", default=False)
    e_devolucao = models.BooleanField("É devolução?", default=False)
    e_estorno = models.BooleanField("É estorno?", default=False)
    aceita_capital = models.BooleanField('Aceita capital?', default=False)
    aceita_custeio = models.BooleanField('Aceita custeio?', default=False)
    aceita_livre = models.BooleanField('Aceita livre aplicação?', default=False)
    e_recursos_proprios = models.BooleanField("Recursos Externos", default=False)

    tipos_conta = models.ManyToManyField(TipoConta, blank=True)
    mensagem_usuario = models.TextField('Mensagem para o usuario', blank=True, default='')
    possui_detalhamento = models.BooleanField('Deve exibir detalhamento?', default=False)

    unidades = models.ManyToManyField('core.Unidade', null=True, blank=True)
    class Meta:
        verbose_name = 'Tipo de receita'
        verbose_name_plural = 'Tipos de receita'

    def __str__(self):
        return self.nome

    def tem_detalhamento(self):
        return self.detalhes_tipo_receita.exists()

    @classmethod
    def get_valores(cls, user=None, associacao_uuid=None):
        query = cls.objects.all()

        if associacao_uuid:
            try:
                associacao = Associacao.objects.get(uuid=associacao_uuid)
            except Associacao.DoesNotExist:
                pass

            if associacao:
                query = query.filter(Q(unidades__isnull=True) | Q(unidades__in=[associacao.unidade]))

        return query.order_by('nome')

auditlog.register(TipoReceita)
