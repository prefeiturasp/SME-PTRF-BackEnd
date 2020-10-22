from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.users.permissoes import PermissaoCRUD

from ....utils.choices_to_json import choices_to_json
from ...models import Ata
from ..serializers import AtaSerializer


class AtasViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoCRUD]
    lookup_field = 'uuid'
    queryset = Ata.objects.all()
    serializer_class = AtaSerializer

    @action(detail=False, url_path='tabelas')
    def tabelas(self, request):

        result = {
            'tipos_ata': choices_to_json(Ata.ATA_CHOICES),
            'tipos_reuniao': choices_to_json(Ata.REUNIAO_CHOICES),
            'convocacoes': choices_to_json(Ata.CONVOCACAO_CHOICES),
            'pareceres': choices_to_json(Ata.PARECER_CHOICES),
        }

        return Response(result)
