from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

import django_filters
from waffle.mixins import WaffleFlagMixin

from ...models import AcaoPdde
from ..serializers.acao_pdde_serializer import AcaoPddeSerializer

from ....core.api.utils.pagination import CustomPagination

from sme_ptrf_apps.users.permissoes import PermissaoAPIApenasSmeComLeituraOuGravacao


class AcaoPddeFiltro(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains')
    categoria__uuid = django_filters.CharFilter(field_name="categoria__uuid", lookup_expr="exact")
    categoria__nome = django_filters.CharFilter(field_name="categoria__nome", lookup_expr="icontains")
    aceita_capital = django_filters.BooleanFilter()
    aceita_custeio = django_filters.BooleanFilter()
    aceita_livre_aplicacao = django_filters.BooleanFilter()

    class Meta:
        model = AcaoPdde
        fields = [
            'nome',
            'categoria__uuid',
            'categoria__nome',
            'aceita_capital',
            'aceita_custeio',
            'aceita_livre_aplicacao'
        ]


class AcoesPddeViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated, PermissaoAPIApenasSmeComLeituraOuGravacao]
    lookup_field = 'uuid'
    queryset = AcaoPdde.objects.all().order_by('nome')
    serializer_class = AcaoPddeSerializer
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = AcaoPddeFiltro

    def valida_campos(self, request):
        nome = request.data.get('nome')
        categoria = request.data.get('categoria')
        if not nome:
            raise serializers.ValidationError(
                {"nome": "Nome da ação PDDE não foi informado."}
            )
        if not categoria:
            raise serializers.ValidationError(
                {"categoria": "A Categoria PDDE não foi informada."}
            )
        return nome, categoria

    def create(self, request):
        """ Método acionado antes do validate do Serializer para validação de
            constraints da Model (ao Criar)"""
        nome, categoria = self.valida_campos(request)

        try:
            AcaoPdde.objects.get(nome=nome, categoria=categoria)
            raise serializers.ValidationError({
                "erro": "Duplicated",
                "detail": ("Erro ao criar Ação PDDE. Já existe uma Ação PDDE " +
                           "cadastrada com este nome e categoria.")
            })
        except AcaoPdde.DoesNotExist:
            # Não existe nenhuma Ação PDDE cadastrada com o nome e categoria informados,
            # ao criar uma ação PDDE
            pass
        return super().create(request)

    def update(self, request, *args, **kwargs):
        """ Método acionado antes do validate do Serializer para validação de
            constraints da Model (Ao Atualizar)"""
        obj = self.get_object()
        nome, categoria = self.valida_campos(request)

        try:
            AcaoPdde.objects.exclude(pk=obj.pk).get(nome=nome, categoria=categoria)
            raise serializers.ValidationError({
                    "erro": "Duplicated",
                    "detail": ("Erro ao atualizar Ação PDDE. Já existe uma " +
                               "Ação PDDE cadastrada com este nome e categoria.")
                })
        except AcaoPdde.DoesNotExist:
            # Não existe nenhuma Ação PDDE cadastrada com o nome e categoria informados,
            # ao atualizar uma Ação PDDE
            pass
        return super().update(request, *args, **kwargs)
