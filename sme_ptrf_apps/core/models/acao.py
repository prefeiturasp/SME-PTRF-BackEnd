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
    recurso = models.ForeignKey(
        "core.Recurso",
        verbose_name="Recurso",
        on_delete=models.PROTECT,
        null=False
    )

    def tem_receitas_previstas_paa_em_elaboracao(self):
        return self.receitas_previstas_paa_em_elaboracao_acao_ptrf().exists()

    def tem_prioridades_paa_em_elaboracao(self):
        return self.prioridades_paa_em_elaboracao_acao_ptrf().exists()

    def prioridades_paa_em_elaboracao_acao_ptrf(self):
        from sme_ptrf_apps.paa.models import PrioridadePaa, Paa
        from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum
        # Utilizando aqui o Queryset de PAA(por ser FK), para obter os PAA em elaboração em
        # um subquery de Prioridades
        paas_em_elaboracao = Paa.objects.filter(pk=models.OuterRef('paa_id')).paas_em_elaboracao()
        prioridades = PrioridadePaa.objects.filter(
            models.Exists(paas_em_elaboracao),
            recurso=RecursoOpcoesEnum.PTRF.name,
            acao_associacao__acao=self
        )
        return prioridades

    def receitas_previstas_paa_em_elaboracao_acao_ptrf(self):
        from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa, Paa
        # Utilizando aqui o Queryset de PAA(por ser FK), para obter os PAA em elaboração em
        # um subquery de Receita prevista
        paas_em_elaboracao = Paa.objects.filter(pk=models.OuterRef('paa_id')).paas_em_elaboracao()
        return ReceitaPrevistaPaa.objects.filter(
            models.Exists(paas_em_elaboracao),
            acao_associacao__acao__uuid=str(self.uuid)
        )

    class Meta:
        verbose_name = "Ação"
        verbose_name_plural = "03.0) Ações"
        unique_together = ['nome',]


auditlog.register(Acao)
