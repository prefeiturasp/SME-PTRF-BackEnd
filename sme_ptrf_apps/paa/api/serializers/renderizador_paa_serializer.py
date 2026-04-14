from typing import Optional

from rest_framework import serializers

from sme_ptrf_apps.paa.models import AtaPaa, DocumentoPaa, Paa
from sme_ptrf_apps.paa.models.documento_paa import obter_documento_final_por_retificacao
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.services.retificacao_paa_service import (
    RetificacaoPaaService,
    ValidacaoRetificacao,
)


def _cor_status_geracao(status: str) -> str:
    if status == DocumentoPaa.StatusChoices.CONCLUIDO or status == AtaPaa.STATUS_CONCLUIDO:
        return 'green'
    if status == DocumentoPaa.StatusChoices.EM_PROCESSAMENTO or status == AtaPaa.STATUS_EM_PROCESSAMENTO:
        return 'orange'
    if status == DocumentoPaa.StatusChoices.ERRO_PROCESSAMENTO:
        return 'red'
    if status == DocumentoPaa.StatusChoices.NAO_GERADO or status == AtaPaa.STATUS_NAO_GERADO:
        return 'red'
    return 'grey'


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
    documento = RenderizadorDocumentoPaaSerializer()
    ata = RenderizadorAtaPaaSerializer()


class RenderizadorPaaSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    referencia = serializers.CharField(allow_blank=True)
    pode_retificar = serializers.BooleanField()
    esta_em_retificacao = serializers.BooleanField()
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
            return {
                'uuid': None,
                'existe_arquivo': False,
                'status': {
                    'status_geracao': DocumentoPaa.StatusChoices.NAO_GERADO,
                    'mensagem': 'Documento pendente de geração.',
                    'cor_mensagem': _cor_status_geracao(DocumentoPaa.StatusChoices.NAO_GERADO),
                    'versao_documento': 1,
                    'retificacao': eh_retificacao,
                },
                'url': '',
            }
        existe = bool(documento.arquivo_pdf)
        return {
            'uuid': documento.uuid,
            'existe_arquivo': existe,
            'status': {
                'status_geracao': documento.status_geracao,
                'mensagem': str(documento),
                'cor_mensagem': _cor_status_geracao(documento.status_geracao),
                'versao_documento': documento.versao_documento,
                'retificacao': documento.retificacao,
            },
            'url': _url_documento_final(self.request, self.paa, eh_retificacao) if existe else '',
        }

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
        if eh_retificacao or not ata or not ata.data_reuniao:
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
        esta_em_retificacao = self.paa.status == PaaStatusEnum.EM_RETIFICACAO.name
        esconde = self._estado_ata_esconde_botoes_acao(ata)

        if eh_retificacao:
            if not esta_em_retificacao:
                return False
            return not esconde

        if esta_em_retificacao:
            return False

        return not esconde

    def _mensagem_exibicao_ata(self, ata: Optional[AtaPaa], existe_arquivo: bool) -> str:
        if not ata:
            return 'Documento pendente de geração.'
        if not existe_arquivo:
            if ata.status_geracao_pdf == AtaPaa.STATUS_EM_PROCESSAMENTO:
                return AtaPaa.STATUS_NOMES[AtaPaa.STATUS_EM_PROCESSAMENTO]
            return 'Documento pendente de geração.'
        if ata.status_geracao_pdf == AtaPaa.STATUS_CONCLUIDO and ata.criado_em:
            return f'Ata PAA gerada dia {ata.alterado_em.strftime("%d/%m/%Y %H:%M")}'
        return ata.nome

    def _ata_render(
        self,
        ata: Optional[AtaPaa],
        eh_retificacao: bool,
        eh_paa_vigente: bool,
    ) -> dict:
        if not ata:
            return {
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
        existe = bool(ata.arquivo_pdf)
        from sme_ptrf_apps.paa.services.ata_paa_service import validar_geracao_ata_paa

        pode = validar_geracao_ata_paa(ata)['is_valid'] if ata else False
        return {
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
            'pode_gerar_ata': pode,
            'apresenta_botoes_acao': self._apresenta_botoes_acao(
                ata, eh_retificacao, eh_paa_vigente
            ),
            'url': _url_ata_paa(self.request, ata) if existe else '',
            'resumo_assembleia': self._texto_resumo_assembleia(ata, eh_retificacao),
        }

    def _ata_por_tipo(self, tipo_ata: str) -> Optional[AtaPaa]:
        return (
            self.paa.atas_da_paa.filter(tipo_ata=tipo_ata).order_by('-pk').first()
        )

    def _pode_retificar(self) -> bool:
        if self.paa.status == PaaStatusEnum.EM_RETIFICACAO.name:
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
        doc_original = obter_documento_final_por_retificacao(self.paa, False)
        ata_original = self._ata_por_tipo(AtaPaa.ATA_APRESENTACAO)

        esta_em_retificacao = self.paa.status == PaaStatusEnum.EM_RETIFICACAO.name
        bloco_retificacao = None
        if esta_em_retificacao:
            doc_ret = obter_documento_final_por_retificacao(self.paa, True)
            ata_ret = self._ata_por_tipo(AtaPaa.ATA_RETIFICACAO)
            bloco_retificacao = {
                'documento': self._documento_render(doc_ret, True),
                'ata': self._ata_render(ata_ret, True, eh_paa_vigente),
            }

        return {
            'uuid': str(self.paa.uuid),
            'referencia': self.paa.periodo_paa.referencia if self.paa.periodo_paa else '',
            'pode_retificar': self._pode_retificar(),
            'esta_em_retificacao': esta_em_retificacao,
            'unidade': self._unidade(),
            'original': {
                'documento': self._documento_render(doc_original, False),
                'ata': self._ata_render(ata_original, False, eh_paa_vigente),
            },
            'retificacao': bloco_retificacao,
        }
