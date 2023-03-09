from rest_framework import status
from sme_ptrf_apps.core.models import SolicitacaoAcertoLancamento, TipoAcertoLancamento


class MarcarComoRealizado:

    def __init__(self, uuids_solicitacoes_acertos_lancamentos):
        self.uuids_solicitacoes_acertos_lancamentos = uuids_solicitacoes_acertos_lancamentos
        self.__set_response()

    def __set_response(self):
        texto_solicitacoes_nao_atendidas = "Não foi possível alterar o status da solicitação, pois os ajustes solicitados não foram realizados."

        self.response = {
            "mensagem": "Status alterados com sucesso!",
            "status": status.HTTP_200_OK,
            "todas_as_solicitacoes_marcadas_como_realizado": True,
        }

        for uuid_solicitacao in self.uuids_solicitacoes_acertos_lancamentos:
            pode_atualizar_status = True

            solicitacao_acerto = SolicitacaoAcertoLancamento.by_uuid(uuid_solicitacao)
            analise_lancamento = solicitacao_acerto.analise_lancamento
            categoria = solicitacao_acerto.tipo_acerto.categoria

            categorias_de_conciliacao = [
                TipoAcertoLancamento.CATEGORIA_CONCILIACAO_LANCAMENTO,
                TipoAcertoLancamento.CATEGORIA_DESCONCILIACAO_LANCAMENTO
            ]

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

                    if solicitacao_acerto.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_JUSTIFICADO:
                        solicitacao_acerto.altera_status_realizacao(
                            novo_status=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE,
                        )

            elif categoria in categorias_de_conciliacao:
                if not analise_lancamento.conciliacao_atualizada:
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_realizado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            elif categoria == TipoAcertoLancamento.CATEGORIA_AJUSTES_EXTERNOS:
                pode_atualizar_status = True

            if pode_atualizar_status:
                solicitacao_acerto.altera_status_realizacao(
                    novo_status=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_REALIZADO,
                )


class JustificarNaoRealizacao:

    def __init__(self, uuids_solicitacoes_acertos_lancamentos, justificativa):
        self.uuids_solicitacoes_acertos_lancamentos = uuids_solicitacoes_acertos_lancamentos
        self.justificativa = justificativa
        self.__set_response()

    def __set_response(self):
        texto_solicitacoes_nao_atendidas = "Não foi possível alterar o status da solicitação, pois os ajustes já foram realizados."

        self.response = {
            "mensagem": "Status alterados com sucesso!",
            "status": status.HTTP_200_OK,
            "todas_as_solicitacoes_marcadas_como_justificado": True,
        }

        for uuid_solicitacao in self.uuids_solicitacoes_acertos_lancamentos:
            pode_atualizar_status = True

            solicitacao_acerto = SolicitacaoAcertoLancamento.by_uuid(uuid_solicitacao)
            analise_lancamento = solicitacao_acerto.analise_lancamento
            categoria = solicitacao_acerto.tipo_acerto.categoria

            categorias_de_conciliacao = [
                TipoAcertoLancamento.CATEGORIA_CONCILIACAO_LANCAMENTO,
                TipoAcertoLancamento.CATEGORIA_DESCONCILIACAO_LANCAMENTO
            ]

            if categoria == TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO:
                if analise_lancamento.lancamento_atualizado:
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_justificado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            elif categoria == TipoAcertoLancamento.CATEGORIA_DEVOLUCAO:
                if analise_lancamento.devolucao_tesouro_atualizada:
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_justificado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            elif categoria == TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO:
                if analise_lancamento.lancamento_excluido:
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_justificado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            elif categoria == TipoAcertoLancamento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO:
                if solicitacao_acerto.esclarecimentos is not None:
                    if solicitacao_acerto.esclarecimentos != "":
                        pode_atualizar_status = False

                        self.response["todas_as_solicitacoes_marcadas_como_justificado"] = False
                        self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            elif categoria in categorias_de_conciliacao:
                if analise_lancamento.conciliacao_atualizada:
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_justificado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            elif categoria == TipoAcertoLancamento.CATEGORIA_AJUSTES_EXTERNOS:
                pode_atualizar_status = True


            if pode_atualizar_status:
                solicitacao_acerto.altera_status_realizacao(
                    novo_status=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_JUSTIFICADO,
                    justificativa=self.justificativa
                )


class LimparStatus:

    def __init__(self, uuids_solicitacoes_acertos_lancamentos):
        self.uuids_solicitacoes_acertos_lancamentos = uuids_solicitacoes_acertos_lancamentos
        self.__set_response()

    def __set_response(self):

        self.response = {
            "mensagem": "Status alterados com sucesso!",
            "status": status.HTTP_200_OK,
        }

        for uuid_solicitacao in self.uuids_solicitacoes_acertos_lancamentos:
            solicitacao_acerto = SolicitacaoAcertoLancamento.by_uuid(uuid_solicitacao)

            solicitacao_acerto.altera_status_realizacao(
                novo_status=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE,
            )


class SolicitacaoAcertoLancamentoService:
    @classmethod
    def marcar_como_realizado(cls, uuids_solicitacoes_acertos_lancamentos):
        return MarcarComoRealizado(
            uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes_acertos_lancamentos
        ).response

    @classmethod
    def justificar_nao_realizacao(cls, uuids_solicitacoes_acertos_lancamentos, justificativa):
        return JustificarNaoRealizacao(
            uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes_acertos_lancamentos,
            justificativa=justificativa
        ).response

    @classmethod
    def limpar_status(cls, uuids_solicitacoes_acertos_lancamentos):
        return LimparStatus(uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes_acertos_lancamentos).response

    @classmethod
    def marcar_como_esclarecido(cls, uuid_solicitacao_acerto, esclarecimento):
        solicitacao_acerto = SolicitacaoAcertoLancamento.by_uuid(uuid_solicitacao_acerto)
        solicitacao_acerto.incluir_esclarecimentos(esclarecimento)

        return {
            "mensagem": "Esclarecimento atualizado com sucesso.",
            "status": status.HTTP_200_OK
        }
