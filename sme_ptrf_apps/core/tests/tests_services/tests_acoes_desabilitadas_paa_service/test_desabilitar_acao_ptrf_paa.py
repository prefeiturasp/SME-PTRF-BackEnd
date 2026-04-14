import pytest

from sme_ptrf_apps.core.services.acoes_desabilitadas_paa import desabilitar_acao_ptrf_paa
from sme_ptrf_apps.paa.enums import PaaStatusEnum, RecursoOpcoesEnum

pytestmark = pytest.mark.django_db


@pytest.fixture
def acao_habilitada(acao_factory):
    """Ação com exibir_paa=True (habilitada)."""
    return acao_factory.create(exibir_paa=True)


@pytest.fixture
def acao_desabilitada(acao_factory):
    """Ação com exibir_paa=False (desabilitada)."""
    return acao_factory.create(exibir_paa=False)


@pytest.fixture
def paa_em_elaboracao(paa_factory, periodo_paa_factory, associacao):
    periodo_paa = periodo_paa_factory.create()
    return paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.EM_ELABORACAO.name, associacao=associacao)


@pytest.fixture
def acao_associacao_habilitada(acao_associacao_factory, associacao, acao_habilitada):
    return acao_associacao_factory.create(associacao=associacao, acao=acao_habilitada)


@pytest.fixture
def acao_associacao_desabilitada(acao_associacao_factory, associacao, acao_desabilitada):
    return acao_associacao_factory.create(associacao=associacao, acao=acao_desabilitada)


@pytest.fixture
def prioridade_paa_vinculada(prioridade_paa_factory, paa_em_elaboracao, acao_associacao_desabilitada):
    return prioridade_paa_factory.create(
        paa=paa_em_elaboracao,
        acao_associacao=acao_associacao_desabilitada,
        recurso=RecursoOpcoesEnum.PTRF.name,
    )


@pytest.fixture
def receita_prevista_paa_vinculada(receita_prevista_paa_factory, paa_em_elaboracao, acao_associacao_desabilitada):
    return receita_prevista_paa_factory.create(
        paa=paa_em_elaboracao,
        acao_associacao=acao_associacao_desabilitada,
    )


# ---------------------------------------------------------------------------
# Testes — ação habilitada (exibir_paa=True)
# ---------------------------------------------------------------------------

def test_retorna_acao_quando_exibir_paa_true(acao_habilitada):
    resultado = desabilitar_acao_ptrf_paa(acao_habilitada)

    assert resultado == acao_habilitada


def test_nao_altera_prioridades_quando_acao_habilitada(
    acao_habilitada, acao_associacao_habilitada, paa_em_elaboracao, prioridade_paa_factory
):
    prioridade = prioridade_paa_factory.create(
        paa=paa_em_elaboracao,
        acao_associacao=acao_associacao_habilitada,
        recurso=RecursoOpcoesEnum.PTRF.name,
    )

    desabilitar_acao_ptrf_paa(acao_habilitada)

    prioridade.refresh_from_db()
    assert prioridade.acao_associacao == acao_associacao_habilitada


def test_nao_exclui_receitas_quando_acao_habilitada(
    acao_habilitada, acao_associacao_habilitada, paa_em_elaboracao, receita_prevista_paa_factory
):
    from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa

    receita = receita_prevista_paa_factory.create(
        paa=paa_em_elaboracao,
        acao_associacao=acao_associacao_habilitada,
    )

    desabilitar_acao_ptrf_paa(acao_habilitada)

    assert ReceitaPrevistaPaa.objects.filter(pk=receita.pk).exists()


# ---------------------------------------------------------------------------
# Testes — ação desabilitada (exibir_paa=False)
# ---------------------------------------------------------------------------

def test_retorna_acao_quando_exibir_paa_false(acao_desabilitada):
    resultado = desabilitar_acao_ptrf_paa(acao_desabilitada)

    assert resultado == acao_desabilitada


def test_limpa_acao_associacao_nas_prioridades_em_elaboracao(
    acao_desabilitada, prioridade_paa_vinculada
):
    desabilitar_acao_ptrf_paa(acao_desabilitada)

    prioridade_paa_vinculada.refresh_from_db()
    assert prioridade_paa_vinculada.acao_associacao is None


def test_exclui_receitas_previstas_em_elaboracao(
    acao_desabilitada, receita_prevista_paa_vinculada
):
    from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa

    pk = receita_prevista_paa_vinculada.pk
    desabilitar_acao_ptrf_paa(acao_desabilitada)

    assert not ReceitaPrevistaPaa.objects.filter(pk=pk).exists()


def test_nao_altera_prioridades_de_paa_nao_em_elaboracao(
    acao_desabilitada, acao_associacao_desabilitada,
    paa_factory, periodo_paa_factory, prioridade_paa_factory,
    documento_paa_factory, ata_paa_factory
):
    from sme_ptrf_apps.paa.models import DocumentoPaa, AtaPaa

    periodo_paa = periodo_paa_factory.create()
    paa_gerado = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.GERADO.name)
    documento_paa_factory.create(
        paa=paa_gerado,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
    ata_paa_factory.create(paa=paa_gerado, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)
    prioridade = prioridade_paa_factory.create(
        paa=paa_gerado,
        acao_associacao=acao_associacao_desabilitada,
        recurso=RecursoOpcoesEnum.PTRF.name,
    )

    desabilitar_acao_ptrf_paa(acao_desabilitada)

    prioridade.refresh_from_db()
    assert prioridade.acao_associacao == acao_associacao_desabilitada


def test_nao_exclui_receitas_de_paa_nao_em_elaboracao(
    acao_desabilitada, acao_associacao_desabilitada,
    paa_factory, periodo_paa_factory, receita_prevista_paa_factory,
    documento_paa_factory, ata_paa_factory
):
    from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa, DocumentoPaa, AtaPaa

    periodo_paa = periodo_paa_factory.create()
    paa_gerado = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.GERADO.name)
    documento_paa_factory.create(
        paa=paa_gerado,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
    ata_paa_factory.create(paa=paa_gerado, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)
    receita = receita_prevista_paa_factory.create(
        paa=paa_gerado,
        acao_associacao=acao_associacao_desabilitada,
    )

    desabilitar_acao_ptrf_paa(acao_desabilitada)

    assert ReceitaPrevistaPaa.objects.filter(pk=receita.pk).exists()


def test_nao_afeta_prioridades_de_outra_acao(
    acao_desabilitada, paa_em_elaboracao,
    acao_associacao_factory, prioridade_paa_factory
):
    outra_acao_associacao = acao_associacao_factory.create()
    prioridade_outra = prioridade_paa_factory.create(
        paa=paa_em_elaboracao,
        acao_associacao=outra_acao_associacao,
        recurso=RecursoOpcoesEnum.PTRF.name,
    )

    desabilitar_acao_ptrf_paa(acao_desabilitada)

    prioridade_outra.refresh_from_db()
    assert prioridade_outra.acao_associacao == outra_acao_associacao


def test_nao_exclui_receitas_de_outra_acao(
    acao_desabilitada, paa_em_elaboracao,
    acao_associacao_factory, receita_prevista_paa_factory
):
    from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa

    outra_acao_associacao = acao_associacao_factory.create()
    receita_outra = receita_prevista_paa_factory.create(
        paa=paa_em_elaboracao,
        acao_associacao=outra_acao_associacao,
    )

    desabilitar_acao_ptrf_paa(acao_desabilitada)

    assert ReceitaPrevistaPaa.objects.filter(pk=receita_outra.pk).exists()


def test_sem_prioridades_nem_receitas_nao_levanta_excecao(acao_desabilitada):
    resultado = desabilitar_acao_ptrf_paa(acao_desabilitada)

    assert resultado == acao_desabilitada


def test_multiplas_prioridades_sao_todas_limpas(
    acao_desabilitada, acao_associacao_desabilitada,
    paa_em_elaboracao, prioridade_paa_factory
):
    prioridades = [
        prioridade_paa_factory.create(
            paa=paa_em_elaboracao,
            acao_associacao=acao_associacao_desabilitada,
            recurso=RecursoOpcoesEnum.PTRF.name,
        )
        for _ in range(3)
    ]

    desabilitar_acao_ptrf_paa(acao_desabilitada)

    for p in prioridades:
        p.refresh_from_db()
        assert p.acao_associacao is None


def test_multiplas_receitas_sao_todas_excluidas(
    acao_desabilitada,
    paa_factory, periodo_paa_factory,
    acao_associacao_factory, receita_prevista_paa_factory
):
    from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa

    # Cada receita prevista exige (paa, acao_associacao) único — usamos PAAs distintos
    pks = []
    for _ in range(3):
        periodo_paa = periodo_paa_factory.create()
        paa = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.EM_ELABORACAO.name)
        acao_associacao = acao_associacao_factory.create(acao=acao_desabilitada)
        receita = receita_prevista_paa_factory.create(paa=paa, acao_associacao=acao_associacao)
        pks.append(receita.pk)

    desabilitar_acao_ptrf_paa(acao_desabilitada)

    assert ReceitaPrevistaPaa.objects.filter(pk__in=pks).count() == 0
