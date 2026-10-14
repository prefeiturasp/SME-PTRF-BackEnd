from django.db import models
from django.core.validators import MinLengthValidator
from sme_ptrf_apps.core.models_abstracts import ModeloBase

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from django.db import models
from .validators import cnpj_validation, normalize_cnpj


class RelatorioRelacaoBens(ModeloBase):
    history = AuditlogHistoryField()

    relacao_bens = models.ForeignKey('RelacaoBens', on_delete=models.CASCADE, null=True, blank=True)

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
        verbose_name = 'Dados da Relação de bens'
        verbose_name_plural = '09.3.1) Dados das Relações de bens'

    def __str__(self):
        return f"Relatório {self.nome_associacao} | {self.periodo_referencia} gerado em {self.data_geracao}"

    def save(self, *args, **kwargs):
        if self.cnpj_associacao:
            self.cnpj_associacao = normalize_cnpj(self.cnpj_associacao)
        return super().save(*args, **kwargs)


class ItemRelatorioRelacaoDeBens(ModeloBase):

    class TipoBem(models.TextChoices):
        ADQUIRIDO = 'ADQUIRIDO', 'Adquirido'
        PRODUZIDO = 'PRODUZIDO', 'Produzido'

    history = AuditlogHistoryField()

    tipo_bem = models.CharField(
        verbose_name='Tipo de Bem',
        max_length=50,
        choices=TipoBem.choices,
        default=TipoBem.ADQUIRIDO,
        blank=True,
        null=True,
    )

    bem_produzido_id = models.PositiveBigIntegerField(
        verbose_name='Bem produzido ID',
        blank=True, 
        null=True
    )

    acao = models.CharField(verbose_name='Ação', max_length=160, blank=True, null=True)
    relatorio = models.ForeignKey('RelatorioRelacaoBens', on_delete=models.CASCADE,
                                  related_name='bens', blank=True, null=True)
    tipo_documento = models.CharField(verbose_name='Tipo documento', max_length=200, blank=True, null=True)
    numero_documento =  models.CharField(verbose_name='Nº do documento', max_length=100, default='', blank=True)
    data_documento = models.DateField(verbose_name='Data documento', null=True, blank=True)
    especificacao_material = models.CharField(verbose_name='Especificação material', max_length=200, blank=True, null=True)
    numero_documento_incorporacao = models.CharField(verbose_name='Nº documento incorporação', max_length=100, default='',
                                                      blank=True)
    quantidade = models.PositiveIntegerField(verbose_name='Quantidade')
    valor_item = models.DecimalField(verbose_name='Valor total', max_digits=8, decimal_places=2, default=0)
    valor_rateio = models.DecimalField(verbose_name='Valor total', max_digits=8, decimal_places=2, default=0)

    @property
    def tipo_bem_label(self):
        return self.TipoBem(self.tipo_bem).label

    def __str__(self):
        return self.numero_documento


class ItemRelatorioBemProduzidoRateio(ModeloBase):
    history = AuditlogHistoryField()

    relatorio = models.ForeignKey(
        'RelatorioRelacaoBens', 
        on_delete=models.CASCADE,       
        blank=True,
        null=True
    )

    bem_produzido_id = models.PositiveBigIntegerField(verbose_name='Bem produzido ID')
    tipo_documento = models.CharField(verbose_name='Tipo documento', max_length=200, blank=True, null=True)
    numero_documento =  models.CharField(verbose_name='Nº do documento', max_length=100, default='', blank=True)
    data_documento = models.DateField(verbose_name='Data documento')
    acao = models.CharField(verbose_name='Ação', max_length=160, blank=True, null=True)
    valor_rateio = models.DecimalField(verbose_name='Valor total', max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return self.numero_documento


auditlog.register(RelatorioRelacaoBens)
auditlog.register(ItemRelatorioRelacaoDeBens)
auditlog.register(ItemRelatorioBemProduzidoRateio)
