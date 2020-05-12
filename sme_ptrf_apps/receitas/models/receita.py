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

    def __str__(self):
        return f'RECEITA<{self.descricao} - {self.data} - {self.valor}>'

    @classmethod
    def receitas_da_acao_associacao_no_periodo(cls, acao_associacao, periodo):
        if periodo.data_fim_realizacao_despesas:
            return cls.objects.filter(acao_associacao=acao_associacao).filter(
                data__range=(periodo.data_inicio_realizacao_despesas, periodo.data_fim_realizacao_despesas)).all()
        else:
            return cls.objects.filter(acao_associacao=acao_associacao).filter(
                data__gte=periodo.data_inicio_realizacao_despesas).all()

    def marcar_conferido(self):
        self.conferido = True
        self.save()
        return self

    def desmarcar_conferido(self):
        self.conferido = False
        self.save()
        return self

    @classmethod
    def conciliar(cls, uuid):
        receita = cls.by_uuid(uuid)
        return receita.marcar_conferido()

    @classmethod
    def desconciliar(cls, uuid):
        receita = cls.by_uuid(uuid)
        return receita.desmarcar_conferido()

auditlog.register(Receita)
