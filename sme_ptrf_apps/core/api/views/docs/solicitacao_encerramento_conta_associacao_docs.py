from drf_spectacular.utils import (
    extend_schema, OpenApiResponse, OpenApiTypes, OpenApiParameter, OpenApiExample, inline_serializer)
from ...serializers import SolicitacaoEncerramentoContaAssociacaoSerializer

DOCS = dict(
    list=extend_schema(
        description="Retorna uma lista paginada de todas as solicitações de encerramento de conta de associação.",
        tags=["Solicitações Encerramento Conta"],
        responses={
            200: SolicitacaoEncerramentoContaAssociacaoSerializer(many=True),
        }
    ),
    retrieve=extend_schema(
        description="Retorna os detalhes de uma solicitação de encerramento específica pelo UUID.",
        tags=["Solicitações Encerramento Conta"],
        responses={
            200: SolicitacaoEncerramentoContaAssociacaoSerializer,
        }
    ),
    create=extend_schema(
        description="Cria uma nova solicitação de encerramento de conta de associação.",
        tags=["Solicitações Encerramento Conta"],
        request=SolicitacaoEncerramentoContaAssociacaoSerializer,
        responses={
            201: SolicitacaoEncerramentoContaAssociacaoSerializer,
        }
    ),
    update=extend_schema(
        description="Atualiza completamente uma solicitação de encerramento de conta.",
        tags=["Solicitações Encerramento Conta"],
        request=SolicitacaoEncerramentoContaAssociacaoSerializer,
        responses={
            200: SolicitacaoEncerramentoContaAssociacaoSerializer,
        }
    ),
    partial_update=extend_schema(
        description="Atualiza parcialmente uma solicitação de encerramento de conta.",
        tags=["Solicitações Encerramento Conta"],
        request=SolicitacaoEncerramentoContaAssociacaoSerializer,
        responses={
            200: SolicitacaoEncerramentoContaAssociacaoSerializer,
        }
    ),
    destroy=extend_schema(
        description="Exclui uma solicitação de encerramento de conta, caso permitido.",
        tags=["Solicitações Encerramento Conta"],
        responses={
            204: "Solicitação excluída com sucesso",
            400: "Solicitação não pode ser apagada",
            404: "Solicitação não encontrada"
        },
        examples=[
            OpenApiExample(
                name="Solicitação não pode ser apagada",
                status_codes=[400],
                value={'mensagem': 'Essa solicitação não pode ser apagada.'}
            ),
            OpenApiExample(
                name="Solicitação não encontrada",
                status_codes=[404],
                value=""
            ),
            OpenApiExample(
                name="Exclusão realizada com sucesso",
                status_codes=[204],
                value=""
            )
        ]
    ),
    reenviar=extend_schema(
        description="Reenvia uma solicitação de encerramento que foi anteriormente rejeitada.",
        tags=["Solicitações Encerramento Conta"],
        request=SolicitacaoEncerramentoContaAssociacaoSerializer,
        responses={
            200: SolicitacaoEncerramentoContaAssociacaoSerializer,
            400: '400',
        },
        examples=[
            OpenApiExample(
                'status_nao_permite_operacao',
                status_codes=[400],
                value={
                    'erro': 'status_nao_permite_operacao',
                    'mensagem': 'Impossível aprovar solicitação com status diferente de REJEITADA'
                }
            ),
        ]
    ),
    aprovar=extend_schema(
        description="Aprova uma solicitação de encerramento de conta que está pendente.",
        tags=["Solicitações Encerramento Conta"],
        responses={
            200: SolicitacaoEncerramentoContaAssociacaoSerializer,
            400: "Status não permite operação",
        },
        examples=[
            OpenApiExample(
                'status_nao_permite_operacao',
                status_codes=[400],
                value={
                    'erro': 'status_nao_permite_operacao',
                    'mensagem': 'Impossível aprovar solicitação com status diferente de PENDENTE'
                }
            )
        ]
    ),
    rejeitar=extend_schema(
        description="Rejeita uma solicitação de encerramento de conta pendente, informando os motivos.",
        tags=["Solicitações Encerramento Conta"],
        request=inline_serializer(
            name='InlinePayload',
            fields={'motivos_rejeicao': [], 'outros_motivos_rejeicao': ""},
            required=['motivos_rejeicao']
        ),
        responses={
            200: SolicitacaoEncerramentoContaAssociacaoSerializer,
            400: "Erro na operação",
        },
        examples=[
            OpenApiExample(
                'Objeto não encontrado',
                status_codes=[400],
                value={
                    'erro': 'Objeto não encontrado.',
                    'mensagem': "O objeto motivo de rejeição para o uuid  uuid-1234 não foi encontrado na base."
                }
            ),
            OpenApiExample(
                'Status não permite operação',
                status_codes=[400],
                value={
                    'erro': 'status_nao_permite_operacao',
                    'mensagem': (
                        'Impossível aprovar solicitação com status diferente '
                        'de STATUS_PENDENTE')
                }
            ),
            OpenApiExample(
                'Exemplo de Payload rejeição',
                value={
                    'motivos_rejeicao': ['uuid-motivo-1', 'uuid-motivo-2'],
                    'outros_motivos_rejeicao': 'Documentação incompleta'
                }
            )
        ],
    ),
)
