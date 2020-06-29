from decimal import Decimal

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.db import models

from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CHOICES, APLICACAO_CUSTEIO


class Receita(ModeloBase):
    history = AuditlogHistoryField()

    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, related_name='receitas',
                                   blank=True, null=True)

    data = models.DateField('Data Receita', blank=True, null=True)

    valor = models.DecimalField('Valor Receita', max_digits=20, decimal_places=2, default=0)

    descricao = models.TextField('Descrição', max_length=400, blank=True, null=True)

    conta_associacao = models.ForeignKey('core.ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='receitas_da_conta', blank=True, null=True)

    acao_associacao = models.ForeignKey('core.AcaoAssociacao', on_delete=models.PROTECT,
                                        related_name='receitas_da_associacao', blank=True, null=True)

    tipo_receita = models.ForeignKey('TipoReceita', on_delete=models.PROTECT, blank=True, null=True)

    conferido = models.BooleanField('Conferido?', default=False)

    categoria_receita = models.CharField(
        'Categoria da receita',
        max_length=15,
        choices=APLICACAO_CHOICES,
        default=APLICACAO_CUSTEIO,
        null=True,
    )

    prestacao_conta = models.ForeignKey('core.PrestacaoConta', on_delete=models.SET_NULL, blank=True, null=True,
                                        related_name='receitas_conciliadas',
                                        verbose_name='prestação de contas de conciliação')

    repasse = models.ForeignKey('Repasse', on_delete=models.PROTECT, related_name='receitas',
                                   blank=True, null=True)

    detalhe_tipo_receita = models.ForeignKey('DetalheTipoReceita', on_delete=models.PROTECT, blank=True, null=True)
    detalhe_outros = models.CharField('Detalhe da despesa (outros)', max_length=160, blank=True, default='')

    def __str__(self):
        return f'RECEITA<{self.descricao} - {self.data} - {self.valor}>'

    @property
    def detalhamento(self):
        if self.detalhe_tipo_receita:
            detalhe = self.detalhe_tipo_receita.nome
        else:
            detalhe = self.detalhe_outros
        return detalhe

    @classmethod
    def receitas_da_acao_associacao_no_periodo(cls, acao_associacao, periodo, conferido=None, conta_associacao=None, categoria_receita=None):
        if periodo.data_fim_realizacao_despesas:
            dataset = cls.objects.filter(acao_associacao=acao_associacao).filter(
                data__range=(periodo.data_inicio_realizacao_despesas, periodo.data_fim_realizacao_despesas))
        else:
            dataset = cls.objects.filter(acao_associacao=acao_associacao).filter(
                data__gte=periodo.data_inicio_realizacao_despesas)

        if conferido is not None:
            dataset = dataset.filter(conferido=conferido)

        if conta_associacao:
            dataset = dataset.filter(conta_associacao=conta_associacao)

        if categoria_receita:
            dataset = dataset.filter(categoria_receita=categoria_receita)

        return dataset.all()

    @classmethod
    def receitas_da_conta_associacao_no_periodo(cls, conta_associacao, periodo, conferido=None):
        if periodo.data_fim_realizacao_despesas:
            dataset = cls.objects.filter(conta_associacao=conta_associacao).filter(
                data__range=(periodo.data_inicio_realizacao_despesas, periodo.data_fim_realizacao_despesas))
        else:
            dataset = cls.objects.filter(conta_associacao=conta_associacao).filter(
                data__gte=periodo.data_inicio_realizacao_despesas)

        if conferido is not None:
            dataset = dataset.filter(conferido=conferido)

        return dataset.all()

    @classmethod
    def totais_por_acao_associacao_no_periodo(cls, acao_associacao, periodo):
        receitas = cls.receitas_da_acao_associacao_no_periodo(acao_associacao=acao_associacao,
                                                              periodo=periodo)
        totais = {
            'total_receitas_capital': Decimal(0.00),
            'total_repasses_capital': Decimal(0.00),
            'total_receitas_custeio': Decimal(0.00),
            'total_repasses_custeio': Decimal(0.00),
            'total_receitas_nao_conciliadas_capital': Decimal(0.00),
            'total_receitas_nao_conciliadas_custeio': Decimal(0.00),

        }

        for receita in receitas:
            if receita.categoria_receita == APLICACAO_CAPITAL:
                totais['total_receitas_capital'] += receita.valor
            else:
                totais['total_receitas_custeio'] += receita.valor

            if receita.tipo_receita.e_repasse:
                if receita.categoria_receita == APLICACAO_CAPITAL:
                    totais['total_repasses_capital'] += receita.valor
                else:
                    totais['total_repasses_custeio'] += receita.valor

            if not receita.conferido:
                if receita.categoria_receita == APLICACAO_CAPITAL:
                    totais['total_receitas_nao_conciliadas_capital'] += receita.valor
                else:
                    totais['total_receitas_nao_conciliadas_custeio'] += receita.valor

        return totais

    def marcar_conferido(self, prestacao_conta=None):
        self.conferido = True
        self.prestacao_conta=prestacao_conta
        self.save()
        return self

    def desmarcar_conferido(self):
        self.conferido = False
        self.prestacao_conta=None
        self.save()
        return self

    @classmethod
    def conciliar(cls, uuid, prestacao_conta):
        receita = cls.by_uuid(uuid)
        return receita.marcar_conferido(prestacao_conta)

    @classmethod
    def desconciliar(cls, uuid):
        receita = cls.by_uuid(uuid)
        return receita.desmarcar_conferido()


auditlog.register(Receita)
