from django.db import models
from django.core.validators import MinLengthValidator
from sme_ptrf_apps.core.models_abstracts import ModeloBase

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from django.db import models
from .validators import cnpj_validation

class RelatorioRelacaoBens(ModeloBase):
    history = AuditlogHistoryField()

    relacao_bens = models.ForeignKey('RelacaoBens', on_delete=models.SET_NULL, null=True, blank=True)

    # cabecalho
    periodo_referencia = models.CharField(verbose_name='Período referência', max_length=200)
    periodo_data_inicio = models.DateField(verbose_name='Período data início', blank=True, null=True)
    periodo_data_fim = models.DateField(verbose_name='Período data fim', blank=True, null=True)
    conta = models.CharField(verbose_name='Conta', max_length=200, blank=True, null=True)

    # identificação APM
    tipo_unidade = models.CharField(verbose_name='Tipo unidade', max_length=200, blank=True, null=True)
    nome_unidade = models.CharField(verbose_name='Nome unidade', max_length=200, blank=True, null=True)
    nome_associacao = models.CharField(verbose_name='Nome associação', max_length=200, blank=True, null=True)
    cnpj_associacao = models.CharField(
        "CNPJ da Associação", max_length=20, validators=[cnpj_validation]
        , blank=True, null=True, default=""
    )
    codigo_eol_associacao = models.CharField(verbose_name='Código eol associação', max_length=6, validators=[MinLengthValidator(6)])
    nome_dre_associacao = models.CharField(verbose_name='Nome DRE associação', max_length=200, blank=True, null=True)
    presidente_diretoria_executiva = models.CharField(verbose_name='Presidente diretoria executiva', max_length=200, blank=True, null=True)
    cargo_substituto_presidente_ausente = models.CharField(verbose_name='Cargo substituto presidente ausente', max_length=200, blank=True, null=True)

    data_geracao = models.DateTimeField(verbose_name='Data geração')
    usuario = models.CharField(verbose_name='Usuário', max_length=200, blank=True, null=True)

    valor_total = models.DecimalField('Valor total', max_digits=8, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Relatório Relação de bens'
        verbose_name_plural = '09.3.1) Relatório Relações de bens'

    def __str__(self):
        return f"Relatório {self.nome_associacao} | {self.periodo_referencia} gerado em {self.data_geracao}"

class ItemRelatorioRelacaoDeBens(ModeloBase):
    history = AuditlogHistoryField()

    relatorio = models.ForeignKey('RelatorioRelacaoBens', on_delete=models.PROTECT,
                                  related_name='bens', blank=True, null=True)
    tipo_documento = models.CharField(verbose_name='Tipo documento', max_length=200, blank=True, null=True)
    numero_documento =  models.CharField(verbose_name='Nº do documento', max_length=100, default='', blank=True)
    data_documento = models.DateField(verbose_name='Data documento')
    especificacao_material = models.CharField(verbose_name='Especificação material', max_length=200, blank=True, null=True)
    numero_documento_incorporacao = models.CharField(verbose_name='Nº documento incorporação', max_length=100, default='',
                                                      blank=True)
    quantidade = models.PositiveIntegerField(verbose_name='Quantidade')
    valor_item = models.DecimalField(verbose_name='Valor total', max_digits=8, decimal_places=2, default=0)
    valor_rateio = models.DecimalField(verbose_name='Valor total', max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return self.numero_documento

auditlog.register(RelatorioRelacaoBens)
auditlog.register(ItemRelatorioRelacaoDeBens)
