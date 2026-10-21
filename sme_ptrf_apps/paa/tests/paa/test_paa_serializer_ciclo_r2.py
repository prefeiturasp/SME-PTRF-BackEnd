import pytest

from sme_ptrf_apps.paa.api.serializers import PaaSerializer
from sme_ptrf_apps.paa.models import AtaPaa, DocumentoPaa

pytestmark = pytest.mark.django_db

FINAL = DocumentoPaa.VersaoChoices.FINAL
CONCLUIDO = DocumentoPaa.StatusChoices.CONCLUIDO
EM_PROCESSAMENTO = DocumentoPaa.StatusChoices.EM_PROCESSAMENTO


def _paa_em_retificacao(paa_factory):
    paa = paa_factory()
    paa.set_paa_status_em_retificacao()
    return paa


def _serializer():
    return PaaSerializer()


# get_tem_documento_final_concluido — comportamento cycle-aware
class TestGetTemDocumentoFinalConcluidoCicloAware:
    """
    Verifica que get_tem_documento_final_concluido distingue documentos do ciclo
    atual vs. ciclos anteriores quando o PAA está em retificação.
    """

    def test_retorna_false_sem_documento_de_retificacao(self, paa_factory, replica_paa_factory):
        """PAA em retificação sem nenhum doc retificado → False."""
        paa = _paa_em_retificacao(paa_factory)
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': None, 'versao_documento': None}},
        )
        assert _serializer().get_tem_documento_final_concluido(paa) is False

    def test_retorna_false_quando_doc_pertence_ao_ciclo_anterior(
        self, paa_factory, documento_paa_factory, replica_paa_factory
    ):
        """UUID do doc == UUID no snapshot → doc de R1 durante R2 → False."""
        paa = _paa_em_retificacao(paa_factory)
        doc_r1 = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=1
        )
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': str(doc_r1.uuid), 'versao_documento': 1}},
        )
        assert _serializer().get_tem_documento_final_concluido(paa) is False

    def test_retorna_true_quando_doc_pertence_ao_ciclo_atual(
        self, paa_factory, documento_paa_factory, replica_paa_factory
    ):
        """UUID do doc ≠ UUID no snapshot → doc de R2 gerado → True."""
        paa = _paa_em_retificacao(paa_factory)
        doc_r1 = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=1
        )
        documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=2
        )
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': str(doc_r1.uuid), 'versao_documento': 1}},
        )
        assert _serializer().get_tem_documento_final_concluido(paa) is True

    def test_retorna_true_sem_replica(self, paa_factory, documento_paa_factory):
        """Sem réplica (primeiro ciclo): qualquer doc CONCLUIDO é do ciclo atual → True."""
        paa = _paa_em_retificacao(paa_factory)
        documento_paa_factory(paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO)
        assert _serializer().get_tem_documento_final_concluido(paa) is True

    def test_retorna_false_quando_doc_esta_em_processamento(
        self, paa_factory, documento_paa_factory, replica_paa_factory
    ):
        """Doc EM_PROCESSAMENTO não conta como concluído → False."""
        paa = _paa_em_retificacao(paa_factory)
        documento_paa_factory(paa=paa, retificacao=True, versao=FINAL, status_geracao=EM_PROCESSAMENTO)
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': None, 'versao_documento': None}},
        )
        assert _serializer().get_tem_documento_final_concluido(paa) is False


# get_tem_ata_concluida — comportamento cycle-aware
class TestGetTemAtaConcluidaCicloAware:
    """
    Verifica que get_tem_ata_concluida distingue atas do ciclo atual vs. ciclos
    anteriores quando o PAA está em retificação.
    """

    def _ata_r1_concluida(self, paa, ata_paa_factory):
        return ata_paa_factory(
            paa=paa,
            tipo_ata=AtaPaa.ATA_RETIFICACAO,
            previa=False,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
            pdf_gerado_previamente=True,
        )

    def test_retorna_false_sem_ata_de_retificacao(self, paa_factory, replica_paa_factory):
        """PAA em retificação sem ata de retificação → False."""
        paa = _paa_em_retificacao(paa_factory)
        replica_paa_factory(
            paa=paa,
            historico={'ata_retificada': {'uuid': None}},
        )
        assert _serializer().get_tem_ata_concluida(paa) is False

    def test_retorna_false_quando_ata_pertence_ao_ciclo_anterior(
        self, paa_factory, ata_paa_factory, replica_paa_factory
    ):
        """UUID da ata == UUID no snapshot → ata de R1 durante R2 → False."""
        paa = _paa_em_retificacao(paa_factory)
        ata_r1 = self._ata_r1_concluida(paa, ata_paa_factory)
        replica_paa_factory(
            paa=paa,
            historico={'ata_retificada': {'uuid': str(ata_r1.uuid)}},
        )
        assert _serializer().get_tem_ata_concluida(paa) is False

    def test_retorna_true_quando_ata_pertence_ao_ciclo_atual(
        self, paa_factory, ata_paa_factory, replica_paa_factory
    ):
        """UUID da ata ≠ UUID no snapshot → ata de R2 gerada → True."""
        paa = _paa_em_retificacao(paa_factory)
        ata_r1 = self._ata_r1_concluida(paa, ata_paa_factory)
        # ata_r2 tem pk maior → retornada pelo order_by('-pk')
        self._ata_r1_concluida(paa, ata_paa_factory)
        replica_paa_factory(
            paa=paa,
            historico={'ata_retificada': {'uuid': str(ata_r1.uuid)}},
        )
        assert _serializer().get_tem_ata_concluida(paa) is True

    def test_retorna_true_sem_replica(self, paa_factory, ata_paa_factory):
        """Sem réplica: ata concluída existente é tratada como do ciclo atual → True."""
        paa = _paa_em_retificacao(paa_factory)
        self._ata_r1_concluida(paa, ata_paa_factory)
        assert _serializer().get_tem_ata_concluida(paa) is True

    def test_retorna_false_quando_ata_nao_concluida(
        self, paa_factory, ata_paa_factory, replica_paa_factory
    ):
        """Ata STATUS_NAO_GERADO não conta como concluída → False."""
        paa = _paa_em_retificacao(paa_factory)
        ata_paa_factory(
            paa=paa,
            tipo_ata=AtaPaa.ATA_RETIFICACAO,
            previa=False,
            status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO,
            pdf_gerado_previamente=False,
        )
        replica_paa_factory(
            paa=paa,
            historico={'ata_retificada': {'uuid': None}},
        )
        assert _serializer().get_tem_ata_concluida(paa) is False

    def test_retorna_false_quando_pdf_nao_gerado_previamente(
        self, paa_factory, ata_paa_factory, replica_paa_factory
    ):
        """pdf_gerado_previamente=False desqualifica a ata do filtro → False."""
        paa = _paa_em_retificacao(paa_factory)
        ata_paa_factory(
            paa=paa,
            tipo_ata=AtaPaa.ATA_RETIFICACAO,
            previa=False,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
            pdf_gerado_previamente=False,
        )
        replica_paa_factory(
            paa=paa,
            historico={'ata_retificada': {'uuid': None}},
        )
        assert _serializer().get_tem_ata_concluida(paa) is False
