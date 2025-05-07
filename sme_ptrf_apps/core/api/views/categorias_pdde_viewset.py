from django.db.models.deletion import ProtectedError

from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from waffle.mixins import WaffleFlagMixin
import django_filters

from ...models import CategoriaPdde, AcaoPdde
from ..serializers.categoria_pdde_serializer import CategoriaPddeSerializer, CategoriasPddeSomatorioTotalSerializer
from ....core.api.utils.pagination import CustomPagination

from sme_ptrf_apps.users.permissoes import PermissaoAPIApenasSmeComLeituraOuGravacao


class CategoriaPddeFiltro(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = CategoriaPdde
        fields = ['nome', ]


class CategoriaPddeViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao]
    lookup_field = 'uuid'
    queryset = CategoriaPdde.objects.all().order_by('nome')
    serializer_class = CategoriaPddeSerializer
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = CategoriaPddeFiltro

    def validar_campos(self, request):
        nome = request.data.get('nome')
        if not nome:
            raise serializers.ValidationError(
                {"nome": "Nome do Programa PDDE não foi informado."}
            )
        return nome

    def create(self, request):
        """ Método acionado antes do validate do Serializer para
            validação de constraints da Model (ao Criar)"""

        nome = self.validar_campos(request)
        if CategoriaPdde.objects.filter(nome__iexact=nome).first():
            raise serializers.ValidationError(
                {
                    "erro": "Duplicated",
                    "detail": ("Erro ao criar Programa PDDE. Já existe um " +
                               "Programa PDDE cadastrado com este nome.")
                }
            )
        return super().create(request)

    def update(self, request, *args, **kwargs):
        """ Método acionado antes do validate do Serializer
            para validação de constraints da Model (Ao Atualizar)"""

        obj = self.get_object()
        nome = request.data.get('nome')
        if CategoriaPdde.objects.exclude(pk=obj.pk).filter(nome__iexact=nome).first():
            raise serializers.ValidationError(
                {
                    "erro": "Duplicated",
                    "detail": ("Erro ao atualizar Programa PDDE. Já existe um " +
                               "Programa PDDE cadastrado com este nome.")
                }
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.acaopdde_set.count() > 0:
            content = {
                'erro': 'ProtectedError',
                'mensagem': ("Não é possível excluir. " +
                            "Este programa ainda está vinculado há alguma ação.")
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(obj)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='totais')
    def somatorio_total_por_categorias(self, request):
        serializer = CategoriasPddeSomatorioTotalSerializer(instance=None)
        return Response(serializer.to_representation(None), status=status.HTTP_200_OK)