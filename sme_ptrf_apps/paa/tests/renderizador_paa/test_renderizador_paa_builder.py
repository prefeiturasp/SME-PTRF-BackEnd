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


# _doc_retificacao_concluido
class TestDocRetificacaoConcluido:
    """
    Verifica que _doc_retificacao_concluido retorna o documento de retificação
    FINAL+CONCLUIDO mais recente (por versao_documento desc), usado como fallback
    quando o ciclo atual ainda não gerou seu próprio documento (cenário Rn).
    """

    def test_retorna_none_sem_documentos_retificacao(self, paa_factory):
        """Sem nenhum doc retificado → None."""
        paa = _paa_em_retificacao(paa_factory)
        assert _builder(paa)._doc_retificacao_concluido() is None

    def test_retorna_none_quando_doc_nao_esta_concluido(self, paa_factory, documento_paa_factory):
        """Doc retificado EM_PROCESSAMENTO não conta como CONCLUIDO → None."""
        paa = _paa_em_retificacao(paa_factory)
        documento_paa_factory(paa=paa, retificacao=True, versao=FINAL, status_geracao=EM_PROCESSAMENTO)
        assert _builder(paa)._doc_retificacao_concluido() is None

    def test_retorna_documento_concluido_unico(self, paa_factory, documento_paa_factory):
        """Um único doc CONCLUIDO → retornado."""
        paa = _paa_em_retificacao(paa_factory)
        doc = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=1
        )
        result = _builder(paa)._doc_retificacao_concluido()
        assert result is not None
        assert result.pk == doc.pk

    def test_retorna_doc_mais_recente_por_versao_documento(self, paa_factory, documento_paa_factory):
        """Com dois docs CONCLUIDOS, retorna o de maior versao_documento."""
        paa = _paa_em_retificacao(paa_factory)
        documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=1
        )
        doc_r2 = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=2
        )
        result = _builder(paa)._doc_retificacao_concluido()
        assert result.pk == doc_r2.pk

    def test_ignora_doc_nao_retificacao(self, paa_factory, documento_paa_factory):
        """Doc original (retificacao=False) não é retornado."""
        paa = _paa_em_retificacao(paa_factory)
        documento_paa_factory(paa=paa, retificacao=False, versao=FINAL, status_geracao=CONCLUIDO)
        assert _builder(paa)._doc_retificacao_concluido() is None


# _ata_retificacao_concluida
class TestAtaRetificacaoConcluida:
    """
    Verifica que _ata_retificacao_concluida retorna a ata de retificação CONCLUIDA
    mais recente (por pk desc), usada como fallback quando o ciclo atual ainda não
    gerou documento.
    """

    def test_retorna_none_sem_ata_retificacao(self, paa_factory):
        """Sem nenhuma ata de retificação → None."""
        paa = _paa_em_retificacao(paa_factory)
        assert _builder(paa)._ata_retificacao_concluida() is None

    def test_retorna_none_quando_ata_nao_concluida(self, paa_factory, ata_paa_factory):
        """Ata STATUS_NAO_GERADO não conta como CONCLUIDA → None."""
        paa = _paa_em_retificacao(paa_factory)
        ata_paa_factory(paa=paa, tipo_ata=AtaPaa.ATA_RETIFICACAO, status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO)
        assert _builder(paa)._ata_retificacao_concluida() is None

    def test_retorna_ata_concluida_unica(self, paa_factory, ata_paa_factory):
        """Uma única ata CONCLUIDA → retornada."""
        paa = _paa_em_retificacao(paa_factory)
        ata = ata_paa_factory(
            paa=paa, tipo_ata=AtaPaa.ATA_RETIFICACAO, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO
        )
        result = _builder(paa)._ata_retificacao_concluida()
        assert result is not None
        assert result.pk == ata.pk

    def test_retorna_ata_mais_recente_por_pk(self, paa_factory, ata_paa_factory):
        """Com duas atas CONCLUIDAS, retorna a de maior pk."""
        paa = _paa_em_retificacao(paa_factory)
        ata_paa_factory(paa=paa, tipo_ata=AtaPaa.ATA_RETIFICACAO, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)
        ata_r2 = ata_paa_factory(
            paa=paa, tipo_ata=AtaPaa.ATA_RETIFICACAO, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO
        )
        result = _builder(paa)._ata_retificacao_concluida()
        assert result.pk == ata_r2.pk

    def test_ignora_ata_apresentacao(self, paa_factory, ata_paa_factory):
        """Ata do tipo ATA_APRESENTACAO não é retornada."""
        paa = _paa_em_retificacao(paa_factory)
        ata_paa_factory(paa=paa, tipo_ata=AtaPaa.ATA_APRESENTACAO, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)
        assert _builder(paa)._ata_retificacao_concluida() is None


# ciclo_retificacao_sem_documento (campo em build())
class TestBuildCicloRetificacaoSemDocumento:
    """
    Verifica que ciclo_retificacao_sem_documento no resultado de build() é True quando
    o PAA está em EM_RETIFICACAO e o ciclo corrente ainda não gerou documento, e False
    em todos os demais casos.
    """

    def test_falso_quando_paa_nao_em_retificacao(self, paa_factory):
        """PAA fora de retificação → ciclo_retificacao_sem_documento=False."""
        paa = paa_factory()
        with patch(
            'sme_ptrf_apps.paa.api.serializers.renderizador_paa_serializer.RetificacaoPaaService'
        ) as mock:
            mock.return_value.valida_pode_retificar.side_effect = ValidacaoRetificacao('não pode')
            result = _builder(paa).build()
        assert result['ciclo_retificacao_sem_documento'] is False

    def test_verdadeiro_quando_r1_sem_documento(self, paa_factory, replica_paa_factory):
        """R1: réplica sem snapshot anterior, sem doc gerado → True."""
        paa = _paa_em_retificacao(paa_factory)
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': None, 'versao_documento': None}},
        )
        result = _builder(paa).build()
        assert result['ciclo_retificacao_sem_documento'] is True

    def test_falso_quando_r1_tem_documento_gerado(
        self, paa_factory, replica_paa_factory, documento_paa_factory
    ):
        """R1 com doc gerado no ciclo atual → False."""
        paa = _paa_em_retificacao(paa_factory)
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': None, 'versao_documento': None}},
        )
        documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=1
        )
        result = _builder(paa).build()
        assert result['ciclo_retificacao_sem_documento'] is False

    def test_verdadeiro_quando_r2_sem_documento_proprio(
        self, paa_factory, replica_paa_factory, documento_paa_factory
    ):
        """R2: snapshot aponta para doc R1 e nenhum doc R2 existe → True."""
        paa = _paa_em_retificacao(paa_factory)
        doc_r1 = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=1
        )
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': str(doc_r1.uuid), 'versao_documento': 1}},
        )
        result = _builder(paa).build()
        assert result['ciclo_retificacao_sem_documento'] is True

    def test_falso_quando_r2_tem_documento_proprio(
        self, paa_factory, replica_paa_factory, documento_paa_factory
    ):
        """R2: snapshot aponta para doc R1 e doc R2 gerado → False."""
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
        result = _builder(paa).build()
        assert result['ciclo_retificacao_sem_documento'] is False


# build() — Rn fallback: exibe dados do ciclo anterior quando ciclo atual não tem doc
class TestBuildRnFallback:
    """
    Verifica que quando o PAA está em EM_RETIFICACAO e o ciclo atual ainda não gerou
    documento, o bloco retificacao exibe os dados do ciclo anterior (fallback), e não
    fica em branco.
    """

    def test_r2_sem_doc_usa_secao_titulo_com_versao_r1(
        self, paa_factory, replica_paa_factory, documento_paa_factory
    ):
        """R2 sem doc próprio: secao_titulo deve referenciar a versão do doc R1 (fallback)."""
        paa = _paa_em_retificacao(paa_factory)
        doc_r1 = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=1
        )
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': str(doc_r1.uuid), 'versao_documento': 1}},
        )
        result = _builder(paa).build()
        assert result['retificacao'] is not None
        assert result['retificacao']['secao_titulo'] == 'PAA Retificado #1'

    def test_r2_sem_doc_exibe_dados_retificacao_true(
        self, paa_factory, replica_paa_factory, documento_paa_factory
    ):
        """R2 sem doc próprio: exibe_dados_retificacao deve ser True (bloco não oculto)."""
        paa = _paa_em_retificacao(paa_factory)
        doc_r1 = documento_paa_factory(
            paa=paa, retificacao=True, versao=FINAL, status_geracao=CONCLUIDO, versao_documento=1
        )
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': str(doc_r1.uuid), 'versao_documento': 1}},
        )
        result = _builder(paa).build()
        assert result['exibe_dados_retificacao'] is True

    def test_r1_pendente_usa_secao_titulo_com_versao_1(self, paa_factory, replica_paa_factory):
        """R1 sem doc (inicial): secao_titulo com número '1' inferido do ciclo."""
        paa = _paa_em_retificacao(paa_factory)
        replica_paa_factory(
            paa=paa,
            historico={'documento_retificado': {'uuid': None, 'versao_documento': None}},
        )
        result = _builder(paa).build()
        assert result['retificacao'] is not None
        assert result['retificacao']['secao_titulo'] == 'PAA Retificado #1'

    def test_r2_com_doc_proprio_usa_versao_r2(
        self, paa_factory, replica_paa_factory, documento_paa_factory
    ):
        """R2 com doc R2 gerado: secao_titulo deve referenciar versão 2."""
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
        result = _builder(paa).build()
        assert result['retificacao']['secao_titulo'] == 'PAA Retificado #2'


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
