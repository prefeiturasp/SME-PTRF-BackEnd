from rest_framework import status
from sme_ptrf_apps.core.models import SolicitacaoAcertoDocumento, TipoAcertoDocumento, AnaliseDocumentoPrestacaoConta, \
    ObservacaoConciliacao
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
            elif categoria == TipoAcertoDocumento.CATEGORIA_EDICAO_INFORMACAO:
                if not solicitacao_acerto.analise_documento.informacao_conciliacao_atualizada:
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
                if solicitacao_acerto.esclarecimentos is not None:
                    if solicitacao_acerto.esclarecimentos != "":
                        pode_atualizar_status = False

                        self.response["todas_as_solicitacoes_marcadas_como_justificado"] = False
                        self.response["mensagem"] = texto_solicitacoes_nao_atendidas

            elif categoria == TipoAcertoDocumento.CATEGORIA_EDICAO_INFORMACAO:
                if solicitacao_acerto.analise_documento.informacao_conciliacao_atualizada:
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


    @classmethod
    def editar_informacao_conciliacao(cls, uuid_analise_documento, justificativa_conciliacao):
        try:
            analise_documento = AnaliseDocumentoPrestacaoConta.by_uuid(uuid_analise_documento)

            conta_associacao = analise_documento.conta_associacao
            periodo = analise_documento.analise_prestacao_conta.prestacao_conta.periodo
            associacao = analise_documento.analise_prestacao_conta.prestacao_conta.associacao

            analise_documento.informacao_conciliacao_atualizada = True
            analise_documento.save()

            observacao, _ = ObservacaoConciliacao.objects.get_or_create(
                periodo=periodo,
                conta_associacao=conta_associacao,
                associacao=associacao,
                defaults={
                    'periodo': periodo,
                    'conta_associacao': conta_associacao,
                    'associacao': associacao,
                }
            )

            observacao.texto = justificativa_conciliacao
            observacao.save()

            return {
                "mensagem": "Edição de informação da conciliação atualizada com sucesso.",
                "status": status.HTTP_200_OK
            }
        except Exception as err:
            return {
                'mensagem': str(err),
                "status": status.HTTP_400_BAD_REQUEST
            }


    @classmethod
    def reataurar_justificativa_original(cls, uuid_solicitacao_acerto):
        try:
            solicitacao_acerto_documento = SolicitacaoAcertoDocumento.by_uuid(uuid_solicitacao_acerto)

            analise_documento = solicitacao_acerto_documento.analise_documento

            conta_associacao = analise_documento.conta_associacao
            periodo = analise_documento.analise_prestacao_conta.prestacao_conta.periodo
            associacao = analise_documento.analise_prestacao_conta.prestacao_conta.associacao

            analise_documento.informacao_conciliacao_atualizada = False
            analise_documento.save()

            observacao = ObservacaoConciliacao.objects.filter(
                periodo=periodo,
                conta_associacao=conta_associacao,
                associacao=associacao,
            ).first()
            if observacao:
                observacao.texto = observacao.justificativa_original
                observacao.save()

            cls.limpar_status(
                uuids_solicitacoes_acertos_documentos=[uuid_solicitacao_acerto],
            )

            return {
                "mensagem": "Restaurar justificativa original realizada com sucesso.",
                "status": status.HTTP_200_OK
            }
        except Exception as err:
            return {
                'mensagem': str(err),
                "status": status.HTTP_400_BAD_REQUEST
            }
