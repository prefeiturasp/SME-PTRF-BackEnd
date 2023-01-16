from rest_framework import status
from sme_ptrf_apps.core.models import SolicitacaoAcertoDocumento, TipoAcertoDocumento
from sme_ptrf_apps.receitas.models import Receita
from sme_ptrf_apps.despesas.models import Despesa


class MarcarComoRealizado:

    def __init__(self, uuids_solicitacoes_acertos_documentos):
        self.uuids_solicitacoes_acertos_documentos = uuids_solicitacoes_acertos_documentos
        self.__set_response()

    def __set_response(self):
        texto_solicitacoes_nao_atendidas = "Não foi possível alterar o status da solicitação, pois os ajustes solicitados não foram realizados."
        self.response = {
            "mensagem": "Status alterados com sucesso!",
            "status": status.HTTP_200_OK,
            "todas_as_solicitacoes_marcadas_como_realizado": True,
        }

        for uuid_solicitacao in self.uuids_solicitacoes_acertos_documentos:
            pode_atualizar_status = True

            solicitacao_acerto = SolicitacaoAcertoDocumento.by_uuid(uuid_solicitacao)
            categoria = solicitacao_acerto.tipo_acerto.categoria

            if categoria == TipoAcertoDocumento.CATEGORIA_INCLUSAO_CREDITO:
                if solicitacao_acerto.receita_incluida is None:
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_realizado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            elif categoria == TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO:
                if solicitacao_acerto.despesa_incluida is None:
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_realizado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas
            elif categoria == TipoAcertoDocumento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO:
                if not solicitacao_acerto.esclarecimentos:
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_realizado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas

                    if solicitacao_acerto.status_realizacao == SolicitacaoAcertoDocumento.STATUS_REALIZACAO_JUSTIFICADO:
                        solicitacao_acerto.altera_status_realizacao(
                            novo_status=SolicitacaoAcertoDocumento.STATUS_REALIZACAO_PENDENTE,
                        )

            elif categoria == TipoAcertoDocumento.CATEGORIA_AJUSTES_EXTERNOS:
                pode_atualizar_status = True

            if pode_atualizar_status:
                solicitacao_acerto.altera_status_realizacao(
                    novo_status=SolicitacaoAcertoDocumento.STATUS_REALIZACAO_REALIZADO,
                )


class LimparStatus:

    def __init__(self, uuids_solicitacoes_acertos_documentos):
        self.uuids_solicitacoes_acertos_documentos = uuids_solicitacoes_acertos_documentos
        self.__set_response()

    def __set_response(self):

        self.response = {
            "mensagem": "Status alterados com sucesso!",
            "status": status.HTTP_200_OK,
        }

        for uuid_solicitacao in self.uuids_solicitacoes_acertos_documentos:
            solicitacao_acerto = SolicitacaoAcertoDocumento.by_uuid(uuid_solicitacao)

            solicitacao_acerto.altera_status_realizacao(
                novo_status=SolicitacaoAcertoDocumento.STATUS_REALIZACAO_PENDENTE,
            )


class JustificarNaoRealizacao:

    def __init__(self, uuids_solicitacoes_acertos_documentos, justificativa):
        self.uuids_solicitacoes_acertos_documentos = uuids_solicitacoes_acertos_documentos
        self.justificativa = justificativa
        self.__set_response()

    def __set_response(self):
        texto_solicitacoes_nao_atendidas = "Não foi possível alterar o status da solicitação, pois os ajustes já foram realizados."

        self.response = {
            "mensagem": "Status alterados com sucesso!",
            "status": status.HTTP_200_OK,
            "todas_as_solicitacoes_marcadas_como_justificado": True,
        }

        for uuid_solicitacao in self.uuids_solicitacoes_acertos_documentos:
            pode_atualizar_status = True

            solicitacao_acerto = SolicitacaoAcertoDocumento.by_uuid(uuid_solicitacao)
            categoria = solicitacao_acerto.tipo_acerto.categoria

            if categoria == TipoAcertoDocumento.CATEGORIA_INCLUSAO_CREDITO:
                if solicitacao_acerto.receita_incluida:
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_justificado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            elif categoria == TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO:
                if solicitacao_acerto.despesa_incluida:
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_justificado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            elif categoria == TipoAcertoDocumento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO:
                if solicitacao_acerto.esclarecimentos != "":
                    pode_atualizar_status = False

                    self.response["todas_as_solicitacoes_marcadas_como_justificado"] = False
                    self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            elif categoria == TipoAcertoDocumento.CATEGORIA_AJUSTES_EXTERNOS:
                pode_atualizar_status = True

            if pode_atualizar_status:
                solicitacao_acerto.altera_status_realizacao(
                    novo_status=SolicitacaoAcertoDocumento.STATUS_REALIZACAO_JUSTIFICADO,
                    justificativa=self.justificativa
                )


class SolicitacaoAcertoDocumentoService:

    @classmethod
    def marcar_como_realizado(cls, uuids_solicitacoes_acertos_documentos):
        return MarcarComoRealizado(
            uuids_solicitacoes_acertos_documentos=uuids_solicitacoes_acertos_documentos
        ).response

    @classmethod
    def limpar_status(cls, uuids_solicitacoes_acertos_documentos):
        return LimparStatus(uuids_solicitacoes_acertos_documentos=uuids_solicitacoes_acertos_documentos).response

    @classmethod
    def justificar_nao_realizacao(cls, uuids_solicitacoes_acertos_documentos, justificativa):
        return JustificarNaoRealizacao(
            uuids_solicitacoes_acertos_documentos=uuids_solicitacoes_acertos_documentos,
            justificativa=justificativa
        ).response

    @classmethod
    def marcar_como_esclarecido(cls, uuid_solicitacao_acerto, esclarecimento):
        solicitacao_acerto = SolicitacaoAcertoDocumento.by_uuid(uuid_solicitacao_acerto)
        solicitacao_acerto.incluir_esclarecimentos(esclarecimento)

        return {
            "mensagem": "Esclarecimento atualizado com sucesso.",
            "status": status.HTTP_200_OK
        }

    @classmethod
    def marcar_como_credito_incluido(cls, uuid_solicitacao_acerto, uuid_credito_incluido):
        credito_incluido = Receita.by_uuid(uuid_credito_incluido)
        solicitacao_acerto = SolicitacaoAcertoDocumento.by_uuid(uuid_solicitacao_acerto)
        solicitacao_acerto.receita_incluida = credito_incluido
        solicitacao_acerto.save()

        return {
            "mensagem": "Crédito incluído atualizado com sucesso.",
            "status": status.HTTP_200_OK
        }

    @classmethod
    def marcar_como_gasto_incluido(cls, uuid_solicitacao_acerto, uuid_gasto_incluido):
        despesa_incluida = Despesa.by_uuid(uuid_gasto_incluido)
        solicitacao_acerto = SolicitacaoAcertoDocumento.by_uuid(uuid_solicitacao_acerto)
        solicitacao_acerto.despesa_incluida = despesa_incluida
        solicitacao_acerto.save()

        return {
            "mensagem": "Gasto incluído atualizado com sucesso.",
            "status": status.HTTP_200_OK
        }
