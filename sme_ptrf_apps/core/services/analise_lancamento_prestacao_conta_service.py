from sme_ptrf_apps.core.models import AnaliseLancamentoPrestacaoConta
from rest_framework import status


class LimparStatus:

    def __init__(self, uuids_analises_lancamentos):
        self.uuids_analises_lancamentos = uuids_analises_lancamentos
        self.__set_response()

    def __set_response(self):
        self.response = {
            "mensagem": "Status alterados com sucesso!",
            "status": status.HTTP_200_OK
        }

        if not self.uuids_analises_lancamentos or len(self.uuids_analises_lancamentos) == 0:
            self.response["erro"] = "parametros_requeridos"
            self.response["mensagem"] = "É necessário enviar pelo menos um uuid da analise de lancamento."
            self.response["status"] = status.HTTP_400_BAD_REQUEST
            return

        for uuid_analise in self.uuids_analises_lancamentos:
            try:
                analise_lancamento = AnaliseLancamentoPrestacaoConta.by_uuid(uuid_analise)
            except AnaliseLancamentoPrestacaoConta.DoesNotExist:
                self.response["erro"] = "Objeto não encontrado."
                self.response["mensagem"] = f"O objeto AnaliseLancamentoPrestacaoConta " \
                                            f"para o uuid {uuid_analise} não foi encontrado."
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break
            except Exception as e:
                self.response["erro"] = "Ocorreu um erro."
                self.response["mensagem"] = f"{e}"
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break

            if analise_lancamento.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE:
                self.response["erro"] = "Status invalido."
                self.response["mensagem"] = "Status realizacao pendente não é aceito nessa ação."
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break

            analise_lancamento.altera_status_realizacao(
                novo_status=AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE
            )


class JustificarNaoRealizacao:

    def __init__(self, uuids_analises_lancamentos, justificativa):
        self.uuids_analises_lancamentos = uuids_analises_lancamentos
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

        if not self.uuids_analises_lancamentos or len(self.uuids_analises_lancamentos) == 0:
            self.response["erro"] = "parametros_requeridos"
            self.response["mensagem"] = "É necessário enviar pelo menos um uuid da analise de lancamento."
            self.response["status"] = status.HTTP_400_BAD_REQUEST
            return

        for uuid_analise in self.uuids_analises_lancamentos:
            try:
                analise_lancamento = AnaliseLancamentoPrestacaoConta.by_uuid(uuid_analise)
            except AnaliseLancamentoPrestacaoConta.DoesNotExist:
                self.response["erro"] = "Objeto não encontrado."
                self.response["mensagem"] = f"O objeto AnaliseLancamentoPrestacaoConta " \
                                            f"para o uuid {uuid_analise} não foi encontrado."
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break
            except Exception as e:
                self.response["erro"] = "Ocorreu um erro."
                self.response["mensagem"] = f"{e}"
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break

            if analise_lancamento.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_JUSTIFICADO:
                self.response["erro"] = "Status invalido."
                self.response["mensagem"] = "Status realizacao justificado não é aceito nessa ação."
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break

            analise_lancamento.altera_status_realizacao(
                novo_status=AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_JUSTIFICADO,
                justificativa=self.justificativa
            )


class MarcarRealizacao:

    def __init__(self, uuids_analises_lancamentos):
        self.uuids_analises_lancamentos = uuids_analises_lancamentos
        self.__set_response()

    def __set_response(self):
        self.response = {
            "mensagem": "Status alterados com sucesso!",
            "status": status.HTTP_200_OK
        }

        if not self.uuids_analises_lancamentos or len(self.uuids_analises_lancamentos) == 0:
            self.response["erro"] = "parametros_requeridos"
            self.response["mensagem"] = "É necessário enviar pelo menos um uuid da analise de lancamento."
            self.response["status"] = status.HTTP_400_BAD_REQUEST
            return

        for uuid_analise in self.uuids_analises_lancamentos:
            try:
                analise_lancamento = AnaliseLancamentoPrestacaoConta.by_uuid(uuid_analise)
            except AnaliseLancamentoPrestacaoConta.DoesNotExist:
                self.response["erro"] = "Objeto não encontrado."
                self.response["mensagem"] = f"O objeto AnaliseLancamentoPrestacaoConta " \
                                            f"para o uuid {uuid_analise} não foi encontrado."
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break
            except Exception as e:
                self.response["erro"] = "Ocorreu um erro."
                self.response["mensagem"] = f"{e}"
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break

            if analise_lancamento.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO:
                self.response["erro"] = "Status invalido."
                self.response["mensagem"] = "Status realizacao realizado não é aceito nessa ação."
                self.response["status"] = status.HTTP_400_BAD_REQUEST
                break

            analise_lancamento.altera_status_realizacao(
                novo_status=AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO,
            )


class AnaliseLancamentoPrestacaoContaService:
    @classmethod
    def limpar_status(cls, uuids_analises_lancamentos):
        return LimparStatus(uuids_analises_lancamentos=uuids_analises_lancamentos).response

    @classmethod
    def justificar_nao_realizacao(cls, uuids_analises_lancamentos, justificativa):
        return JustificarNaoRealizacao(
            uuids_analises_lancamentos=uuids_analises_lancamentos,
            justificativa=justificativa
        ).response

    @classmethod
    def marcar_como_realizado(cls, uuids_analises_lancamentos):
        return MarcarRealizacao(uuids_analises_lancamentos=uuids_analises_lancamentos).response
