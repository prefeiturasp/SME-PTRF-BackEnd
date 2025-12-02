from rest_framework import status
from rest_framework.response import Response
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


class OutroRecursoFiltro(django_filters.FilterSet):
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


class OutrosRecursosPaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = OutroRecurso.objects.all().order_by('nome')
    serializer_class = OutroRecursoSerializer
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = OutroRecursoFiltro

    def destroy(self, request, *args, **kwargs):
        """ Customização de response quando um recurso não for encontrado """
        try:
            self.get_object()
        except (Http404, ObjectDoesNotExist, OutroRecurso.DoesNotExist):
            return Response(
                {"detail": "Recurso não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        return super().destroy(request, *args, **kwargs)
