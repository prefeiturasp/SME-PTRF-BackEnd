import pytest

from sme_ptrf_apps.core.models import Associacao, MembroAssociacao
from sme_ptrf_apps.mandatos.models import Composicao, CargoComposicao, OcupanteCargo

pytestmark = pytest.mark.django_db


def test_solicitacao_migracao_unidade(
    settings,
    mandato_2023_a_2025__teste_solicitacao_de_migracao,
    solicitacao_de_migracao_eol_unidade_teste_service,
    membro_associacao_teste_solicitacao_de_migracao,
    unidade_teste_solicitacao_de_migracao,
    associacao_teste_solicitacao_de_migracao,
):
    from sme_ptrf_apps.mandatos.tasks import solicitacao_de_migracao_async

    assert not associacao_teste_solicitacao_de_migracao.migrada_para_historico_de_membros
    assert not Composicao.objects.filter(associacao=associacao_teste_solicitacao_de_migracao).exists()
    assert not CargoComposicao.objects.all().exists()
    assert not OcupanteCargo.objects.all().exists()

    settings.CELERY_TASK_ALWAYS_EAGER = True

    solicitacao_de_migracao_async.apply_async(
        (
            solicitacao_de_migracao_eol_unidade_teste_service.uuid,
            solicitacao_de_migracao_eol_unidade_teste_service.eol_unidade.codigo_eol if solicitacao_de_migracao_eol_unidade_teste_service.eol_unidade and solicitacao_de_migracao_eol_unidade_teste_service.eol_unidade.codigo_eol else None,
            solicitacao_de_migracao_eol_unidade_teste_service.dre.codigo_eol if solicitacao_de_migracao_eol_unidade_teste_service.dre and solicitacao_de_migracao_eol_unidade_teste_service.dre.codigo_eol else None,
        ), countdown=1
    )

    # Seta a associacao como migrada
    associacao = Associacao.objects.get(uuid=associacao_teste_solicitacao_de_migracao.uuid)
    assert associacao.migrada_para_historico_de_membros

    # Cria a Composição
    assert Composicao.objects.get(associacao=associacao_teste_solicitacao_de_migracao)

    # Cria o Cargo Composição
    composicao = Composicao.objects.get(associacao=associacao_teste_solicitacao_de_migracao)
    cargo_composicao = CargoComposicao.objects.get(composicao=composicao)
    assert cargo_composicao.cargo_associacao == "VOGAL_1"

    # Cria o Ocupante do Cargo
    ocupante_do_cargo = OcupanteCargo.objects.get(nome="Jose Testando Solicitação de Migração")
    assert ocupante_do_cargo.representacao == membro_associacao_teste_solicitacao_de_migracao.representacao
    assert ocupante_do_cargo.cargo_educacao == membro_associacao_teste_solicitacao_de_migracao.cargo_educacao
    assert ocupante_do_cargo.cpf_responsavel == membro_associacao_teste_solicitacao_de_migracao.cpf


def test_solicitacao_migracao_dre(
    settings,
    mandato_2023_a_2025__teste_solicitacao_de_migracao,
    solicitacao_de_migracao_dre_teste_service,
    membro_associacao_teste_solicitacao_de_migracao,
    membro_associacao_teste_solicitacao_de_migracao_02,
    dre_teste_solicitacao_de_migracao,
    unidade_teste_solicitacao_de_migracao,
    unidade_teste_solicitacao_de_migracao_02,
    associacao_teste_solicitacao_de_migracao,
    associacao_teste_solicitacao_de_migracao_02,
):
    from sme_ptrf_apps.mandatos.tasks import solicitacao_de_migracao_async

    assert not associacao_teste_solicitacao_de_migracao.migrada_para_historico_de_membros
    assert not associacao_teste_solicitacao_de_migracao_02.migrada_para_historico_de_membros
    assert not Composicao.objects.filter(associacao=associacao_teste_solicitacao_de_migracao).exists()
    assert not Composicao.objects.filter(associacao=associacao_teste_solicitacao_de_migracao_02).exists()
    assert not CargoComposicao.objects.all().exists()
    assert not OcupanteCargo.objects.all().exists()

    settings.CELERY_TASK_ALWAYS_EAGER = True

    solicitacao_de_migracao_async.apply_async(
        (
            solicitacao_de_migracao_dre_teste_service.uuid,
            solicitacao_de_migracao_dre_teste_service.eol_unidade.codigo_eol if solicitacao_de_migracao_dre_teste_service.eol_unidade and solicitacao_de_migracao_dre_teste_service.eol_unidade.codigo_eol else None,
            solicitacao_de_migracao_dre_teste_service.dre.codigo_eol if solicitacao_de_migracao_dre_teste_service.dre and solicitacao_de_migracao_dre_teste_service.dre.codigo_eol else None,
        ), countdown=1
    )

    qs = Associacao.objects.filter(unidade__dre=dre_teste_solicitacao_de_migracao)

    for associacao in qs:
        # Seta a associacao como migrada
        associacao_migrada = Associacao.objects.get(uuid=associacao.uuid)
        assert associacao_migrada.migrada_para_historico_de_membros

        # Cria a Composição
        assert Composicao.objects.get(associacao=associacao)

        # Cria o Cargo Composição
        composicao = Composicao.objects.get(associacao=associacao)
        cargo_composicao = CargoComposicao.objects.get(composicao=composicao)
        assert cargo_composicao

        # Cria o Ocupante do Cargo
        membro_associacao = MembroAssociacao.objects.get(associacao=associacao)
        ocupante_do_cargo = OcupanteCargo.objects.get(nome=membro_associacao.nome)
        assert ocupante_do_cargo.representacao == membro_associacao.representacao
        assert ocupante_do_cargo.cargo_educacao == membro_associacao.cargo_educacao
        assert ocupante_do_cargo.cpf_responsavel == membro_associacao.cpf


def test_solicitacao_migracao_todas_as_unidades(
    settings,
    mandato_2023_a_2025__teste_solicitacao_de_migracao,
    solicitacao_de_migracao_todas_as_unidades_teste_service,
    membro_associacao_teste_solicitacao_de_migracao,
    membro_associacao_teste_solicitacao_de_migracao_02,
    dre_teste_solicitacao_de_migracao,
    unidade_teste_solicitacao_de_migracao,
    unidade_teste_solicitacao_de_migracao_02,
    associacao_teste_solicitacao_de_migracao,
    associacao_teste_solicitacao_de_migracao_02,
):
    from sme_ptrf_apps.mandatos.tasks import solicitacao_de_migracao_async

    assert not associacao_teste_solicitacao_de_migracao.migrada_para_historico_de_membros
    assert not associacao_teste_solicitacao_de_migracao_02.migrada_para_historico_de_membros
    assert not Composicao.objects.filter(associacao=associacao_teste_solicitacao_de_migracao).exists()
    assert not Composicao.objects.filter(associacao=associacao_teste_solicitacao_de_migracao_02).exists()
    assert not CargoComposicao.objects.all().exists()
    assert not OcupanteCargo.objects.all().exists()

    settings.CELERY_TASK_ALWAYS_EAGER = True

    solicitacao_de_migracao_async.apply_async(
        (
            solicitacao_de_migracao_todas_as_unidades_teste_service.uuid,
            solicitacao_de_migracao_todas_as_unidades_teste_service.eol_unidade.codigo_eol if solicitacao_de_migracao_todas_as_unidades_teste_service.eol_unidade and solicitacao_de_migracao_todas_as_unidades_teste_service.eol_unidade.codigo_eol else None,
            solicitacao_de_migracao_todas_as_unidades_teste_service.dre.codigo_eol if solicitacao_de_migracao_todas_as_unidades_teste_service.dre and solicitacao_de_migracao_todas_as_unidades_teste_service.dre.codigo_eol else None,
        ), countdown=1
    )

    qs = Associacao.objects.all()

    for associacao in qs:
        # Seta a associacao como migrada
        associacao_migrada = Associacao.objects.get(uuid=associacao.uuid)
        assert associacao_migrada.migrada_para_historico_de_membros

        # Cria a Composição
        assert Composicao.objects.get(associacao=associacao)

        # Cria o Cargo Composição
        composicao = Composicao.objects.get(associacao=associacao)
        cargo_composicao = CargoComposicao.objects.get(composicao=composicao)
        assert cargo_composicao

        # Cria o Ocupante do Cargo
        membro_associacao = MembroAssociacao.objects.get(associacao=associacao)
        ocupante_do_cargo = OcupanteCargo.objects.get(nome=membro_associacao.nome)
        assert ocupante_do_cargo.representacao == membro_associacao.representacao
        assert ocupante_do_cargo.cargo_educacao == membro_associacao.cargo_educacao
        assert ocupante_do_cargo.cpf_responsavel == membro_associacao.cpf
