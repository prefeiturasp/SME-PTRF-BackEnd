from factory import DjangoModelFactory, SubFactory, Sequence
from faker import Faker
from sme_ptrf_apps.core.models.unidade import Unidade
from ..providers.unidade_provider import provider_tipos_de_unidades_desconsiderando_tipo_dre, provider_anos_dre_designacao_ano
import random

fake = Faker("pt_BR")
fake.add_provider(provider_anos_dre_designacao_ano)
fake.add_provider(provider_tipos_de_unidades_desconsiderando_tipo_dre)

class DreFactory(DjangoModelFactory):
    class Meta:
        model = Unidade

    nome = Sequence(lambda n: f"DIRETORIA REGIONAL DE EDUCACAO {fake.unique.name().upper()}")
    tipo_unidade = "DRE"
    codigo_eol = Sequence(lambda n: str(fake.unique.random_int(min=100000, max=999999)))
    sigla = Sequence(lambda n: fake.unique.lexify(text="??", letters="ABCDEFGHIJK"))
    dre_cnpj = Sequence(lambda n: fake.unique.cnpj())
    dre_diretor_regional_rf = Sequence(lambda n: str(fake.unique.random_int(min=1000000, max=9999999)))
    dre_diretor_regional_nome = Sequence(lambda n:fake.unique.name().upper())
    dre_designacao_portaria = Sequence(lambda n: f"{fake.random_number(digits=4)}/{fake.random_number(digits=4)}")
    dre_designacao_ano = fake.provider_anos_dre_designacao_ano()
    
class UnidadeFactory(DjangoModelFactory):
    class Meta:
        model = Unidade

    nome = Sequence(lambda n: fake.name().upper())
    tipo_unidade = Sequence(lambda n: fake.provider_tipos_de_unidades_desconsiderando_tipo_dre())
    codigo_eol = Sequence(lambda n: str(fake.unique.random_int(min=100000, max=999999)))
    dre = SubFactory(DreFactory)
    cep = Sequence(lambda n: str(fake.unique.random_int(min=10000000, max=99999999)))
    email = Sequence(lambda n: fake.unique.email())
    numero = Sequence(lambda n: random.choice(["S/N", str(fake.random_int(min=100, max=999))]))
    telefone = Sequence(lambda n: fake.unique.phone_number())
    tipo_logradouro = Sequence(lambda n: random.choice(["Rua", "Avenida"]))
    observacao = Sequence(lambda n: fake.paragraph(nb_sentences=1))