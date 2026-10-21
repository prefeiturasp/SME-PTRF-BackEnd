import pytest
from rest_framework import status

from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.models import DocumentoPaa

pytestmark = pytest.mark.django_db

FINAL = DocumentoPaa.VersaoChoices.FINAL
PREVIA = DocumentoPaa.VersaoChoices.PREVIA
CONCLUIDO = DocumentoPaa.StatusChoices.CONCLUIDO
EM_PROCESSAMENTO = DocumentoPaa.StatusChoices.EM_PROCESSAMENTO


def _url(paa):
    return f'/api/paa/{paa.uuid}/status-geracao/'


@pytest.fixture
def paa_elaboracao(paa_factory):
    return paa_factory()


@pytest.fixture
def paa_em_retificacao(paa_factory):
    paa = paa_factory()
    paa.status = PaaStatusEnum.EM_RETIFICACAO.name
    paa.save()
    return paa


# Cenários fora de retificação

class TestStatusGeracaoSemRetificacao:
    """Comportamento do endpoint para PAA em elaboração (sem ciclo de retificação ativo)."""

    def test_retorna_pendente_sem_nenhum_documento(
        self, jwt_authenticated_client_sme, flag_paa, paa_elaboracao
    ):
        response = jwt_authenticated_client_sme.get(_url(paa_elaboracao))

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["mensagem"] == "Documento pendente de geração"

    def test_retorna_preview_quando_em_processamento(
        self, jwt_authenticated_client_sme, flag_paa, paa_elaboracao, documento_paa_factory
    ):
        documento_paa_factory(
            paa=paa_elaboracao,
            versao=PREVIA,
            retificacao=False,
            status_geracao=EM_PROCESSAMENTO,
        )

        response = jwt_authenticated_client_sme.get(_url(paa_elaboracao))
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["versao"] == PREVIA
        assert data["status"] == EM_PROCESSAMENTO
        assert data["retificacao"] is False

    def test_retorna_documento_final_concluido(
        self, jwt_authenticated_client_sme, flag_paa, paa_elaboracao, documento_paa_factory
    ):
        documento_paa_factory(
            paa=paa_elaboracao,
            versao=FINAL,
            retificacao=False,
            status_geracao=CONCLUIDO,
        )

        response = jwt_authenticated_client_sme.get(_url(paa_elaboracao))
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["versao"] == FINAL
        assert data["status"] == CONCLUIDO
        assert data["retificacao"] is False

    def test_preview_tem_prioridade_sobre_final(
        self, jwt_authenticated_client_sme, flag_paa, paa_elaboracao, documento_paa_factory
    ):
        """Quando preview e final existem simultaneamente, o preview é retornado."""
        documento_paa_factory(
            paa=paa_elaboracao,
            versao=PREVIA,
            retificacao=False,
            status_geracao=EM_PROCESSAMENTO,
        )
        documento_paa_factory(
            paa=paa_elaboracao,
            versao=FINAL,
            retificacao=False,
            status_geracao=CONCLUIDO,
        )

        response = jwt_authenticated_client_sme.get(_url(paa_elaboracao))
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["versao"] == PREVIA


# Cenários em retificação (R1)

class TestStatusGeracaoEmRetificacaoR1:
    """Comportamento durante o primeiro ciclo de retificação (R1)."""

    def test_retorna_preview_retificacao_em_processamento(
        self, jwt_authenticated_client_sme, flag_paa, paa_em_retificacao, documento_paa_factory
    ):
        documento_paa_factory(
            paa=paa_em_retificacao,
            versao=PREVIA,
            retificacao=True,
            status_geracao=EM_PROCESSAMENTO,
        )

        response = jwt_authenticated_client_sme.get(_url(paa_em_retificacao))
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["versao"] == PREVIA
        assert data["status"] == EM_PROCESSAMENTO
        assert data["retificacao"] is True

    def test_retorna_documento_final_retificacao_em_processamento(
        self, jwt_authenticated_client_sme, flag_paa, paa_em_retificacao,
        documento_paa_factory, replica_paa_factory
    ):
        """Doc de R1 gerado no ciclo atual (sem snapshot anterior) → retornado."""
        replica_paa_factory(
            paa=paa_em_retificacao,
            historico={'documento_retificado': {'uuid': None, 'versao_documento': None}},
        )
        documento_paa_factory(
            paa=paa_em_retificacao,
            versao=FINAL,
            retificacao=True,
            status_geracao=EM_PROCESSAMENTO,
        )

        response = jwt_authenticated_client_sme.get(_url(paa_em_retificacao))
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["versao"] == FINAL
        assert data["status"] == EM_PROCESSAMENTO
        assert data["retificacao"] is True

    def test_preview_retificacao_nao_e_confundida_com_preview_original(
        self, jwt_authenticated_client_sme, flag_paa, paa_em_retificacao, documento_paa_factory
    ):
        """Preview retificacao=False não é visível quando PAA está em retificação."""
        documento_paa_factory(
            paa=paa_em_retificacao,
            versao=PREVIA,
            retificacao=False,  # preview do PAA original
            status_geracao=CONCLUIDO,
        )

        response = jwt_authenticated_client_sme.get(_url(paa_em_retificacao))

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["mensagem"] == "Documento pendente de geração"


# Cenários de segundo ciclo de retificação (R2)

class TestStatusGeracaoR2:
    """
    Testa o comportamento cycle-aware do endpoint durante R2.

    O banco contém documentos de R1 (retificacao=True FINAL CONCLUIDO).
    A réplica registra o UUID desses documentos no snapshot.
    O endpoint deve reconhecer que esses documentos pertencem ao ciclo anterior
    e retornar 'Documento pendente de geração' até que R2 gere o seu próprio doc.
    """

    @pytest.fixture
    def doc_r1(self, paa_em_retificacao, documento_paa_factory):
        return documento_paa_factory(
            paa=paa_em_retificacao,
            versao=FINAL,
            retificacao=True,
            status_geracao=CONCLUIDO,
            versao_documento=1,
        )

    @pytest.fixture
    def replica_r2(self, paa_em_retificacao, doc_r1, replica_paa_factory):
        return replica_paa_factory(
            paa=paa_em_retificacao,
            historico={
                'documento_retificado': {'uuid': str(doc_r1.uuid), 'versao_documento': 1},
                'ata_retificada': {'uuid': None},
            },
        )

    def test_retorna_pendente_quando_apenas_doc_r1_existe(
        self, jwt_authenticated_client_sme, flag_paa,
        paa_em_retificacao, doc_r1, replica_r2
    ):
        """
        R2 recém-iniciado: banco tem doc de R1 (CONCLUIDO), réplica aponta para ele.
        Antes da correção, o endpoint retornava CONCLUIDO (bug).
        Após a correção, deve retornar 'pendente'.
        """
        response = jwt_authenticated_client_sme.get(_url(paa_em_retificacao))

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["mensagem"] == "Documento pendente de geração"

    def test_retorna_preview_r2_quando_em_processamento(
        self, jwt_authenticated_client_sme, flag_paa,
        paa_em_retificacao, doc_r1, replica_r2, documento_paa_factory
    ):
        """Preview de R2 (retificacao=True PREVIA) deve ser retornada."""
        documento_paa_factory(
            paa=paa_em_retificacao,
            versao=PREVIA,
            retificacao=True,
            status_geracao=EM_PROCESSAMENTO,
            versao_documento=2,
        )

        response = jwt_authenticated_client_sme.get(_url(paa_em_retificacao))
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["versao"] == PREVIA
        assert data["status"] == EM_PROCESSAMENTO
        assert data["retificacao"] is True

    def test_retorna_doc_r2_quando_final_em_processamento(
        self, jwt_authenticated_client_sme, flag_paa,
        paa_em_retificacao, doc_r1, replica_r2, documento_paa_factory
    ):
        """Doc final de R2 EM_PROCESSAMENTO (UUID ≠ snapshot) deve ser retornado."""
        doc_r2 = documento_paa_factory(
            paa=paa_em_retificacao,
            versao=FINAL,
            retificacao=True,
            status_geracao=EM_PROCESSAMENTO,
            versao_documento=2,
        )

        response = jwt_authenticated_client_sme.get(_url(paa_em_retificacao))
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["versao"] == FINAL
        assert data["status"] == EM_PROCESSAMENTO
        assert data["retificacao"] is True
        assert str(doc_r2.uuid) in data["mensagem"] or data["status"] == EM_PROCESSAMENTO
