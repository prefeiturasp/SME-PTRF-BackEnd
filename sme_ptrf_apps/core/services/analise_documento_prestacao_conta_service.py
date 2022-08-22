from sme_ptrf_apps.core.models import AnaliseDocumentoPrestacaoConta
from sme_ptrf_apps.receitas.models import Receita
from rest_framework import status


class LimparStatus:

    def __init__(self, uuids_analises_documentos):
        self.uuids_analises_documentos = uuids_analises_documentos
        self.__set_response()

    def __set_response(self):
        self.response = {
            "mensagem": "Status alterados com sucesso!",
            "status": status.HTTP_200_OK
        }

        if not self.uuids_analises_documentos or len(self.uuids_analises_documentos) == 0:
            self.response["erro"] = "parametros_requeridos"
            self.response["mensagem"] = "É necessário enviar pelo menos um uuid da analise de documento."
            self.response["status"] = status.HTTP_400_BAD_REQUEST
            return

        for uuid_analise in self.uuids_analises_documentos:
            try:
                analise_documento = AnaliseDocumentoPrestacaoConta.by_uuid(uuid_analise)
            except AnaliseDocumentoPrestacaoConta.DoesNotExist:
                self.response["erro"] = "Objeto não encontrado."
                self.response["mensagem"] = f"O objeto AnaliseDocumentoPrestacaoConta " \
                                            f"para o uuid {uuid_analise} não foi encontrado."
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break
            except Exception as e:
                self.response["erro"] = "Ocorreu um erro."
                self.response["mensagem"] = f"{e}"
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break

            if analise_documento.status_realizacao == AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE:
                self.response["erro"] = "Status invalido."
                self.response["mensagem"] = "Status realizacao pendente não é aceito nessa ação."
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break

            analise_documento.altera_status_realizacao(
                novo_status=AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE
            )


class JustificarNaoRealizacao:

    def __init__(self, uuids_analises_documentos, justificativa):
        self.uuids_analises_documentos = uuids_analises_documentos
        self.justificativa = justificativa
        self.__set_response()

    def __set_response(self):
        self.response = {
            "mensagem": "Status alterados com sucesso!",
            "status": status.HTTP_200_OK
        }

        if not self.justificativa:
            self.response["erro"] = "parametros_requeridos"
            self.response["mensagem"] = "É necessário enviar a justificativa de não realizacação."
            self.response["status"] = status.HTTP_400_BAD_REQUEST
            return

        if not self.uuids_analises_documentos or len(self.uuids_analises_documentos) == 0:
            self.response["erro"] = "parametros_requeridos"
            self.response["mensagem"] = "É necessário enviar pelo menos um uuid da analise de documento."
            self.response["status"] = status.HTTP_400_BAD_REQUEST
            return

        for uuid_analise in self.uuids_analises_documentos:
            try:
                analise_documento = AnaliseDocumentoPrestacaoConta.by_uuid(uuid_analise)
            except AnaliseDocumentoPrestacaoConta.DoesNotExist:
                self.response["erro"] = "Objeto não encontrado."
                self.response["mensagem"] = f"O objeto AnaliseDocumentoPrestacaoConta " \
                                            f"para o uuid {uuid_analise} não foi encontrado."
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break
            except Exception as e:
                self.response["erro"] = "Ocorreu um erro."
                self.response["mensagem"] = f"{e}"
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break

            if analise_documento.status_realizacao == AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_JUSTIFICADO:
                self.response["erro"] = "Status invalido."
                self.response["mensagem"] = "Status realizacao justificado não é aceito nessa ação."
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break

            analise_documento.altera_status_realizacao(
                novo_status=AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_JUSTIFICADO,
                justificativa=self.justificativa
            )


class MarcarRealizacao:

    def __init__(self, uuids_analises_documentos):
        self.uuids_analises_documentos = uuids_analises_documentos
        self.__set_response()

    def __set_response(self):
        self.response = {
            "mensagem": "Status alterados com sucesso!",
            "status": status.HTTP_200_OK
        }

        if not self.uuids_analises_documentos or len(self.uuids_analises_documentos) == 0:
            self.response["erro"] = "parametros_requeridos"
            self.response["mensagem"] = "É necessário enviar pelo menos um uuid da analise de documento."
            self.response["status"] = status.HTTP_400_BAD_REQUEST
            return

        for uuid_analise in self.uuids_analises_documentos:
            try:
                analise_documento = AnaliseDocumentoPrestacaoConta.by_uuid(uuid_analise)
            except AnaliseDocumentoPrestacaoConta.DoesNotExist:
                self.response["erro"] = "Objeto não encontrado."
                self.response["mensagem"] = f"O objeto AnaliseDocumentoPrestacaoConta " \
                                            f"para o uuid {uuid_analise} não foi encontrado."
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break
            except Exception as e:
                self.response["erro"] = "Ocorreu um erro."
                self.response["mensagem"] = f"{e}"
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break

            if analise_documento.status_realizacao == AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO:
                self.response["erro"] = "Status invalido."
                self.response["mensagem"] = "Status realizacao realizado não é aceito nessa ação."
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break

            analise_documento.altera_status_realizacao(
                novo_status=AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO,
            )


class AnaliseDocumentoPrestacaoContaService:
    @classmethod
    def limpar_status(cls, uuids_analises_documentos):
        return LimparStatus(uuids_analises_documentos=uuids_analises_documentos).response

    @classmethod
    def justificar_nao_realizacao(cls, uuids_analises_documentos, justificativa):
        return JustificarNaoRealizacao(
            uuids_analises_documentos=uuids_analises_documentos,
            justificativa=justificativa
        ).response

    @classmethod
    def marcar_como_realizado(cls, uuids_analises_documentos):
        return MarcarRealizacao(uuids_analises_documentos=uuids_analises_documentos).response

    @classmethod
    def marcar_como_credito_incluido(cls, uuid_analise_documento, uuid_credito_incluido):
        try:
            analise_documento = AnaliseDocumentoPrestacaoConta.by_uuid(uuid_analise_documento)
        except(AnaliseDocumentoPrestacaoConta.DoesNotExist, Exception):
            return {
                "erro": "Objeto não encontrado.",
                "mensagem": f"O objeto AnaliseDocumentoPrestacaoConta para o uuid {uuid_analise_documento} não foi encontrado.",
                "status": status.HTTP_404_NOT_FOUND
            }

        try:
            credito_incluido = Receita.by_uuid(uuid_credito_incluido)
        except(Receita.DoesNotExist, Exception):
            return {
                "erro": "Objeto não encontrado.",
                "mensagem": f"O objeto Receita para o uuid {uuid_credito_incluido} não foi encontrado.",
                "status": status.HTTP_404_NOT_FOUND
            }

        analise_documento.receita_incluida = credito_incluido
        analise_documento.save()

        return {
            "mensagem": "Crédito incluído atualizado com sucesso.",
            "status": status.HTTP_200_OK
        }
