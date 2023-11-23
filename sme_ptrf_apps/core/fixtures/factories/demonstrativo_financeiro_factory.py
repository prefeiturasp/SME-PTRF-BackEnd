from factory import DjangoModelFactory, SubFactory, LazyFunction, Sequence, LazyAttribute
from faker import Faker
from sme_ptrf_apps.core.models import (
    DemonstrativoFinanceiro,
    DadosDemonstrativoFinanceiro,
    ItemResumoPorAcao,
    ItemCredito,
    ItemDespesa,
    CategoriaDespesaChoices,
    InformacaoDespesaChoices
)
from .conta_associacao_factory import ContaAssociacaoFactory
from .periodo_factory import PeriodoFactory

fake = Faker("pt_BR")


class DemonstrativoFinanceiroFactory(DjangoModelFactory):
    class Meta:
        model = DemonstrativoFinanceiro

    arquivo = None
    arquivo_pdf = None
    conta_associacao = SubFactory(ContaAssociacaoFactory)
    prestacao_conta = None
    periodo_previa = SubFactory(PeriodoFactory)
    status = DemonstrativoFinanceiro.STATUS_CONCLUIDO
    versao = DemonstrativoFinanceiro.VERSAO_FINAL


class DadosDemonstrativoFinanceiroFactory(DjangoModelFactory):
    class Meta:
        model = DadosDemonstrativoFinanceiro

    demonstrativo = SubFactory(DemonstrativoFinanceiro)

    periodo_referencia = LazyFunction(lambda: fake.year() + f".{fake.random_int(min=1, max=3)}")
    periodo_data_inicio = Sequence(lambda obj: fake.past_date())
    periodo_data_fim = LazyAttribute(lambda obj: fake.future_date(end_date="+120d"))
    conta_associacao = Sequence(lambda n: f'Conta {fake.unique.lexify(text="?????", letters="ABCDEFGHIJK")}')

    nome_associacao = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    cnpj_associacao = Sequence(lambda n: fake.unique.cnpj())
    nome_dre_associacao = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    codigo_eol_associacao = Sequence(lambda n: fake.random_number(digits=6))

    banco = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    agencia = Sequence(lambda n: f"{fake.random_number(digits=6)}")
    conta = Sequence(lambda n: f"{fake.random_number(digits=6)}")
    data_extrato = fake.date_time()
    saldo_extrato = Sequence(lambda n: fake.random_number(digits=3))
    conta_encerrada_em = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))

    total_creditos = Sequence(lambda n: fake.random_number(digits=3))
    total_despesas_demonstradas = Sequence(lambda n: fake.random_number(digits=3))
    total_despesas_nao_demonstradas = Sequence(lambda n: fake.random_number(digits=3))
    total_despesas_nao_demonstradas_periodos_anteriores = Sequence(lambda n: fake.random_number(digits=3))

    justificativa_info_adicionais = Sequence(lambda n: fake.name())

    cargo_substituto_presidente_ausente = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    presidente_diretoria_executiva = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    presidente_conselho_fiscal = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))

    tipo_unidade = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    nome_unidade = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    texto_rodape = Sequence(lambda n: f'Documento parcial gerado pelo usuário {fake.random_number(digits=6)}')
    data_geracao = fake.date_time()


class ItemResumoPorAcaoFactory(DjangoModelFactory):
    class Meta:
        model = ItemResumoPorAcao

    dados_demonstrativo = SubFactory(DadosDemonstrativoFinanceiroFactory)

    acao_associacao = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    total_geral = False

    custeio_saldo_anterior = Sequence(lambda n: fake.random_number(digits=3))
    custeio_credito = Sequence(lambda n: fake.random_number(digits=3))
    custeio_despesa_realizada = Sequence(lambda n: fake.random_number(digits=3))
    custeio_despesa_nao_realizada = Sequence(lambda n: fake.random_number(digits=3))
    custeio_saldo_reprogramado_proximo = Sequence(lambda n: fake.random_number(digits=3))
    custeio_despesa_nao_demostrada_outros_periodos = Sequence(lambda n: fake.random_number(digits=3))
    custeio_valor_saldo_bancario_custeio = Sequence(lambda n: fake.random_number(digits=3))

    livre_saldo_anterior = Sequence(lambda n: fake.random_number(digits=3))
    livre_credito = Sequence(lambda n: fake.random_number(digits=3))
    livre_saldo_reprogramado_proximo = Sequence(lambda n: fake.random_number(digits=3))
    livre_valor_saldo_reprogramado_proximo_periodo = Sequence(lambda n: fake.random_number(digits=3))

    capital_saldo_anterior = Sequence(lambda n: fake.random_number(digits=3))
    capital_credito = Sequence(lambda n: fake.random_number(digits=3))
    capital_despesa_realizada = Sequence(lambda n: fake.random_number(digits=3))
    capital_despesa_nao_realizada = Sequence(lambda n: fake.random_number(digits=3))
    capital_saldo_reprogramado_proximo = Sequence(lambda n: fake.random_number(digits=3))
    capital_despesa_nao_demostrada_outros_periodos = Sequence(lambda n: fake.random_number(digits=3))
    capital_valor_saldo_bancario_capital = Sequence(lambda n: fake.random_number(digits=3))

    total_valores = Sequence(lambda n: fake.random_number(digits=3))
    saldo_bancario = Sequence(lambda n: fake.random_number(digits=3))


class ItemCreditoFactory(DjangoModelFactory):
    class Meta:
        model = ItemCredito

    dados_demonstrativo = SubFactory(DadosDemonstrativoFinanceiroFactory)
    tipo_receita = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    detalhamento = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    nome_acao = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    data = fake.date_time()
    valor = Sequence(lambda n: fake.random_number(digits=3))

    receita_estornada = False
    data_estorno = fake.date_time()
    numero_documento_despesa = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    motivos_estorno = Sequence(lambda n: fake.name())
    outros_motivos_estorno = Sequence(lambda n: fake.name())


class ItemDespesaFactory(DjangoModelFactory):
    class Meta:
        model = ItemDespesa

    dados_demonstrativo = SubFactory(DadosDemonstrativoFinanceiroFactory)
    categoria_despesa = CategoriaDespesaChoices.DEMONSTRADA
    info_despesa = InformacaoDespesaChoices.NAO_GEROU_IMPOSTOS

    uuid_despesa_referencia = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    uuid_rateio_referencia = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    razao_social = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    cnpj_cpf = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    tipo_documento = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    numero_documento = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    data_documento = fake.date_time()
    nome_acao_documento = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    especificacao_material = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    tipo_despesa = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    tipo_transacao = Sequence(lambda n: fake.unique.lexify(text="???", letters="ABCDEFGHIJK"))
    data_transacao = fake.date_time()
    valor = Sequence(lambda n: fake.random_number(digits=3))
    valor_total = Sequence(lambda n: fake.random_number(digits=3))

    # TODO Adicionar factory para despesa imposto (many to many de auto relacionamento)
