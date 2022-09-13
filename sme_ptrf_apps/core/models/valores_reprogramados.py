from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.receitas.tipos_aplicacao_recurso_receitas import APLICACAO_CHOICES
from sme_ptrf_apps.receitas.tipos_aplicacao_recurso_receitas import \
    APLICACAO_CAPITAL, APLICACAO_CUSTEIO, APLICACAO_LIVRE

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class ValoresReprogramados(ModeloBase):
    history = AuditlogHistoryField()

    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT,
                                   related_name='valores_reprogramados_associacao')

    periodo = models.ForeignKey('Periodo', on_delete=models.PROTECT, related_name='valores_reprogramados')

    conta_associacao = models.ForeignKey('ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='valores_reprogramados_da_conta')

    acao_associacao = models.ForeignKey('AcaoAssociacao', on_delete=models.PROTECT,
                                        related_name='valores_reprogramados_da_acao')

    aplicacao_recurso = models.CharField(
        'Tipo de aplicação do recurso',
        max_length=15,
        choices=APLICACAO_CHOICES,
    )

    valor_ue = models.DecimalField('Valor UE', max_digits=12, decimal_places=2, blank=True, null=True)

    valor_dre = models.DecimalField('Valor DRE', max_digits=12, decimal_places=2, blank=True, null=True)

    @classmethod
    def criar(cls, associacao, periodo, conta_associacao, acao_associacao, aplicacao_recurso, valor_ue,
              valor_dre, visao_selecionada):

        valores_reprogramados = None

        if visao_selecionada == "UE":
            valores_reprogramados, _ = cls.objects.update_or_create(
                associacao=associacao,
                periodo=periodo,
                conta_associacao=conta_associacao,
                acao_associacao=acao_associacao,
                aplicacao_recurso=aplicacao_recurso,
                defaults={
                    'valor_ue': valor_ue,
                },
            )
        elif visao_selecionada == "DRE":
            valores_reprogramados, _ = cls.objects.update_or_create(
                associacao=associacao,
                periodo=periodo,
                conta_associacao=conta_associacao,
                acao_associacao=acao_associacao,
                aplicacao_recurso=aplicacao_recurso,
                defaults={
                    'valor_dre': valor_dre,
                },
            )

        return valores_reprogramados

    @classmethod
    def criar_valor_reprogramado_custeio(cls, associacao, conta_associacao, acao_associacao, fechamento_implantacao):
        periodo = fechamento_implantacao.periodo if fechamento_implantacao else associacao.periodo_inicial
        valor_ue_custeio = fechamento_implantacao.saldo_reprogramado_custeio if fechamento_implantacao else 0.00
        valor_dre_custeio = fechamento_implantacao.saldo_reprogramado_custeio if fechamento_implantacao else 0.00

        valores_reprogramados = cls.objects.create(
            associacao=associacao,
            periodo=periodo,
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            aplicacao_recurso=APLICACAO_CUSTEIO,
            valor_dre=valor_dre_custeio,
            valor_ue=valor_ue_custeio
        )

        return valores_reprogramados

    @classmethod
    def criar_valor_reprogramado_capital(cls, associacao, conta_associacao, acao_associacao, fechamento_implantacao):
        periodo = fechamento_implantacao.periodo if fechamento_implantacao else associacao.periodo_inicial
        valor_ue_capital = fechamento_implantacao.saldo_reprogramado_capital if fechamento_implantacao else 0.00
        valor_dre_capital = fechamento_implantacao.saldo_reprogramado_capital if fechamento_implantacao else 0.00

        valores_reprogramados = cls.objects.create(
            associacao=associacao,
            periodo=periodo,
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            aplicacao_recurso=APLICACAO_CAPITAL,
            valor_dre=valor_dre_capital,
            valor_ue=valor_ue_capital
        )

        return valores_reprogramados

    @classmethod
    def criar_valor_reprogramado_livre(cls, associacao, conta_associacao, acao_associacao, fechamento_implantacao):
        periodo = fechamento_implantacao.periodo if fechamento_implantacao else associacao.periodo_inicial
        valor_ue_livre = fechamento_implantacao.saldo_reprogramado_livre if fechamento_implantacao else 0.00
        valor_dre_livre = fechamento_implantacao.saldo_reprogramado_livre if fechamento_implantacao else 0.00

        valores_reprogramados = cls.objects.create(
            associacao=associacao,
            periodo=periodo,
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            aplicacao_recurso=APLICACAO_LIVRE,
            valor_dre=valor_dre_livre,
            valor_ue=valor_ue_livre
        )

        return valores_reprogramados

    class Meta:
        verbose_name = "Valores reprogramados"
        verbose_name_plural = "18.0) Valores reprogramados"


auditlog.register(ValoresReprogramados)
