from factory import DjangoModelFactory, SubFactory, LazyFunction, Sequence, LazyAttribute
from faker import Faker
from sme_ptrf_apps.core.models import RelacaoBens, RelatorioRelacaoBens, ItemRelatorioRelacaoDeBens
from .conta_associacao_factory import ContaAssociacaoFactory
from .periodo_factory import PeriodoFactory

fake = Faker("pt_BR")

class RelacaoBensFactory(DjangoModelFactory):
    class Meta:
        model = RelacaoBens

    arquivo = None
    arquivo_pdf = None
    conta_associacao = SubFactory(ContaAssociacaoFactory)
    # TODO implementar factory PrestacaoContaFactory
    prestacao_conta = None
    periodo_previa = SubFactory(PeriodoFactory)

    status = RelacaoBens.STATUS_CONCLUIDO
    versao = RelacaoBens.VERSAO_FINAL


class RelatorioRelacaoBensFactory(DjangoModelFactory):
    class Meta:
        model = RelatorioRelacaoBens

    relacao_bens = SubFactory(RelacaoBensFactory)

    periodo_referencia = LazyFunction(lambda: fake.year() + f".{fake.random_int(min=1, max=3)}")
    periodo_data_inicio = Sequence(lambda obj: fake.past_date())
    periodo_data_fim = LazyAttribute(lambda obj: fake.future_date(end_date="+120d"))

    conta = Sequence(lambda n: f'Conta {fake.name()}')
    tipo_unidade = Sequence(lambda n: f'Tipo {fake.name()}')
    nome_unidade = Sequence(lambda n: fake.name())
    nome_associacao = Sequence(lambda n: fake.name())
    cnpj_associacao = Sequence(lambda n: fake.unique.cnpj())
    codigo_eol_associacao = Sequence(lambda n:fake.random_number(digits=6))
    nome_dre_associacao = Sequence(lambda n: fake.name())
    presidente_diretoria_executiva = Sequence(lambda n:fake.name())
    cargo_substituto_presidente_ausente = Sequence(lambda n:fake.name())
    data_geracao = fake.date_time()

    valor_total = Sequence(lambda n: fake.random_number(digits=3))


class ItemRelatorioRelacaoDeBensFactory(DjangoModelFactory):
    class Meta:
        model = ItemRelatorioRelacaoDeBens

    tipo_documento = Sequence(lambda n:fake.name())
    numero_documento = Sequence(lambda n: fake.name())
    data_documento = Sequence(lambda n: fake.date())
    especificacao_material = Sequence(lambda n: fake.sentences(1))
    numero_documento_incorporacao = Sequence(lambda n: fake.random_number(digits=6))
    quantidade = Sequence(lambda n: fake.random_number(digits=1))
    valor_item = Sequence(lambda n: fake.random_number(digits=3))
    valor_rateio = Sequence(lambda n: fake.random_number(digits=3))

    relatorio = SubFactory(RelatorioRelacaoBensFactory)
