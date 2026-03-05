import pytest
from django.contrib import admin

from ...models import Acao
from sme_ptrf_apps.paa.enums import PaaStatusEnum, RecursoOpcoesEnum
from sme_ptrf_apps.paa.models import AtaPaa, DocumentoPaa

pytestmark = pytest.mark.django_db


def test_instance_model(acao):
    model = acao
    assert isinstance(model, Acao)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.posicao_nas_pesquisas
    assert not model.e_recursos_proprios


def test_srt_model(acao):
    assert acao.__str__() == 'PTRF'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Acao]


def test_receitas_previstas_paa_em_elaboracao_acao_ptrf_retorna_receitas_vinculadas(
    acao, acao_associacao, paa_factory, periodo_paa_factory, receita_prevista_paa_factory
):
    periodo_paa = periodo_paa_factory.create()
    paa = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.EM_ELABORACAO.name)
    receita_prevista_paa_factory.create(paa=paa, acao_associacao=acao_associacao)

    resultado = acao.receitas_previstas_paa_em_elaboracao_acao_ptrf()

    assert resultado.count() == 1


def test_receitas_previstas_paa_em_elaboracao_acao_ptrf_nao_retorna_quando_paa_gerado(
    acao, acao_associacao, paa_factory, periodo_paa_factory, receita_prevista_paa_factory,
    documento_paa_factory, ata_paa_factory
):
    periodo_paa = periodo_paa_factory.create()
    paa = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.GERADO.name)
    receita_prevista_paa_factory.create(paa=paa, acao_associacao=acao_associacao)
    documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
    ata_paa_factory.create(
        paa=paa,
        status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
    )

    resultado = acao.receitas_previstas_paa_em_elaboracao_acao_ptrf()

    assert resultado.count() == 0


def test_receitas_previstas_paa_em_elaboracao_acao_ptrf_nao_retorna_receitas_de_outra_acao(
    acao, paa_factory, periodo_paa_factory, receita_prevista_paa_factory, acao_associacao_factory
):
    outra_acao_associacao = acao_associacao_factory.create()
    periodo_paa = periodo_paa_factory.create()
    paa = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.EM_ELABORACAO.name)
    receita_prevista_paa_factory.create(paa=paa, acao_associacao=outra_acao_associacao)

    resultado = acao.receitas_previstas_paa_em_elaboracao_acao_ptrf()

    assert resultado.count() == 0


def test_receitas_previstas_paa_em_elaboracao_acao_ptrf_retorna_queryset_vazio_sem_receitas(acao):
    resultado = acao.receitas_previstas_paa_em_elaboracao_acao_ptrf()

    assert resultado.count() == 0


def test_prioridades_paa_em_elaboracao_acao_ptrf_retorna_prioridades_vinculadas(
    acao, acao_associacao, paa_factory, periodo_paa_factory, prioridade_paa_factory
):
    periodo_paa = periodo_paa_factory.create()
    paa = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.EM_ELABORACAO.name)
    prioridade_paa_factory.create(paa=paa, acao_associacao=acao_associacao, recurso=RecursoOpcoesEnum.PTRF.name)

    resultado = acao.prioridades_paa_em_elaboracao_acao_ptrf()

    assert resultado.count() == 1


def test_prioridades_paa_em_elaboracao_acao_ptrf_nao_retorna_quando_paa_gerado(
    acao, acao_associacao, paa_factory, periodo_paa_factory, prioridade_paa_factory,
    documento_paa_factory, ata_paa_factory
):
    periodo_paa = periodo_paa_factory.create()
    paa = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.GERADO.name)
    prioridade_paa_factory.create(paa=paa, acao_associacao=acao_associacao, recurso=RecursoOpcoesEnum.PTRF.name)
    documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
    ata_paa_factory.create(
        paa=paa,
        status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
    )

    resultado = acao.prioridades_paa_em_elaboracao_acao_ptrf()

    assert resultado.count() == 0


def test_prioridades_paa_em_elaboracao_acao_ptrf_nao_retorna_quando_recurso_nao_ptrf(
    acao, acao_associacao, paa_factory, periodo_paa_factory, prioridade_paa_factory
):
    periodo_paa = periodo_paa_factory.create()
    paa = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.EM_ELABORACAO.name)
    prioridade_paa_factory.create(paa=paa, acao_associacao=acao_associacao, recurso=RecursoOpcoesEnum.PDDE.name)

    resultado = acao.prioridades_paa_em_elaboracao_acao_ptrf()

    assert resultado.count() == 0


def test_prioridades_paa_em_elaboracao_acao_ptrf_nao_retorna_prioridades_de_outra_acao(
    acao, paa_factory, periodo_paa_factory, prioridade_paa_factory, acao_associacao_factory, ata_paa_factory
):
    outra_acao_associacao = acao_associacao_factory.create()
    periodo_paa = periodo_paa_factory.create()
    paa = paa_factory.create(
        periodo_paa=periodo_paa,
        status=PaaStatusEnum.EM_ELABORACAO.name
    )
    prioridade_paa_factory.create(paa=paa, acao_associacao=outra_acao_associacao, recurso=RecursoOpcoesEnum.PTRF.name)

    resultado = acao.prioridades_paa_em_elaboracao_acao_ptrf()

    assert resultado.count() == 0


def test_prioridades_paa_em_elaboracao_acao_ptrf_retorna_queryset_vazio_sem_prioridades(acao):
    resultado = acao.prioridades_paa_em_elaboracao_acao_ptrf()

    assert resultado.count() == 0
