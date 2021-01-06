from datetime import datetime

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from sme_ptrf_apps.core.models import Periodo
from sme_ptrf_apps.users.permissoes import PermissaoReceita

from ...models import Receita, Repasse
from ...tipos_aplicacao_recurso_receitas import APLICACAO_CAPITAL, APLICACAO_CUSTEIO
from ..serializers import RepasseSerializer


class RepasseViewSet(GenericViewSet):
    queryset = Repasse.objects.all()
    permission_classes = [IsAuthenticated & PermissaoReceita]

    @action(detail=False, methods=['GET'])
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
