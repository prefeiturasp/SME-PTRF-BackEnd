"""
Módulo de API paragerenciamento dos outros recursos do PAA.

Este módulo concentra os endpoints de listagem, consulta, criação,
atualização e exclusão dos outros recursos do PAA.
Permite a filtragem pelo OutroRecursoFiltro.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
import django_filters
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from waffle.mixins import WaffleFlagMixin
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.paa.models import OutroRecurso
from sme_ptrf_apps.paa.api.serializers.outros_recursos_serializer import OutroRecursoSerializer
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from drf_spectacular.utils import extend_schema_view
from .docs.outros_recursos_docs import DOCS


class OutroRecursoFiltro(django_filters.FilterSet):
    """
    FilterSet responsável pela filtragem dos outros recursos.

    Permite filtrar os objetivos pelos seguintes campos:

    - nome
    - aceita_capital
    - aceita_custeio
    - aceita_livre_aplicacao
    """
    nome = django_filters.CharFilter(lookup_expr='icontains')
    aceita_capital = django_filters.BooleanFilter()
    aceita_custeio = django_filters.BooleanFilter()
    aceita_livre_aplicacao = django_filters.BooleanFilter()

    class Meta:
        model = OutroRecurso
        fields = [
            'nome',
            'aceita_capital',
            'aceita_custeio',
            'aceita_livre_aplicacao'
        ]


@extend_schema_view(**DOCS)
class OutrosRecursosPaaViewSet(WaffleFlagMixin, ModelViewSet):
    """
    ViewSet responsável pelo gerenciamento dos outros recursos do PAA.

    Disponibiliza operações de listagem, consulta, criação, atualização
    e exclusão dos outros recursos do PAA.
    Permite a filtragem pelo OutroRecursoFiltro.
    """
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = OutroRecurso.objects.all().order_by('nome')
    serializer_class = OutroRecursoSerializer
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = OutroRecursoFiltro

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """ Customização de response quando um recurso não for encontrado """
        try:
            self.get_object()
        except (Http404, ObjectDoesNotExist, OutroRecurso.DoesNotExist):
            return Response(
                {"detail": "Recurso não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        return super().destroy(request, *args, **kwargs)
