from sme_ptrf_apps.core.models import TipoAcertoLancamento
from ...utils.choices_to_json import choices_to_json


class TipoAcertoLancamentoAgrupadoPorCategoria:

    def __init__(self, choices):
        self.choices = choices
        self.__set_agrupamento()

    def __set_agrupamento(self):
        self.agrupamento = []

        for choice in self.choices:
            categoria_id = choice[0]
            categoria_nome = choice[1]

            tipos_acertos_lancamentos = TipoAcertoLancamento.objects.filter(
                categoria=categoria_id).filter(ativo=True).values("id", "nome", "categoria", "ativo", "uuid")

            if not tipos_acertos_lancamentos:
                continue

            info_categoria = self.__texto_e_cor_categoria(self, categoria_id)

            dados_categoria = {
                "id": categoria_id,
                "nome": categoria_nome,
                "texto": info_categoria["texto"],
                "cor": info_categoria["cor"],
                "tipos_acerto_lancamento": list(tipos_acertos_lancamentos)
            }

            self.agrupamento.append(dados_categoria)

    @staticmethod
    def __texto_e_cor_categoria(self, categoria_id):
        if TipoAcertoLancamento.CATEGORIA_DEVOLUCAO == categoria_id:
            return {
                "texto": "Esse tipo de acerto demanda informação da data de pagamento da devolução.",
                "cor": 1
            }
        elif TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO == categoria_id:
            return {
                "texto": "Esse tipo de acerto reabre o lançamento para edição.",
                "cor": 1
            }
        elif TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO == categoria_id:
            return {
                "texto": "Esse tipo de acerto reabre o lançamento para exclusão.",
                "cor": 1
            }
        elif TipoAcertoLancamento.CATEGORIA_AJUSTES_EXTERNOS == categoria_id:
            return {
                "texto": "Esse tipo de acerto requer apenas ações externas ao sistema e "
                         "não reabre o lançamento para alteração.",
                "cor": 2
            }
        elif TipoAcertoLancamento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO == categoria_id:
            return {
                "texto": "Esse tipo de acerto requer que o usuário digite uma justificativa e "
                         "não reabre o lançamento para alteração.",
                "cor": 2
            }


class TipoAcertoLancamentoCategorias:

    def __init__(self, choices):
        self.choices = choices
        self.__set_choices_json()

    def __set_choices_json(self):
        self.choices_json = choices_to_json(self.choices)


class TipoAcertoLancamentoService:
    @classmethod
    def agrupado_por_categoria(cls, choices):
        return TipoAcertoLancamentoAgrupadoPorCategoria(choices=choices).agrupamento

    @classmethod
    def categorias(cls, choices):
        return TipoAcertoLancamentoCategorias(choices=choices).choices_json
