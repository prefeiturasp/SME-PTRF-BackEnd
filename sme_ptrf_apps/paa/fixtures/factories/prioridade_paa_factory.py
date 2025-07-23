from factory import SubFactory, Sequence, LazyFunction
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models import PrioridadePaa
from sme_ptrf_apps.paa.fixtures.factories import AcaoPddeFactory, ProgramaPddeFactory, PaaFactory
from sme_ptrf_apps.core.fixtures.factories.acao_associacao_factory import AcaoAssociacaoFactory
from sme_ptrf_apps.despesas.fixtures.factories import TipoCusteioFactory, EspecificacaoMaterialServicoFactory
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum
import random


fake = Faker("pt_BR")


class PrioridadePaaFactory(DjangoModelFactory):
    class Meta:
        model = PrioridadePaa

    paa = SubFactory(PaaFactory)
    prioridade = True
    recurso = LazyFunction(lambda: random.choice([e.name for e in RecursoOpcoesEnum]))
    acao_associacao = SubFactory(AcaoAssociacaoFactory)
    acao_pdde = SubFactory(AcaoPddeFactory)
    programa_pdde = SubFactory(ProgramaPddeFactory)
    tipo_aplicacao = LazyFunction(lambda: random.choice([e.name for e in TipoAplicacaoOpcoesEnum]))
    tipo_despesa_custeio = SubFactory(TipoCusteioFactory)
    especificacao_material = SubFactory(EspecificacaoMaterialServicoFactory)
    valor_total = Sequence(lambda n: fake.random_number(digits=3))
