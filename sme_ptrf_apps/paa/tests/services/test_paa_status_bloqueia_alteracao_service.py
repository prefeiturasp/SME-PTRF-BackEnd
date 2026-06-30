from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.models.ata_paa import AtaPaa
from model_bakery import baker
from datetime import date
from unittest.mock import patch
import pytest

from sme_ptrf_apps.paa.services.paa_status_bloqueia_alteracao_service import (
    PaaStatusBloqueiaAlteracaoException,
    PaaStatusBloqueiaAlteracaoService,
    TipoBloqueioPaa,
)


@pytest.fixture
def paa_em_elaboracao(paa_factory, periodo_paa_factory):
    periodo_paa = periodo_paa_factory.create()
    paa_gerado = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.EM_ELABORACAO.name)
    return paa_gerado


@pytest.fixture
def paa_gerado(paa_factory, periodo_paa_factory):
    periodo_paa = periodo_paa_factory.create()
    paa_gerado = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.GERADO.name)
    return paa_gerado


@pytest.fixture
def especificacao_material():
    return baker.make('EspecificacaoMaterialServico', descricao='Material teste')


@pytest.fixture
def outro_recurso_periodo(periodo_paa_factory, outro_recurso_factory, outro_recurso_periodo_factory):
    periodo_paa = periodo_paa_factory.create(
        referencia='2000.10',
        data_inicial=date(2000, 1, 1),
        data_final=date(2000, 4, 30),
    )
    outro_recurso = outro_recurso_factory.create(nome='Teste 2000')
    return outro_recurso_periodo_factory.create(
        outro_recurso=outro_recurso,
        periodo_paa=periodo_paa,
        ativo=True
    )


class TestChecarStatusGerado:

    def test_nao_deve_lancar_excecao_quando_status_nao_gerado(self, paa_em_elaboracao):
        PaaStatusBloqueiaAlteracaoService.checar_status_gerado(paa_em_elaboracao)

    def test_deve_lancar_excecao_quando_status_gerado(self, paa_gerado):

        with pytest.raises(PaaStatusBloqueiaAlteracaoException) as exc:
            PaaStatusBloqueiaAlteracaoService.checar_status_gerado(paa_gerado)

        assert exc.value.detail == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }


class TestChecarAtaConcluida:

    def test_nao_deve_lancar_excecao_quando_ata_nao_concluida(self, paa_gerado, ata_paa_factory):
        ata_paa_factory.create(
            paa=paa_gerado,
            status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO,
        )

        PaaStatusBloqueiaAlteracaoService.checar_ata_concluida(paa_gerado)

    def test_deve_lancar_excecao_quando_ata_concluida(self, paa_gerado, ata_paa_factory):
        ata_paa_factory.create(
            paa=paa_gerado,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        with pytest.raises(PaaStatusBloqueiaAlteracaoException) as exc:
            PaaStatusBloqueiaAlteracaoService.checar_ata_concluida(paa_gerado)

            assert exc.value.detail == {
                "mensagem": (
                    "A Ata Final do PAA já foi concluida. "
                    "Para realizar alterações, utilize o fluxo de retificação."
                )
            }


class TestChecarAtaConcluidaEmRetificacao:

    def test_nao_levanta_excecao_quando_em_retificacao_sem_ata_concluida(
        self, paa_factory, periodo_paa_factory
    ):
        periodo_paa = periodo_paa_factory.create()
        paa = paa_factory.create(
            periodo_paa=periodo_paa, status=PaaStatusEnum.EM_RETIFICACAO.name
        )
        with patch(
            'sme_ptrf_apps.paa.services.ciclo_retificacao_service.CicloRetificacaoService'
        ) as mock_ciclo:
            mock_ciclo.return_value.tem_ata_concluida = False
            PaaStatusBloqueiaAlteracaoService.checar_ata_concluida(paa)

    def test_levanta_excecao_quando_em_retificacao_com_ata_concluida(
        self, paa_factory, periodo_paa_factory
    ):
        periodo_paa = periodo_paa_factory.create()
        paa = paa_factory.create(
            periodo_paa=periodo_paa, status=PaaStatusEnum.EM_RETIFICACAO.name
        )
        with patch(
            'sme_ptrf_apps.paa.services.ciclo_retificacao_service.CicloRetificacaoService'
        ) as mock_ciclo:
            mock_ciclo.return_value.tem_ata_concluida = True
            with pytest.raises(PaaStatusBloqueiaAlteracaoException) as exc:
                PaaStatusBloqueiaAlteracaoService.checar_ata_concluida(paa)
            assert 'Ata Final' in exc.value.detail['mensagem']


class TestValidarLista:

    def test_nao_deve_lancar_excecao_quando_lista_status_gerado_sem_bloqueio(
        self,
        paa_factory,
        periodo_paa_factory,
    ):
        periodo_paa = periodo_paa_factory.create()
        paa_1 = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.EM_ELABORACAO.name)
        paa_2 = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.EM_ELABORACAO.name)

        PaaStatusBloqueiaAlteracaoService.validar_lista(
            [paa_1, paa_2],
            TipoBloqueioPaa.STATUS_GERADO
        )

    def test_deve_lancar_excecao_quando_algum_paa_status_gerado(
        self,
        paa_factory,
        periodo_paa_factory,
    ):
        periodo_paa = periodo_paa_factory.create()
        paa_1 = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.GERADO.name)
        paa_2 = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.GERADO.name)

        with pytest.raises(PaaStatusBloqueiaAlteracaoException) as exc:
            PaaStatusBloqueiaAlteracaoService.validar_lista(
                [paa_1, paa_2],
                TipoBloqueioPaa.STATUS_GERADO
            )

        assert exc.value.detail == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }

    def test_nao_deve_lancar_excecao_quando_lista_ata_nao_concluida(
        self,
        paa_factory,
        periodo_paa_factory,
        ata_paa_factory
    ):
        periodo_paa = periodo_paa_factory.create()
        paa_1 = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.GERADO.name)
        paa_2 = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.GERADO.name)

        ata_paa_factory.create(
            paa=paa_1,
            status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO,
        )

        ata_paa_factory.create(
            paa=paa_2,
            status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO,
        )

        PaaStatusBloqueiaAlteracaoService.validar_lista(
            [paa_1, paa_2],
            TipoBloqueioPaa.ATA_CONCLUIDA
        )

    def test_deve_lancar_excecao_quando_algum_paa_possui_ata_concluida(
        self,
        paa_factory,
        periodo_paa_factory,
        ata_paa_factory
    ):
        periodo_paa = periodo_paa_factory.create()
        paa_1 = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.GERADO.name)
        paa_2 = paa_factory.create(periodo_paa=periodo_paa, status=PaaStatusEnum.GERADO.name)

        ata_paa_factory.create(
            paa=paa_1,
            status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO,
        )

        ata_paa_factory.create(
            paa=paa_2,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        with pytest.raises(PaaStatusBloqueiaAlteracaoException) as exc:
            PaaStatusBloqueiaAlteracaoService.validar_lista(
                [paa_1, paa_2],
                TipoBloqueioPaa.ATA_CONCLUIDA
            )

        assert exc.value.detail == {
            "mensagem": (
                "A Ata Final do PAA já foi concluida. "
                "Para realizar alterações, utilize o fluxo de retificação."
            )
        }


# Testes de integração
class TestPrioridadesMixinBloqueios():

    def test_nao_deve_criar_prioridade_quando_paa_status_gerado(
        self,
        jwt_authenticated_client_sme,
        paa_gerado,
        especificacao_material,
        acao_associacao,
        flag_paa
    ):

        payload = {
            "paa": str(paa_gerado.uuid),
            "prioridade": 1,
            "recurso": "PTRF",
            "tipo_aplicacao": "CAPITAL",
            "especificacao_material": str(especificacao_material.uuid),
            "acao_associacao": acao_associacao.uuid,
            "valor_total": 0
        }

        response = jwt_authenticated_client_sme.post(
            "/api/prioridades-paa/",
            data=payload,
        )

        assert response.status_code == 400

        assert response.json() == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }

    def test_nao_deve_atualizar_prioridade_quando_paa_status_gerado(
        self,
        jwt_authenticated_client_sme,
        paa_gerado,
        prioridade_paa_factory,
        acao_associacao,
        especificacao_material,
        flag_paa,
    ):

        prioridade = prioridade_paa_factory.create(
            paa=paa_gerado
        )

        payload = {
            "paa": str(paa_gerado.uuid),
            "prioridade": 1,
            "recurso": "PTRF",
            "tipo_aplicacao": "CAPITAL",
            "especificacao_material": str(especificacao_material.uuid),
            "acao_associacao": acao_associacao.uuid,
            "valor_total": 0
        }

        response = jwt_authenticated_client_sme.patch(
            f"/api/prioridades-paa/{str(prioridade.uuid)}/",
            data=payload
        )

        assert response.status_code == 400

        assert response.json() == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }

    def test_nao_deve_excluir_prioridade_quando_paa_status_gerado(
        self,
        jwt_authenticated_client_sme,
        paa_gerado,
        prioridade_paa_factory,
        flag_paa,
    ):

        prioridade = prioridade_paa_factory.create(
            paa=paa_gerado
        )

        response = jwt_authenticated_client_sme.delete(
            f"/api/prioridades-paa/{prioridade.uuid}/"
        )

        assert response.status_code == 400

        assert response.json() == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }


class TestPaaMixinBloqueios:
    """ Este texte considera todos os dados básicas que são feitos: objetivos e atividades estatutarias"""
    def test_nao_deve_atualizar_dados_quando_paa_status_gerado(
        self,
        jwt_authenticated_client_sme,
        paa_gerado,
        flag_paa,
    ):

        payload = {
            "texto_introducao": "<p>teste</p>",
            "texto_conclusao": "<p>teste</p>",
            "objetivos": [],
            "atividades_estatutarias_paa": []
        }

        response = jwt_authenticated_client_sme.patch(
            f"/api/paa/{str(paa_gerado.uuid)}/",
            data=payload
        )

        assert response.status_code == 400

        assert response.json() == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }


class TestReceitasPrevistasPaaBloqueios:

    def test_nao_deve_criar_receita_prevista_quando_paa_gerado(
        self,
        jwt_authenticated_client_sme,
        acao_associacao,
        paa_gerado,
        flag_paa
    ):

        payload = {
            "paa": str(paa_gerado.uuid),
            "acao_associacao": str(acao_associacao.uuid),
            "previsao_valor_capital": 10,
            "previsao_valor_custeio": 0,
            "previsao_valor_livre": 0,
        }

        response = jwt_authenticated_client_sme.post(
            "/api/receitas-previstas-paa/",
            data=payload,
        )

        assert response.status_code == 400

        assert response.json() == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }

    def test_nao_deve_atualizar_receita_prevista_quando_paa_gerado(
        self,
        jwt_authenticated_client_sme,
        receita_prevista_paa_factory,
        acao_associacao,
        paa_gerado,
        flag_paa,
    ):

        receita = receita_prevista_paa_factory.create(
            paa=paa_gerado
        )

        response = jwt_authenticated_client_sme.patch(
            f"/api/receitas-previstas-paa/{receita.uuid}/",
            data={
                "paa": str(paa_gerado.uuid),
                "acao_associacao": str(acao_associacao.uuid),
                "previsao_valor_capital": 100
            },
        )

        assert response.status_code == 400

        assert response.json() == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }


class TestReceitasPrevistasPddePaaBloqueios:

    def test_nao_deve_criar_receita_prevista_pdde_quando_paa_gerado(
        self,
        jwt_authenticated_client_sme,
        paa_gerado,
        acao_pdde_factory,
        flag_paa
    ):

        acao_pdde = acao_pdde_factory.create(status='ATIVA')

        payload = {
            "paa": str(paa_gerado.uuid),
            "acao_pdde": str(acao_pdde.uuid),
            "previsao_valor_capital": 10,
            "previsao_valor_custeio": 0,
            "previsao_valor_livre": 0,
        }

        response = jwt_authenticated_client_sme.post(
            "/api/receitas-previstas-pdde/",
            data=payload,
        )

        assert response.status_code == 400

        assert response.json() == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }

    def test_nao_deve_atualizar_receita_prevista_quando_paa_gerado(
        self,
        jwt_authenticated_client_sme,
        receita_prevista_pdde_factory,
        acao_pdde_factory,
        paa_gerado,
        flag_paa,
    ):
        acao_pdde = acao_pdde_factory.create(status='ATIVA')

        receita = receita_prevista_pdde_factory.create(
            paa=paa_gerado,
            acao_pdde=acao_pdde
        )

        response = jwt_authenticated_client_sme.patch(
            f"/api/receitas-previstas-pdde/{receita.uuid}/",
            data={
                "paa": str(paa_gerado.uuid),
                "acao_pdde": str(acao_pdde.uuid),
                "previsao_valor_capital": 100
            },
        )

        assert response.status_code == 400

        assert response.json() == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }


class TestReceitasRecursosPropriosPaaBloqueios:

    def test_nao_deve_criar_recursos_proprios_quando_paa_gerado(
        self,
        jwt_authenticated_client_sme,
        paa_gerado,
        fonte_recurso_paa_factory,
        associacao,
        flag_paa
    ):

        fonte_recurso = fonte_recurso_paa_factory.create(nome="Fonte recurso 1")

        payload = {
            "paa": str(paa_gerado.uuid),
            "associacao": str(associacao.uuid),
            "fonte_recurso": str(fonte_recurso.uuid),
            "descricao": "teste",
            "data_prevista": "2024-04-04",
            "valor": 0,
        }

        response = jwt_authenticated_client_sme.post(
            "/api/recursos-proprios-paa/",
            data=payload,
        )

        assert response.status_code == 400

        assert response.json() == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }

    def test_nao_deve_atualizar_recursos_proprios_quando_paa_gerado(
        self,
        jwt_authenticated_client_sme,
        recurso_proprio_paa_factory,
        fonte_recurso_paa_factory,
        paa_gerado,
        associacao,
        flag_paa,
    ):
        fonte_recurso = fonte_recurso_paa_factory.create(nome="Fonte recurso 1")

        recurso_proprio = recurso_proprio_paa_factory.create(
            paa=paa_gerado,
            fonte_recurso=fonte_recurso,
            associacao=associacao
        )

        response = jwt_authenticated_client_sme.patch(
            f"/api/recursos-proprios-paa/{recurso_proprio.uuid}/",
            data={
                "paa": str(paa_gerado.uuid),
                "associacao": str(associacao.uuid),
                "descricao": "teste2",
                "data_prevista": "2024-04-05",
                "fonte_recurso": str(fonte_recurso.uuid),
                "valor": 100
            },
        )

        assert response.status_code == 400

        assert response.json() == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }

    def test_nao_deve_excluir_recursos_proprios_quando_paa_gerado(
        self,
        jwt_authenticated_client_sme,
        recurso_proprio_paa_factory,
        fonte_recurso_paa_factory,
        paa_gerado,
        associacao,
        flag_paa,
    ):
        fonte_recurso = fonte_recurso_paa_factory.create(nome="Fonte recurso 1")

        recurso_proprio = recurso_proprio_paa_factory.create(
            paa=paa_gerado,
            fonte_recurso=fonte_recurso,
            associacao=associacao
        )

        response = jwt_authenticated_client_sme.delete(
            f"/api/recursos-proprios-paa/{recurso_proprio.uuid}/",
        )

        assert response.status_code == 400

        assert response.json() == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }


class TestReceitasOutrosRecursosBloqueios:

    def test_nao_deve_criar_outros_recursos_quando_paa_gerado(
        self,
        jwt_authenticated_client_sme,
        paa_gerado,
        outro_recurso_periodo,
        flag_paa
    ):

        payload = {
            "paa": str(paa_gerado.uuid),
            "outro_recurso_periodo": str(outro_recurso_periodo.uuid),
            "saldo_custeio": 0,
            "saldo_capital": 0,
            "saldo_livre": 0,
            "previsao_valor_custeio": 10,
            "previsao_valor_capital": 0,
            "previsao_valor_livre": 0
        }

        response = jwt_authenticated_client_sme.post(
            "/api/receitas-previstas-outros-recursos-periodo/",
            data=payload,
        )

        assert response.status_code == 400

        assert response.json() == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }

    def test_nao_deve_atualizar_outros_recursos_quando_paa_gerado(
        self,
        jwt_authenticated_client_sme,
        outro_recurso_periodo,
        receita_prevista_outro_recurso_periodo_factory,
        paa_gerado,
        flag_paa,
    ):

        receita = receita_prevista_outro_recurso_periodo_factory.create(
            paa=paa_gerado,
            outro_recurso_periodo=outro_recurso_periodo,
        )

        response = jwt_authenticated_client_sme.patch(
            f"/api/receitas-previstas-outros-recursos-periodo/{receita.uuid}/",
            data={
                "paa": str(paa_gerado.uuid),
                "outro_recurso_periodo": str(outro_recurso_periodo.uuid),
                "saldo_custeio": 10,
                "saldo_capital": 10,
                "saldo_livre": 10,
                "previsao_valor_custeio": 10,
                "previsao_valor_capital": 10,
                "previsao_valor_livre": 10
            },
        )

        assert response.status_code == 400

        assert response.json() == {
            "mensagem": (
                "O PAA já foi gerado. Para realizar alterações, "
                "utilize o fluxo de retificação do PAA."
            )
        }


class TestAtaPaaMixinBloqueios:

    def test_nao_deve_atualizar_ata_concluida(
        self,
        jwt_authenticated_client_sme,
        paa_gerado,
        ata_paa_factory,
        flag_paa,
    ):

        ata_paa_concluida = ata_paa_factory.create(
            paa=paa_gerado,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        payload = {
            "data_reuniao": "2026-06-02",
            "local_reuniao": "teste",
            "justificativa": "",
            "presentes_na_ata_paa": [],
            "hora_reuniao": "10:10",
        }

        response = jwt_authenticated_client_sme.patch(
            f"/api/atas-paa/{str(ata_paa_concluida.uuid)}/",
            data=payload
        )

        assert response.status_code == 400

        assert response.json() == {
            "mensagem": (
                'A Ata Final do PAA já foi concluida. '
                'Para realizar alterações, utilize o fluxo de retificação.'
            )
        }
