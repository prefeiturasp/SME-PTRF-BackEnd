from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class Acao(ModeloIdNome):
    history = AuditlogHistoryField()
    posicao_nas_pesquisas = models.CharField(
        'posição nas pesquisas',
        max_length=10,
        blank=True,
        default='ZZZZZZZZZZ',
        help_text='A ordem alfabética desse texto definirá a ordem que a ação será exibida nas pesquisas.'
    )

    e_recursos_proprios = models.BooleanField("Recursos Externos", default=False)
    aceita_capital = models.BooleanField('Aceita capital?', default=False)
    aceita_custeio = models.BooleanField('Aceita custeio?', default=False)
    aceita_livre = models.BooleanField('Aceita livre aplicação?', default=False)
    exibir_paa = models.BooleanField(
        'Exibir no PAA?', default=True,
        help_text='Considera a Ação para o PAA (Receitas previstas PAA, Prioridades do PAA)')

    def tem_receitas_previstas_paa_em_elaboracao(self):
        return self.receitas_previstas_paa_em_elaboracao_acao_ptrf().exists()

    def tem_prioridades_paa_em_elaboracao(self):
        return self.prioridades_paa_em_elaboracao_acao_ptrf().exists()

    def prioridades_paa_em_elaboracao_acao_ptrf(self):
        from sme_ptrf_apps.paa.models import PrioridadePaa
        from sme_ptrf_apps.paa.enums import PaaStatusEnum, RecursoOpcoesEnum
        return PrioridadePaa.objects.filter(
            paa__status=PaaStatusEnum.EM_ELABORACAO.name,
            recurso=RecursoOpcoesEnum.PTRF.name,
            acao_associacao__acao=self
        )

    def receitas_previstas_paa_em_elaboracao_acao_ptrf(self):
        from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa
        from sme_ptrf_apps.paa.enums import PaaStatusEnum
        return ReceitaPrevistaPaa.objects.filter(
            paa__status=PaaStatusEnum.EM_ELABORACAO.name,
            acao_associacao__acao__uuid=str(self.uuid)
        )

    class Meta:
        verbose_name = "Ação"
        verbose_name_plural = "03.0) Ações"
        unique_together = ['nome',]


auditlog.register(Acao)
