import logging
import uuid as uuid

from datetime import datetime

from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.core.models import (
    Unidade,
    Periodo,
    Associacao,
    ContaAssociacao,
)

from ..choices.tipos_unidade import TIPOS_CHOICE

from .validators import cnpj_validation

logger = logging.getLogger(__name__)


class StatusProcessamento(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    SUCESSO = "SUCESSO", "Sucesso"
    ABORTADO = "ABORTADO", "Abortado"
    ERRO = "ERRO", "Erro"
    PROCESSANDO = "PROCESSANDO", "Processando..."


class ComportamentoContas(models.TextChoices):
    TRANSFERE_SELECIONADA = (
        "TRANSFERE_SELECIONADA",
        "Transferir apenas o tipo de conta selecionada e inativa-la na associação original.",
    )
    COPIA_TODAS = (
        "COPIA_TODAS",
        "Copiar todas as contas da associação original para a nova associação mantendo-as ativas em ambas.",
    )


class TransferenciaEol(ModeloBase):
    """
    Transferência de código EOL de uma unidade para outra.

    Esse modelo é usado para apoiar a transferência do código EOL de uma unidade para uma nova.

    Comportamento: Transferência de conta de certo tipo incluindo seus lançamentos.
    O cenário de uso é o seguinte:
    - Uma unidade/associação será inativada e o código EOL será transferido para outra unidade/associação.
    - É necessário manter o histórico de receitas e despesas da unidade/associação que será inativada.
    - Existem receitas e despesas lançados que já se referem a nova unidade/associação
    - A movimentação referente à nova associação são os que ocorreram após a data de início de suas atividades.
    - Também são identificados pelo tipo da conta_associação que difere da conta_associação da associação que será inativada.
    - Para referenciar o histórico será criada uma unidade com o código EOL de histórico.
    - A Associação original passará a referenciar a unidade histórico.
    - A Associação nova irá referenciar a unidade original com o código EOL transferido.
    - A conta_associacao do tipo_conta_transferido da Associação original será copiado para a nova e inativado na original.
    - As receitas e despesas da Associação original serão copiados para a nova e inativados na original.

    Comportamento: Cópia de todas as contas. Caso: CEU Perús - História 105534:

    - É necessário separar o histórico de prestações de contas da Associação CEU Perús em dois momentos: Antes e depois do período 2023.1
    - A associação atual ficará com o histórico e terá o seu código EOL alterado. O seu código EOL será transferido para a nova associação.
    - É necessário manter o histórico de receitas e despesas da unidade/associação de histórico.
    - Para referenciar o histórico será criada uma unidade com o código EOL de histórico.
    - A Associação original passará a referenciar a unidade histórico.
    - A Associação nova irá referenciar a unidade original com o código EOL transferido.
    - Nesse caso NÃO existem receitas e despesas lançados que já se referem a nova unidade/associação
    - NÃO há ainda movimentação referente à nova associação.
    - O tipo de conta indica a conta que deve ser copiada para a nova associação. Se não informado, serão copiadas todas as contas.
    - A conta de tipo selecionado ou todas as conta_associacao da Associação original serão copiadas para a nova, mas MANTIDAS ATIVAS NA ORIGINAL.
    - Nesse caso NÃO HÁ COPIA DE receitas e despesas da Associação original.

    A transferência é realizada pelo método 'transferir'.

    """

    eol_transferido = models.CharField(
        "EOL a ser transferido",
        max_length=6,
        help_text="É o código eol que será transferido para a nova unidade.",
    )

    eol_historico = models.CharField(
        "EOL usado para o histórico",
        max_length=6,
        help_text="É o código que será usado para o histórico da unidade que usava anteriormente o condigo transferido.",
    )

    tipo_nova_unidade = models.CharField(
        max_length=10,
        choices=TIPOS_CHOICE,
        default="CEMEI",
        help_text="Tipo da nova unidade que receberá o código transferido.",
    )

    cnpj_nova_associacao = models.CharField(
        "CNPJ",
        max_length=20,
        validators=[cnpj_validation],
        blank=True,
        default="",
        help_text="CNPJ da nova associação.",
    )

    data_inicio_atividades = models.DateField(
        "Data de início das atividades",
        help_text="Data de início das atividades da nova unidade.",
    )

    comportamento_contas = models.CharField(
        "Comportamento quanto às contas",
        max_length=30,
        choices=ComportamentoContas.choices,
        default=ComportamentoContas.TRANSFERE_SELECIONADA,
        help_text="O que deseja fazer com as contas da associação original?",
    )

    tipo_conta_transferido = models.ForeignKey(
        "TipoConta",
        on_delete=models.PROTECT,
        help_text="Tipo de conta que será transferido para a nova unidade. Deixe vazio, caso o comportamento escolhido seja copiar todas as contas.",
        blank=True,
        null=True,
    )

    status_processamento = models.CharField(
        "Status do processamento",
        max_length=20,
        choices=StatusProcessamento.choices,
        default=StatusProcessamento.PENDENTE,
        help_text="Status do processamento da transferência.",
    )

    log_execucao = models.TextField(
        "Log de execução",
        blank=True,
        null=True,
        help_text="Log de execução da transferência.",
    )

    def __str__(self):
        return f"{self.eol_transferido} -> {self.eol_historico}"

    class Meta:
        verbose_name = "Transferência de Código EOL"
        verbose_name_plural = "99.9) Transferências de Código EOL"

    def adicionar_log(self, log):
        if not hasattr(self, "lista_logs"):
            self.lista_logs = []
        self.lista_logs.append(f'{datetime.now().strftime("%H:%M:%S")} - {log}')

    def salvar_logs(self):
        if hasattr(self, "lista_logs"):
            self.log_execucao = "\n".join(self.lista_logs)
            self.save()

    def adicionar_log_info(self, texto_log):
        logging.info(texto_log)
        self.adicionar_log(texto_log)

    def adicionar_log_erro(self, texto_log):
        logging.error(texto_log)
        self.adicionar_log(texto_log)

    def transferencia_possivel(self):
        """
        Verifica se é possível realizar a transferência de um código EOL para uma nova unidade/associação.

        Retorna uma tupla com um valor booleano indicando se a transferência é possível ou não, e uma mensagem de erro
        caso a transferência não seja possível.

        Requisitos para a transferência:
        - A unidade com o EOL que está sendo transferido deve existir;
        - Deve existir uma associação para o código EOL que está sendo transferido;
        - O código EOL que será usado para o histórico NÃO deve existir;
        - Deve existir um período para a data de início das atividades da nova unidade;
        - Não deve existir fechamentos na associação original para o período de início das atividades da nova unidade;
        - A conta_associação que será transferida para a nova associação deve existir. Apenas para o modo de transferência de conta.
        - Não devem existir despesas na associação original com rateios em múltiplas contas. Apenas para o modo de transferência de conta.
        """

        # O código EOL transferido deve existir
        if not Unidade.objects.filter(codigo_eol=self.eol_transferido).exists():
            return False, f"Código EOL transferido {self.eol_transferido} não existe."

        # O código EOL de histórico não deve existir
        if Unidade.objects.filter(codigo_eol=self.eol_historico).exists():
            return False, f"Código EOL de histórico {self.eol_historico} já existe."

        # Deve existir um período para a data de início das atividades
        periodo_da_data_inicio_atividades = Periodo.da_data(self.data_inicio_atividades)
        if periodo_da_data_inicio_atividades is None:
            return (
                False,
                f"Não existe período para a data de início das atividades {self.data_inicio_atividades}.",
            )

        # Deve existir uma associação para o código EOL transferido
        if not Associacao.objects.filter(
            unidade__codigo_eol=self.eol_transferido
        ).exists():
            return (
                False,
                f"Não existe associação para o código EOL transferido {self.eol_transferido}.",
            )

        # Não devem existir fechamentos para a associação do eol de transferência no período da data de início das atividades da nova associação
        associacao_original = Associacao.objects.get(
            unidade__codigo_eol=self.eol_transferido
        )
        if associacao_original.fechamentos_associacao.filter(
            periodo=periodo_da_data_inicio_atividades
        ).exists():
            return (
                False,
                f"Já existem fechamentos para a associação original {associacao_original} no período {periodo_da_data_inicio_atividades}.",
            )

        # Deve existir uma conta_associacao do tipo tipo_conta_transferido para a associação do código eol transferido
        if (
            self.comportamento_contas == ComportamentoContas.TRANSFERE_SELECIONADA
            and not ContaAssociacao.objects.filter(
                associacao=associacao_original, tipo_conta=self.tipo_conta_transferido
            ).exists()
        ):
            return (
                False,
                f"Não existe conta_associacao do tipo {self.tipo_conta_transferido} para a associação original {associacao_original}.",
            )

        # Nao devem existir despesas da associação original que tenham com rateios no tipo_conta_transferido e em outro tipo de conta
        if self.comportamento_contas == ComportamentoContas.TRANSFERE_SELECIONADA:
            for despesa in associacao_original.despesas.all():
                if despesa.tem_pagamentos_em_multiplas_contas():
                    return (
                        False,
                        f"A associação original {associacao_original} possui despesas com rateios no tipo de conta {self.tipo_conta_transferido} e em outro tipo de conta.",
                    )

        # Caso o comportamento para as contas seja copiar todas não deve haver despesas com data de transação a partir da data de início das atividades da nova associação
        if (
            self.comportamento_contas == ComportamentoContas.COPIA_TODAS
            and associacao_original.despesas.filter(
                data_transacao__gte=self.data_inicio_atividades
            ).exists()
        ):
            return (
                False,
                f"A associação original {associacao_original} possui despesas com data de transação a partir da data de início das atividades da nova associação {self.data_inicio_atividades}.",
            )

        return True, ""

    def clonar_unidade(self):
        self.adicionar_log_info(
            f"Clonando unidade de código EOL {self.eol_transferido} para {self.eol_historico}."
        )
        unidade_transferida = Unidade.objects.get(codigo_eol=self.eol_transferido)
        unidade_transferida.codigo_eol = self.eol_historico
        unidade_transferida.uuid = uuid.uuid4()
        unidade_transferida.save()
        self.adicionar_log_info(
            f"Unidade de código EOL {self.eol_transferido} clonada para {self.eol_historico}."
        )
        return unidade_transferida

    def atualizar_unidade_transferida(self):
        self.adicionar_log_info(
            f"Atualizando unidade de código EOL {self.eol_transferido} para o tipo_nova_unidade."
        )
        unidade_transferida = Unidade.objects.get(codigo_eol=self.eol_transferido)
        unidade_transferida.tipo_unidade = self.tipo_nova_unidade
        unidade_transferida.save()
        self.adicionar_log_info(
            f"Unidade de código EOL {self.eol_transferido} atualizada para o tipo_nova_unidade."
        )
        return unidade_transferida

    def clonar_associacao(self, associacao_original_uuid, unidade_historico):
        associacao_historico = Associacao.by_uuid(associacao_original_uuid)

        self.adicionar_log_info(
            f"Clonando associação da unidade de código EOL {self.eol_transferido}."
        )
        associacao_nova = Associacao.by_uuid(associacao_original_uuid)
        associacao_nova.pk = None
        associacao_nova.uuid = uuid.uuid4()
        associacao_nova.cnpj = self.cnpj_nova_associacao
        associacao_nova.save()

        self.adicionar_log_info(
            f"Transferindo associação de histórico para a unidade de código EOL {self.eol_historico}."
        )
        associacao_historico.unidade = unidade_historico
        associacao_historico.save()

        self.adicionar_log_info(
            f"Associação clonada e a original transferida para a unidade de histórico."
        )
        return associacao_nova

    def copiar_acoes_associacao(self, associacao_original, associacao_nova):
        self.adicionar_log_info(
            f"Copiando ações_associacao da associação original para a nova associação."
        )
        acoes_associacao_original = associacao_original.acoes.all()

        if not acoes_associacao_original.exists():
            self.adicionar_log_info(f"Associação original não possui ações_associacao.")
            return

        for acao_associacao in acoes_associacao_original:
            acao_associacao.pk = None
            acao_associacao.uuid = uuid.uuid4()
            acao_associacao.associacao = associacao_nova
            acao_associacao.save()
            self.adicionar_log_info(
                f"Ação_associacao {acao_associacao} copiada para a nova associação."
            )

        self.adicionar_log_info(
            f"Ações_associacao da associação original copiadas para a nova associação."
        )

    def copiar_contas_associacao(self, associacao_original, associacao_nova):
        if self.comportamento_contas == ComportamentoContas.TRANSFERE_SELECIONADA:
            self.adicionar_log_info(
                f"Copiando contas_associacao do tipo {self.tipo_conta_transferido} da associação original para a nova associação."
            )
            contas_associacao_original = associacao_original.contas.filter(
                tipo_conta=self.tipo_conta_transferido
            ).all()
        else:
            self.adicionar_log_info(
                f"Copiando todas as contas_associacao da associação original para a nova associação."
            )
            contas_associacao_original = associacao_original.contas.all()

        if not contas_associacao_original.exists():
            self.adicionar_log_info(
                f"Associação original não possui contas_associacao a serem copiadas."
            )
            return

        for conta_associacao in contas_associacao_original:
            conta_associacao.pk = None
            conta_associacao.uuid = uuid.uuid4()
            conta_associacao.associacao = associacao_nova
            conta_associacao.save()
            self.adicionar_log_info(
                f"Conta_associacao {conta_associacao} copiada para a nova associação."
            )

        if self.comportamento_contas == ComportamentoContas.TRANSFERE_SELECIONADA:
            self.adicionar_log_info(
                f"Contas_associacao do tipo {self.tipo_conta_transferido} da associação original copiadas para a nova associação."
            )
        else:
            self.adicionar_log_info(
                f"Todas as contas_associacao da associação original copiadas para a nova associação."
            )

    def inativar_contas_associacao_do_tipo_transferido(self, associacao_original):
        self.adicionar_log_info(
            f"Inativando contas_associacao do tipo {self.tipo_conta_transferido} da associação original."
        )
        contas_associacao_original = associacao_original.contas.filter(
            tipo_conta=self.tipo_conta_transferido
        ).all()

        if not contas_associacao_original.exists():
            self.adicionar_log_info(
                f"Associação original não possui contas_associacao do tipo {self.tipo_conta_transferido} a serem inativadas."
            )
            return

        for conta_associacao in contas_associacao_original:
            conta_associacao.inativar()
            self.adicionar_log_info(f"Conta_associacao {conta_associacao} inativada.")

        self.adicionar_log_info(
            f"Contas_associacao do tipo {self.tipo_conta_transferido} da associação original inativadas."
        )

    def copiar_despesas_associacao_do_tipo_transferido(
        self, associacao_original, associacao_nova
    ):
        self.adicionar_log_info(
            f"Copiando despesas_associacao do tipo {self.tipo_conta_transferido} da associação original para a nova associação."
        )

        despesas_associacao_original = associacao_original.despesas.filter(
            rateios__conta_associacao__tipo_conta=self.tipo_conta_transferido
        ).distinct()

        if not despesas_associacao_original.exists():
            self.adicionar_log_info(
                f"Associação original não possui despesas_associacao em conta {self.tipo_conta_transferido}."
            )
            return

        for despesa_associacao in despesas_associacao_original:
            rateios_original = despesa_associacao.rateios.filter(
                conta_associacao__tipo_conta=self.tipo_conta_transferido
            ).all()

            despesa_associacao.pk = None
            despesa_associacao.uuid = uuid.uuid4()
            despesa_associacao.associacao = associacao_nova
            despesa_associacao.save()

            self.adicionar_log_info(
                f"Despesa_associacao {despesa_associacao} copiada para a nova associação."
            )

            for rateio in rateios_original:
                rateio.pk = None
                rateio.uuid = uuid.uuid4()
                rateio.despesa_associacao = despesa_associacao
                rateio.conta_associacao = associacao_nova.contas.filter(
                    tipo_conta=self.tipo_conta_transferido
                ).first()
                rateio.acao_associacao = associacao_nova.acoes.filter(
                    acao=rateio.acao_associacao.acao
                ).first()
                rateio.save()
                self.adicionar_log_info(
                    f"Rateio {rateio} copiado para a nova despesa_associacao."
                )

    def inativar_despesas_associacao_do_tipo_transferido(self, associacao_original):
        self.adicionar_log_info(
            f"Inativando despesas da conta {self.tipo_conta_transferido} da associação original."
        )

        despesas_associacao_original = associacao_original.despesas.filter(
            rateios__conta_associacao__tipo_conta=self.tipo_conta_transferido
        ).distinct()

        if not despesas_associacao_original.exists():
            self.adicionar_log_info(
                f"Associação original não possui despesas_associacao em conta {self.tipo_conta_transferido} a serem inativadas."
            )
            return

        for despesa_associacao in despesas_associacao_original:
            despesa_associacao.inativar_despesa()
            self.adicionar_log_info(f"Despesa {despesa_associacao} inativada.")

        self.adicionar_log_info(
            f"Despesas da conta {self.tipo_conta_transferido} da associação original inativadas."
        )

    def copiar_receitas_associacao_do_tipo_transferido(
        self, associacao_original, associacao_nova
    ):
        self.adicionar_log_info(
            f"Copiando receitas da conta {self.tipo_conta_transferido} da associação original para a nova associação."
        )

        receitas_associacao_original = associacao_original.receitas.filter(
            conta_associacao__tipo_conta=self.tipo_conta_transferido
        ).all()

        if not receitas_associacao_original.exists():
            self.adicionar_log_info(
                f"Associação original não possui receitas em conta {self.tipo_conta_transferido}."
            )
            return

        for receita in receitas_associacao_original:
            receita.pk = None
            receita.uuid = uuid.uuid4()
            receita.associacao = associacao_nova
            receita.conta_associacao = associacao_nova.contas.filter(
                tipo_conta=self.tipo_conta_transferido
            ).first()
            receita.acao_associacao = associacao_nova.acoes.filter(
                acao=receita.acao_associacao.acao
            ).first()
            receita.save()
            self.adicionar_log_info(
                f"Receita  {receita} copiada para a nova associação."
            )

            # Se a receita tiver um repasse, transfere o repasse para a associação nova
            if receita.repasse:
                repasse = receita.repasse
                repasse.associacao = associacao_nova
                repasse.conta_associacao = associacao_nova.contas.filter(
                    tipo_conta=self.tipo_conta_transferido
                ).first()
                repasse.acao_associacao = associacao_nova.acoes.filter(
                    acao=repasse.acao_associacao.acao
                ).first()
                repasse.save()
                self.adicionar_log_info(
                    f"Repasse {repasse} transferido para a nova associação."
                )

    def inativar_receitas_associacao_do_tipo_transferido(self, associacao_original):
        self.adicionar_log_info(
            f"Inativando receitas da conta {self.tipo_conta_transferido} da associação original."
        )

        receitas_associacao_original = associacao_original.receitas.filter(
            conta_associacao__tipo_conta=self.tipo_conta_transferido
        ).all()

        if not receitas_associacao_original.exists():
            self.adicionar_log_info(
                f"Associação original não possui receitas em conta {self.tipo_conta_transferido} a serem inativadas."
            )
            return

        for receita in receitas_associacao_original:
            receita.inativar_receita()
            self.adicionar_log_info(f"Receita {receita} inativada.")

        self.adicionar_log_info(
            f"Receitas da conta {self.tipo_conta_transferido} da associação original inativadas."
        )

    @property
    def associacao_original(self):
        return Associacao.by_uuid(self.associacao_original_uuid)

    def criar_associacao_nova(self):
        unidade_historico = self.clonar_unidade()
        self.atualizar_unidade_transferida()
        associacao_nova = self.clonar_associacao(
            self.associacao_original_uuid, unidade_historico
        )
        return associacao_nova

    def inicializar_transferencia(self):
        self.adicionar_log_info(
            f"Iniciando transferência de código EOL {self.eol_transferido} usando {self.eol_historico} para o histórico. Data: {datetime.today()}"
        )
        self.status_processamento = StatusProcessamento.PROCESSANDO
        self.save()
        self.associacao_original_uuid = Associacao.objects.get(
            unidade__codigo_eol=self.eol_transferido
        ).uuid

    def abortar_transferencia(self, motivo, excecao=False):
        self.adicionar_log_info(
            f"Abortando transferência de código EOL {self.eol_transferido} usando {self.eol_historico} para o histórico. Motivo: {motivo}"
        )
        self.status_processamento = (
            StatusProcessamento.ERRO if excecao else StatusProcessamento.ABORTADO
        )
        self.save()
        self.salvar_logs()

    def copiar_contas(self, associacao_original, associacao_nova):
        if self.comportamento_contas == ComportamentoContas.TRANSFERE_SELECIONADA:
            self.copiar_contas_associacao(associacao_original, associacao_nova)
            self.inativar_contas_associacao_do_tipo_transferido(associacao_original)
        else:
            self.copiar_contas_associacao(associacao_original, associacao_nova)

    def transferir_lancamentos(self, associacao_original, associacao_nova):
        self.copiar_despesas_associacao_do_tipo_transferido(
            associacao_original, associacao_nova
        )
        self.inativar_despesas_associacao_do_tipo_transferido(associacao_original)
        self.copiar_receitas_associacao_do_tipo_transferido(
            associacao_original, associacao_nova
        )
        self.inativar_receitas_associacao_do_tipo_transferido(associacao_original)

    def finalizar_transferencia(self):
        self.adicionar_log_info(
            f"Finalizada com sucesso a transferência de código EOL {self.eol_transferido} usando {self.eol_historico} para o histórico."
        )
        self.status_processamento = StatusProcessamento.SUCESSO
        self.save()
        self.salvar_logs()

    def executar_transferencia(self):
        associacao_nova = self.criar_associacao_nova()

        self.copiar_acoes_associacao(self.associacao_original, associacao_nova)

        self.copiar_contas(self.associacao_original, associacao_nova)

        if self.comportamento_contas == ComportamentoContas.TRANSFERE_SELECIONADA:
            self.transferir_lancamentos(self.associacao_original, associacao_nova)

        self.finalizar_transferencia()

    def transferir(self):
        try:
            self.inicializar_transferencia()

            pode_transferir, motivo = self.transferencia_possivel()
            if not pode_transferir:
                self.abortar_transferencia(motivo)
                return

            self.executar_transferencia()

        except Exception as e:
            self.adicionar_log_erro(f"Erro ao executar transferência: {str(e)}")
            self.abortar_transferencia(str(e), excecao=True)
            raise e
