from datetime import datetime

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoAPITodosComLeituraOuGravacao

from ...models import Receita, Repasse

from ..serializers import RepasseSerializer


class RepasseViewSet(GenericViewSet):
    queryset = Repasse.objects.all()
    permission_classes = [IsAuthenticated & PermissaoApiUe]

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def pendentes(self, request, *args, **kwargs):
        associacao_uuid = self.request.query_params.get('associacao')

        if not associacao_uuid:
            return Response("uuid da associação é obrigatório.", status=HTTP_400_BAD_REQUEST)

        repasses = Repasse.objects\
            .filter(
                associacao__uuid=associacao_uuid,
                status='PENDENTE')\
            .order_by('-criado_em').all()

        serializer = RepasseSerializer(repasses, many=True)

        return Response(serializer.data)
