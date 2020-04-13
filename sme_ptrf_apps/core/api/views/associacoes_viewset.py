from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers.associacao_serializer import AssociacaoSerializer

from ...models import Associacao


class AssociacoesViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         GenericViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = Associacao.objects.all()
    serializer_class = AssociacaoSerializer

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return AssociacaoSerializer
        else:
            return AssociacaoSerializer
