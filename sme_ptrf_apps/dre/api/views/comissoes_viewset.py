from django.db.models import Q
from uuid import UUID

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError

from sme_ptrf_apps.core.models.recurso import Recurso
from ...models import Comissao

from ..serializers.comissao_serializer import ComissaoSerializer, ComissaoParametrizacaoSerializer

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre,
)


class ComissoesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = Comissao.objects.all()
    serializer_class = ComissaoSerializer

    @action(detail=False, url_path='comissao-responsavel-analise-pc-por-recurso', methods=['get'],
            permission_classes=[IsAuthenticated])
    def comissao_responsavel_analise_pc_por_recurso(self, request):
        recurso_uuid = request.query_params.get('recurso_uuid', None)
        if not recurso_uuid:
            raise DRFValidationError({
                "non_field_errors": "O parâmetro recurso_uuid é obrigatório."
            })

        comissao = self.get_queryset().filter(recursos__uuid=recurso_uuid, responsavel_analise_pc=True).distinct()

        if not comissao.exists():
            raise DRFValidationError({
                "non_field_errors": "Nenhuma comissão encontrada para o recurso fornecido."
            })

        serializer = self.get_serializer(comissao.first(), many=False)
        return Response(serializer.data)


class ComissoesParametrizacaoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = Comissao.objects.all()
    serializer_class = ComissaoParametrizacaoSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        comissoes_uuid = self.request.query_params.get('comissoes_uuid', "")
        recursos_uuid = self.request.query_params.get('recursos_uuid', "")
        responsavel_analise_pc = self.request.query_params.get('responsavel_analise_pc', False)

        filters = Q()
        if comissoes_uuid:
            try:
                comissoes_uuid = [UUID(id_) for id_ in comissoes_uuid.split(',')]
            except ValueError:
                raise DRFValidationError({
                    "non_field_errors": "Por favor, forneça UUIDs de comissões válidos, separados por vírgula."
                })

            filters &= Q(uuid__in=comissoes_uuid)

        if responsavel_analise_pc:
            filters &= Q(responsavel_analise_pc=True)

        if recursos_uuid:
            try:
                recursos_uuid = [UUID(id_) for id_ in recursos_uuid.split(',')]
            except ValueError:
                raise DRFValidationError({
                    "non_field_errors": "Por favor, forneça UUIDs de recursos válidos, separados por vírgula."
                })

            recursos = Recurso.objects.filter(uuid__in=recursos_uuid).values_list('uuid', flat=True)
            if recursos:
                filters &= Q(recursos__uuid__in=recursos)

        return Comissao.objects.filter(filters).order_by('nome').distinct()


    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.membros.exists():
            content = {
                'mensagem': (
                    'Há membros associados a esta comissão. Remova os membros antes de excluir a comissão.'
                )
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(detail=False, url_path='filtro-por-nome', methods=['get'],
            permission_classes=[IsAuthenticated])
    def filtro_por_nome(self, request):
        nome = request.query_params.get('nome', '').strip()
        nome = ' '.join(nome.split())

        if not nome:
            return Response([])

        comissoes = Comissao.objects.filter(nome__icontains=nome).order_by('nome')
        serializer = self.get_serializer(comissoes, many=True)
        return Response(serializer.data)
