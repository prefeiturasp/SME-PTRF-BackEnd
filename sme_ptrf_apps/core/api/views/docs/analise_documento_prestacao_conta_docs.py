from sme_ptrf_apps.core.models import AnaliseDocumentoPrestacaoConta
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiExample

DOCS = dict(
    limpar_status=extend_schema(
        description="Limpa o status de múltiplas solicitações de acerto de documento informadas por UUID.",
        request={
            'application/json': {
                'example': {
                    "uuids_solicitacoes_acertos_documentos": ["uuid1", "uuid2"],
                    "justificativa": ""
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Status alterados com sucesso!"),
        },
    ),
    justificar_nao_realizacao=extend_schema(
        description="Registra uma justificativa para a não realização de solicitações de acerto de documento.",
        request={
            'application/json': {
                'example': {
                    "uuids_solicitacoes_acertos_documentos": ["uuid1", "uuid2"],
                    "justificativa": ""
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Status alterados com sucesso!"),
        },
    ),
    marcar_como_realizado=extend_schema(
        description="Marca um ou mais documentos de solicitação de acerto como realizados.",
        request={
            'application/json': {
                'example': {
                    "uuids_solicitacoes_acertos_documentos": ["uuid1", "uuid2"],
                    "justificativa": ""
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Status alterados com sucesso!"),
        },
    ),
    tabelas=extend_schema(
        description="Retorna status possíveis e informações sobre editabilidade da análise.",
        parameters=[
            OpenApiParameter(name='uuid_analise_prestacao', description='UUID da análise de prestação',
                             required=True, type=str),
            OpenApiParameter(name='visao', description='Visão do usuário (ex: UE, DRE, SME)',
                             required=True, type=str, enum=['UE', 'DRE', 'SME']),
        ],
        responses={200: "result"},
        examples=[
            OpenApiExample(
                'Resposta',
                value={
                    "status_realizacao": [{"id": "PENDENTE", "nome": "Pendente"}],
                    "status_realizacao_solicitacao": [{"id": "REALIZADO", "label": "Realizado"}],
                    "editavel": True
                }
            )
        ]
    ),
    marcar_como_credito_incluido=extend_schema(
        description="Marca crédito um crédito incluído a uma solicitação de acerto.",
        request={
            'application/json': {
                'example': {
                    "uuid_solicitacao_acerto": "uuid-solicitacao",
                    "uuid_credito_incluido": "uuid-credito"
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Crédito incluído atuaizado com sucesso."),
        },
    ),
    marcar_como_gasto_incluido=extend_schema(
        description="Marca um gasto incluído a uma solicitação de acerto de documento.",
        request={
            'application/json': {
                'example': {
                    "uuid_solicitacao_acerto": "uuid-solicitacao",
                    "uuid_gasto_incluido": "uuid-gasto"
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Status alterados com sucesso!"),
        },
    ),
    marcar_como_esclarecido=extend_schema(
        description="Registra um esclarecimento para uma solicitação de acerto de documento.",
        request={
            'application/json': {
                'example': {
                    "uuid_solicitacao_acerto": "uuid-solicitacao",
                    "esclarecimento": "O documento foi reenviado com as informações corretas."
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Esclarecimento atualizado com sucesso."),
        },
    ),
    editar_informacao_conciliacao=extend_schema(
        description="Permite editar ou justificar informações de conciliação bancária de um documento.",
        request={
            'application/json': {
                'example': {
                    "uuid_analise_documento": "uuid-analise-doc",
                    "justificativa_conciliacao": "Divergência entre saldo e extrato bancário."
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Edição de informação da conciliação atualizada com sucesso."),
        },
    ),
    reataurar_justificativa_original=extend_schema(
        description="Desfaz alterações e restaura a justificativa original da solicitação de acerto.",
        request={
            'application/json': {
                'example': {
                    "uuid_solicitacao_acerto": "uuid-solicitacao"
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Restaurar justificativa original realizada com sucesso."),
        },
    ),
    tags_informacoes_conferencia_list=extend_schema(
        description="Retorna a lista de tags disponíveis para conferência de documentos de prestação de contas.",
        responses={200: 'result'},
        examples=[
            OpenApiExample(
                'Resposta',
                value={
                    "tags": [
                        AnaliseDocumentoPrestacaoConta.TAG_AJUSTE,
                        AnaliseDocumentoPrestacaoConta.TAG_CORRETO,
                        AnaliseDocumentoPrestacaoConta.TAG_NAO_CONFERIDO,
                    ]
                }
            )
        ]
    ),
)
