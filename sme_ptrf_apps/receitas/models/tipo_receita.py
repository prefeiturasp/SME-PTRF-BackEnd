from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from sme_ptrf_apps.core.models import TipoConta

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

    class Meta:
        verbose_name = 'Tipo de receita'
        verbose_name_plural = 'Tipos de receita'

    def __str__(self):
        return self.nome

    def tem_detalhamento(self):
        return self.detalhes_tipo_receita.exists()


auditlog.register(TipoReceita)
