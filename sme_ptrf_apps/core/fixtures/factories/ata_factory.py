from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.models.ata import Ata
from sme_ptrf_apps.core.models.participante import Participante
from sme_ptrf_apps.core.fixtures.factories.periodo_factory import PeriodoFactory
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory

fake = Faker("pt_BR")


class AtaFactory(DjangoModelFactory):
    class Meta:
        model = Ata

    periodo = SubFactory(PeriodoFactory)
    associacao = SubFactory(AssociacaoFactory)

    tipo_ata = Ata.ATA_APRESENTACAO
    tipo_reuniao = Ata.REUNIAO_ORDINARIA
    convocacao = Ata.CONVOCACAO_PRIMEIRA
    status_geracao_pdf = Ata.STATUS_NAO_GERADO
    parecer_conselho = Ata.PARECER_APROVADA

    data_reuniao = fake.date_this_decade()
    hora_reuniao = fake.time()
    local_reuniao = fake.city()
    comentarios = fake.sentence(nb_words=8)
    justificativa_repasses_pendentes = fake.sentence(nb_words=10)

    previa = False
    pdf_gerado_previamente = False


class ParticipanteFactory(DjangoModelFactory):
    class Meta:
        model = Participante

    ata = SubFactory(AtaFactory)
    identificacao = Sequence(lambda n: fake.unique.cpf())
    nome = Sequence(lambda n: fake.name())
