from datetime import date
from decimal import Decimal

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models import Associacao, Periodo, Parametros
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from ..tipos_aplicacao_recurso_receitas import APLICACAO_CAPITAL, APLICACAO_CHOICES, APLICACAO_CUSTEIO


class Receita(ModeloBase):
    history = AuditlogHistoryField()

    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, related_name='receitas',
                                   blank=True, null=True)

    data = models.DateField('Data Receita', blank=True, null=True)

    valor = models.DecimalField('Valor Receita', max_digits=20, decimal_places=2, default=0)

    conta_associacao = models.ForeignKey('core.ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='receitas_da_conta', blank=True, null=True)

    acao_associacao = models.ForeignKey('core.AcaoAssociacao', on_delete=models.PROTECT,
                                        related_name='receitas_da_associacao', blank=True, null=True)

    tipo_receita = models.ForeignKey('TipoReceita', on_delete=models.PROTECT, blank=True, null=True)

    conferido = models.BooleanField('Conferido?', default=False)

    update_conferido = models.BooleanField('Atualiza conferido?', default=False)

    categoria_receita = models.CharField(
        'Categoria da receita',
        max_length=15,
        choices=APLICACAO_CHOICES,
        default=APLICACAO_CUSTEIO,
        null=True,
    )

    repasse = models.ForeignKey('Repasse', on_delete=models.PROTECT, related_name='receitas',
                                blank=True, null=True)

    detalhe_tipo_receita = models.ForeignKey('DetalheTipoReceita', on_delete=models.PROTECT, blank=True, null=True)
    detalhe_outros = models.CharField('Detalhe da despesa (outros)', max_length=160, blank=True, default='')

    referencia_devolucao = models.ForeignKey(Periodo, on_delete=models.PROTECT,
                                             related_name='+', blank=True, null=True)

    periodo_conciliacao = models.ForeignKey('core.Periodo', on_delete=models.SET_NULL, blank=True, null=True,
                                        related_name='receitas_conciliadas_no_periodo',
                                        verbose_name='período de conciliação')

    saida_do_recurso = models.CharField('Saída do Recurso (Despesa Uuid)', max_length=100, default='', blank=True)

    def __str__(self):
        return f'RECEITA<{self.detalhamento} - {self.data} - {self.valor}>'

    @property
    def detalhamento(self):
        if self.detalhe_tipo_receita:
            detalhe = self.detalhe_tipo_receita.nome
        else:
            detalhe = self.detalhe_outros
        return detalhe

    @property
    def notificar_dias_nao_conferido(self):
        """
        Se não conferida, retorna o tempo decorrido desde o lançamento, caso esse tempo seja superior ao parametrizado.
        Caso contrário, retorna 0
        :rtype: int
        """
        result = 0
        if not self.conferido:
            decorrido = (date.today() - self.data).days
            limite = Parametros.get().tempo_notificar_nao_demonstrados
            result = decorrido if decorrido >= limite else 0
        return result

    @classmethod
    def receitas_da_acao_associacao_no_periodo(cls, acao_associacao, periodo, conferido=None, conta_associacao=None,
                                               categoria_receita=None):
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
    def totais_por_acao_associacao_no_periodo(cls, acao_associacao, periodo, conta=None):
        receitas = cls.receitas_da_acao_associacao_no_periodo(acao_associacao=acao_associacao,
                                                              periodo=periodo, conta_associacao=conta)
        totais = {
            'total_receitas_capital': Decimal(0.00),
            'total_receitas_devolucao_capital': Decimal(0.00),
            'total_repasses_capital': Decimal(0.00),
            'total_receitas_custeio': Decimal(0.00),
            'total_receitas_devolucao_custeio': Decimal(0.00),
            'total_receitas_devolucao_livre': Decimal(0.00),
            'total_repasses_custeio': Decimal(0.00),
            'total_receitas_livre': Decimal(0.00),
            'total_repasses_livre': Decimal(0.00),
            'total_receitas_nao_conciliadas_capital': Decimal(0.00),
            'total_receitas_nao_conciliadas_custeio': Decimal(0.00),
            'total_receitas_nao_conciliadas_livre': Decimal(0.00),

        }

        for receita in receitas:
            if receita.categoria_receita == APLICACAO_CAPITAL:
                totais['total_receitas_capital'] += receita.valor
            elif receita.categoria_receita == APLICACAO_CUSTEIO:
                totais['total_receitas_custeio'] += receita.valor
            else:
                totais['total_receitas_livre'] += receita.valor

            if receita.tipo_receita.e_repasse:
                if receita.categoria_receita == APLICACAO_CAPITAL:
                    totais['total_repasses_capital'] += receita.valor
                elif receita.categoria_receita == APLICACAO_CUSTEIO:
                    totais['total_repasses_custeio'] += receita.valor
                else:
                    totais['total_repasses_livre'] += receita.valor

            if not receita.conferido:
                if receita.categoria_receita == APLICACAO_CAPITAL:
                    totais['total_receitas_nao_conciliadas_capital'] += receita.valor
                elif receita.categoria_receita == APLICACAO_CUSTEIO:
                    totais['total_receitas_nao_conciliadas_custeio'] += receita.valor
                else:
                    totais['total_receitas_nao_conciliadas_livre'] += receita.valor

            if receita.tipo_receita.e_devolucao:
                if receita.categoria_receita == APLICACAO_CAPITAL:
                    totais['total_receitas_devolucao_capital'] += receita.valor
                elif receita.categoria_receita == APLICACAO_CUSTEIO:
                    totais['total_receitas_devolucao_custeio'] += receita.valor
                else:
                    totais['total_receitas_devolucao_livre'] += receita.valor

        return totais

    def marcar_conferido(self, periodo_conciliacao=None):
        self.update_conferido = True
        self.conferido = True
        self.periodo_conciliacao = periodo_conciliacao
        self.save()
        return self

    def desmarcar_conferido(self):
        self.update_conferido = True
        self.conferido = False
        self.periodo_conciliacao = None
        self.save()
        return self

    def salvar_saida_recurso(self, despesa_uuid=None):
        self.saida_do_recurso = despesa_uuid
        self.save()
        return self

    @classmethod
    def conciliar(cls, uuid, periodo_conciliacao):
        receita = cls.by_uuid(uuid)
        return receita.marcar_conferido(periodo_conciliacao)

    @classmethod
    def desconciliar(cls, uuid):
        receita = cls.by_uuid(uuid)
        return receita.desmarcar_conferido()

    @classmethod
    def atrelar_saida_recurso(cls, uuid, despesa_uuid):
        receita = cls.by_uuid(uuid)
        return receita.salvar_saida_recurso(despesa_uuid)


@receiver(pre_save, sender=Receita)
def rateio_pre_save(instance, **kwargs):
    if instance.tipo_receita.tem_detalhamento():
        instance.detalhe_outros = ""
    else:
        instance.detalhe_tipo_receita = None

    if not instance.update_conferido:
        instance.conferido = False
        instance.periodo_conciliacao = None

    instance.update_conferido = False

auditlog.register(Receita)
