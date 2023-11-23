from factory import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.receitas.models import TipoReceita

fake = Faker("pt_BR")

class TipoReceitaFactory(DjangoModelFactory):
    class Meta:
        model = TipoReceita

    nome = fake.unique.name()
    e_repasse = False
    e_rendimento = False
    e_devolucao = False
    e_estorno = False
    aceita_capital = False
    aceita_custeio = False
    aceita_livre = False
    e_recursos_proprios = False
    mensagem_usuario = ""
    possui_detalhamento = False
