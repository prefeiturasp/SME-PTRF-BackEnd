import pytest
from django.db.utils import IntegrityError
from decimal import Decimal
from sme_ptrf_apps.paa.models import ReplicaPaa


@pytest.mark.django_db
def test_criar_replica_paa(paa_factory):
    paa = paa_factory()

    historico = {
        "texto_introducao": "Intro",
        "texto_conclusao": "Conclusão",
        "objetivos": [],
        "receitas_ptrf": [],
        "receitas_pdde": [],
        "receitas_outros_recursos": [],
        "prioridades": []
    }

    replica = ReplicaPaa.objects.create(
        paa=paa,
        historico=historico
    )

    assert replica.id is not None
    assert replica.paa == paa
    assert replica.historico == historico


@pytest.mark.django_db
def test_str_replica_paa(paa_factory):
    paa = paa_factory()

    replica = ReplicaPaa.objects.create(
        paa=paa,
        historico={}
    )

    expected = f"Réplica do PAA {paa.periodo_paa.referencia} ({paa.associacao})"

    assert str(replica) == expected


@pytest.mark.django_db
def test_one_to_one_nao_permite_duplicidade(paa_factory):
    paa = paa_factory()

    ReplicaPaa.objects.create(
        paa=paa,
        historico={}
    )

    with pytest.raises(IntegrityError):
        ReplicaPaa.objects.create(
            paa=paa,
            historico={}
        )


@pytest.mark.django_db
def test_jsonfield_aceita_estrutura_complexa(paa_factory):
    paa = paa_factory()

    historico = {
        "texto_introducao": "Intro",
        "objetivos": [
            {"nome": "Objetivo 1"},
            {"nome": "Objetivo 2"}
        ],
        "receitas_ptrf": [
            {"valor": 1000.50}
        ],
        "prioridades": [
            {"descricao": "Alta"}
        ]
    }

    replica = ReplicaPaa.objects.create(
        paa=paa,
        historico=historico
    )

    replica.refresh_from_db()

    assert replica.historico["objetivos"][0]["nome"] == "Objetivo 1"
    assert replica.historico["receitas_ptrf"][0]["valor"] == Decimal(1000.50)


@pytest.mark.django_db
def test_relacionamento_reverse(paa_factory):
    paa = paa_factory()

    replica = ReplicaPaa.objects.create(
        paa=paa,
        historico={}
    )

    assert paa.replica == replica
