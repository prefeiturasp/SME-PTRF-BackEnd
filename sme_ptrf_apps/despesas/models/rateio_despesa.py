from datetime import date
from decimal import Decimal

from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models import Tag, Parametros
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from ..status_cadastro_completo import STATUS_CHOICES, STATUS_COMPLETO, STATUS_INCOMPLETO
from ..tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CHOICES, APLICACAO_CUSTEIO

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class RateiosCompletosManager(models.Manager):
    def get_queryset(self):
        return super(RateiosCompletosManager, self).get_queryset().filter(despesa__status=STATUS_COMPLETO)


class RateioDespesa(ModeloBase):
    history = AuditlogHistoryField()
    despesa = models.ForeignKey('Despesa', on_delete=models.CASCADE, related_name='rateios', blank=True, null=True)

    associacao = models.ForeignKey('core.Associacao', on_delete=models.PROTECT, related_name='rateios_associacao',
                                   blank=True, null=True)

    conta_associacao = models.ForeignKey('core.ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='rateios_da_conta', blank=True, null=True)

    acao_associacao = models.ForeignKey('core.AcaoAssociacao', on_delete=models.PROTECT,
                                        related_name='rateios_da_associacao', blank=True, null=True)

    aplicacao_recurso = models.CharField(
        'Tipo de aplicação do recurso',
        max_length=15,
        choices=APLICACAO_CHOICES,
        default=APLICACAO_CUSTEIO,
        null=True,
    )

    tipo_custeio = models.ForeignKey('TipoCusteio', on_delete=models.PROTECT, blank=True, null=True)

    especificacao_material_servico = models.ForeignKey('EspecificacaoMaterialServico', on_delete=models.PROTECT,
                                                       blank=True, null=True)

    valor_rateio = models.DecimalField('Valor', max_digits=8, decimal_places=2, default=0)

    quantidade_itens_capital = models.PositiveSmallIntegerField('Quantidade de itens', default=0)
    valor_item_capital = models.DecimalField('Valor unitário ', max_digits=8, decimal_places=2, default=0)
    numero_processo_incorporacao_capital = models.CharField('Nº processo incorporação', max_length=100, default='',
                                                            blank=True)

    valor_original = models.DecimalField('Valor original', max_digits=8, decimal_places=2,
                                         default=0)

    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_INCOMPLETO
    )

    conferido = models.BooleanField('Conferido?', default=False)

    update_conferido = models.BooleanField('Atualiza conferido?', default=False)

    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, blank=True,
                            null=True, related_name='rateios')

    periodo_conciliacao = models.ForeignKey('core.Periodo', on_delete=models.SET_NULL, blank=True, null=True,
                                            related_name='despesas_conciliadas_no_periodo',
                                            verbose_name='período de conciliação')

    saida_de_recurso_externo = models.BooleanField('É saída de recurso externo?', default=False)

    eh_despesa_sem_comprovacao_fiscal = models.BooleanField('É despesa sem comprovação fiscal?', default=False)

    objects = models.Manager()  # Manager Padrão
    completos = RateiosCompletosManager()

    def __str__(self):
        # O retorno de informações da Despesa quebra o auditlog

        return f"Rateio {self.pk}"

    def cadastro_completo(self):
        completo = self.conta_associacao and \
                   self.acao_associacao and \
                   self.aplicacao_recurso and \
                   self.valor_rateio

        if not self.saida_de_recurso_externo and not self.eh_despesa_sem_comprovacao_fiscal:
            completo = completo and self.especificacao_material_servico

        if self.aplicacao_recurso == APLICACAO_CUSTEIO:
            if not self.saida_de_recurso_externo and not self.eh_despesa_sem_comprovacao_fiscal:
                completo = completo and self.tipo_custeio
        elif self.aplicacao_recurso == APLICACAO_CAPITAL:
            completo = completo and \
                       self.quantidade_itens_capital > 0 and \
                       self.valor_item_capital > 0 and self.numero_processo_incorporacao_capital

        return completo

    @property
    def notificar_dias_nao_conferido(self):
        """
        Se não conferida, retorna o tempo decorrido desde o lançamento, caso esse tempo seja superior ao parametrizado.
        Caso contrário, retorna 0
        :rtype: int
        """
        result = 0
        if not self.conferido and self.despesa.data_transacao:
            decorrido = (date.today() - self.despesa.data_transacao).days
            limite = Parametros.get().tempo_notificar_nao_demonstrados
            result = decorrido if decorrido >= limite else 0
        return result

    @classmethod
    def rateios_da_acao_associacao_no_periodo(cls, acao_associacao, periodo, conferido=None, conta_associacao=None,
                                              exclude_despesa=None, aplicacao_recurso=None):
        if periodo.data_fim_realizacao_despesas:
            dataset = cls.completos.filter(acao_associacao=acao_associacao).filter(
                despesa__data_documento__range=(
                    periodo.data_inicio_realizacao_despesas, periodo.data_fim_realizacao_despesas))
        else:
            dataset = cls.completos.filter(acao_associacao=acao_associacao).filter(
                despesa__data_documento__gte=periodo.data_inicio_realizacao_despesas)

        if conferido is not None:
            dataset = dataset.filter(conferido=conferido)

        if conta_associacao:
            dataset = dataset.filter(conta_associacao=conta_associacao)

        if exclude_despesa:
            dataset = dataset.exclude(despesa__uuid=exclude_despesa)

        if aplicacao_recurso:
            dataset = dataset.filter(aplicacao_recurso=aplicacao_recurso)

        return dataset.all()

    @classmethod
    def rateios_da_conta_associacao_no_periodo(cls, conta_associacao, periodo, conferido=None,
                                               exclude_despesa=None, aplicacao_recurso=None, acao_associacao=None):
        if periodo.data_fim_realizacao_despesas:
            dataset = cls.completos.filter(conta_associacao=conta_associacao).filter(
                despesa__data_documento__range=(
                    periodo.data_inicio_realizacao_despesas, periodo.data_fim_realizacao_despesas))
        else:
            dataset = cls.completos.filter(conta_associacao=conta_associacao).filter(
                despesa__data_documento__gte=periodo.data_inicio_realizacao_despesas)

        if conferido is not None:
            dataset = dataset.filter(conferido=conferido)

        if exclude_despesa:
            dataset = dataset.exclude(despesa__uuid=exclude_despesa)

        if aplicacao_recurso:
            dataset = dataset.filter(aplicacao_recurso=aplicacao_recurso)

        if acao_associacao:
            dataset = dataset.filter(acao_associacao=acao_associacao)

        return dataset.all()

    @classmethod
    def rateios_da_conta_associacao_em_periodos_anteriores(cls, conta_associacao, periodo, conferido=None,
                                                           exclude_despesa=None, aplicacao_recurso=None):

        dataset = cls.completos.filter(conta_associacao=conta_associacao).filter(
            despesa__data_documento__lte=periodo.data_inicio_realizacao_despesas)

        if conferido is not None:
            dataset = dataset.filter(conferido=conferido)

        if exclude_despesa:
            dataset = dataset.exclude(despesa__uuid=exclude_despesa)

        if aplicacao_recurso:
            dataset = dataset.filter(aplicacao_recurso=aplicacao_recurso)

        return dataset.all()

    @classmethod
    def especificacoes_dos_rateios_da_acao_associacao_no_periodo(cls, acao_associacao, periodo, conferido=None,
                                                                 conta_associacao=None,
                                                                 exclude_despesa=None):

        rateios = cls.rateios_da_acao_associacao_no_periodo(acao_associacao=acao_associacao,
                                                            periodo=periodo, conferido=conferido,
                                                            conta_associacao=conta_associacao,
                                                            exclude_despesa=exclude_despesa)

        especificacoes = {
            APLICACAO_CAPITAL: set(),
            APLICACAO_CUSTEIO: set()
        }
        for rateio in rateios:
            if rateio.especificacao_material_servico:
                especificacoes[rateio.aplicacao_recurso].add(rateio.especificacao_material_servico.descricao)

        return {
            APLICACAO_CAPITAL: sorted(especificacoes[APLICACAO_CAPITAL]),
            APLICACAO_CUSTEIO: sorted(especificacoes[APLICACAO_CUSTEIO])
        }

    @classmethod
    def rateios_da_acao_associacao_em_qualquer_periodo(cls, acao_associacao, conferido=None, conta_associacao=None,
                                                       exclude_despesa=None, aplicacao_recurso=None):

        dataset = cls.completos.filter(acao_associacao=acao_associacao,
                                       despesa__data_documento__lte=date.today())

        if conferido is not None:
            dataset = dataset.filter(conferido=conferido)

        if exclude_despesa:
            dataset = dataset.exclude(despesa__uuid=exclude_despesa)

        if conta_associacao:
            dataset = dataset.filter(conta_associacao=conta_associacao)

        if aplicacao_recurso:
            dataset = dataset.filter(aplicacao_recurso=aplicacao_recurso)

        return dataset.all()

    @classmethod
    def rateios_da_acao_associacao_em_periodo_anteriores(cls, acao_associacao, periodo, conferido=None,
                                                         conta_associacao=None,
                                                         exclude_despesa=None, aplicacao_recurso=None):

        dataset = cls.completos.filter(acao_associacao=acao_associacao,
                                       despesa__data_documento__lte=periodo.data_inicio_realizacao_despesas)

        if conferido is not None:
            dataset = dataset.filter(conferido=conferido)

        if exclude_despesa:
            dataset = dataset.exclude(despesa__uuid=exclude_despesa)

        if conta_associacao:
            dataset = dataset.filter(conta_associacao=conta_associacao)

        if aplicacao_recurso:
            dataset = dataset.filter(aplicacao_recurso=aplicacao_recurso)

        return dataset.all()

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

    @classmethod
    def conciliar(cls, uuid, periodo_conciliacao):
        rateio_despesa = cls.by_uuid(uuid)
        return rateio_despesa.marcar_conferido(periodo_conciliacao)

    @classmethod
    def desconciliar(cls, uuid):
        rateio_despesa = cls.by_uuid(uuid)
        return rateio_despesa.desmarcar_conferido()

    @classmethod
    def totais_por_acao_associacao_no_periodo(cls, acao_associacao, periodo, conta=None):
        despesas = cls.rateios_da_acao_associacao_no_periodo(acao_associacao=acao_associacao,
                                                             periodo=periodo, conta_associacao=conta)
        totais = {
            'total_despesas_capital': Decimal(0.00),
            'total_despesas_custeio': Decimal(0.00),
            'total_despesas_nao_conciliadas_capital': Decimal(0.00),
            'total_despesas_nao_conciliadas_custeio': Decimal(0.00),
        }

        for despesa in despesas:
            if despesa.aplicacao_recurso == APLICACAO_CAPITAL:
                totais['total_despesas_capital'] += despesa.valor_rateio
            else:
                totais['total_despesas_custeio'] += despesa.valor_rateio

            if not despesa.conferido:
                if despesa.aplicacao_recurso == APLICACAO_CAPITAL:
                    totais['total_despesas_nao_conciliadas_capital'] += despesa.valor_rateio
                else:
                    totais['total_despesas_nao_conciliadas_custeio'] += despesa.valor_rateio

        return totais

    class Meta:
        verbose_name = "Rateio de despesa"
        verbose_name_plural = "Rateios de despesas"


@receiver(pre_save, sender=RateioDespesa)
def rateio_pre_save(instance, **kwargs):
    instance.status = STATUS_COMPLETO if instance.cadastro_completo() else STATUS_INCOMPLETO

    if not instance.update_conferido:
        instance.conferido = False
        instance.periodo_conciliacao = None

    instance.update_conferido = False


@receiver(post_save, sender=RateioDespesa)
def rateio_post_save(instance, created, **kwargs):
    if instance and instance.despesa:
        instance.despesa.atualiza_status()


auditlog.register(RateioDespesa)
