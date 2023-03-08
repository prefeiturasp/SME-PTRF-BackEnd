import logging
import uuid as uuid

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

# status processamento
PENDENTE = 'PENDENTE'
SUCESSO = 'SUCESSO'
ABORTADO = 'ABORTADO'
ERRO = 'ERRO'
PROCESSANDO = "PROCESSANDO"

STATUS_PROCESSAMENTO = {
    PENDENTE: 'Pendente',
    SUCESSO: 'Sucesso',
    ABORTADO: 'Abortado',
    ERRO: 'Erro',
    PROCESSANDO: 'Processando...'
}

STATUS_PROCESSAMENTO_CHOICES = (
    (PENDENTE, STATUS_PROCESSAMENTO[PENDENTE]),
    (SUCESSO, STATUS_PROCESSAMENTO[SUCESSO]),
    (ABORTADO, STATUS_PROCESSAMENTO[ABORTADO]),
    (ERRO, STATUS_PROCESSAMENTO[ERRO]),
    (PROCESSANDO, STATUS_PROCESSAMENTO[PROCESSANDO]),
)


class TransferenciaEol(ModeloBase):

    eol_transferido = models.CharField(
        'EOL a ser transferido',
        max_length=6,
        help_text='É o código eol que será transferido para a nova unidade.',
    )

    eol_historico = models.CharField(
        'EOL usado para o histórico',
        max_length=6,
        help_text='É o código que será usado para o histórico da unidade que usava anteriormente o condigo transferido.',
    )

    tipo_nova_unidade = models.CharField(
        max_length=10,
        choices=TIPOS_CHOICE,
        default='CEMEI',
        help_text='Tipo da nova unidade que receberá o código transferido.',
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
        'Data de início das atividades',
        help_text='Data de início das atividades da nova unidade.',
    )

    tipo_conta_transferido = models.ForeignKey(
        'TipoConta',
        on_delete=models.PROTECT,
        help_text='Tipo de conta que será transferido para a nova unidade.',
    )

    status_processamento = models.CharField(
        'Status do processamento',
        max_length=20,
        choices=STATUS_PROCESSAMENTO_CHOICES,
        default=PENDENTE,
        help_text='Status do processamento da transferência.',
    )

    log_execucao = models.TextField(
        'Log de execução',
        blank=True,
        null=True,
        help_text='Log de execução da transferência.',
    )

    def __str__(self):
        return f'{self.eol_transferido} -> {self.eol_historico}'

    class Meta:
        verbose_name = 'Transferência de Código EOL'
        verbose_name_plural = '99.9) Transferências de Código EOL'

    def adicionar_log(self, log):
        if not hasattr(self, 'lista_logs'):
            self.lista_logs = []
        self.lista_logs.append(log)

    def salvar_logs(self):
        if hasattr(self, 'lista_logs'):
            self.log_execucao = '\n'.join(self.lista_logs)
            self.save()

    def adicionar_log_info(self, texto_log):
        logging.info(texto_log)
        self.adicionar_log(texto_log)

    def transferencia_possivel(self):
        # O código EOL transferido deve existir
        if not Unidade.objects.filter(codigo_eol=self.eol_transferido).exists():
            return False, f'Código EOL transferido {self.eol_transferido} não existe.'

        # O código EOL de histórico não deve existir
        if Unidade.objects.filter(codigo_eol=self.eol_historico).exists():
            return False, f'Código EOL de histórico {self.eol_historico} já existe.'

        # Deve existir um período para a data de início das atividades
        periodo_da_data_inicio_atividades = Periodo.da_data(self.data_inicio_atividades)
        if periodo_da_data_inicio_atividades is None:
            return False, f'Não existe período para a data de início das atividades {self.data_inicio_atividades}.'

        # Deve existir uma associação para o código EOL transferido
        if not Associacao.objects.filter(unidade__codigo_eol=self.eol_transferido).exists():
            return False, f'Não existe associação para o código EOL transferido {self.eol_transferido}.'

        # Não devem existir fechamentos para a associação do eol de tranferência no período da data de início das atividades da nova associação
        associacao_original = Associacao.objects.get(unidade__codigo_eol=self.eol_transferido)
        if associacao_original.fechamentos_associacao.filter(periodo=periodo_da_data_inicio_atividades).exists():
            return False, f'Já existem fechamentos para a associação original {associacao_original} no período {periodo_da_data_inicio_atividades}.'

        # Deve existir uma conta_associacao do tipo tipo_conta_transferido para a associação do código eol transferido
        if not ContaAssociacao.objects.filter(associacao=associacao_original,
                                              tipo_conta=self.tipo_conta_transferido).exists():
            return False, f'Não existe conta_associacao do tipo {self.tipo_conta_transferido} para a associação original {associacao_original}.'

        # Nao devem existir despesas da associação original que tenham com rateios no tipo_conta_transferido e em outro tipo de conta
        for despesa in associacao_original.despesas.all():
            if despesa.tem_pagamentos_em_multiplas_contas():
                return False, f'A associação original {associacao_original} possui despesas com rateios no tipo de conta {self.tipo_conta_transferido} e em outro tipo de conta.'

        return False, "Não implementado."

    # clonar a unidade de código transferido para uma nova usando o código histórico
    def clonar_unidade(self):
        self.adicionar_log_info(f'Clonando unidade de código EOL {self.eol_transferido} para {self.eol_historico}.')
        unidade_transferida = Unidade.objects.get(codigo_eol=self.eol_transferido)
        unidade_transferida.codigo_eol = self.eol_historico
        unidade_transferida.uuid = uuid.uuid4()
        unidade_transferida.save()
        self.adicionar_log_info(f'Unidade de código EOL {self.eol_transferido} clonada para {self.eol_historico}.')
        return unidade_transferida

    def atualizar_unidade_transferida(self):
        self.adicionar_log_info(f'Atualizando unidade de código EOL {self.eol_transferido} para o tipo_nova_unidade.')
        unidade_transferida = Unidade.objects.get(codigo_eol=self.eol_transferido)
        unidade_transferida.tipo_unidade = self.tipo_nova_unidade
        unidade_transferida.save()
        self.adicionar_log_info(f'Unidade de código EOL {self.eol_transferido} atualizada para o tipo_nova_unidade.')
        return unidade_transferida

    def clonar_associacao(self):
        self.adicionar_log_info(f'Clonando associação da unidade de código EOL {self.eol_transferido}.')
        associacao_transferida = Associacao.objects.get(unidade__codigo_eol=self.eol_transferido)
        associacao_transferida.pk = None
        associacao_transferida.uuid = uuid.uuid4()
        associacao_transferida.cnpj = self.cnpj_nova_associacao
        associacao_transferida.save()
        self.adicionar_log_info(f'Associação da unidade de código EOL {self.eol_transferido} clonada.')
        return associacao_transferida

    def copiar_acoes_associacao(self, associacao_transferida, associacao_nova):
        self.adicionar_log_info(f'Copiando ações_associacao da associação original para a nova associação.')
        acoes_associacao_transferidas = associacao_transferida.acoes.all()
        for acao_associacao_transferida in acoes_associacao_transferidas:
            acao_associacao_transferida.pk = None
            acao_associacao_transferida.uuid = uuid.uuid4()
            acao_associacao_transferida.associacao = associacao_nova
            acao_associacao_transferida.save()
        self.adicionar_log_info(f'Ações_associacao da associação original copiadas para a nova associação.')

    def get_associacao_transferida(self):
        return Associacao.objects.get(unidade__codigo_eol=self.eol_transferido)

    def transferir(self):
        self.adicionar_log_info(f'Iniciando transferência de código EOL {self.eol_transferido} usando {self.eol_historico} para o histórico.')

        # verifica se a transferência é possível
        pode_transferir, motivo = self.transferencia_possivel()
        if not pode_transferir:
            self.adicionar_log_info(f'Abortando transferência de código EOL {self.eol_transferido} usando {self.eol_historico} para o histórico. Motivo: {motivo}')
            self.status_processamento = ABORTADO
            self.save()
            self.salvar_logs()
            return

        # clona a unidade de código transferido para uma nova usando o código histórico
        unidade_historico = self.clonar_unidade()

        # atualiza a unidade de código transferido para o tipo_nova_unidade
        unidade_transferida = self.atualizar_unidade_transferida()

        # clona associacao da unidade de código transferido para uma nova associação
        associacao_nova = self.clonar_associacao()

        associacao_transferida = self.get_associacao_transferida()

        # copiar as ações_associacao da associação original para a nova associação (guardando o "de-para" para atualizar os gastos e créditos.)
        self.copiar_acoes_associacao(associacao_transferida, associacao_nova)

        # copiar a conta_associacao de tipo_conta_transferido da associação original para a nova associação
        # desativar a conta_associacao de tipo_conta_transferido da associação original
        # desvincular a associação da unidade de código transferido e vincula-la a unidade de código histórico
        # vincular a nova associação a unidade de código transferido
        # copiar gastos e rateios vinculados à conta_associacao de tipo_conta_transferido da associação original para a nova associação
        # desativar gastos e rateios vinculados à conta_associacao de tipo_conta_transferido da associação original
        # copiar créditos vinculados à conta_associacao de tipo_conta_transferido da associação original para a nova associação
        # desativar créditos vinculados à conta_associacao de tipo_conta_transferido da associação original
        # gravar log de execução
        # atualizar status do processamento
