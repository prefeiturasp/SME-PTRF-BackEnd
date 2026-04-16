from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory

from sme_ptrf_apps.dre.fixtures.factories.ata_parecer_tecnico_factory import AtaParecerTecnicoFactory
from sme_ptrf_apps.dre.models import AtaParecerTecnicoSnapshot


class AtaParecerTecnicoSnapshotFactory(DjangoModelFactory):
    class Meta:
        model = AtaParecerTecnicoSnapshot

    ata = SubFactory(AtaParecerTecnicoFactory)
    dados = {
        "cabecalho": {"titulo": "PTRF"},
        "aprovadas": {"contas": []},
        "aprovadas_ressalva": {"contas": [], "motivos": []},
        "reprovadas": {"contas": [], "motivos": []},
    }
    schema_version = 1
    origem = AtaParecerTecnicoSnapshot.ORIGEM_PUBLICACAO
    hash_dados = Sequence(lambda n: f"hash-{n}")
