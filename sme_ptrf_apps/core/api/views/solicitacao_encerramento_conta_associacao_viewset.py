import logging

from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from sme_ptrf_apps.users.permissoes import (
    PermissaoAPIApenasDreComGravacao,
    PermissaoAPITodosComGravacao
)

from ..serializers import SolicitacaoEncerramentoContaAssociacaoSerializer
from ...models import SolicitacaoEncerramentoContaAssociacao, MotivoRejeicaoEncerramentoContaAssociacao

logger = logging.getLogger(__name__)

class SolicitacaoEncerramentoContaAssociacaoViewset(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = SolicitacaoEncerramentoContaAssociacao.objects.all()
    serializer_class = SolicitacaoEncerramentoContaAssociacaoSerializer

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.pode_apagar:
            self.perform_destroy(obj)
        else:
            return Response({'mensagem': 'Essa solicitação não pode ser apagada.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def reenviar(self, request, uuid):
        solicitacao = self.get_object()

        if not solicitacao.rejeitada:
            erro = {
                'erro': 'status_nao_permite_operacao',
                'mensagem': f'Impossível aprovar solicitação com status diferente de {SolicitacaoEncerramentoContaAssociacao.STATUS_REJEITADA}'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        serializer = SolicitacaoEncerramentoContaAssociacaoSerializer(data=request.data, instance=solicitacao)
        if serializer.is_valid():
            serializer.save()
            solicitacao.reenviar()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'],
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def aprovar(self, request, uuid):
        solicitacao = self.get_object()

        if not solicitacao.pendente:
            erro = {
                'erro': 'status_nao_permite_operacao',
                'mensagem': f'Impossível aprovar solicitação com status diferente de {SolicitacaoEncerramentoContaAssociacao.STATUS_PENDENTE}'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        solicitacao.aprovar()

        serializer = self.get_serializer(solicitacao)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'],
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def rejeitar(self, request, uuid):
        solicitacao = self.get_object()

        motivos_rejeicao_uuid = request.data.get('motivos_rejeicao', [])
        outros_motivos_rejeicao = request.data.get('outros_motivos_rejeicao', '')

        motivos = []
        for motivo_uuid in motivos_rejeicao_uuid:
            try:
                motivo_aprovacao_ressalva = MotivoRejeicaoEncerramentoContaAssociacao.objects.get(uuid=motivo_uuid)
                motivos.append(motivo_aprovacao_ressalva)
            except MotivoRejeicaoEncerramentoContaAssociacao.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto motivo de rejeição para o uuid {motivo_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)


        if not solicitacao.pendente:
            erro = {
                'erro': 'status_nao_permite_operacao',
                'mensagem': f'Impossível aprovar solicitação com status diferente de {SolicitacaoEncerramentoContaAssociacao.STATUS_PENDENTE}'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        solicitacao.motivos_rejeicao.set(motivos)
        solicitacao.outros_motivos_rejeicao = outros_motivos_rejeicao
        solicitacao.reprovar()

        serializer = self.get_serializer(solicitacao)

        return Response(serializer.data, status=status.HTTP_200_OK)

