from django.db.models.deletion import ProtectedError

from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from waffle.mixins import WaffleFlagMixin
import django_filters

from ...models import CategoriaPdde, AcaoPdde
from ..serializers.categoria_pdde_serializer import CategoriaPddeSerializer
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
                {"nome": "Nome da Categoria PDDE não foi informado."}
            )
        return nome

    def create(self, request):
        """ Método acionado antes do validate do Serializer para
            validação de constraints da Model (ao Criar)"""

        nome = self.validar_campos(request)
        try:
            CategoriaPdde.objects.get(nome=nome)
            raise serializers.ValidationError(
                {
                    "erro": "Duplicated",
                    "detail": ("Erro ao criar Categoria PDDE. Já existe uma " +
                               "Categoria PDDE cadastrada com este nome.")
                }
            )
        except CategoriaPdde.DoesNotExist:
            # Não existe nenhuma Categoria PDDE cadastrada com o nome informado,
            # ao cadastrar uma Categoria PDDE
            pass
        return super().create(request)

    def update(self, request, *args, **kwargs):
        """ Método acionado antes do validate do Serializer
            para validação de constraints da Model (Ao Atualizar)"""

        obj = self.get_object()
        nome = request.data.get('nome')
        try:
            CategoriaPdde.objects.exclude(pk=obj.pk).get(nome=nome)
            raise serializers.ValidationError(
                {
                    "erro": "Duplicated",
                    "detail": ("Erro ao atualizar Categoria PDDE. Já existe uma " +
                               "Categoria PDDE cadastrada com este nome.")
                }
            )
        except CategoriaPdde.DoesNotExist:
            # Não existe nenhuma Categoria PDDE cadastrada com o nome informado,
            # ao atualizar uma Categoria PDDE
            pass
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        acao_pdde_uuid = self.request.query_params.get('acao_pdde_uuid')

        # verificando se a categoria está vinculada à ação pdde que está sendo editada
        acao_pdde = AcaoPdde.objects.filter(uuid=acao_pdde_uuid, categoria=obj).first()
        if acao_pdde:
            # verificando se existe mais ações pdde vinculadas à categoria com excção da ação pdde que está sendo editada
            acoes_quantidade = AcaoPdde.objects.filter(categoria=obj).exclude(id=acao_pdde.id).count()
            if acoes_quantidade > 0:
                content = {
                    'erro': 'ProtectedError',
                    'mensagem': ("Essa operação não pode ser realizada. " +
                                "Há Ações PDDE vinculadas a esta categoria.")
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            # excluindo uma categoria de outra ação pdde que não está sendo editada
            # buscando ações pdde vinculadas à categoria
            acoes_pdde = AcaoPdde.objects.filter(categoria=obj).count()
            if acoes_pdde > 0:
                content = {
                    'erro': 'ProtectedError',
                    'mensagem': ("Essa operação não pode ser realizada. " +
                                "Há Ações PDDE vinculadas a esta categoria.")
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(obj)

        return Response(status=status.HTTP_204_NO_CONTENT)
