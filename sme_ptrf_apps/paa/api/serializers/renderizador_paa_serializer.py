from typing import Optional

from rest_framework import serializers

from sme_ptrf_apps.paa.models import AtaPaa, DocumentoPaa, Paa
from sme_ptrf_apps.paa.models.documento_paa import obter_documento_final_por_retificacao
from sme_ptrf_apps.paa.services.retificacao_paa_service import (
    RetificacaoPaaService,
    ValidacaoRetificacao,
)
from sme_ptrf_apps.paa.services.ciclo_retificacao_service import CicloRetificacaoService


_DOCUMENTO_PENDENTE_GERACAO = 'Documento pendente de geração.'
STATUS_COLORS = {
    DocumentoPaa.StatusChoices.CONCLUIDO: "green",
    AtaPaa.STATUS_CONCLUIDO: "green",

    DocumentoPaa.StatusChoices.EM_PROCESSAMENTO: "orange",
    AtaPaa.STATUS_EM_PROCESSAMENTO: "orange",

    DocumentoPaa.StatusChoices.ERRO_PROCESSAMENTO: "red",
    DocumentoPaa.StatusChoices.NAO_GERADO: "red",
    AtaPaa.STATUS_NAO_GERADO: "red",
}


def _cor_status_geracao(status: str) -> str:
    return STATUS_COLORS.get(status, "grey")


def _url_documento_final(request, paa: Paa, eh_retificacao: bool) -> str:
    if not request:
        return ''
    path = f'/api/paa/{paa.uuid}/documento-final/?retificacao={"true" if eh_retificacao else "false"}'
    return request.build_absolute_uri(path)


def _url_ata_paa(request, ata: Optional[AtaPaa]) -> str:
    if not request or not ata:
        return ''
    path = f'/api/atas-paa/download-arquivo-ata-paa/?ata-paa-uuid={ata.uuid}'
    return request.build_absolute_uri(path)


class RenderizadorStatusDocumentoPaaSerializer(serializers.Serializer):
    status_geracao = serializers.CharField()
    mensagem = serializers.CharField()
    cor_mensagem = serializers.CharField()
    versao_documento = serializers.IntegerField()
    versao = serializers.CharField()
    retificacao = serializers.BooleanField()


class RenderizadorDocumentoPaaSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(allow_null=True)
    existe_arquivo = serializers.BooleanField()
    status = RenderizadorStatusDocumentoPaaSerializer()
    url = serializers.CharField(allow_blank=True)


class RenderizadorStatusAtaPaaSerializer(serializers.Serializer):
    status_geracao = serializers.CharField()
    mensagem = serializers.CharField()
    cor_mensagem = serializers.CharField()
    versao_documento = serializers.IntegerField()
    retificacao = serializers.BooleanField()


class RenderizadorAtaPaaSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(allow_null=True)
    existe_arquivo = serializers.BooleanField()
    status = RenderizadorStatusAtaPaaSerializer()
    justificativa = serializers.CharField(allow_blank=True)
    pode_gerar_ata = serializers.BooleanField()
    apresenta_botoes_acao = serializers.BooleanField()
    url = serializers.CharField(allow_blank=True)
    resumo_assembleia = serializers.CharField(allow_blank=True)


class RenderizadorBlocoDocumentacaoSerializer(serializers.Serializer):
    secao_titulo = serializers.CharField(allow_blank=False)
    documento = RenderizadorDocumentoPaaSerializer()
    ata = RenderizadorAtaPaaSerializer()


class RenderizadorPaaSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    referencia = serializers.CharField(allow_blank=True)
    pode_retificar = serializers.BooleanField()
    esta_em_retificacao = serializers.BooleanField()
    exibe_dados_retificacao = serializers.BooleanField()
    ciclo_retificacao_sem_documento = serializers.BooleanField()
    unidade = serializers.DictField()
    original = RenderizadorBlocoDocumentacaoSerializer()
    retificacao = RenderizadorBlocoDocumentacaoSerializer(allow_null=True)


class RenderizadorPaaBuilder:
    """DTO de renderização com regras de negócio aplicadas no backend."""

    def __init__(self, paa: Paa, request=None, usuario=None):
        self.paa = paa
        self.request = request
        self.usuario = usuario

    def _documento_render(self, documento: Optional[DocumentoPaa], eh_retificacao: bool) -> dict:
        if not documento:
            dados = {
                'uuid': None,
                'existe_arquivo': False,
                'status': {
                    'status_geracao': DocumentoPaa.StatusChoices.NAO_GERADO,
                    'mensagem': _DOCUMENTO_PENDENTE_GERACAO,
                    'cor_mensagem': _cor_status_geracao(DocumentoPaa.StatusChoices.NAO_GERADO),
                    'versao_documento': 1,
                    'versao': '-',
                    'retificacao': eh_retificacao,
                },
                'url': '',
            }
            serialized = RenderizadorDocumentoPaaSerializer(data=dados, many=False)
            if not serialized.is_valid():
                raise serializers.ValidationError(
                    {'mensagem': 'Falha na serialização de dados no renderizador do Documento(inexistente) do PAA.'})
            return serialized.data

        existe = bool(documento.arquivo_pdf)
        dados = {
            'uuid': documento.uuid,
            'existe_arquivo': existe,
            'status': {
                'status_geracao': documento.status_geracao,
                'mensagem': str(documento),
                'cor_mensagem': _cor_status_geracao(documento.status_geracao),
                'versao_documento': documento.versao_documento,
                'versao': documento.versao,
                'retificacao': documento.retificacao,
            },
            'url': _url_documento_final(self.request, self.paa, eh_retificacao) if existe else '',
        }
        serialized = RenderizadorDocumentoPaaSerializer(data=dados, many=False)
        if not serialized.is_valid():
            raise serializers.ValidationError(
                {'mensagem': 'Falha na serialização de dados no renderizador do Documento do PAA.'})
        return serialized.data

    def _texto_justificativa_ata(self, ata: Optional[AtaPaa], eh_retificacao: bool) -> str:
        if not ata:
            return ''
        if eh_retificacao:
            return ata.justificativa or ''
        # Apresentação: manifestações na ata e, se houver, justificativa de rejeição
        partes = [ata.comentarios or '', ata.justificativa or '']
        return '\n'.join(p for p in partes if p).strip()

    def _texto_resumo_assembleia(self, ata: Optional[AtaPaa], eh_retificacao: bool) -> str:
        """
        Texto exibido abaixo do bloco PAA Original (ata de apresentação), com parecer do conselho
        e data/hora da assembleia (campos da ata).
        Só é exibido após a ata de apresentação estar gerada (PDF concluído).
        """
        if not ata or not ata.data_reuniao:
            return ''
        if ata.status_geracao_pdf != AtaPaa.STATUS_CONCLUIDO:
            return ''
        parecer = AtaPaa.PARECER_NOMES.get(ata.parecer_conselho, '')
        if not parecer:
            return ''
        parecer_lc = parecer.lower()
        data_str = ata.data_reuniao.strftime('%d/%m/%Y')
        hr = ata.hora_reuniao
        hora_str = hr.strftime('%Hh%M') if hr is not None else '00h00'

        return (
            f'Plano Anual de Atividades {parecer_lc} em Assembleia Geral em {data_str} à {hora_str}.'
        )

    def _estado_ata_esconde_botoes_acao(self, ata: Optional[AtaPaa]) -> bool:
        """Geração em andamento ou ata já concluída — não exibir coluna de ações."""
        if not ata:
            return False
        if ata.status_geracao_pdf == AtaPaa.STATUS_EM_PROCESSAMENTO:
            return True
        if ata.status_geracao_pdf == AtaPaa.STATUS_CONCLUIDO:
            return True
        return False

    def _apresenta_botoes_acao(
        self,
        ata: Optional[AtaPaa],
        eh_retificacao: bool,
        eh_paa_vigente: bool,
    ) -> bool:
        """
        Planos anteriores: nunca exibe botões na listagem.
        Vigente em retificação: só no bloco da ata de retificação, até essa ata ser gerada.
        Vigente fora de retificação: só no bloco da ata de apresentação, até gerada / em processamento.
        """
        if not eh_paa_vigente:
            return False

        esconde = self._estado_ata_esconde_botoes_acao(ata)

        if eh_retificacao:
            if not self.paa.status_em_retificacao:
                return False
            return not esconde

        if self.paa.status_em_retificacao:
            return False

        return not esconde

    def _mensagem_exibicao_ata(self, ata: Optional[AtaPaa], existe_arquivo: bool) -> str:
        """ Mensagem exibida quanto ao status da Ata """
        if not ata:
            return _DOCUMENTO_PENDENTE_GERACAO
        if not existe_arquivo:
            if ata.status_geracao_pdf == AtaPaa.STATUS_EM_PROCESSAMENTO:
                return AtaPaa.STATUS_NOMES[AtaPaa.STATUS_EM_PROCESSAMENTO]
            return _DOCUMENTO_PENDENTE_GERACAO
        if ata.status_geracao_pdf == AtaPaa.STATUS_CONCLUIDO and ata.criado_em:
            return ata.status_label_geracao()
        return ata.nome

    def _ata_render(
        self,
        ata: Optional[AtaPaa],
        eh_retificacao: bool,
        eh_paa_vigente: bool,
    ) -> dict:
        """ DTO de renderização para documento de Ata """
        if not ata:
            dados = {
                'uuid': None,
                'existe_arquivo': False,
                'status': {
                    'status_geracao': AtaPaa.STATUS_NAO_GERADO,
                    'mensagem': self._mensagem_exibicao_ata(ata, False),
                    'cor_mensagem': _cor_status_geracao(AtaPaa.STATUS_NAO_GERADO),
                    'versao_documento': 0,
                    'retificacao': eh_retificacao,
                },
                'justificativa': '',
                'pode_gerar_ata': False,
                'apresenta_botoes_acao': self._apresenta_botoes_acao(
                    None, eh_retificacao, eh_paa_vigente
                ),
                'url': '',
                'resumo_assembleia': '',
            }
            serialized = RenderizadorAtaPaaSerializer(data=dados, many=False)
            if not serialized.is_valid():
                raise serializers.ValidationError(
                    {'mensagem': 'Falha na serialização de dados no renderizador da Ata(inexistente) do PAA.'})
            return serialized.data

        existe = bool(ata.arquivo_pdf)
        from sme_ptrf_apps.paa.services.ata_paa_service import validar_geracao_ata_paa

        pode_gerar_ata = validar_geracao_ata_paa(ata).get('is_valid')
        dados = {
            'uuid': ata.uuid,
            'existe_arquivo': existe,
            'status': {
                'status_geracao': ata.status_geracao_pdf,
                'mensagem': self._mensagem_exibicao_ata(ata, existe),
                'cor_mensagem': _cor_status_geracao(ata.status_geracao_pdf),
                'versao_documento': 1,
                'retificacao': eh_retificacao,
            },
            'justificativa': self._texto_justificativa_ata(ata, eh_retificacao),
            'pode_gerar_ata': pode_gerar_ata,
            'apresenta_botoes_acao': self._apresenta_botoes_acao(
                ata, eh_retificacao, eh_paa_vigente
            ),
            'url': _url_ata_paa(self.request, ata) if existe else '',
            'resumo_assembleia': self._texto_resumo_assembleia(ata, eh_retificacao),
        }
        serialized = RenderizadorAtaPaaSerializer(data=dados, many=False)
        if not serialized.is_valid():
            raise serializers.ValidationError(
                {'mensagem': 'Falha na serialização de dados no renderizador da Ata do PAA.'})
        return serialized.data

    def _ata_por_tipo(self, tipo_ata: str) -> Optional[AtaPaa]:
        return (
            self.paa.atas_da_paa.filter(tipo_ata=tipo_ata).order_by('-pk').first()
        )

    def _doc_retificacao_concluido(self) -> Optional[DocumentoPaa]:
        """Documento de retificação FINAL CONCLUIDO mais recente (ciclo anterior ao corrente).

        Usado como fallback quando o ciclo atual ainda não gerou seu próprio documento,
        para manter os dados da retificação anterior visíveis na UI.
        """
        return (
            self.paa.documentopaa_set
            .filter(
                retificacao=True,
                versao=DocumentoPaa.VersaoChoices.FINAL,
                status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
            )
            .order_by('-versao_documento')
            .first()
        )

    def _ata_retificacao_concluida(self) -> Optional[AtaPaa]:
        """Ata de retificação CONCLUIDA mais recente (ciclo anterior ao corrente).

        Usada como fallback junto com ``_doc_retificacao_concluido`` quando
        o ciclo atual ainda não gerou seu próprio documento.
        """
        return (
            self.paa.atas_da_paa
            .filter(
                tipo_ata=AtaPaa.ATA_RETIFICACAO,
                status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
            )
            .order_by('-pk')
            .first()
        )

    def _pode_retificar(self) -> bool:
        if self.paa.status_em_retificacao:
            return False
        try:
            RetificacaoPaaService(paa=self.paa, usuario=self.usuario).valida_pode_retificar()
            return True
        except ValidacaoRetificacao:
            return False

    def _unidade(self) -> dict:
        unidade = self.paa.associacao.unidade
        codigo = unidade.codigo_eol
        try:
            codigo_eol = int(codigo)
        except (TypeError, ValueError):
            codigo_eol = codigo
        return {
            'nome': unidade.nome,
            'tipo': unidade.tipo_unidade,
            'codigo_eol': codigo_eol,
        }

    def build(self, eh_paa_vigente: bool = True) -> dict:
        """
            Constrói o DTO de renderização do PAA, com dados do documento final e das atas.
            Args:
                eh_paa_vigente: Indica se o PAA é o vigente (True) ou um plano anterior (False).
        """
        doc_original = obter_documento_final_por_retificacao(self.paa, False)
        ata_original = self._ata_por_tipo(AtaPaa.ATA_APRESENTACAO)

        if self.paa.status_em_retificacao:
            ciclo = CicloRetificacaoService(self.paa)
            ciclo_doc_atual = ciclo.documento_atual
            # True quando o ciclo corrente ainda não gerou seu próprio documento.
            # Usado pelo frontend para exibir o botão de retificação sem depender
            # do campo versao do documento exibido (que pode ser fallback do ciclo anterior).
            ciclo_retificacao_sem_documento = ciclo_doc_atual is None

            if ciclo_doc_atual:
                # Ciclo atual já gerou seu documento → exibe dados do ciclo corrente.
                doc_retificacao = ciclo_doc_atual
                versao_retificacao = str(doc_retificacao.versao_documento)
                ata_retificacao = self._ata_por_tipo(AtaPaa.ATA_RETIFICACAO)
            else:
                doc_anterior = self._doc_retificacao_concluido()
                if doc_anterior:
                    # Rn (n≥2): ciclo atual sem doc ainda → exibe dados do ciclo anterior
                    # concluído até que o ciclo corrente gere o seu próprio documento.
                    doc_retificacao = doc_anterior
                    ata_retificacao = self._ata_retificacao_concluida()
                    versao_retificacao = str(doc_anterior.versao_documento)
                else:
                    # R1: não há ciclo anterior → exibe pendente com o número do ciclo atual.
                    doc_retificacao = None
                    ata_retificacao = self._ata_por_tipo(AtaPaa.ATA_RETIFICACAO)
                    versao_retificacao = str(ciclo.numero_versao)
        else:
            ciclo_retificacao_sem_documento = False
            doc_retificacao = obter_documento_final_por_retificacao(self.paa, True)
            versao_retificacao = str(doc_retificacao.versao_documento) if doc_retificacao else ''
            ata_retificacao = self._ata_por_tipo(AtaPaa.ATA_RETIFICACAO)

        bloco_docs_originais = {
            'secao_titulo': 'PAA Original',
            'documento': self._documento_render(doc_original, False),
            'ata': self._ata_render(ata_original, False, eh_paa_vigente),
        }

        exibe_dados_retificacao = bool(
            self.paa.status_em_retificacao or doc_retificacao or ata_retificacao
        )
        bloco_docs_retificacao = {
            'secao_titulo': f'Retificado #{versao_retificacao}' if versao_retificacao else 'Retificado',
            'documento': self._documento_render(doc_retificacao, True),
            'ata': self._ata_render(ata_retificacao, True, eh_paa_vigente),
        } if exibe_dados_retificacao else None
        dados = {
            'uuid': str(self.paa.uuid),
            'referencia': self.paa.periodo_paa.referencia if self.paa.periodo_paa else '',
            'pode_retificar': self._pode_retificar(),
            'esta_em_retificacao': self.paa.status_em_retificacao,
            'exibe_dados_retificacao': exibe_dados_retificacao,
            'ciclo_retificacao_sem_documento': ciclo_retificacao_sem_documento,
            'unidade': self._unidade(),
            'original': bloco_docs_originais,
            'retificacao': bloco_docs_retificacao,
        }
        serializer = RenderizadorPaaSerializer(data=dados)
        if not serializer.is_valid():
            raise serializers.ValidationError(
                {'mensagem': 'Falha na serialização de dados do renderizador do PAA.'})
        return serializer.data
