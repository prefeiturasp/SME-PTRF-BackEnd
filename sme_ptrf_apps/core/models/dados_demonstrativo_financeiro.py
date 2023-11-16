import logging

from django.db import models
from django.core.validators import MinLengthValidator

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


from sme_ptrf_apps.core.models_abstracts import ModeloBase


logger = logging.getLogger(__name__)


class DadosDemonstrativoFinanceiro(ModeloBase):
    history = AuditlogHistoryField()

    demonstrativo = models.ForeignKey('DemonstrativoFinanceiro', on_delete=models.CASCADE, related_name="dados", default=None, null=True)

    # cabecalho
    periodo_referencia = models.CharField('Periodo de referencia', max_length=10, default='')
    periodo_data_inicio = models.DateField('Periodo de data inicio', blank=True, null=True, default=None)
    periodo_data_fim = models.DateField('Periodo de data fim', blank=True, null=True, default=None)
    conta_associacao = models.CharField('Conta associação', max_length=160, default='')

    # bloco 1
    nome_associacao = models.CharField('Nome da associação', max_length=160, default='')
    cnpj_associacao = models.CharField('Nome da associação', max_length=20, default='')
    nome_dre_associacao = models.CharField('Nome da dre', max_length=160, default='')
    codigo_eol_associacao = models.CharField('Codigo eol', max_length=6, validators=[MinLengthValidator(6)], default='000000')

    # bloco 2
    banco = models.CharField('Nome do banco', max_length=50, default='')
    agencia = models.CharField('Nº agência', max_length=15, default='')
    conta = models.CharField('Nº conta', max_length=30, blank=True, default='')
    data_extrato = models.DateField('Data extrato', blank=True, null=True, default=None)
    saldo_extrato = models.DecimalField('Saldo do extrato', max_digits=12, decimal_places=2, default=0)
    conta_encerrada_em = models.CharField('Conta encerrada em', max_length=50, default='', blank=True)

    # bloco 3 estará relacionado pela FK de ItemResumoPorAcao

    # bloco 4
    total_creditos = models.DecimalField('Total créditos', max_digits=12, decimal_places=2, default=0)

    # bloco 5
    total_despesas_demonstradas = models.DecimalField(
        'Total despesas demonstradas', max_digits=12, decimal_places=2, default=0)

    # bloco 6
    total_despesas_nao_demonstradas = models.DecimalField(
        'Total despesas não demonstradas', max_digits=12, decimal_places=2, default=0)

    # bloco 7
    total_despesas_nao_demonstradas_periodos_anteriores = models.DecimalField(
        'Total despesas não demonstradas de periodos anteriores', max_digits=12, decimal_places=2, default=0)

    # bloco 8
    justificativa_info_adicionais = models.TextField(
        'Justificativa e informações adicionais', blank=True, default=None, null=True)

    # bloco 9
    cargo_substituto_presidente_ausente = models.CharField(
        'Cargo substituto presidente ausente', max_length=160, blank=True, default=None, null=True)
    presidente_diretoria_executiva = models.CharField(
        'Presidente da diretoria executiva', max_length=160, blank=True, default=None, null=True)
    presidente_conselho_fiscal = models.CharField(
        'Presidente do conselho fiscal', max_length=160, blank=True, default=None, null=True)

    # rodape
    tipo_unidade = models.CharField('Tipo unidade', max_length=50, default='')
    nome_unidade = models.CharField('Nome unidade', max_length=160, default='')
    texto_rodape = models.TextField('Texto rodapé', blank=True, default=None, null=True)
    data_geracao = models.DateField('Data geração', blank=True, null=True, default=None)

    class Meta:
        verbose_name = 'Dados Demonstrativo Financeiro'
        verbose_name_plural = '20.0) Dados dos Demonstrativos Financeiros'


class ItemResumoPorAcao(ModeloBase):
    history = AuditlogHistoryField()

    dados_demonstrativo = models.ForeignKey(
        'DadosDemonstrativoFinanceiro', on_delete=models.CASCADE, related_name="itens_resumo_por_acao")

    acao_associacao = models.CharField('Nome da ação associação', max_length=160)
    total_geral = models.BooleanField('É registro de total geral ?', default=False)

    custeio_saldo_anterior = models.DecimalField(
        'Linha custeio saldo anterior', max_digits=12, decimal_places=2, default=0)
    custeio_credito = models.DecimalField(
        'Linha custeio credito', max_digits=12, decimal_places=2, default=0)
    custeio_despesa_realizada = models.DecimalField(
        'Linha custeio despesa realizada', max_digits=12, decimal_places=2, default=0)
    custeio_despesa_nao_realizada = models.DecimalField(
        'Linha custeio despesa não realizada', max_digits=12, decimal_places=2, default=0)
    custeio_saldo_reprogramado_proximo = models.DecimalField(
        'Linha custeio saldo reprogramado proximo periodo', max_digits=12, decimal_places=2, default=0)
    custeio_despesa_nao_demostrada_outros_periodos = models.DecimalField(
        'Linha custeio despesa não demonstrada outros períodos', max_digits=12, decimal_places=2, default=0)
    custeio_valor_saldo_bancario_custeio = models.DecimalField(
        'Linha custeio valor saldo bancario', max_digits=12, decimal_places=2, default=0)

    livre_saldo_anterior = models.DecimalField(
        'Linha livre saldo anterior', max_digits=12, decimal_places=2, default=0)
    livre_credito = models.DecimalField(
        'Linha livre credito', max_digits=12, decimal_places=2, default=0)
    livre_saldo_reprogramado_proximo = models.DecimalField(
        'Linha livre saldo reprogramado proximo periodo', max_digits=12, decimal_places=2, default=0)
    livre_valor_saldo_reprogramado_proximo_periodo = models.DecimalField(
        'Linha livre valor saldo reprogramado proximo periodo', max_digits=12, decimal_places=2, default=0)

    capital_saldo_anterior = models.DecimalField(
        'Linha capital saldo anterior', max_digits=12, decimal_places=2, default=0)
    capital_credito = models.DecimalField(
        'Linha capital credito', max_digits=12, decimal_places=2, default=0)
    capital_despesa_realizada = models.DecimalField(
        'Linha capital despesa realizada', max_digits=12, decimal_places=2, default=0)
    capital_despesa_nao_realizada = models.DecimalField(
        'Linha capital despesa não realizada', max_digits=12, decimal_places=2, default=0)
    capital_saldo_reprogramado_proximo = models.DecimalField(
        'Linha capital saldo reprogramado proximo periodo', max_digits=12, decimal_places=2, default=0)
    capital_despesa_nao_demostrada_outros_periodos = models.DecimalField(
        'Linha capital despesa não demonstrada outros periodos', max_digits=12, decimal_places=2, default=0)
    capital_valor_saldo_bancario_capital = models.DecimalField(
        'Linha capital valor saldo bancario', max_digits=12, decimal_places=2, default=0)

    total_valores = models.DecimalField('Total valores', max_digits=12, decimal_places=2, default=0)
    saldo_bancario = models.DecimalField('Saldo bancario', max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Dados Demonstrativo Financeiro Item Resumo por Ação'
        verbose_name_plural = '20.1) Dados dos Demonstrativos Financeiros Itens Resumo por Ação'


class ItemCredito(ModeloBase):
    history = AuditlogHistoryField()

    dados_demonstrativo = models.ForeignKey(
        'DadosDemonstrativoFinanceiro', on_delete=models.CASCADE, related_name="itens_creditos")

    tipo_receita = models.CharField('Tipo receita', max_length=160, default=None, null=True)
    detalhamento = models.CharField('Detalhamento', max_length=160, default=None, null=True, blank=True)
    nome_acao = models.CharField('Ação', max_length=160, default=None, null=True)
    data = models.DateField('Data', null=True, default=None)
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2, null=True, default=0)

    receita_estornada = models.BooleanField('É um estorno', default=False)
    data_estorno = models.DateField('Data estorno', null=True, blank=True, default=None)
    numero_documento_despesa = models.CharField('N documento despesa', max_length=160, default=None, blank=True, null=True)
    motivos_estorno = models.TextField('Motivos para estorno', blank=True, default=None, null=True)
    outros_motivos_estorno = models.TextField('Outros motivos para estorno', blank=True, default=None, null=True)

    class Meta:
        verbose_name = 'Dados Demonstrativo Financeiro Item de Crédito'
        verbose_name_plural = '20.2) Dados dos Demonstrativos Financeiros Itens de Créditos'


class CategoriaDespesaChoices(models.TextChoices):
    DEMONSTRADA = "DEMONSTRADA", "Demonstrada"
    NAO_DEMONSTRADA = "NAO_DEMONSTRADA", "Não Demonstrada"
    NAO_DEMONSTRADA_PERIODO_ANTERIOR = "NAO_DEMONSTRADA_PERIODO_ANTERIOR", "Não demonstrada periodo anterior"


class InformacaoDespesaChoices(models.TextChoices):
    NAO_GEROU_IMPOSTOS = "NAO_GEROU_IMPOSTOS", "Despesa não gerou impostos"
    GEROU_IMPOSTOS = "GEROU_IMPOSTOS", "Despesa gerou impostos"
    IMPOSTO_GERADO = "IMPOSTO_GERADO", "Imposto gerado"


class ItemDespesa(ModeloBase):
    history = AuditlogHistoryField()

    dados_demonstrativo = models.ForeignKey(
        'DadosDemonstrativoFinanceiro', on_delete=models.CASCADE, related_name="itens_despesa")

    categoria_despesa = models.CharField(
        "Categoria despesa",
        max_length=50,
        choices=CategoriaDespesaChoices.choices,
        default=CategoriaDespesaChoices.DEMONSTRADA,
    )

    info_despesa = models.CharField(
        "Informação despesa",
        max_length=50,
        choices=InformacaoDespesaChoices.choices,
        default=InformacaoDespesaChoices.NAO_GEROU_IMPOSTOS,
        help_text="Informação se a despesa é uma geradora de impostos, um imposto ou uma despesa sem impostos"
    )

    uuid_despesa_referencia = models.CharField(
        'Uuid despesa', max_length=300, default=None, null=True, help_text="Referencia da despesa utilizada para gravação dos dados")
    uuid_rateio_referencia = models.CharField(
        'Uuid rateio', max_length=300, default=None, null=True, help_text="Referencia do rateio utilizado para gravação dos dados")

    razao_social = models.CharField('Razão social', max_length=300, default=None, null=True)
    cnpj_cpf = models.CharField('CNPJ ou CPF', max_length=20)
    tipo_documento = models.CharField('Tipo documento', max_length=160, default=None, null=True)
    numero_documento = models.CharField('Numero documento', max_length=100, default=None, null=True)
    data_documento = models.DateField('Data documento', null=True, default=None)
    nome_acao_documento = models.CharField('Tipo documento', max_length=300, default=None, null=True)
    especificacao_material = models.CharField('Especificacao material', max_length=300, default=None, null=True)
    tipo_despesa = models.CharField('Tipo despesa', max_length=100, default=None, null=True)
    tipo_transacao = models.CharField('Tipo transação', max_length=200, default=None, null=True)
    data_transacao = models.DateField('Data transacao', null=True, default=None)
    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2, null=True, default=0)
    despesas_impostos = models.ManyToManyField('ItemDespesa', blank=True, related_name='despesa_geradora')

    class Meta:
        verbose_name = 'Dados Demonstrativo Financeiro Item de Despesa'
        verbose_name_plural = '20.3) Dados dos Demonstrativos Financeiros Itens de Despesas'


auditlog.register(DadosDemonstrativoFinanceiro)
auditlog.register(ItemResumoPorAcao)
auditlog.register(ItemCredito)
auditlog.register(ItemDespesa)
