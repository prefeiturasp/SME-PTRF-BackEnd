from rest_framework import status
from sme_ptrf_apps.core.models import SolicitacaoAcertoLancamento, TipoAcertoLancamento


class MarcarComoRealizado:

    def __init__(self, uuids_solicitacoes_acertos_lancamentos):
        self.uuids_solicitacoes_acertos_lancamentos = uuids_solicitacoes_acertos_lancamentos
        self.__set_response()

    def __set_response(self):
        pode_atualizar_status = True
        texto_solicitacoes_nao_atendidas = "Não foi possível alterar o status de algumas solicitações " \
                                           "pois os ajustes não foram realizados."

        self.response = {
            "mensagem": "Status alterados com sucesso!",
            "status": status.HTTP_200_OK,
            "todas_as_solicitacoes_marcadas_como_realizado": True,
        }

        for uuid_solicitacao in self.uuids_solicitacoes_acertos_lancamentos:

            solicitacao_acerto = SolicitacaoAcertoLancamento.by_uuid(uuid_solicitacao)
            analise_lancamento = solicitacao_acerto.analise_lancamento
            categoria = solicitacao_acerto.tipo_acerto.categoria

            if categoria == TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO:
                if not analise_lancamento.lancamento_atualizado:
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_realizado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            elif categoria == TipoAcertoLancamento.CATEGORIA_DEVOLUCAO:
                if not analise_lancamento.devolucao_tesouro_atualizada:
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_realizado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            elif categoria == TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO:
                if not analise_lancamento.lancamento_excluido:
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_realizado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            elif categoria == TipoAcertoLancamento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO:
                if not solicitacao_acerto.esclarecimentos:
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_realizado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            if pode_atualizar_status:
                solicitacao_acerto.altera_status_realizacao(
                    novo_status=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_REALIZADO,
                )


class SolicitacaoAcertoLancamentoService:
    @classmethod
    def marcar_como_realizado(cls, uuids_solicitacoes_acertos_lancamentos):
        return MarcarComoRealizado(
            uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes_acertos_lancamentos
        ).response
