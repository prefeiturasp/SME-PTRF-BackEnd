from datetime import time
from factory import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models import AtaPaa, ParticipanteAtaPaa
from sme_ptrf_apps.paa.fixtures.factories.paa import PaaFactory

fake = Faker("pt_BR")


class AtaPaaFactory(DjangoModelFactory):
    class Meta:
        model = AtaPaa

    paa = SubFactory(PaaFactory)

    tipo_ata = AtaPaa.ATA_APRESENTACAO
    tipo_reuniao = AtaPaa.REUNIAO_ORDINARIA
    convocacao = AtaPaa.CONVOCACAO_PRIMEIRA
    status_geracao_pdf = AtaPaa.STATUS_NAO_GERADO
    parecer_conselho = AtaPaa.PARECER_APROVADA

    data_reuniao = fake.date_this_decade()
    hora_reuniao = time(0, 0)
    local_reuniao = fake.city()
    comentarios = fake.sentence(nb_words=8)
    justificativa_repasses_pendentes = ''

    previa = False
    pdf_gerado_previamente = False


class ParticipanteAtaPaaFactory(DjangoModelFactory):
    class Meta:
        model = ParticipanteAtaPaa

    ata_paa = SubFactory(AtaPaaFactory)
    identificacao = fake.random_int(min=1000000, max=9999999)
    nome = fake.name()
    cargo = fake.job()
    membro = False
    conselho_fiscal = False
    presente = True
    professor_gremio = False

