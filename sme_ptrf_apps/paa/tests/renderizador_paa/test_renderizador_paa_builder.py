import pytest
from datetime import date, time
from unittest.mock import patch, MagicMock

from sme_ptrf_apps.paa.api.serializers.renderizador_paa_serializer import (
    RenderizadorPaaBuilder,
    _cor_status_geracao,
    _url_documento_final,
    _url_ata_paa,
)
from sme_ptrf_apps.paa.models import DocumentoPaa, AtaPaa
from sme_ptrf_apps.paa.services.retificacao_paa_service import ValidacaoRetificacao

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


# _cor_status_geracao
class TestCorStatusGeracao:

    def test_concluido_retorna_green(self):
        assert _cor_status_geracao(DocumentoPaa.StatusChoices.CONCLUIDO) == 'green'

    def test_em_processamento_retorna_orange(self):
        assert _cor_status_geracao(DocumentoPaa.StatusChoices.EM_PROCESSAMENTO) == 'orange'

    def test_nao_gerado_retorna_red(self):
        assert _cor_status_geracao(DocumentoPaa.StatusChoices.NAO_GERADO) == 'red'

    def test_status_desconhecido_retorna_grey(self):
        assert _cor_status_geracao('STATUS_DESCONHECIDO') == 'grey'

    def test_ata_concluido_retorna_green(self):
        assert _cor_status_geracao(AtaPaa.STATUS_CONCLUIDO) == 'green'

    def test_ata_em_processamento_retorna_orange(self):
        assert _cor_status_geracao(AtaPaa.STATUS_EM_PROCESSAMENTO) == 'orange'


# _url_documento_final
class TestUrlDocumentoFinal:

    def test_sem_request_retorna_vazio(self, paa_factory):
        paa = paa_factory()
        assert _url_documento_final(None, paa, False) == ''

    def test_com_request_retificacao_false(self, paa_factory):
        paa = paa_factory()
        request = MagicMock()
        request.build_absolute_uri.return_value = (
            f'http://testserver/api/paa/{paa.uuid}/documento-final/?retificacao=false')
        result = _url_documento_final(request, paa, False)
        assert 'retificacao=false' in result

    def test_com_request_retificacao_true(self, paa_factory):
        paa = paa_factory()
        request = MagicMock()
        request.build_absolute_uri.return_value = (
            f'http://testserver/api/paa/{paa.uuid}/documento-final/?retificacao=true')
        result = _url_documento_final(request, paa, True)
        assert 'retificacao=true' in result


# _url_ata_paa
class TestUrlAtaPaa:

    def test_sem_request_retorna_vazio(self, ata_paa_factory):
        ata = ata_paa_factory()
        assert _url_ata_paa(None, ata) == ''

    def test_sem_ata_retorna_vazio(self):
        request = MagicMock()
        assert _url_ata_paa(request, None) == ''

    def test_com_request_e_ata_retorna_url(self, ata_paa_factory):
        ata = ata_paa_factory()
        request = MagicMock()
        request.build_absolute_uri.return_value = (
            f'http://testserver/api/atas-paa/download-arquivo-ata-paa/?ata-paa-uuid={ata.uuid}')
        result = _url_ata_paa(request, ata)
        assert str(ata.uuid) in result


# _pode_retificar
class TestPodeRetificar:

    def test_retorna_false_quando_em_retificacao(self, paa_factory):
        paa = _paa_em_retificacao(paa_factory)
        assert _builder(paa)._pode_retificar() is False

    def test_retorna_true_quando_validacao_ok(self, paa_factory):
        paa = paa_factory()
        with patch(
            'sme_ptrf_apps.paa.api.serializers.renderizador_paa_serializer.RetificacaoPaaService'
        ) as mock_service:
            mock_service.return_value.valida_pode_retificar.return_value = None
            assert _builder(paa)._pode_retificar() is True

    def test_retorna_false_quando_validacao_falha(self, paa_factory):
        paa = paa_factory()
        with patch(
            'sme_ptrf_apps.paa.api.serializers.renderizador_paa_serializer.RetificacaoPaaService'
        ) as mock_service:
            mock_service.return_value.valida_pode_retificar.side_effect = ValidacaoRetificacao('não pode')
            assert _builder(paa)._pode_retificar() is False


# _unidade
class TestUnidade:

    def test_retorna_dict_com_campos_corretos(self, paa_factory):
        paa = paa_factory()
        resultado = _builder(paa)._unidade()
        assert 'nome' in resultado
        assert 'tipo' in resultado
        assert 'codigo_eol' in resultado

    def test_codigo_eol_numerico_convertido_para_int(self, paa_factory):
        paa = paa_factory()
        paa.associacao.unidade.codigo_eol = '12345'
        resultado = _builder(paa)._unidade()
        assert resultado['codigo_eol'] == 12345

    def test_codigo_eol_nao_numerico_permanece_string(self, paa_factory):
        paa = paa_factory()
        paa.associacao.unidade.codigo_eol = 'ABC'
        resultado = _builder(paa)._unidade()
        assert resultado['codigo_eol'] == 'ABC'


# _texto_justificativa_ata
class TestTextoJustificativaAta:

    def test_sem_ata_retorna_vazio(self, paa_factory):
        paa = paa_factory()
        assert _builder(paa)._texto_justificativa_ata(None, False) == ''

    def test_eh_retificacao_retorna_justificativa(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(paa=paa, justificativa='Motivo da retificação')
        assert _builder(paa)._texto_justificativa_ata(ata, True) == 'Motivo da retificação'

    def test_nao_retificacao_retorna_comentarios(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(paa=paa, comentarios='Comentário da assembleia', justificativa='')
        resultado = _builder(paa)._texto_justificativa_ata(ata, False)
        assert 'Comentário da assembleia' in resultado

    def test_nao_retificacao_combina_comentarios_e_justificativa(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(paa=paa, comentarios='Comentários', justificativa='Justificativa')
        resultado = _builder(paa)._texto_justificativa_ata(ata, False)
        assert 'Comentários' in resultado
        assert 'Justificativa' in resultado


# _texto_resumo_assembleia
class TestTextoResumoAssembleia:

    def test_sem_ata_retorna_vazio(self, paa_factory):
        paa = paa_factory()
        assert _builder(paa)._texto_resumo_assembleia(None, False) == ''

    def test_sem_data_reuniao_retorna_vazio(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(paa=paa, data_reuniao=None)
        assert _builder(paa)._texto_resumo_assembleia(ata, False) == ''

    def test_status_nao_concluido_retorna_vazio(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(
            paa=paa, data_reuniao=date(2025, 1, 1),
            status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO,
        )
        assert _builder(paa)._texto_resumo_assembleia(ata, False) == ''

    def test_aprovada_nao_retificacao_retorna_texto_correto(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(
            paa=paa,
            data_reuniao=date(2025, 1, 15),
            hora_reuniao=time(10, 0),
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
            parecer_conselho=AtaPaa.PARECER_APROVADA,
        )
        resultado = _builder(paa)._texto_resumo_assembleia(ata, False)
        assert 'Plano Anual de Atividades' in resultado
        assert 'aprovado' in resultado
        assert '15/01/2025' in resultado

    def test_aprovada_retificacao_retorna_texto_correto(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(
            paa=paa,
            data_reuniao=date(2025, 1, 15),
            hora_reuniao=time(10, 0),
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
            parecer_conselho=AtaPaa.PARECER_APROVADA,
        )
        resultado = _builder(paa)._texto_resumo_assembleia(ata, True)
        assert 'Plano Anual de Atividades aprovado' in resultado

    def test_sem_parecer_retorna_vazio(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(
            paa=paa,
            data_reuniao=date(2025, 1, 15),
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
            parecer_conselho='',
        )
        assert _builder(paa)._texto_resumo_assembleia(ata, False) == ''


# _estado_ata_esconde_botoes_acao
class TestEstadoAtaEscondeBotoesAcao:

    def test_sem_ata_retorna_false(self, paa_factory):
        paa = paa_factory()
        assert _builder(paa)._estado_ata_esconde_botoes_acao(None) is False

    def test_em_processamento_retorna_true(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(paa=paa, status_geracao_pdf=AtaPaa.STATUS_EM_PROCESSAMENTO)
        assert _builder(paa)._estado_ata_esconde_botoes_acao(ata) is True

    def test_concluido_retorna_true(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(paa=paa, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)
        assert _builder(paa)._estado_ata_esconde_botoes_acao(ata) is True

    def test_nao_gerado_retorna_false(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(paa=paa, status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO)
        assert _builder(paa)._estado_ata_esconde_botoes_acao(ata) is False


# _apresenta_botoes_acao
class TestApresentaBotoesAcao:

    def test_paa_nao_vigente_retorna_false(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(paa=paa, status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO)
        assert _builder(paa)._apresenta_botoes_acao(ata, False, False) is False

    def test_vigente_fora_retificacao_ata_nao_gerada_retorna_true(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(paa=paa, status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO)
        assert _builder(paa)._apresenta_botoes_acao(ata, False, True) is True

    def test_vigente_fora_retificacao_ata_concluida_retorna_false(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(paa=paa, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)
        assert _builder(paa)._apresenta_botoes_acao(ata, False, True) is False

    def test_vigente_em_retificacao_bloco_retificacao_ata_nao_gerada_retorna_true(
        self, paa_factory, ata_paa_factory
    ):
        paa = _paa_em_retificacao(paa_factory)
        ata = ata_paa_factory(paa=paa, status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO)
        assert _builder(paa)._apresenta_botoes_acao(ata, True, True) is True

    def test_vigente_em_retificacao_bloco_original_retorna_false(
        self, paa_factory, ata_paa_factory
    ):
        paa = _paa_em_retificacao(paa_factory)
        ata = ata_paa_factory(paa=paa, status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO)
        assert _builder(paa)._apresenta_botoes_acao(ata, False, True) is False


# _mensagem_exibicao_ata
class TestMensagemExibicaoAta:

    def test_sem_ata_retorna_pendente(self, paa_factory):
        paa = paa_factory()
        resultado = _builder(paa)._mensagem_exibicao_ata(None, False)
        assert 'pendente' in resultado.lower()

    def test_sem_arquivo_em_processamento(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(paa=paa, status_geracao_pdf=AtaPaa.STATUS_EM_PROCESSAMENTO)
        resultado = _builder(paa)._mensagem_exibicao_ata(ata, False)
        assert resultado == AtaPaa.STATUS_NOMES[AtaPaa.STATUS_EM_PROCESSAMENTO]

    def test_sem_arquivo_nao_em_processamento_retorna_pendente(self, paa_factory, ata_paa_factory):
        paa = paa_factory()
        ata = ata_paa_factory(paa=paa, status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO)
        resultado = _builder(paa)._mensagem_exibicao_ata(ata, False)
        assert 'pendente' in resultado.lower()
