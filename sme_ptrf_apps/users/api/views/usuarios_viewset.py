# TODO Substitui user.py que deve ser removida ao fim da implantação da nova gestão de usuários.

import logging
import waffle
import datetime

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

from sme_ptrf_apps.mandatos.models import CargoComposicao
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

from sme_ptrf_apps.users.models import UnidadeEmSuporte

from sme_ptrf_apps.users.services import GestaoUsuarioService

from sme_ptrf_apps.core.api.serializers import UnidadeListSerializer

from waffle.mixins import WaffleFlagMixin

User = get_user_model()

logger = logging.getLogger(__name__)

# TODO Mover para um arquivo de constantes
UUID_OR_SME_REGEX = r'(?:[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}|SME)'


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


class UsuariosViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "gestao-usuarios"
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

        if self.action == 'retrieve':
            qs = self.queryset
            return qs
        else:
            qs = self.queryset
            qs = qs.exclude(visoes=None)

            uuid_unidade_base = self.request.query_params.get('uuid_unidade_base')

            if not uuid_unidade_base or uuid_unidade_base == 'SME':
                return qs.filter(Q(unidades__isnull=False) | Q(visoes__nome='SME')).distinct('name', 'id')

            unidade_base = Unidade.objects.filter(uuid=uuid_unidade_base).first()

            if not unidade_base:
                raise ValidationError(f"Não foi encontrada uma unidade com uuid {uuid_unidade_base}.")

            visao_consulta = 'DRE' if unidade_base.tipo_unidade == 'DRE' else 'UE'

            if visao_consulta == 'UE':
                return qs.filter(unidades__uuid=uuid_unidade_base)

            if visao_consulta == 'DRE':
                unidades_da_dre = Unidade.dres.get(
                    uuid=uuid_unidade_base).unidades_da_dre.values_list("uuid", flat=True)
                return qs.filter(Q(unidades__uuid=uuid_unidade_base) | Q(unidades__uuid__in=unidades_da_dre)).distinct('name', 'id')

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

        flag_historico_de_membros = waffle.flag_is_active(request, 'historico-de-membros')

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

        try:
            user_sig_escola = User.objects.get(username=username)
            info_sig_escola = {
                'info_sig_escola': {
                    'visoes': user_sig_escola.visoes.values_list('nome', flat=True),
                    'unidades': user_sig_escola.unidades.values_list('codigo_eol', flat=True),
                    'user_id': user_sig_escola.id
                },
                'mensagem': 'Usuário encontrado no Sig.Escola.',
            }
        except User.DoesNotExist as e:
            info_sig_escola = {
                'info_sig_escola': None,
                'mensagem': 'Usuário não encontrado no Sig.Escola.',
            }

        visao_base = None
        if unidade:
            visao_base = 'DRE' if unidade.tipo_unidade == 'DRE' else 'UE'
        else:
            visao_base = 'SME' if unidade_uuid == 'SME' else None

        pode_acessar, mensagem_pode_acessar, info_exercicio = pode_acessar_unidade(
            username, e_servidor, visao_base, unidade, flag_historico_de_membros=flag_historico_de_membros)

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

    # TODO Extrair validações para um serializer
    @extend_schema(request=None)
    @action(detail=True, methods=['put'], url_path=f'remover-acessos-unidade-base/(?P<unidade_uuid>{UUID_OR_SME_REGEX})')
    def remover_acessos(self, request, unidade_uuid, id=None):
        usuario = self.get_object()
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
        elif unidade_uuid == 'SME':
            unidade = "SME"

        if not unidade:
            return Response("Parâmetro unidade_uuid obrigatório.", status=status.HTTP_400_BAD_REQUEST)

        if unidade:
            try:
                remover_acessos_a_unidade_e_subordinadas(usuario=usuario, unidade_base=unidade)
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                logger.error('Erro ao remover acessos: %r', e)
                return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='unidades-do-usuario')
    def unidades_do_usuario(self, request):
        from ....core.models import Unidade
        from sme_ptrf_apps.users.api.validations.usuario_validations import UnidadesDoUsuarioSerializer

        query = UnidadesDoUsuarioSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        # Validados no serializer
        usuario = User.objects.get(username=request.query_params.get('username'))
        unidade_uuid = request.query_params.get('uuid_unidade')
        unidade = 'SME' if unidade_uuid == 'SME' else Unidade.objects.get(uuid=unidade_uuid)
        visao_base = request.query_params.get('visao_base')

        gestao_usuario = GestaoUsuarioService(usuario=usuario)
        result = gestao_usuario.unidades_do_usuario(unidade_base=unidade, visao_base=visao_base)

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='habilitar-acesso')
    def habilitar_acesso(self, request):

        from sme_ptrf_apps.users.api.validations.usuario_validations import HabilitarDesabilitarAcessoSerializer

        query = HabilitarDesabilitarAcessoSerializer(data=request.data)
        query.is_valid(raise_exception=True)

        # Validado no serializer
        usuario = User.objects.get(username=request.data.get("username"))
        unidade_uuid = request.data.get('uuid_unidade')
        unidade = 'SME' if unidade_uuid == 'SME' else Unidade.by_uuid(unidade_uuid)

        gestao_usuario = GestaoUsuarioService(usuario=usuario)
        response = gestao_usuario.habilitar_acesso(unidade=unidade)

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='desabilitar-acesso')
    def desabilitar_acesso(self, request):
        from sme_ptrf_apps.users.api.validations.usuario_validations import HabilitarDesabilitarAcessoSerializer

        query = HabilitarDesabilitarAcessoSerializer(data=request.data)
        query.is_valid(raise_exception=True)

        # Validado no serializer
        visao_base = request.data.get('visao_base')
        usuario = User.objects.get(username=request.data.get("username"))
        unidade_uuid = request.data.get('uuid_unidade')
        unidade = 'SME' if unidade_uuid == 'SME' else Unidade.by_uuid(unidade_uuid)
        acesso_concedido_sme = request.data.get('acesso_concedido_sme', False)

        gestao_usuario = GestaoUsuarioService(usuario=usuario)
        response = gestao_usuario.desabilitar_acesso(unidade=unidade, acesso_concedido_sme=acesso_concedido_sme)

        gestao_usuario.remover_grupos_acesso_apos_remocao_acesso_unidade(unidade=unidade, visao_base=visao_base)

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='unidades-disponiveis-para-inclusao')
    def unidades_disponiveis_para_inclusao(self, request):
        from sme_ptrf_apps.users.api.validations.usuario_validations import UnidadesDisponiveisInclusaoSerializer

        query = UnidadesDisponiveisInclusaoSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        # validar no serializer
        usuario = User.objects.get(username=request.query_params.get('username'))
        search = request.query_params.get('search')
        gestao_usuario = GestaoUsuarioService(usuario=usuario)

        result = gestao_usuario.unidades_disponiveis_para_inclusao(search)

        page = self.paginate_queryset(result)
        if page is not None:
            serializer = UnidadeListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='incluir-unidade')
    def incluir_unidade(self, request):
        from sme_ptrf_apps.users.api.validations.usuario_validations import IncluirUnidadeSerializer

        query = IncluirUnidadeSerializer(data=request.data)
        query.is_valid(raise_exception=True)

        usuario = User.objects.get(username=request.data.get("username"))
        unidade = Unidade.by_uuid(request.data.get('uuid_unidade'))

        gestao_usuario = GestaoUsuarioService(usuario=usuario)
        response = gestao_usuario.incluir_unidade(unidade=unidade)

        return Response(response, status=status.HTTP_201_CREATED)


# TODO Mover para um service
# TODO Criar testes unitários
def pode_acessar_unidade(username, e_servidor, visao_base, unidade, flag_historico_de_membros=False):

    info_exercicio = ''

    if e_servidor:
        try:
            info_exercicio = SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor(username)
        except SmeIntegracaoException as e:
            logger.error('Erro ao obter informações de lotação e exercício: %r', e)
            return False, 'Erro ao obter informações de lotação e exercício.', ''

        unidade_exercicio = info_exercicio['unidadeExercicio']['codigo'] if info_exercicio['unidadeExercicio'] else None
        unidade_lotacao = info_exercicio['unidadeLotacao']['codigo'] if info_exercicio['unidadeLotacao'] else None
        logger.info(f'EOL da unidade_exercicio: {unidade_exercicio}')
        logger.info(f'EOL da unidade_lotacao: {unidade_lotacao}')

        unidade_servidor = unidade_exercicio if unidade_exercicio else unidade_lotacao

        if visao_base == 'SME' and not unidade_servidor:
            return False, 'Servidor não está em exercício em uma unidade.', info_exercicio

        if visao_base == 'DRE':
            unidades_dre = unidade.unidades_da_dre.values_list("codigo_eol", flat=True)
            if unidade_servidor != unidade.codigo_eol and unidade_servidor not in unidades_dre:
                return False, 'Servidor em exercício em outra unidade.', info_exercicio

        if visao_base == 'UE':
            e_membro_associacao = eh_membro_associacao(visao_base, username, unidade, eh_servidor=True, flag_historico_de_membros=flag_historico_de_membros)

            em_exercicio_na_unidade = unidade_servidor == unidade.codigo_eol

            if not em_exercicio_na_unidade and e_membro_associacao:
                logger.info('Servidor é membro da associação da unidade, mas não está em exercício nesta unidade.')
                return False, 'O usuário é membro da associação, porém não está em exercício nesta unidade. Favor entrar em contato com a DRE.', info_exercicio

            if not em_exercicio_na_unidade and not e_membro_associacao:
                logger.info('Servidor não está em exercício nesta unidade e não é membro da associação.')
                return False, 'Servidor em exercício em outra unidade.', info_exercicio

            if em_exercicio_na_unidade and not e_membro_associacao:
                logger.info('Servidor não é membro da associação da unidade.')
                return False, 'Servidor não é membro da associação da unidade.', info_exercicio

    else:
        # Inclui a máscara de CPF ao username. O cadastro de membros usa o CPF com máscara para membros não servidores.
        codigo_membro = format_cpf(username)

        mensagens_nao_membro = {
            'SME': 'Usuário não é membro de nenhuma associação.',
            'DRE': 'Usuário não é membro de nenhuma associação da DRE.',
            'UE': 'Usuário não é membro da associação.',
        }

        e_membro_associacao = eh_membro_associacao(visao_base, codigo_membro, unidade, eh_servidor=False, flag_historico_de_membros=flag_historico_de_membros)

        if not e_membro_associacao and visao_base in mensagens_nao_membro:
            return False, mensagens_nao_membro[visao_base], ''

    return True, '', info_exercicio


def eh_membro_associacao(visao_base, codigo_membro, unidade, eh_servidor, flag_historico_de_membros):
    """
    Verifica se o usuário é membro da associação da unidade.
    Decide qual versão da função chamar de acordo com a feature flag "historico-de-membros".
    """
    if flag_historico_de_membros is None:
        raise ValidationError('Parâmetro flag_historico_de_membros obrigatório.')

    if flag_historico_de_membros:
        return eh_membro_associacao_v2(visao_base, codigo_membro, unidade, eh_servidor)
    else:
        return eh_membro_associacao_v1(visao_base, codigo_membro, unidade, eh_servidor)


def eh_membro_associacao_v2(visao_base, codigo_membro, unidade, eh_servidor):
    """
    Verifica se o usuário é membro da associação da unidade.
    Caso a feature flag "historico-de-membros" esteja ativa, a verificação é feita na tabela CargoComposicao.
    """
    logger.info(f'V2 Validando se {codigo_membro} é membro da associação da unidade {unidade}.')
    if visao_base == 'UE':
        if eh_servidor:
            return CargoComposicao.objects.filter(
                ocupante_do_cargo__codigo_identificacao=codigo_membro,
                composicao__associacao__unidade__codigo_eol=unidade.codigo_eol,
                data_inicio_no_cargo__lte=datetime.date.today(),
                data_fim_no_cargo__gte=datetime.date.today()
            ).exists()
        else:
            return CargoComposicao.objects.filter(
                ocupante_do_cargo__cpf_responsavel=codigo_membro,
                composicao__associacao__unidade__codigo_eol=unidade.codigo_eol,
                data_inicio_no_cargo__lte=datetime.date.today(),
                data_fim_no_cargo__gte=datetime.date.today()
            ).exists()

    if visao_base == 'DRE':
        return CargoComposicao.objects.filter(
            ocupante_do_cargo__cpf_responsavel=codigo_membro,
            composicao__associacao__unidade__codigo_eol__in=unidade.unidades_da_dre.values_list("codigo_eol", flat=True),
            data_inicio_no_cargo__lte = datetime.date.today(),
            data_fim_no_cargo__gte = datetime.date.today()
        ).exists()

    if visao_base == 'SME':
        return CargoComposicao.objects.filter(
            ocupante_do_cargo__cpf_responsavel=codigo_membro,
            data_inicio_no_cargo__lte=datetime.date.today(),
            data_fim_no_cargo__gte=datetime.date.today()
        ).exists()

    return False


def eh_membro_associacao_v1(visao_base, codigo_membro, unidade, eh_servidor):
    """
    Verifica se o usuário é membro da associação da unidade.
    Caso a feature flag "historico-de-membros" esteja desativada, a verificação é feita na tabela MembroAssociacao.
    """
    logger.info(f'V1 Validando se {codigo_membro} é membro da associação da unidade {unidade}.')
    if visao_base == 'UE':
        if eh_servidor:
            return MembroAssociacao.objects.filter(
                codigo_identificacao=codigo_membro,
                associacao__unidade__codigo_eol=unidade.codigo_eol
            ).exists()
        else:
            return MembroAssociacao.objects.filter(
                cpf=codigo_membro,
                associacao__unidade__codigo_eol=unidade.codigo_eol
            ).exists()

    if visao_base == 'DRE':
        return MembroAssociacao.objects.filter(
            cpf=codigo_membro,
            associacao__unidade__codigo_eol__in=unidade.unidades_da_dre.values_list("codigo_eol", flat=True)
        ).exists()

    if visao_base == 'SME':
        return MembroAssociacao.objects.filter(cpf=codigo_membro).exists()

    return False

# TODO Mover para um service
# TODO Criar testes unitários
def remover_acessos_a_unidade_e_subordinadas(usuario, unidade_base):
    logger.info(f'Removendo acessos do usuário {usuario} à unidade {unidade_base} e subordinadas.')

    if not unidade_base:
        raise ValidationError('Parâmetro unidade_base obrigatório.')

    if unidade_base != 'SME' and not isinstance(unidade_base, Unidade):
        raise ValidationError('Parâmetro unidade_base deve ser uma string "SME" ou um objeto Unidade.')

    if unidade_base == 'SME':
        visao_base = 'SME'
    else:
        visao_base = 'DRE' if unidade_base.tipo_unidade == 'DRE' else 'UE'

    if visao_base == 'UE':
        logger.info(f'Unidade base é uma UE. Removendo acessos à unidade {unidade_base} para o usuário {usuario}.')
        usuario.remove_unidade_se_existir(unidade_base.codigo_eol)
        return

    if visao_base == 'DRE':
        logger.info(
            f'Unidade base é uma DRE. Removendo acessos à unidade {unidade_base} e subordinadas para o usuário {usuario}.')
        usuario.remove_unidade_se_existir(unidade_base.codigo_eol)
        unidades_subordinadas = unidade_base.unidades_da_dre.values_list("codigo_eol", flat=True)
        for unidade in usuario.unidades.filter(codigo_eol__in=unidades_subordinadas):
            usuario.remove_unidade_se_existir(unidade.codigo_eol)
        return

    if visao_base == 'SME':
        logger.info(f'Unidade base é a SME. Removendo acessos a todas as unidades para o usuário {usuario}.')
        usuario.unidades.clear()
        UnidadeEmSuporte.objects.filter(user=usuario).delete()
        usuario.remove_visao_se_existir('SME')
        return
