from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from sme_ptrf_apps.core.choices.tipos_carga import CARGA_CHOICES, CARGA_REPASSE_REALIZADO, CARGA_REQUER_PERIODO, CARGA_REQUER_TIPO_CONTA

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


# Delimitador do arquivo csv
DELIMITADOR_PONTO_VIRGULA = 'DELIMITADOR_PONTO_VIRGULA'
DELIMITADOR_VIRGULA = 'DELIMITADOR_VIRGULA'

DELIMITADOR_NOMES = {
    DELIMITADOR_PONTO_VIRGULA: 'Delimitador ponto e vírgula',
    DELIMITADOR_VIRGULA: 'Delimitador vírgula'
}

DELIMITADOR_CHOICES = (
    (DELIMITADOR_PONTO_VIRGULA, DELIMITADOR_NOMES[DELIMITADOR_PONTO_VIRGULA]),
    (DELIMITADOR_VIRGULA, DELIMITADOR_NOMES[DELIMITADOR_VIRGULA]),
)

# status processamento
PENDENTE = 'PENDENTE'
SUCESSO = 'SUCESSO'
ERRO = 'ERRO'
PROCESSADO_COM_ERRO = 'PROCESSADO_COM_ERRO'
PROCESSANDO = "PROCESSANDO"

STATUS_PROCESSAMENTO = {
    PENDENTE: 'Pendente',
    SUCESSO: 'Sucesso',
    ERRO: 'Erro',
    PROCESSADO_COM_ERRO: 'Processado com erro',
    PROCESSANDO: 'Processando...'
}

STATUS_PROCESSAMENTO_CHOICES = (
    (PENDENTE, STATUS_PROCESSAMENTO[PENDENTE]),
    (SUCESSO, STATUS_PROCESSAMENTO[SUCESSO]),
    (ERRO, STATUS_PROCESSAMENTO[ERRO]),
    (PROCESSADO_COM_ERRO, STATUS_PROCESSAMENTO[PROCESSADO_COM_ERRO]),
    (PROCESSANDO, STATUS_PROCESSAMENTO[PROCESSANDO]),
)


class Arquivo(ModeloBase):
    history = AuditlogHistoryField()

    identificador = models.SlugField(unique=True)
    conteudo = models.FileField(blank=True, null=True)
    tipo_carga = models.CharField(
        'tipo de carga',
        max_length=35,
        choices=CARGA_CHOICES,
        default=CARGA_REPASSE_REALIZADO
    )
    tipo_delimitador = models.CharField(
        'tipo delimitador',
        max_length=35,
        choices=DELIMITADOR_CHOICES,
        default=DELIMITADOR_VIRGULA
    )
    status = models.CharField(
        'status',
        max_length=35,
        choices=STATUS_PROCESSAMENTO_CHOICES,
        default=PENDENTE
    )
    log = models.TextField(blank=True, null=True)
    ultima_execucao = models.DateTimeField("Ultima execução", blank=True, null=True)
    periodo = models.ForeignKey(
        'Periodo',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Período',
        help_text='Período associado ao arquivo (opcional dependendo do tipo de carga)'
    )
    
    tipo_de_conta = models.ForeignKey(
        'TipoConta',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Tipo de conta',
        help_text='Tipo de conta associado ao arquivo (opcional dependendo do tipo de carga)'
    )

    class Meta:
        verbose_name = "arquivo de carga"
        verbose_name_plural = "02.0) Arquivos de carga"

    def __str__(self):
        return self.identificador

    def inicia_processamento(self):
        self.status = PROCESSANDO
        self.save()
        
    def requer_periodo(self):
        return CARGA_REQUER_PERIODO.get(self.tipo_carga, False)
    
    def requer_tipo_de_conta(self):
        return CARGA_REQUER_TIPO_CONTA.get(self.tipo_carga, False)

    @classmethod
    def status_to_json(cls):
        return [{
                'id': choice[0],
                'nome': choice[1]
                }
                for choice in STATUS_PROCESSAMENTO_CHOICES]

    @classmethod
    def tipos_cargas_to_json(cls):
        return [{
                'id': choice[0],
                'nome': choice[1],
                'requer_periodo': CARGA_REQUER_PERIODO.get(choice[0], False),
                'requer_tipo_de_conta': CARGA_REQUER_TIPO_CONTA.get(choice[0], False),
                }
                for choice in CARGA_CHOICES]

    @classmethod
    def delimitadores_to_json(cls):
        return [{
                'id': choice[0],
                'nome': choice[1]
                }
                for choice in DELIMITADOR_CHOICES]


auditlog.register(Arquivo)
