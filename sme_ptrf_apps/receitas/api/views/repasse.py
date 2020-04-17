from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.viewsets import GenericViewSet

from ...models import Repasse
from ..serializers import RepasseSerializer


class RepasseViewSet(GenericViewSet):

    @action(detail=False, methods=['GET'])
    def pendentes(self, request, *args, **kwargs):
        acao_associacao_uuid = self.request.query_params.get('acao-associacao')
        if not acao_associacao_uuid:
            return Response("uuid da ação-associação não foi passado", status=HTTP_400_BAD_REQUEST)
        
        repasse = Repasse.objects\
            .filter(acao_associacao__uuid=acao_associacao_uuid, status='PENDENTE')\
            .order_by('-criado_em').last()
        
        if not repasse:
            return Response("Repasse não encontrado para não encontrado.", status=HTTP_404_NOT_FOUND)

        serializer = RepasseSerializer(repasse)
        return Response(serializer.data)
