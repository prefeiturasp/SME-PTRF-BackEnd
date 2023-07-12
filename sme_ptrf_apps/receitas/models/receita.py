from datetime import date, datetime
from decimal import Decimal

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import Q

from sme_ptrf_apps.core.models import Associacao, Periodo, Parametros
from sme_ptrf_apps.despesas.models import Despesa, RateioDespesa
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from ..tipos_aplicacao_recurso_receitas import APLICACAO_CAPITAL, APLICACAO_CHOICES, APLICACAO_CUSTEIO


class ReceitasCompletasManager(models.Manager):
    def get_queryset(self):
        return super(ReceitasCompletasManager, self).get_queryset().filter(status=Receita.STATUS_COMPLETO)


class Receita(ModeloBase):
    history = AuditlogHistoryField()

    TAG_INATIVA = {"id": "6", "nome": "Excluído", "descricao": "Lançamento excluído."}

    STATUS_COMPLETO = 'COMPLETO'
    STATUS_INATIVO = 'INATIVO'

    STATUS_NOMES = {
        STATUS_COMPLETO: 'Completo',
        STATUS_INATIVO: 'Inativo',
    }

    STATUS_CHOICES = (
        (STATUS_COMPLETO, STATUS_NOMES[STATUS_COMPLETO]),
        (STATUS_INATIVO, STATUS_NOMES[STATUS_INATIVO]),
    )

    associacao = models.ForeignKey(Associacao, on_delete=models.PROTECT, related_name='receitas',
                                   blank=True, null=True)

    data = models.DateField('Data Receita', blank=True, null=True)

    valor = models.DecimalField('Valor Receita', max_digits=20, decimal_places=2, default=0)

    conta_associacao = models.ForeignKey('core.ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='receitas_da_conta', blank=True, null=True)

    acao_associacao = models.ForeignKey('core.AcaoAssociacao', on_delete=models.PROTECT,
                                        related_name='receitas_da_associacao', blank=True, null=True)

    tipo_receita = models.ForeignKey('TipoReceita', on_delete=models.PROTECT, blank=True, null=True)

    conferido = models.BooleanField('Conferido?', default=True)

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

    saida_do_recurso = models.ForeignKey(Despesa, on_delete=models.SET_NULL, blank=True, null=True,
                                         related_name='receitas_saida_do_recurso',
                                         verbose_name='Saída do Recurso (Despesa)')

    rateio_estornado = models.ForeignKey(RateioDespesa, on_delete=models.CASCADE, blank=True, null=True,
                                         related_name='estorno',
                                         verbose_name='Rateio estornado')

    motivos_estorno = models.ManyToManyField('MotivoEstorno', blank=True, related_name='receitas_do_motivo')

    outros_motivos_estorno = models.TextField('Outros motivos para estorno', blank=True,
                                                           default='')

    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_COMPLETO
    )

    data_e_hora_de_inativacao = models.DateTimeField("Data e hora de inativação", blank=True, null=True)

    objects = models.Manager()  # Manager Padrão
    completas = ReceitasCompletasManager()

    def __str__(self):
        return f'RECEITA<{self.detalhamento} - {self.data} - {self.valor}>'

    @property
    def inativar_em_vez_de_excluir(self):
        from sme_ptrf_apps.core.models import PrestacaoConta
        return PrestacaoConta.objects.filter(
            associacao=self.associacao,
            periodo=self.periodo_conciliacao
        ).exists()

    @property
    def detalhamento(self):
        if self.detalhe_tipo_receita:
            detalhe = self.detalhe_tipo_receita.nome
        else:
            detalhe = self.detalhe_outros
        return detalhe

    @property
    def tags_de_informacao(self):
        """
        Arquitetura dinâmica para futuras tags que poderam ser atribuidas.
        """
        tags = []
        if self.e_receita_inativa():
            tags.append(tag_informacao(
                self.TAG_INATIVA,
                f"Este crédito foi excluído em {self.data_e_hora_de_inativacao.strftime('%d/%m/%Y %H:%M:%S')}"
            ))
        return tags

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

    @property
    def mensagem_inativacao(self):
        return f"Este crédito foi excluído em {self.data_e_hora_de_inativacao.strftime('%d/%m/%Y %H:%M:%S')}" \
            if self.status == "INATIVO" else None

    @classmethod
    def get_tags_informacoes_list(cls):
        return [cls.TAG_INATIVA]

    @classmethod
    def receitas_da_acao_associacao_no_periodo(cls, acao_associacao, periodo, conferido=None, conta_associacao=None,
                                               categoria_receita=None):
        if periodo.data_fim_realizacao_despesas:
            dataset = cls.completas.filter(acao_associacao=acao_associacao).filter(
                data__range=(periodo.data_inicio_realizacao_despesas, periodo.data_fim_realizacao_despesas))
        else:
            dataset = cls.completas.filter(acao_associacao=acao_associacao).filter(
                data__gte=periodo.data_inicio_realizacao_despesas)

        if conferido is not None:
            dataset = dataset.filter(conferido=conferido)

        if conta_associacao:
            dataset = dataset.filter(conta_associacao=conta_associacao)

        if categoria_receita:
            dataset = dataset.filter(categoria_receita=categoria_receita)

        return dataset.all()

    @classmethod
    def receitas_da_acao_associacao_entre_periodos(
        cls,
        acao_associacao,
        periodo_inicial,
        periodo_final,
        conferido=None,
        conta_associacao=None,
        categoria_receita=None
    ):
        if periodo_final.data_fim_realizacao_despesas:
            dataset = cls.completas.filter(acao_associacao=acao_associacao).filter(
                data__range=(periodo_inicial.data_inicio_realizacao_despesas, periodo_final.data_fim_realizacao_despesas))
        else:
            dataset = cls.completas.filter(acao_associacao=acao_associacao).filter(
                data__gte=periodo_inicial.data_inicio_realizacao_despesas)

        if conferido is not None:
            dataset = dataset.filter(conferido=conferido)

        if conta_associacao:
            dataset = dataset.filter(conta_associacao=conta_associacao)

        if categoria_receita:
            dataset = dataset.filter(categoria_receita=categoria_receita)

        return dataset.all()

    @classmethod
    def receitas_da_conta_associacao_no_periodo(cls, conta_associacao, periodo, conferido=None, acao_associacao=None, filtrar_por_data_inicio=None, filtrar_por_data_fim=None, inclui_inativas=False, filtro_informacoes_list=None, filtro_conferencia_list=None, analise_prestacao_conta=None):
        if inclui_inativas:
            dataset = cls.objects
        else:
            dataset = cls.completas

        if periodo.data_fim_realizacao_despesas:
            dataset = dataset.filter(conta_associacao=conta_associacao).filter(
                data__range=(periodo.data_inicio_realizacao_despesas, periodo.data_fim_realizacao_despesas)).order_by('data')
        else:
            dataset = dataset.filter(conta_associacao=conta_associacao).filter(
                data__gte=periodo.data_inicio_realizacao_despesas).order_by('data')

        if conferido is not None:
            dataset = dataset.filter(conferido=conferido).order_by('data')

        if acao_associacao:
            dataset = dataset.filter(acao_associacao=acao_associacao).order_by('data')

        if filtrar_por_data_inicio and filtrar_por_data_fim:
            dataset = dataset.filter(data__range=[filtrar_por_data_inicio, filtrar_por_data_fim]).order_by('data')

        elif filtrar_por_data_inicio and not filtrar_por_data_fim:
            dataset = dataset.filter(
                Q(data__gte=filtrar_por_data_inicio)
            ).order_by('data')

        elif not filtrar_por_data_inicio and filtrar_por_data_fim:
            dataset = dataset.filter(
                Q(data__lte=filtrar_por_data_fim)
            ).order_by('data')

        if filtro_informacoes_list is not None and Receita.TAG_INATIVA['id'] in filtro_informacoes_list:
            dataset = dataset.filter(status=cls.STATUS_INATIVO).order_by('data')

        if filtro_conferencia_list and analise_prestacao_conta:
            ids_para_excluir = []
            for receita in dataset:
                excluir_receita = True
                analise_lancamento = analise_prestacao_conta.analises_de_lancamentos.filter(receita=receita).first()

                if 'AJUSTE' in filtro_conferencia_list and analise_lancamento and analise_lancamento.resultado == 'AJUSTE':
                    excluir_receita = False

                if 'CORRETO' in filtro_conferencia_list and analise_lancamento and analise_lancamento.resultado == 'CORRETO' and analise_lancamento.houve_considerados_corretos_automaticamente == False:
                    excluir_receita = False

                if 'CONFERENCIA_AUTOMATICA' in filtro_conferencia_list and analise_lancamento and analise_lancamento.houve_considerados_corretos_automaticamente == True:
                    excluir_receita = False

                if 'NAO_CONFERIDO' in filtro_conferencia_list and not analise_lancamento:
                    excluir_receita = False

                if excluir_receita:
                    ids_para_excluir.append(receita.id)

            dataset = dataset.exclude(id__in=ids_para_excluir)

        return dataset.all()

    @classmethod
    def receitas_da_conta_associacao_entre_periodos(
        cls,
        conta_associacao,
        periodo_inicial,
        periodo_final,
        conferido=None,
        acao_associacao=None
    ):
        if periodo_final.data_fim_realizacao_despesas:
            dataset = cls.completas.filter(conta_associacao=conta_associacao).filter(
                data__range=(
                    periodo_inicial.data_inicio_realizacao_despesas,
                    periodo_final.data_fim_realizacao_despesas
                )).order_by('data')
        else:
            dataset = cls.completas.filter(conta_associacao=conta_associacao).filter(
                data__gte=periodo_inicial.data_inicio_realizacao_despesas).order_by('data')

        if conferido is not None:
            dataset = dataset.filter(conferido=conferido).order_by('data')

        if acao_associacao:
            dataset = dataset.filter(acao_associacao=acao_associacao).order_by('data')

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
        # A logica de conciliação está sendo feito no pre_save

        self.conferido = True
        self.save()
        return self

    def desmarcar_conferido(self):
        self.conferido = False
        self.periodo_conciliacao = None
        self.save()
        return self

    def salvar_saida_recurso(self, despesa=None):
        self.saida_do_recurso = despesa
        self.save()
        despesa.atualiza_rateios_como_saida_recurso_externo()
        return self

    def adiciona_motivos_estorno(self, motivos_estorno, outros_motivos_estorno):
        motivos_list = []
        for motivo in motivos_estorno:
            motivos_list.append(motivo.id)

        self.motivos_estorno.set(motivos_list)
        self.outros_motivos_estorno = outros_motivos_estorno

        self.save()

    def e_receita_inativa(self):
        return self.status == self.STATUS_INATIVO

    @classmethod
    def conciliar(cls, uuid, periodo_conciliacao):
        receita = cls.by_uuid(uuid)
        return receita.marcar_conferido(periodo_conciliacao)

    @classmethod
    def desconciliar(cls, uuid):
        receita = cls.by_uuid(uuid)
        return receita.desmarcar_conferido()

    @classmethod
    def atrelar_saida_recurso(cls, uuid, despesa):
        receita = cls.by_uuid(uuid)
        return receita.salvar_saida_recurso(despesa)

    def inativar_receita(self):
        self.status = self.STATUS_INATIVO
        self.data_e_hora_de_inativacao = datetime.now()

        if self.rateio_estornado:
            self.rateio_estornado = None

        self.save()
        return self


@receiver(pre_save, sender=Receita)
def receita_pre_save(instance, **kwargs):
    if instance.tipo_receita.tem_detalhamento():
        instance.detalhe_outros = ""
    else:
        instance.detalhe_tipo_receita = None

    if instance.data:
        periodo = Periodo.da_data(instance.data)
        instance.periodo_conciliacao = periodo


def tag_informacao(tipo_de_tag, hint):
    return {
        'tag_id': tipo_de_tag['id'],
        'tag_nome': tipo_de_tag['nome'],
        'tag_hint': hint,
    }


auditlog.register(Receita)
