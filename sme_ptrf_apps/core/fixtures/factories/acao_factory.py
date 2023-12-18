from factory import DjangoModelFactory,Sequence
from faker import Faker
from sme_ptrf_apps.core.models.acao import Acao

fake = Faker("pt_BR")

class AcaoFactory(DjangoModelFactory):
    class Meta:
        model = Acao
        
    nome = Sequence(lambda n: fake.unique.name())
    posicao_nas_pesquisas = "ZZZZZZZZZZ"
    e_recursos_proprios = False
    aceita_capital = False
    aceita_custeio = False
    aceita_livre = False