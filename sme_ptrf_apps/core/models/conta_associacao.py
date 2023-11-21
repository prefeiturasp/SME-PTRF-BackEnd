from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class ContasAtivasComSolicitacaoEmAberto(models.Manager):
    def get_queryset(self):
        from ..models import SolicitacaoEncerramentoContaAssociacao
        return super(ContasAtivasComSolicitacaoEmAberto, self).get_queryset().filter(Q(status=ContaAssociacao.STATUS_ATIVA) |
                                                               Q(solicitacao_encerramento__status=SolicitacaoEncerramentoContaAssociacao.STATUS_PENDENTE) |
                                                               Q(solicitacao_encerramento__status=SolicitacaoEncerramentoContaAssociacao.STATUS_REJEITADA))

class ContasComSolicitacaoDeEncerramento(models.Manager):
    def get_queryset(self):
        return super(ContasComSolicitacaoDeEncerramento, self).get_queryset().filter(solicitacao_encerramento__isnull=False)

class ContasEncerradas(models.Manager):
    def get_queryset(self):
        from ..models import SolicitacaoEncerramentoContaAssociacao
        return super(ContasEncerradas, self).get_queryset().filter(Q(status=ContaAssociacao.STATUS_INATIVA) &
                                                                 Q(solicitacao_encerramento__isnull=False)  &
                                                                 Q(solicitacao_encerramento__status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA))


class ContaAssociacao(ModeloBase):
    history = AuditlogHistoryField()

    # Status Choice
    STATUS_ATIVA = 'ATIVA'
    STATUS_INATIVA = 'INATIVA'

    STATUS_NOMES = {
        STATUS_ATIVA: 'Ativa',
        STATUS_INATIVA: 'Inativa',
    }

    STATUS_CHOICES = (
        (STATUS_ATIVA, STATUS_NOMES[STATUS_ATIVA]),
        (STATUS_INATIVA, STATUS_NOMES[STATUS_INATIVA]),
    )

    associacao = models.ForeignKey('Associacao', on_delete=models.CASCADE, related_name='contas', blank=True, null=True)
    tipo_conta = models.ForeignKey('TipoConta', on_delete=models.PROTECT, blank=True, null=True)
    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_ATIVA
    )
    banco_nome = models.CharField('Nome do banco', max_length=50, blank=True, default='')
    agencia = models.CharField('Nº agência',  max_length=15, blank=True, default='')
    numero_conta = models.CharField('Nº conta', max_length=30, blank=True, default='')
    numero_cartao = models.CharField('Nº do cartão', max_length=80, blank=True, default='')
    data_inicio = models.DateField(verbose_name='Data de início da conta', blank=True, null=True)

    objects = models.Manager()
    ativas_com_solicitacao_em_aberto = ContasAtivasComSolicitacaoEmAberto()
    com_solicitacao_de_encerramento = ContasComSolicitacaoDeEncerramento()
    encerradas = ContasEncerradas()

    def __str__(self):
        associacao = self.associacao.nome if self.associacao else 'ACM indefinida'
        tipo_conta = self.tipo_conta.nome if self.tipo_conta else 'Tipo de conta indefinido'
        status = ContaAssociacao.STATUS_NOMES[self.status]
        return f"{associacao} - Conta {tipo_conta} - {status}"

    def inativar(self):
        self.status = self.STATUS_INATIVA
        self.save()

    def ativar(self):
        self.status = self.STATUS_ATIVA
        self.save()

    @property
    def periodo_encerramento(self):
        from sme_ptrf_apps.core.models import Periodo
        if self.data_encerramento:
            periodo = Periodo.da_data(self.data_encerramento)
            if periodo:
                return periodo
        return None

    @property
    def inativa(self):
        return self.status == self.STATUS_INATIVA

    @property
    def data_encerramento(self):
        data_encerramento = None
        if hasattr(self, 'solicitacao_encerramento'):
            data_encerramento = self.solicitacao_encerramento.data_de_encerramento_na_agencia
        return data_encerramento

    def conta_encerrada_em_periodos_anteriores(self, periodo):
        from sme_ptrf_apps.core.models import Periodo

        if hasattr(self, 'solicitacao_encerramento'):
            if self.solicitacao_encerramento.aprovada:
                data_encerramento = self.solicitacao_encerramento.data_de_encerramento_na_agencia
                periodo_data_encerramento = Periodo.da_data(data_encerramento)

                return periodo_data_encerramento.data_inicio_realizacao_despesas < periodo.data_inicio_realizacao_despesas

        return None

    def conta_encerrada_em(self, periodo, adiciona_prefixo=True, origem_relatorio_consolidado=False):
        from sme_ptrf_apps.core.models import Periodo

        if hasattr(self, 'solicitacao_encerramento'):
            if self.solicitacao_encerramento.aprovada:
                data_encerramento = self.solicitacao_encerramento.data_de_encerramento_na_agencia
                periodo_data_encerramento = Periodo.da_data(data_encerramento)

                if origem_relatorio_consolidado:
                    if periodo_data_encerramento == periodo or periodo_data_encerramento.data_inicio_realizacao_despesas > periodo.data_inicio_realizacao_despesas:

                        if adiciona_prefixo:
                            return f"Conta encerrada em {data_encerramento.strftime('%d/%m/%Y')}"
                        else:
                            return f"{data_encerramento.strftime('%d/%m/%Y')}"
                else:
                    if periodo_data_encerramento == periodo:

                        if adiciona_prefixo:
                            return f"Conta encerrada em {data_encerramento.strftime('%d/%m/%Y')}"
                        else:
                            return f"{data_encerramento.strftime('%d/%m/%Y')}"

        return None

    def pode_encerrar(self, data_encerramento):
        from sme_ptrf_apps.core.services.encerramento_conta_associacao_service import ValidaDataDeEncerramento

        validacao = ValidaDataDeEncerramento(associacao=self.associacao, data_de_encerramento=data_encerramento)
        return validacao.pode_encerrar

    def get_saldo_atual_conta(self):
        from sme_ptrf_apps.core.services.info_por_acao_services import info_conta_associacao_no_periodo
        from sme_ptrf_apps.core.models import Periodo
        periodo = Periodo.periodo_atual()
        saldos_conta = info_conta_associacao_no_periodo(self, periodo=periodo)
        saldo_conta = saldos_conta['saldo_atual_custeio'] + saldos_conta['saldo_atual_capital'] + saldos_conta['saldo_atual_livre']

        return saldo_conta

    def ativa_no_periodo(self, periodo):
        from sme_ptrf_apps.core.models import SolicitacaoEncerramentoContaAssociacao

        if not self.conta_criada_no_periodo_ou_periodo_anteriores(periodo=periodo):
            return False

        if hasattr(self, 'solicitacao_encerramento'):
            if self.solicitacao_encerramento.status == SolicitacaoEncerramentoContaAssociacao.STATUS_REJEITADA:
                return True

            # Só ira executar esse bloco se o status for aprovada ou pendente
            data_encerramento = self.solicitacao_encerramento.data_de_encerramento_na_agencia
            if data_encerramento < periodo.data_inicio_realizacao_despesas:
                return False

            return True
        else:
            return True

    def todos_valores_reprogramados_foram_preenchidos(self, valida_valor_dre=False):
        from sme_ptrf_apps.core.models import ValoresReprogramados, Associacao
        from sme_ptrf_apps.receitas.tipos_aplicacao_recurso_receitas import \
            APLICACAO_CAPITAL, APLICACAO_CUSTEIO, APLICACAO_LIVRE

        valores_reprogramados = ValoresReprogramados.objects.filter(
            associacao=self.associacao, conta_associacao=self).all()

        lista_de_valores_reprogramados = []

        # Levando em consideração que deve haver um registro de valor reprogramado
        # para cada aplicação (Custeio, Capital, Livre) que a ação aceite
        qtde_esperado = 0

        for acao_associacao in self.associacao.acoes.exclude(acao__e_recursos_proprios=True):
            valores_reprogramados_da_acao = valores_reprogramados.filter(acao_associacao=acao_associacao)

            if acao_associacao.acao.aceita_custeio:
                qtde_esperado = qtde_esperado + 1

                valor_reprogramado_por_aplicacao = valores_reprogramados_da_acao.filter(
                    aplicacao_recurso=APLICACAO_CUSTEIO)

                if valor_reprogramado_por_aplicacao.exists():
                    lista_de_valores_reprogramados.append(valor_reprogramado_por_aplicacao.first())

            if acao_associacao.acao.aceita_capital:
                qtde_esperado = qtde_esperado + 1

                valor_reprogramado_por_aplicacao = valores_reprogramados_da_acao.filter(
                    aplicacao_recurso=APLICACAO_CAPITAL)

                if valor_reprogramado_por_aplicacao.exists():
                    lista_de_valores_reprogramados.append(valor_reprogramado_por_aplicacao.first())

            if acao_associacao.acao.aceita_livre:
                qtde_esperado = qtde_esperado + 1

                valor_reprogramado_por_aplicacao = valores_reprogramados_da_acao.filter(
                    aplicacao_recurso=APLICACAO_LIVRE)

                if valor_reprogramado_por_aplicacao.exists():
                    lista_de_valores_reprogramados.append(valor_reprogramado_por_aplicacao.first())

        if valida_valor_dre:
            valores_reprogramados_preenchidos = valores_reprogramados.exclude(valor_ue=None).exclude(valor_dre=None)
        else:
            valores_reprogramados_preenchidos = valores_reprogramados.exclude(valor_ue=None)

        qtde_lista_valores = len(lista_de_valores_reprogramados)

        if qtde_esperado == qtde_lista_valores and qtde_esperado == valores_reprogramados_preenchidos.count():
            return True

        return False

    def valida_se_algum_valor_reprogramado_foi_preenchido(self):
        from sme_ptrf_apps.core.models import ValoresReprogramados

        valores_reprogramados = ValoresReprogramados.objects.filter(
            associacao=self.associacao, conta_associacao=self).exists()

        return valores_reprogramados

    def valida_status_valores_reprogramados(self):
        from sme_ptrf_apps.core.models import Associacao

        resultado = {
            "pode_encerrar_conta": False,
            "mensagem": None
        }

        pc_do_primeiro_periodo_de_uso_do_sistema = self.associacao.prestacoes_de_conta_da_associacao.filter(
            periodo=self.associacao.periodo_inicial.proximo_periodo)

        if pc_do_primeiro_periodo_de_uso_do_sistema.exists():
            resultado["pode_encerrar_conta"] = True
            return resultado

        # Esse trecho só é executado caso a primeira PC não exista
        status_atual = self.associacao.status_valores_reprogramados
        status_nao_finalizado = Associacao.STATUS_VALORES_REPROGRAMADOS_NAO_FINALIZADO
        status_correcao_ue = Associacao.STATUS_VALORES_REPROGRAMADOS_EM_CORRECAO_UE
        status_conferencia_dre = Associacao.STATUS_VALORES_REPROGRAMADOS_EM_CONFERENCIA_DRE
        status_corretos = Associacao.STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS

        if status_atual == status_nao_finalizado:
            if not self.valida_se_algum_valor_reprogramado_foi_preenchido():
                resultado["pode_encerrar_conta"] = True
                resultado["mensagem"] = None
            else:
                if not self.todos_valores_reprogramados_foram_preenchidos():
                    resultado["pode_encerrar_conta"] = False
                    resultado["mensagem"] = "Existem valores reprogramados preenchidos, mas não concluídos. É necessário finalizar o preenchimento dos Valores reprogramados para solicitar o encerramento da conta bancária."
                else:
                    resultado["pode_encerrar_conta"] = True
                    resultado["mensagem"] = None

        elif status_atual == status_correcao_ue or status_atual == status_conferencia_dre:
            if self.todos_valores_reprogramados_foram_preenchidos(valida_valor_dre=True):
                resultado["pode_encerrar_conta"] = True
                resultado["mensagem"] = "O pedido de solicitação de encerramento de conta bancária foi efetuado com sucesso. Existem valores reprogramados concluídos e o encerramento definitivo da conta será realizado após a geração da PC e a conclusão da análise pela DRE."
            else:
                resultado["pode_encerrar_conta"] = False
                resultado["mensagem"] = "Existem valores reprogramados que não foram preenchidos pela DRE. É necessário aguardar a finalização do preenchimento para solicitar o encerramento da conta bancária."

        elif status_atual == status_corretos:
            if self.todos_valores_reprogramados_foram_preenchidos(valida_valor_dre=True):
                resultado["pode_encerrar_conta"] = True
                resultado["mensagem"] = "O pedido de solicitação de encerramento de conta bancária foi efetuado com sucesso. O encerramento definitivo da conta será realizado após a geração da PC e a conclusão da análise pela DRE."

        return resultado

    def get_info_solicitacao_encerramento(self):
        from sme_ptrf_apps.core.models import SolicitacaoEncerramentoContaAssociacao

        info = {
            "data_encerramento": None,
            "saldo": None,
            "possui_solicitacao_encerramento": False
        }

        if hasattr(self, 'solicitacao_encerramento'):
            if self.solicitacao_encerramento.status != SolicitacaoEncerramentoContaAssociacao.STATUS_REJEITADA:
                data_encerramento = self.solicitacao_encerramento.data_de_encerramento_na_agencia
                saldo = 0

                info["data_encerramento"] = data_encerramento
                info["saldo"] = saldo
                info["possui_solicitacao_encerramento"] = True

        return info

    def conta_criada_no_periodo_ou_periodo_anteriores(self, periodo):
        from sme_ptrf_apps.core.models import Periodo

        if not self.data_inicio:
            return False

        periodo_da_data = Periodo.da_data(self.data_inicio)
        if periodo_da_data == periodo:
            return True

        periodos_anteriores = Periodo.objects.filter(
            data_inicio_realizacao_despesas__lt=periodo.data_inicio_realizacao_despesas).order_by('-referencia')
        if periodo_da_data in list(periodos_anteriores):
            return True

        return False

    @property
    def msg_sucesso_ao_encerrar(self):
        mensagem = self.valida_status_valores_reprogramados()["mensagem"]

        return mensagem


    @classmethod
    def get_valores(cls, user=None, associacao_uuid=None):
        query = cls.objects.all()
        if user:
            query = query.filter(associacao__uuid=associacao_uuid)
        return query.all()

    class Meta:
        verbose_name = "Conta de Associação"

        verbose_name_plural = "07.1) Contas de Associações"

@receiver(pre_save, sender=ContaAssociacao)
def conta_associacao_pre_save(instance, **kwargs):
    if instance.tipo_conta.banco_nome and not instance.banco_nome:
        instance.banco_nome = instance.tipo_conta.banco_nome

    if instance.tipo_conta.agencia and not instance.agencia:
        instance.agencia = instance.tipo_conta.agencia

    if instance.tipo_conta.numero_conta and not instance.numero_conta:
        instance.numero_conta = instance.tipo_conta.numero_conta

    if instance.tipo_conta.numero_cartao and not instance.numero_cartao:
        instance.numero_cartao = instance.tipo_conta.numero_cartao


auditlog.register(ContaAssociacao)
