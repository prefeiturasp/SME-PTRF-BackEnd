import pytest
from django.utils import timezone
from django.contrib import admin
from freezegun import freeze_time
from model_bakery import baker
from ...models import AtaParecerTecnico
from sme_ptrf_apps.core.models import Unidade, Periodo
from datetime import datetime, date

pytestmark = pytest.mark.django_db

@pytest.fixture
@freeze_time('2020-07-01 10:00:00')
def ata_parecer_tecnico_t1(dre, periodo, consolidado_dre_ata_parecer_tecnico):
    return baker.make(
        'AtaParecerTecnico',
        arquivo_pdf=None,
        periodo=periodo,
        dre=dre,
        status_geracao_pdf='NAO_GERADO',
        numero_ata=1,
        data_reuniao=date(2020, 7, 1),
        local_reuniao='Escola Teste',
        comentarios='Teste',
        consolidado_dre=consolidado_dre_ata_parecer_tecnico,
        data_portaria=date(2026, 8, 10),
        numero_portaria="123",
        sequencia_de_publicacao=1,
        sequencia_de_retificacao=1,
    )


def test_instance_model(ata_parecer_tecnico_t1):
    model = ata_parecer_tecnico_t1

    assert isinstance(model, AtaParecerTecnico)
    assert isinstance(model.periodo, Periodo)
    assert isinstance(model.dre, Unidade)
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.status_geracao_pdf
    assert model.numero_ata
    assert model.data_reuniao
    assert model.hora_reuniao
    assert model.local_reuniao
    assert model.comentarios
    assert model.data_portaria
    assert model.numero_portaria
    assert model.sequencia_de_publicacao
    assert model.sequencia_de_retificacao


def test_str_model(ata_parecer_tecnico_t1):
    assert (
        ata_parecer_tecnico_t1.__str__()
        == f"<DRE: {ata_parecer_tecnico_t1.dre} Periodo: {ata_parecer_tecnico_t1.periodo}>"
    )


def test_admin():
    assert admin.site._registry[AtaParecerTecnico]


def test_portaria_publicada_anterior_data_corte(ata_parecer_tecnico_t1):
    ata_parecer_tecnico_t1.DATA_CORTE_PORTARIA = date(2026, 8, 19)
    ata_parecer_tecnico_t1.criado_em = timezone.make_aware(datetime(2026, 8, 18))
    ata_parecer_tecnico_t1.data_portaria = date(2026, 8, 10)

    assert ata_parecer_tecnico_t1.portaria_publicada() == "de 10/08/2026"


def test_portaria_publicada_data_corte_ou_posterior(ata_parecer_tecnico_t1):
    ata_parecer_tecnico_t1.DATA_CORTE_PORTARIA = date(2026, 8, 19)
    ata_parecer_tecnico_t1.criado_em = timezone.make_aware(datetime(2026, 8, 19))
    ata_parecer_tecnico_t1.data_portaria = date(2026, 8, 10)

    assert ata_parecer_tecnico_t1.portaria_publicada() == "publicada em 10/08/2026"


def test_portaria_publicada_sem_data_portaria(ata_parecer_tecnico_t1):
    ata_parecer_tecnico_t1.data_portaria = None

    assert ata_parecer_tecnico_t1.portaria_publicada() == ""
