import pytest

from sme_ptrf_apps.paa.api.serializers.renderizador_paa_serializer import RenderizadorPaaBuilder
from sme_ptrf_apps.paa.models import DocumentoPaa

pytestmark = pytest.mark.django_db

FINAL = DocumentoPaa.VersaoChoices.FINAL
CONCLUIDO = DocumentoPaa.StatusChoices.CONCLUIDO
EM_PROCESSAMENTO = DocumentoPaa.StatusChoices.EM_PROCESSAMENTO


def _paa_em_retificacao(paa_factory):
    paa = paa_factory()
    paa.set_paa_status_em_retificacao()
    return paa


def _builder(paa):
    return RenderizadorPaaBuilder(paa)


# _doc_retificacao_ciclo_atual
class TestDocRetificacaoCicloAtual:
    """
    Verifica que _doc_retificacao_ciclo_atual retorna o documento do ciclo corrente
    ou None quando o único doc existente pertence ao ciclo anterior.
    """

    def test_retorna_none_sem_documento(self, paa_factory, replica_paa_factory):
        """Sem nenhum doc retificado → None."""
        paa = _paa_em_retificacao(paa_factory)
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': None, 'versao_documento': None}},
        )
        assert _builder(paa)._doc_retificacao_ciclo_atual() is None

    def test_retorna_none_quando_doc_pertence_ao_ciclo_anterior(
        self, paa_factory, documento_paa_factory, replica_paa_factory
    ):
        """UUID do doc == UUID no snapshot → doc de R1 → None durante R2."""
        paa = _paa_em_retificacao(paa_factory)
        doc_r1 = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=1
        )
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': str(doc_r1.uuid), 'versao_documento': 1}},
        )
        assert _builder(paa)._doc_retificacao_ciclo_atual() is None

    def test_retorna_doc_quando_pertence_ao_ciclo_atual_concluido(
        self, paa_factory, documento_paa_factory, replica_paa_factory
    ):
        """UUID do doc ≠ UUID no snapshot → doc de R2 CONCLUIDO retornado."""
        paa = _paa_em_retificacao(paa_factory)
        doc_r1 = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=1
        )
        doc_r2 = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=2
        )
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': str(doc_r1.uuid), 'versao_documento': 1}},
        )
        result = _builder(paa)._doc_retificacao_ciclo_atual()
        assert result is not None
        assert result.pk == doc_r2.pk

    def test_retorna_doc_quando_pertence_ao_ciclo_atual_em_processamento(
        self, paa_factory, documento_paa_factory, replica_paa_factory
    ):
        """Doc de R2 EM_PROCESSAMENTO (task em andamento) também é retornado."""
        paa = _paa_em_retificacao(paa_factory)
        doc_r1 = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=1
        )
        doc_r2 = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=EM_PROCESSAMENTO, versao_documento=2
        )
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': str(doc_r1.uuid), 'versao_documento': 1}},
        )
        result = _builder(paa)._doc_retificacao_ciclo_atual()
        assert result is not None
        assert result.pk == doc_r2.pk

    def test_retorna_doc_sem_replica(self, paa_factory, documento_paa_factory):
        """Sem réplica, qualquer doc existente é retornado (sem referência de snapshot)."""
        paa = _paa_em_retificacao(paa_factory)
        doc = documento_paa_factory(paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO)
        result = _builder(paa)._doc_retificacao_ciclo_atual()
        assert result is not None
        assert result.pk == doc.pk


# _numero_versao_retificacao
class TestNumeroVersaoRetificacao:
    """
    Verifica que _numero_versao_retificacao retorna a string correta com o número
    da versão de retificação, inferindo do snapshot quando o doc ainda não foi gerado.
    """

    def test_usa_versao_do_documento_quando_disponivel(self, paa_factory, documento_paa_factory):
        """Doc passado diretamente → usa doc.versao_documento."""
        paa = paa_factory()
        doc = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=3
        )
        assert _builder(paa)._numero_versao_retificacao(doc) == '3'

    def test_retorna_vazio_quando_sem_doc_e_nao_em_retificacao(self, paa_factory):
        """doc=None e PAA fora de retificação → '' (sem versão determinável)."""
        paa = paa_factory()
        assert _builder(paa)._numero_versao_retificacao(None) == ''

    def test_infere_versao_1_para_r1_pendente_sem_snapshot_anterior(
        self, paa_factory, replica_paa_factory
    ):
        """R1 em andamento: snapshot sem doc anterior → versao_documento=None → número 1."""
        paa = _paa_em_retificacao(paa_factory)
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': None, 'versao_documento': None}},
        )
        assert _builder(paa)._numero_versao_retificacao(None) == '1'

    def test_infere_versao_2_para_r2_pendente_com_snapshot_r1(
        self, paa_factory, replica_paa_factory
    ):
        """R2 em andamento: snapshot tem versao_documento=1 → número inferido = 2."""
        paa = _paa_em_retificacao(paa_factory)
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': 'qualquer-uuid', 'versao_documento': 1}},
        )
        assert _builder(paa)._numero_versao_retificacao(None) == '2'

    def test_infere_versao_1_quando_nao_ha_replica(self, paa_factory):
        """Sem réplica (DoesNotExist): fallback para '1'."""
        paa = _paa_em_retificacao(paa_factory)
        assert _builder(paa)._numero_versao_retificacao(None) == '1'

    def test_r2_com_doc_gerado_retorna_versao_do_doc(
        self, paa_factory, documento_paa_factory, replica_paa_factory
    ):
        """R2 com doc já gerado: usa doc.versao_documento=2, não o snapshot."""
        paa = _paa_em_retificacao(paa_factory)
        doc_r1 = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=1
        )
        doc_r2 = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=2
        )
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': str(doc_r1.uuid), 'versao_documento': 1}},
        )
        assert _builder(paa)._numero_versao_retificacao(doc_r2) == '2'
