import logging

from django.contrib.auth import get_user_model
from django.db.models import Q

from requests import ConnectTimeout, ReadTimeout
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sme_ptrf_apps.users.api.serializers import (
    AlteraEmailSerializer,
    RedefinirSenhaSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserRetrieveSerializer
)
from sme_ptrf_apps.users.models import Grupo, Visao
from sme_ptrf_apps.users.services import SmeIntegracaoException, SmeIntegracaoService, criar_acesso_de_suporte
from sme_ptrf_apps.users.services.unidades_e_permissoes_service import unidades_do_usuario_e_permissoes_na_visao
from sme_ptrf_apps.users.services.validacao_username_service import validar_username
from sme_ptrf_apps.core.models import Unidade

User = get_user_model()


logger = logging.getLogger(__name__)


class UserViewSet(ModelViewSet):
    lookup_field = "id"
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by("name", "id")
    permission_classes = [IsAuthenticated ]

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer

        elif self.action == 'retrieve':
            return UserRetrieveSerializer

        else:
            return UserCreateSerializer

    def get_queryset(self, *args, **kwargs):
        """
        Visão == SME - Se a visão for SME, todos os usuários devem ser retornados, caso tenham alguma visão associada

        Visão == DRE - Se a visão for DRE, devem ser retornados todos os usuários da DRE e das UEs subordinadas

        Visão == UE - Se a visão for UE, devem ser retornados apenas os usuários da unidade
        """
        qs = self.queryset
        qs = qs.exclude(visoes=None)

        visao = self.request.query_params.get('visao')
        unidade_uuid = self.request.query_params.get('unidade_uuid')

        if visao == 'UE':
            qs = qs.filter(unidades__uuid=unidade_uuid)
        elif visao == 'DRE':
            unidades_da_dre = Unidade.dres.get(uuid=unidade_uuid).unidades_da_dre.values_list("uuid", flat=True)
            qs = qs.filter(Q(unidades__uuid=unidade_uuid) | Q(unidades__uuid__in=unidades_da_dre) ).distinct('name', 'id')

        groups__id = self.request.query_params.get('groups__id')
        if groups__id:
            qs = qs.filter(groups__id=groups__id)

        search = self.request.query_params.get('search')
        if search is not None:
            qs = qs.filter(Q(name__unaccent__icontains=search) | Q(username=search))

        associacao_uuid = self.request.query_params.get('associacao_uuid')
        if associacao_uuid:
            qs = qs.filter(unidades__associacoes__uuid=associacao_uuid)

        username = self.request.query_params.get('username')
        if username:
            qs = qs.filter(username=username)

        servidor = self.request.query_params.get('servidor')
        if servidor:
            e_servidor = servidor == 'True'
            qs = qs.filter(e_servidor=e_servidor)

        unidade_nome = self.request.query_params.get('unidade_nome')
        if unidade_nome:
            qs = qs.filter(unidades__nome__unaccent__icontains=unidade_nome)

        return qs

    @action(detail=False, methods=["GET"])
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=True, url_path='altera-email', methods=['patch'])
    def altera_email(self, request, id):
        data = request.data
        serialize = AlteraEmailSerializer()
        validated_data = serialize.validate(data)
        usuario = User.objects.get(username=id)
        instance = serialize.update(usuario, validated_data)
        if isinstance(instance, Response):
            return instance
        return Response(UserSerializer(instance, context={'request': request}).data, status=status.HTTP_200_OK)

    @action(detail=True, url_path='altera-senha', methods=['patch'])
    def altera_senha(self, request, id):
        data = request.data
        serializer = RedefinirSenhaSerializer()
        validated_data = serializer.validate(data)
        usuario = User.objects.get(username=id)
        instance = serializer.update(usuario, validated_data)
        if isinstance(instance, Response):
            return instance
        return Response(UserSerializer(instance, context={'request': request}).data, status=status.HTTP_200_OK)

    @action(detail=False, url_path="grupos", methods=['get'])
    def grupos(self, request):
        logger.info("Buscando grupos para usuario: %s", request.user)
        usuario = request.user
        visao = request.query_params.get('visao')

        if not visao:
            return Response("Parâmetro visão é obrigatório.", status=status.HTTP_400_BAD_REQUEST)

        if visao not in ["SME", "DRE", "UE"]:
            erro = {
                    'erro': 'erro_ao_consultar_grupos',
                    'mensagem': f'Visao {visao} nao foi encontrada. Os valores permitidos sao SME, DRE ou UE'
                }
            logging.info("Erro ao buscar grupos do usuário %s", erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if visao == 'SME':
            try:
                grupos = Grupo.objects.all().order_by('name')
                return Response(
                    [{'id': str(grupo.id), "nome": grupo.name, "descricao": grupo.descricao, "visao": visao} for grupo
                     in grupos])
            except Exception as err:
                erro = {
                    'erro': 'erro_ao_consultar_grupos',
                    'mensagem': str(err)
                }
                logging.info("Erro ao buscar grupos do usuário %s", erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
        elif visao == "DRE":
            try:
                grupos = Grupo.objects.filter(Q(visoes__nome="DRE") | Q(visoes__nome="UE")).order_by('name')
                return Response(
                         [{'id': str(grupo.id), "nome": grupo.name, "descricao": grupo.descricao, "visao": visao} for grupo in grupos])
            except Exception as err:
                erro = {
                    'erro': 'erro_ao_consultar_grupos',
                    'mensagem': str(err)
                }
                logging.info("Erro ao buscar grupos do usuário %s", erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                grupos = Grupo.objects.filter(visoes__nome="UE").order_by('name')
                return Response(
                         [{'id': str(grupo.id), "nome": grupo.name, "descricao": grupo.descricao, "visao": visao} for grupo in grupos])
            except Exception as err:
                erro = {
                    'erro': 'erro_ao_consultar_grupos',
                    'mensagem': str(err)
                }
                logging.info("Erro ao buscar grupos do usuário %s", erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

    # TODO Rever url_path 'usuarios/consultar'. É boa prática em APIs Rest evitar verbos. Poderia ser 'servidores'
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

    @action(detail=False, methods=['get'], url_path='status')
    def usuario_status(self, request):
        from ....core.models import MembroAssociacao, Unidade

        username = request.query_params.get('username')

        if not username:
            return Response("Parâmetro username obrigatório.", status=status.HTTP_400_BAD_REQUEST)

        e_servidor = request.query_params.get('servidor', 'True') == 'True'

        unidade_uuid = request.query_params.get('unidade')
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
        }

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='unidades-e-permissoes-na-visao/(?P<visao>[^/.]+)')
    def unidades_e_permissoes_na_visao(self, request, visao, id):
        from ....core.models import Unidade

        unidade_logada_uuid = request.query_params.get('unidade_logada_uuid')

        if visao not in ["SME", "DRE", "UE"]:
            erro = {
                'erro': 'Visão inválida',
                'mensagem': f"A visão {visao} não é uma visão válida. Esperado UE, DRE ou SME."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if visao != "SME" and not unidade_logada_uuid:
            erro = {
                'erro': 'Parâmetro obrigatório',
                'mensagem': f"Para visões UE e DRE é necessário informar o parâmetro unidade_logada_uuid."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        unidade_logada = None
        if unidade_logada_uuid:
            try:
                unidade_logada = Unidade.objects.get(uuid=unidade_logada_uuid)
            except Unidade.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto unidade para o uuid {unidade_logada_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        unidades_e_permissoes = unidades_do_usuario_e_permissoes_na_visao(
            usuario=self.get_object(),
            visao=visao,
            unidade_logada=unidade_logada
        )

        return Response(unidades_e_permissoes, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='unidades')
    def cria_vinculo_usuario_unidade(self, request, id):
        """ (post) /usuarios/{usuario.id}/unidades/  """
        usuario = self.get_object()

        codigo_eol = request.data.get('codigo_eol')
        if not codigo_eol:
            return Response("Campo 'codigo_eol' não encontrado no payload.", status=status.HTTP_400_BAD_REQUEST)

        usuario.add_unidade_se_nao_existir(codigo_eol=codigo_eol)
        return Response({"mensagem": "Unidade vinculada com sucesso"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='unidades/(?P<codigo_eol>[0-9]+)')
    def deleta_vinculo_usuario_unidade(self, request, codigo_eol, id):
        """ (delete) /usuarios/{usuario.id}/unidades/{codigo_eol}  """
        usuario = self.get_object()
        usuario.remove_unidade_se_existir(codigo_eol=codigo_eol)
        return Response({"mensagem": "Unidade desvinculada com sucesso"}, status=status.HTTP_201_CREATED)

    @action(detail=False, url_path="visoes", methods=['get'])
    def visoes(self, request):
        try:
            visoes = Visao.objects.all().order_by("nome")

            return Response([{'id': str(visao.id), "nome": visao.nome} for visao in visoes])
        except Exception as err:
            erro = {
                'erro': 'erro_ao_consultar_visoes',
                'mensagem': str(err)
            }
            logging.info("Erro ao buscar visoes %s", erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='viabilizar-acesso-suporte')
    def viabilizar_acesso_suporte_usuario_unidade(self, request, id):
        """ (post) /usuarios/{usuario.id}/viabilizar-acesso-suporte/  """
        usuario = self.get_object()

        codigo_eol = request.data.get('codigo_eol')
        if not codigo_eol:
            return Response("Campo 'codigo_eol' não encontrado no payload.", status=status.HTTP_400_BAD_REQUEST)

        try:
            unidade = Unidade.objects.get(codigo_eol=codigo_eol)
        except Unidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto Unidade para o código EOL {codigo_eol} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        criar_acesso_de_suporte(unidade_do_suporte=unidade, usuario_do_suporte=usuario)

        return Response({"mensagem": "Acesso de suporte viabilizado."}, status=status.HTTP_201_CREATED)
