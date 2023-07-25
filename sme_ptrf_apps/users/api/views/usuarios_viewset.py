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

from brazilnum.cpf import format_cpf

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
from sme_ptrf_apps.core.models import Unidade, MembroAssociacao

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
    # TODO Extrair validações para um serializer
    # TODO Extrair regras de negócio para um service
    @action(detail=False, methods=['get'], url_path='status')
    def usuario_status(self, request):
        from ....core.models import MembroAssociacao, Unidade

        username = request.query_params.get('username')

        if not username:
            return Response("Parâmetro username obrigatório.", status=status.HTTP_400_BAD_REQUEST)

        e_servidor = request.query_params.get('e_servidor', 'True') == 'True'

        unidade_uuid = request.query_params.get('uuid_unidade')
        unidade = None
        if unidade_uuid and unidade_uuid != 'SME':
            try:
                unidade = Unidade.objects.get(uuid=unidade_uuid)
            except Unidade.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto unidade para o uuid {unidade_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # e_servidor_na_unidade = False
        # if e_servidor and unidade:
        #     e_servidor_na_unidade = SmeIntegracaoService.get_cargos_do_rf_na_escola(
        #         rf=username,
        #         codigo_eol=unidade.codigo_eol
        #     ) != []

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

        # onde_e_membro = MembroAssociacao.associacoes_onde_cpf_e_membro(cpf=username) if not e_servidor else []
        try:
            user_sig_escola = User.objects.get(username=username)
            info_sig_escola = {
                'info_sig_escola': {
                    'visoes': user_sig_escola.visoes.values_list('nome', flat=True),
                    'unidades': user_sig_escola.unidades.values_list('codigo_eol', flat=True),
                    'user_id': user_sig_escola.id
                },
                'mensagem': 'Usuário encontrado no Sig.Escola.',
                # 'associacoes_que_e_membro': onde_e_membro,
            }
        except User.DoesNotExist as e:
            info_sig_escola = {
                'info_sig_escola': None,
                'mensagem': 'Usuário não encontrado no Sig.Escola.',
                # 'associacoes_que_e_membro': onde_e_membro,
            }

        visao_base = None
        if unidade:
            visao_base = 'DRE' if unidade.tipo_unidade == 'DRE' else 'UE'
        else:
            visao_base = 'SME' if unidade_uuid == 'SME' else None

        # pode_acessar_unidade = False
        # if e_servidor:
        #     if visao_base == 'SME':
        #         pode_acessar_unidade =

        pode_acessar, mensagem_pode_acessar, info_exercicio = pode_acessar_unidade(username, e_servidor, visao_base, unidade)

        info_membro_nao_servidor = ""
        if not e_servidor:
            membro_associacao = MembroAssociacao.objects.filter(cpf=format_cpf(username)).first()
            if membro_associacao:
                info_membro_nao_servidor = {
                    'nome': membro_associacao.nome,
                    'email': membro_associacao.email,
                    'cpf': membro_associacao.cpf,
                    'associacao': membro_associacao.associacao.nome if membro_associacao.associacao else '',
                    'codigo_eol': membro_associacao.associacao.unidade.codigo_eol if membro_associacao.associacao else '',
                    'cargo_associacao': membro_associacao.cargo_associacao,
                }

        result = {
            'usuario_core_sso': info_core_sso,
            'usuario_sig_escola': info_sig_escola,
            'validacao_username': validar_username(username=username, e_servidor=e_servidor),
            # 'e_servidor_na_unidade': e_servidor_na_unidade,
            'info_membro_nao_servidor': info_membro_nao_servidor,
            'pode_acessar_unidade': {
                'visao_base': visao_base,
                'unidade': unidade_uuid,
                'pode_acessar': pode_acessar,
                'mensagem': mensagem_pode_acessar,
                # TODO Remover info_exercicio do resultado final após implantação. Apenas para debug.
                'info_exercicio': info_exercicio
            }
        }

        return Response(result, status=status.HTTP_200_OK)



# TODO Mover para um service
# TODO Criar testes unitários
def pode_acessar_unidade(username, e_servidor, visao_base, unidade):

    info_exercicio = ''

    if e_servidor:
        try:
            info_exercicio = SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor(username)
        except SmeIntegracaoException as e:
            logger.error('Erro ao obter informações de lotação e exercício: %r', e)
            return False, 'Erro ao obter informações de lotação e exercício.', ''

        unidade_exercicio = info_exercicio['unidadeExercicio']['codigo'] if info_exercicio['unidadeExercicio'] else None
        unidade_lotacao = info_exercicio['unidadeLotacao']['codigo'] if info_exercicio['unidadeLotacao'] else None
        logger.info(f'EOL da unidade_exercicio: {unidade_exercicio}' )
        logger.info(f'EOL da unidade_lotacao: {unidade_lotacao}' )

        unidade_servidor = unidade_exercicio if unidade_exercicio else unidade_lotacao

        if visao_base == 'SME' and not unidade_servidor:
            return False, 'Servidor não está em exercício em uma unidade.', info_exercicio

        if visao_base == 'DRE':
            unidades_dre = unidade.unidades_da_dre.values_list("codigo_eol", flat=True)
            if unidade_servidor != unidade.codigo_eol and unidade_servidor not in unidades_dre:
                return False, 'Servidor em exercício em outra unidade.', info_exercicio

        if visao_base == 'UE' and unidade_servidor != unidade.codigo_eol:
            if  MembroAssociacao.objects.filter(codigo_identificacao=username, associacao__unidade__codigo_eol=unidade.codigo_eol).exists():
                logger.info('Servidor é membro da associação da unidade, mas não está em exercício nesta unidade.')
                return False, 'O usuário é membro da associação, porém não está em exercício nesta unidade. Favor entrar em contato com a DRE.', info_exercicio
            else:
                logger.info('Servidor não está em exercício nesta unidade e não é membro da associação.')
                return False, 'Servidor em exercício em outra unidade.', info_exercicio

    else:
        # Inclui a máscara de CPF ao username. O cadastro de membros usa o CPF com máscara para membros não servidores.
        codigo_membro = format_cpf(username)
        if visao_base == 'SME' and not MembroAssociacao.objects.filter(cpf=codigo_membro).exists():
            return False, 'Usuário não é membro de nenhuma associação.', ''

        if visao_base == 'DRE':
            unidades_dre = unidade.unidades_da_dre.values_list("codigo_eol", flat=True)
            if not MembroAssociacao.objects.filter(cpf=codigo_membro, associacao__unidade__codigo_eol__in=unidades_dre).exists():
                return False, 'Usuário não é membro de nenhuma associação da DRE.', ''

        if visao_base == 'UE' and not MembroAssociacao.objects.filter(cpf=codigo_membro, associacao__unidade__codigo_eol=unidade.codigo_eol).exists():
            return False, 'Usuário não é membro da associação.', ''

    return True, '', info_exercicio
