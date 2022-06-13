from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ....core.models import FechamentoPeriodo
from ....core.models import Unidade, Associacao
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from ....utils.choices_to_json import choices_to_json
from ..serializers.valores_reprogramados_serializer import ValoresReprogramadosListSerializer
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre,
)


class ValoresReprogramadosViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = FechamentoPeriodo.objects.all()
    serializer_class = ValoresReprogramadosListSerializer

    def get_queryset(self):
        dre_uuid = self.request.query_params.get("dre_uuid")

        if dre_uuid:
            try:
                dre = Unidade.dres.get(uuid=dre_uuid)
            except Unidade.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
                }

                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

            qs = FechamentoPeriodo.objects.filter(associacao__unidade__dre=dre).filter(
                status='IMPLANTACAO').exclude(associacao__periodo_inicial=None)

            qs = qs.distinct("associacao__uuid")

            # Filtros
            search = self.request.query_params.get('search')
            if search:
                qs = qs.filter(
                    Q(associacao__nome__unaccent__icontains=search) |
                    Q(associacao__unidade__nome__unaccent__icontains=search) |
                    Q(associacao__unidade__codigo_eol=search)
                )

            tipo_unidade = self.request.query_params.get('tipo_unidade')
            if tipo_unidade:
                qs = qs.filter(associacao__unidade__tipo_unidade=tipo_unidade)

            status_valores_reprogramados = self.request.query_params.get('status')
            status_list = status_valores_reprogramados.split(',') if status_valores_reprogramados else []
            if status_list:
                qs = qs.filter(associacao__status_valores_reprogramados__in=status_list)

            return qs

    @action(detail=False, url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoApiDre])
    def tabelas(self, _):
        result = {
            "status": choices_to_json(Associacao.STATUS_VALORES_REPROGRAMADOS_CHOICES)
        }

        return Response(result)
