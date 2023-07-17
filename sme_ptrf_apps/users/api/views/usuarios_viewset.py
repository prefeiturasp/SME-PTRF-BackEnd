# TODO Substitui user.py que deve ser removida ao fim da implantação da nova gestão de usuários.

import logging

from django.contrib.auth import get_user_model
from django.db.models import Q
import django_filters
from django_filters import rest_framework as filters

from requests import ConnectTimeout, ReadTimeout
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from sme_ptrf_apps.users.api.serializers import (
    UsuarioSerializer,
    UsuarioRetrieveSerializer,
    UsuarioCreateSerializer,
)
from sme_ptrf_apps.users.services import (
    SmeIntegracaoException,
    SmeIntegracaoService,
)
from sme_ptrf_apps.users.services.validacao_username_service import validar_username
from sme_ptrf_apps.core.models import Unidade

from django.core.exceptions import ValidationError

User = get_user_model()

logger = logging.getLogger(__name__)


class CustomPagination(PageNumberPagination):
    page_size = 10
    def get_paginated_response(self, data):
        return Response(
            {
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link(),
                },
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'results': data,
            }
        )

class UsuariosFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    username = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    unidades__nome = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = User
        fields = [
            'name',
            'username',
            'email',
            'groups__id',
            'e_servidor',
            'unidades__codigo_eol',
            'unidades__nome',
            'unidades__uuid',
            'visoes__nome',
        ]

class UsuariosViewSet(ModelViewSet):
    lookup_field = "id"
    serializer_class = UsuarioSerializer
    queryset = User.objects.all().order_by("name", "id")
   # TODO: Voltar com a permissão de autenticação
   # permission_classes = [IsAuthenticated ]
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    search_fields = ['name', 'username', ]
    filterset_class = UsuariosFilter

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return super().get_serializer(*args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        uuid_unidade_base = self.request.query_params.get('uuid_unidade_base')

        visao_consulta = None

        if not uuid_unidade_base or uuid_unidade_base == 'SME':
            visao_consulta = 'SME'

        elif uuid_unidade_base:
            unidade_base = Unidade.objects.filter(uuid=uuid_unidade_base).first()
            if unidade_base:
                visao_consulta = 'DRE' if unidade_base.tipo_unidade == 'DRE' else 'UE'

        if visao_consulta:
            context.update({'visao_consulta': visao_consulta})

        return context

    def get_serializer_class(self):
        if self.action == 'list':
            return UsuarioSerializer

        elif self.action == 'retrieve':
            return UsuarioRetrieveSerializer

        else:
            return UsuarioCreateSerializer

    def get_queryset(self, *args, **kwargs):
        """
        Uso do parâmetro codigo_eol_base:
        Texto "SME"    - Considera todos os usuários que tenham alguma visão associada

        EOL de uma DRE - Considera todos os usuários da DRE e das UEs subordinadas

        EOL de uma UE  - Considera apenas os usuários da unidade
        """
        qs = self.queryset
        qs = qs.exclude(visoes=None)

        uuid_unidade_base = self.request.query_params.get('uuid_unidade_base')

        if not uuid_unidade_base or uuid_unidade_base == 'SME':
            return qs

        unidade_base = Unidade.objects.filter(uuid=uuid_unidade_base).first()

        if not unidade_base:
            raise ValidationError(f"Não foi encontrada uma unidade com uuid {uuid_unidade_base}.")

        visao_consulta = 'DRE' if unidade_base.tipo_unidade == 'DRE' else 'UE'

        if visao_consulta  == 'UE':
            return qs.filter(unidades__uuid=uuid_unidade_base)

        if visao_consulta  == 'DRE':
            unidades_da_dre = Unidade.dres.get(uuid=uuid_unidade_base).unidades_da_dre.values_list("uuid", flat=True)
            return qs.filter(Q(unidades__uuid=uuid_unidade_base) | Q(unidades__uuid__in=unidades_da_dre) ).distinct('name', 'id')

    @extend_schema(parameters=[
        OpenApiParameter(
            name='uuid_unidade_base',
            description='UUID da unidade ou "SME". Para exibir usuários da unidade e subordinadas. ',
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # TODO Rever url_path 'usuarios/consultar'. É boa prática em APIs Rest evitar verbos. Poderia ser 'servidores'
    @extend_schema(parameters=[
        OpenApiParameter(
            name='username',
            description='Id do usuário',
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
    ])
    @action(detail=False, methods=['get'], url_path='consultar')
    def consulta_servidor_sgp(self, request):
        username = self.request.query_params.get('username')

        if not username:
            return Response("Parâmetro username obrigatório.", status=status.HTTP_400_BAD_REQUEST)

        try:
            result = SmeIntegracaoService.informacao_usuario_sgp(username)
            return Response(result, status=status.HTTP_200_OK)
        except SmeIntegracaoException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(parameters=[
        OpenApiParameter(
            name='username',
            description='Id do usuário',
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name='e_servidor',
            description='É servidor? ("True" ou "False")',
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name='uuid_unidade',
            description='UUID da unidade base.',
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
    ])
    @action(detail=False, methods=['get'], url_path='status')
    def usuario_status(self, request):
        from ....core.models import MembroAssociacao, Unidade

        username = request.query_params.get('username')

        if not username:
            return Response("Parâmetro username obrigatório.", status=status.HTTP_400_BAD_REQUEST)

        e_servidor = request.query_params.get('e_servidor', 'True') == 'True'

        unidade_uuid = request.query_params.get('uuid_unidade')
        unidade = None
        if unidade_uuid:
            try:
                unidade = Unidade.objects.get(uuid=unidade_uuid)
            except Unidade.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto unidade para o uuid {unidade_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        e_servidor_na_unidade = False
        if e_servidor and unidade:
            e_servidor_na_unidade = SmeIntegracaoService.get_cargos_do_rf_na_escola(
                rf=username,
                codigo_eol=unidade.codigo_eol
            ) != []

        try:
            user_core_sso = SmeIntegracaoService.usuario_core_sso_or_none(username)
            info_core_sso = {
                'info_core_sso': user_core_sso,
                'mensagem': 'Usuário encontrado no CoreSSO.' if user_core_sso else 'Usuário não encontrado no CoreSSO.'
            }
        except SmeIntegracaoException as e:
            info_core_sso = {
                'info_core_sso': None,
                'mensagem': 'Erro ao buscar usuário no CoreSSO!'
            }

        onde_e_membro = MembroAssociacao.associacoes_onde_cpf_e_membro(cpf=username) if not e_servidor else []
        try:
            user_sig_escola = User.objects.get(username=username)
            info_sig_escola = {
                'info_sig_escola': {
                    'visoes': user_sig_escola.visoes.values_list('nome', flat=True),
                    'unidades': user_sig_escola.unidades.values_list('codigo_eol', flat=True),
                    'user_id': user_sig_escola.id
                },
                'mensagem': 'Usuário encontrado no Sig.Escola.',
                'associacoes_que_e_membro': onde_e_membro,
            }
        except User.DoesNotExist as e:
            info_sig_escola = {
                'info_sig_escola': None,
                'mensagem': 'Usuário não encontrado no Sig.Escola.',
                'associacoes_que_e_membro': onde_e_membro,
            }

        result = {
            'usuario_core_sso': info_core_sso,
            'usuario_sig_escola': info_sig_escola,
            'validacao_username': validar_username(username=username, e_servidor=e_servidor),
            'e_servidor_na_unidade': e_servidor_na_unidade,
            'pode_acessar_unidade': {
                'unidade': unidade_uuid,
                'pode_acessar': False,
                'mensagem': 'Servidor não está em execício na unidade.'
            }
        }

        return Response(result, status=status.HTTP_200_OK)

