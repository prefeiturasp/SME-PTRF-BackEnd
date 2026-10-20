from datetime import date

import pytest
from freezegun import freeze_time

from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.mandatos.fixtures.factories.ocupante_cargo_factory import OcupanteCargoFactory
from sme_ptrf_apps.mandatos.models import ComposicaoVacancia, CargoComposicaoVacancia, OcupanteCargo

pytestmark = pytest.mark.django_db


@freeze_time('2025-12-01 10:20:00')
def test_solicitacao_migracao_vacancia_unidade(
    settings,
    mandato_2023_a_2025__teste_solicitacao_de_migracao,
    solicitacao_de_migracao_eol_unidade_teste_service,
    membro_associacao_teste_solicitacao_de_migracao,
    unidade_teste_solicitacao_de_migracao,
    associacao_teste_solicitacao_de_migracao,
):
    """Migra uma única unidade (por código EOL) para a v2 (ComposicaoVacancia).

    Verifica que a task cria a ComposicaoVacancia, o CargoComposicaoVacancia e o OcupanteCargo
    equivalentes ao MembroAssociacao legado, e marca a associação como migrada.
    """
    from sme_ptrf_apps.mandatos.tasks import solicitacao_de_migracao_vacancia_async

    assert not associacao_teste_solicitacao_de_migracao.migrada_para_historico_de_membros
    assert not ComposicaoVacancia.objects.filter(associacao=associacao_teste_solicitacao_de_migracao).exists()
    assert not CargoComposicaoVacancia.objects.all().exists()
    assert not OcupanteCargo.objects.all().exists()

    settings.CELERY_TASK_ALWAYS_EAGER = True

    solicitacao_de_migracao_vacancia_async.apply_async(
        (
            solicitacao_de_migracao_eol_unidade_teste_service.uuid,
            solicitacao_de_migracao_eol_unidade_teste_service.eol_unidade.codigo_eol,
            None,
        ), countdown=1
    )

    # Seta a associacao como migrada
    associacao = Associacao.objects.get(uuid=associacao_teste_solicitacao_de_migracao.uuid)
    assert associacao.migrada_para_historico_de_membros

    # Cria a Composição Vacância
    composicao = ComposicaoVacancia.objects.get(associacao=associacao_teste_solicitacao_de_migracao)

    # Cria o Cargo Composição Vacância
    cargo_composicao = CargoComposicaoVacancia.objects.get(composicao=composicao)
    assert cargo_composicao.cargo_associacao == "VOGAL_1"
    assert cargo_composicao.data_inicio_no_cargo == mandato_2023_a_2025__teste_solicitacao_de_migracao.data_inicial

    # Cria o Ocupante do Cargo
    ocupante_do_cargo = OcupanteCargo.objects.get(nome="Jose Testando Solicitação de Migração")
    assert ocupante_do_cargo.representacao == membro_associacao_teste_solicitacao_de_migracao.representacao
    assert ocupante_do_cargo.cargo_educacao == membro_associacao_teste_solicitacao_de_migracao.cargo_educacao
    assert ocupante_do_cargo.cpf_responsavel == membro_associacao_teste_solicitacao_de_migracao.cpf


@freeze_time('2025-12-01 10:20:00')
def test_solicitacao_migracao_vacancia_dre(
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
    """ Migra todas as unidades de uma DRE para a v2. """
    from sme_ptrf_apps.mandatos.tasks import solicitacao_de_migracao_vacancia_async

    settings.CELERY_TASK_ALWAYS_EAGER = True

    solicitacao_de_migracao_vacancia_async.apply_async(
        (
            solicitacao_de_migracao_dre_teste_service.uuid,
            None,
            dre_teste_solicitacao_de_migracao.codigo_eol,
        ), countdown=1
    )

    qs = Associacao.objects.filter(unidade__dre=dre_teste_solicitacao_de_migracao)
    assert qs.count() == 2

    for associacao in qs:
        associacao_migrada = Associacao.objects.get(uuid=associacao.uuid)
        assert associacao_migrada.migrada_para_historico_de_membros

        composicao = ComposicaoVacancia.objects.get(associacao=associacao)
        assert CargoComposicaoVacancia.objects.filter(composicao=composicao).exists()


@freeze_time('2025-12-01 10:20:00')
def test_solicitacao_migracao_vacancia_todas_as_unidades(
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
    """ Migra todas as associações do sistema para a v2, sem filtro de unidade/DRE. """
    from sme_ptrf_apps.mandatos.tasks import solicitacao_de_migracao_vacancia_async

    settings.CELERY_TASK_ALWAYS_EAGER = True

    solicitacao_de_migracao_vacancia_async.apply_async(
        (
            solicitacao_de_migracao_todas_as_unidades_teste_service.uuid,
            None,
            None,
        ), countdown=1
    )

    qs = Associacao.objects.all()

    for associacao in qs:
        associacao_migrada = Associacao.objects.get(uuid=associacao.uuid)
        assert associacao_migrada.migrada_para_historico_de_membros

        composicao = ComposicaoVacancia.objects.get(associacao=associacao)
        assert CargoComposicaoVacancia.objects.filter(composicao=composicao).exists()


@freeze_time('2025-12-01 10:20:00')
def test_solicitacao_migracao_vacancia_reaproveita_composicao_existente(
    settings,
    mandato_2023_a_2025__teste_solicitacao_de_migracao,
    solicitacao_de_migracao_eol_unidade_teste_service,
    membro_associacao_teste_solicitacao_de_migracao,
    unidade_teste_solicitacao_de_migracao,
    associacao_teste_solicitacao_de_migracao,
):
    """ Garante que a migração reaproveita a ComposicaoVacancia já existente, em vez de recriá-la. """
    from sme_ptrf_apps.mandatos.services import ServicoHistoricoCargoComposicao
    from sme_ptrf_apps.mandatos.services.mandato_vacancia_service import ServicoMandatoVigenteVacancia
    from sme_ptrf_apps.mandatos.tasks import solicitacao_de_migracao_vacancia_async

    mandato_vigente = ServicoMandatoVigenteVacancia().get_mandato_vigente()
    composicao_pre_existente = ServicoHistoricoCargoComposicao.get_or_create_composicao_vacancia(
        associacao=associacao_teste_solicitacao_de_migracao,
        mandato=mandato_vigente,
    )

    settings.CELERY_TASK_ALWAYS_EAGER = True

    solicitacao_de_migracao_vacancia_async.apply_async(
        (
            solicitacao_de_migracao_eol_unidade_teste_service.uuid,
            solicitacao_de_migracao_eol_unidade_teste_service.eol_unidade.codigo_eol,
            None,
        ), countdown=1
    )

    composicao_apos_migracao = ComposicaoVacancia.objects.get(associacao=associacao_teste_solicitacao_de_migracao)
    assert composicao_apos_migracao.uuid == composicao_pre_existente.uuid


@freeze_time('2025-12-01 10:20:00')
def test_solicitacao_migracao_vacancia_retira_ocupante_com_substituicao_direta_pre_existente(
    settings,
    mandato_2023_a_2025__teste_solicitacao_de_migracao,
    solicitacao_de_migracao_eol_unidade_teste_service,
    membro_associacao_teste_solicitacao_de_migracao,
    unidade_teste_solicitacao_de_migracao,
    associacao_teste_solicitacao_de_migracao,
):
    """Regressão: re-migrar uma associação com substituição direta não pode falhar com ProtectedError.

    `substituido_por` é `PROTECT` - excluir os `CargoComposicaoVacancia` da composição em lote
    (`.delete()` direto) falha sempre que existe uma substituição direta, porque o registro
    substituído ainda é referenciado pelo registro substituto. A retirada dos ocupantes precisa
    passar pelo fluxo normal de cancelamento (`cancelar_entrada`/`cancelar_saida`), que desfaz o
    vínculo antes de remover.

    Args:
        settings: fixture do pytest-django, usada para ligar `CELERY_TASK_ALWAYS_EAGER`.
        mandato_2023_a_2025__teste_solicitacao_de_migracao: mandato vigente usado como destino.
        solicitacao_de_migracao_eol_unidade_teste_service: SolicitacaoDeMigracao filtrada por
            código EOL de uma única unidade.
        membro_associacao_teste_solicitacao_de_migracao: membro legado a ser migrado (cargo
            VOGAL_1) - usado pra recriar o mesmo cargo após a retirada.
        unidade_teste_solicitacao_de_migracao: unidade da associação a ser migrada.
        associacao_teste_solicitacao_de_migracao: associação alvo, com uma substituição direta
            pré-existente no cargo VOGAL_1 antes da migração rodar.
    """
    from sme_ptrf_apps.mandatos.services import ServicoHistoricoCargoComposicao
    from sme_ptrf_apps.mandatos.services.mandato_vacancia_service import ServicoMandatoVigenteVacancia
    from sme_ptrf_apps.mandatos.tasks import solicitacao_de_migracao_vacancia_async

    mandato_vigente = ServicoMandatoVigenteVacancia().get_mandato_vigente()
    composicao_vigente = ServicoHistoricoCargoComposicao.get_or_create_composicao_vacancia(
        associacao=associacao_teste_solicitacao_de_migracao,
        mandato=mandato_vigente,
    )

    # Simula o resultado de uma migração anterior com substituição direta: Antigo (substituído)
    # -> Sucessor (vigente), ambos no mesmo cargo do membro legado (VOGAL_1).
    antigo = CargoComposicaoVacancia.objects.create(
        composicao=composicao_vigente,
        ocupante_do_cargo=OcupanteCargoFactory(nome='Antigo Ocupante'),
        cargo_associacao='VOGAL_1',
        data_inicio_no_cargo=mandato_vigente.data_inicial,
        data_fim_no_cargo=date(2024, 6, 30),
    )
    sucessor = CargoComposicaoVacancia.objects.create(
        composicao=composicao_vigente,
        ocupante_do_cargo=OcupanteCargoFactory(nome='Sucessor Ocupante'),
        cargo_associacao='VOGAL_1',
        data_inicio_no_cargo=date(2024, 7, 1),
        data_fim_no_cargo=mandato_vigente.data_final,
    )
    antigo.substituido_por = sucessor
    antigo.save()

    settings.CELERY_TASK_ALWAYS_EAGER = True

    solicitacao_de_migracao_vacancia_async.apply_async(
        (
            solicitacao_de_migracao_eol_unidade_teste_service.uuid,
            solicitacao_de_migracao_eol_unidade_teste_service.eol_unidade.codigo_eol,
            None,
        ), countdown=1
    )

    solicitacao = solicitacao_de_migracao_eol_unidade_teste_service
    solicitacao.refresh_from_db()
    assert solicitacao.status_processamento == 'SUCESSO', solicitacao.log_execucao

    assert not CargoComposicaoVacancia.objects.filter(uuid__in=[antigo.uuid, sucessor.uuid]).exists()

    cargo_composicao = CargoComposicaoVacancia.objects.get(composicao=composicao_vigente, cargo_associacao='VOGAL_1')
    assert cargo_composicao.ocupante_do_cargo.nome == 'Jose Testando Solicitação de Migração'
    assert cargo_composicao.data_inicio_no_cargo == mandato_vigente.data_inicial
    assert cargo_composicao.data_fim_no_cargo == mandato_vigente.data_final


@freeze_time('2025-12-01 10:20:00')
def test_solicitacao_migracao_vacancia_falha_sem_mandato_vigente_marca_erro(
    settings,
    solicitacao_de_migracao_eol_unidade_teste_service,
    membro_associacao_teste_solicitacao_de_migracao,
    unidade_teste_solicitacao_de_migracao,
    associacao_teste_solicitacao_de_migracao,
):
    """Garante que uma falha durante a migração é registrada como erro, não propagada sem tratamento. """
    from sme_ptrf_apps.mandatos.models import SolicitacaoDeMigracao, StatusProcessamento
    from sme_ptrf_apps.mandatos.tasks import solicitacao_de_migracao_vacancia_async

    settings.CELERY_TASK_ALWAYS_EAGER = True

    solicitacao_de_migracao_vacancia_async.apply_async(
        (
            solicitacao_de_migracao_eol_unidade_teste_service.uuid,
            solicitacao_de_migracao_eol_unidade_teste_service.eol_unidade.codigo_eol,
            None,
        ), countdown=1
    )

    solicitacao = SolicitacaoDeMigracao.objects.get(uuid=solicitacao_de_migracao_eol_unidade_teste_service.uuid)
    assert solicitacao.status_processamento == StatusProcessamento.ERRO
