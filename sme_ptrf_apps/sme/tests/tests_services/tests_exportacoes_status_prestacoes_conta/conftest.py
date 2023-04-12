import datetime
import pytest

from model_bakery import baker

from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta

pytestmark = pytest.mark.django_db

@pytest.fixture
def motivo_aprovacao_ressalva_1():
    return baker.make(
        'MotivoAprovacaoRessalva',
        motivo="Motivo aprovação 1"
    )

@pytest.fixture
def motivo_aprovacao_ressalva_2():
    return baker.make(
        'MotivoAprovacaoRessalva',
        motivo="Motivo aprovação 2"
    )

@pytest.fixture
def motivo_reprovacao_1():
    return baker.make(
        'MotivoReprovacao',
        motivo="Motivo reprovação 1"
    )

@pytest.fixture
def motivo_reprovacao_2():
    return baker.make(
        'MotivoReprovacao',
        motivo="Motivo reprovação 2"
    )

@pytest.fixture
def prestacao_conta_aprovada_com_ressalva(periodo, associacao, motivo_aprovacao_ressalva_1, motivo_aprovacao_ressalva_2):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        recomendacoes="Recomendação teste",
        status='APROVADA_RESSALVA',
        outros_motivos_aprovacao_ressalva='Teste outro motivo aprovação ressalva',
        motivos_aprovacao_ressalva=[motivo_aprovacao_ressalva_1, motivo_aprovacao_ressalva_2],
        criado_em=datetime.date(2020, 1, 1)
    )

@pytest.fixture
def prestacao_conta_reprovada(periodo, outra_associacao, motivo_reprovacao_1, motivo_reprovacao_2):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=outra_associacao,
        status='REPROVADA',
        outros_motivos_reprovacao='Teste outro motivo reprovação',
        motivos_reprovacao=[motivo_reprovacao_1, motivo_reprovacao_2],
        criado_em=datetime.date(2021, 1, 1)
    )

@pytest.fixture
def ambiente():
    return baker.make(
        'Ambiente',
        prefixo='dev-sig-escola',
        nome='Ambiente de desenvolvimento',
    )

@pytest.fixture
def queryset_ordered(prestacao_conta_aprovada_com_ressalva, prestacao_conta_reprovada):
    return PrestacaoConta.objects.all().order_by('criado_em')

