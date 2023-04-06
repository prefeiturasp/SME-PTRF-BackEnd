from sme_ptrf_apps.core.models import TipoAcertoDocumento
from ...utils.choices_to_json import choices_to_json


class TipoAcertoDocumentoAgrupadoPorCategoria:

    def __init__(self, choices, tipos_documento_prestacao__uuid):
        self.choices = choices
        self.tipos_documento_prestacao__uuid = tipos_documento_prestacao__uuid
        self.__set_agrupamento()

    def __set_agrupamento(self):
        self.agrupamento = []

        for choice in self.choices:
            categoria_id = choice[0]
            categoria_nome = choice[1]

            tipos_acertos_documentos = TipoAcertoDocumento.objects.filter(
                categoria=categoria_id).filter(ativo=True).values("nome", "uuid")

            if self.tipos_documento_prestacao__uuid is not None:
                tipos_acertos_documentos = tipos_acertos_documentos.filter(
                    tipos_documento_prestacao__uuid=self.tipos_documento_prestacao__uuid)

            if not tipos_acertos_documentos:
                continue

            info_categoria = self.__texto_e_cor_categoria(self, categoria_id)

            dados_categoria = {
                "id": categoria_id,
                "nome": categoria_nome,
                "texto": info_categoria["texto"],
                "cor": info_categoria["cor"],
                "tipos_acerto_documento": list(tipos_acertos_documentos)
            }

            self.agrupamento.append(dados_categoria)

    @staticmethod
    def __texto_e_cor_categoria(self, categoria_id):
        if TipoAcertoDocumento.CATEGORIA_INCLUSAO_CREDITO == categoria_id:
            return {
                "texto": "Esse tipo de acerto reabre o período para inclusão de um crédito.",
                "cor": 1
            }
        elif TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO == categoria_id:
            return {
                "texto": "Esse tipo de acerto reabre o período para inclusão de um gasto.",
                "cor": 1
            }
        elif TipoAcertoDocumento.CATEGORIA_AJUSTES_EXTERNOS == categoria_id:
            return {
                "texto": "Esse tipo de acerto requer apenas ações externas ao sistema e "
                         "não reabre o lançamento para alteração.",
                "cor": 2
            }
        elif TipoAcertoDocumento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO == categoria_id:
            return {
                "texto": "Esse tipo de acerto requer que o usuário digite uma justificativa e "
                         "não reabre o lançamento para alteração.",
                "cor": 2
            }
        elif TipoAcertoDocumento.CATEGORIA_EDICAO_INFORMACAO == categoria_id:
            return {
                "texto": "Esse tipo de acerto requer que o usuário preencha o campo Justificativas e "
                         "informações adicionais e o documento será gerado novamente.",
                "cor": 2
            }


class TipoAcertoDocumentoCategorias:

    def __init__(self, choices):
        self.choices = choices
        self.__set_choices_json()

    def __set_choices_json(self):
        self.choices_json = choices_to_json(self.choices)


class TipoAcertoDocumentoService:

    @classmethod
    def agrupado_por_categoria(cls, choices, tipos_documento_prestacao__uuid=None):
        return TipoAcertoDocumentoAgrupadoPorCategoria(
            choices=choices, tipos_documento_prestacao__uuid=tipos_documento_prestacao__uuid
        ).agrupamento

    @classmethod
    def categorias(cls, choices):
        return TipoAcertoDocumentoCategorias(choices=choices).choices_json
