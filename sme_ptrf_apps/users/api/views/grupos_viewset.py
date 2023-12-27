from django_filters import rest_framework as filters
from django.core.exceptions import ValidationError
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from ..serializers import GrupoSerializer
from ...models import Grupo, User, Unidade

class GruposViewSet(mixins.ListModelMixin, GenericViewSet):
    # TODO: Voltar a usar IsAuthenticated
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    lookup_field = 'id'
    queryset = Grupo.objects.all().order_by('name')
    serializer_class = GrupoSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    search_fields = ['name', 'descricao', ]
    filter_fields = ('visoes__id', 'visoes__nome')

    def get_queryset(self, *args, **kwargs):
        """
        Uso do parâmetro visao_base:
        "SME" - Considera os grupos de todas as visões (SME, DRE e UE)

        "DRE" - Considera os grupos de DRE e UE

        "UE"  - Considera os grupos de UE apenas
        """
        qs = self.queryset
        qs = qs.exclude(visoes=None)

        visao_base= self.request.query_params.get('visao_base')

        if visao_base and visao_base not in ['SME', 'DRE', 'UE']:
            raise ValidationError({"visao_base": "O valor do parâmetro visao_base deve ser SME, DRE ou UE"})

        if not visao_base or visao_base == 'SME':
            return qs

        if visao_base  == 'UE':
            return qs.filter(visoes__nome=visao_base)

        if visao_base  == 'DRE':
            return qs.filter(visoes__nome__in=['DRE', 'UE'])

    @extend_schema(parameters=[
        OpenApiParameter(
            name='visao_base',
            description='"UE", "DRE" ou "SME". Para exibirapenas grupos da visão e suas subordinadas. ',
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='grupos-disponiveis-por-acesso-visao')
    def grupos_disponiveis_por_acesso_visao(self, request):
        from sme_ptrf_apps.users.services.gestao_usuario_service import GestaoUsuarioService
        from sme_ptrf_apps.users.api.validations.grupos_acesso_validations import GruposDisponiveisPorAcessoVisaoSerializer

        query = GruposDisponiveisPorAcessoVisaoSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        
        unidade_uuid = request.query_params.get('uuid_unidade')
        unidade = 'SME' if unidade_uuid == 'SME' else Unidade.objects.get(uuid=unidade_uuid)
        
        qs = self.queryset
        qs = qs.exclude(visoes=None)

        usuario = User.objects.get(username=request.query_params.get('username'))
        visao_base= self.request.query_params.get('visao_base')

        if visao_base is None or (visao_base not in ['SME', 'DRE', 'UE']):
            raise ValidationError({"visao_base": "O valor do parâmetro visao_base deve ser SME, DRE ou UE."})

        grupos_acesso_usuario = []
        for group in usuario.groups.all():
            grupos_acesso_usuario.append(group.id)

        gestao_usuario = GestaoUsuarioService(usuario=usuario)
        tipos_unidades_usuario_tem_acesso = gestao_usuario.tipos_unidades_usuario_tem_acesso(unidade_base=unidade, visao_base=visao_base)
        lista_tipos_unidades_usuario_tem_acesso = list(tipos_unidades_usuario_tem_acesso)

        if visao_base == 'UE':
            acessos_disponiveis = qs.filter(visoes__nome="UE").distinct()
        else:
            acessos_disponiveis = qs.filter(visoes__nome__in=lista_tipos_unidades_usuario_tem_acesso).distinct()


        acessos_disponiveis_usuario = []
        for acesso in acessos_disponiveis:
            acessos_disponiveis_usuario.append({
                "id": acesso.id,
                "grupo": acesso.name,
                "descricao": acesso.descricao,
                "possui_acesso": bool(acesso.id in grupos_acesso_usuario)
            })

        return Response(acessos_disponiveis_usuario, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='habilitar-grupo-acesso')
    def habilitar_grupo_acesso(self, request):
        from sme_ptrf_apps.users.api.validations.grupos_acesso_validations import HabilitarGrupoAcessoSerializer

        query = HabilitarGrupoAcessoSerializer(data=request.data)
        query.is_valid(raise_exception=True)

        usuario = User.objects.get(username=request.data.get('username'))
        grupo = Grupo.objects.get(id=request.data.get('id_grupo'))

        usuario.habilita_grupo_acesso(group_id=grupo.id)

        response = {
            "mensagem": "Grupo de acesso habilitado para o usuario."
        }

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='desabilitar-grupo-acesso')
    def desabilitar_grupo_acesso(self, request):
        from sme_ptrf_apps.users.api.validations.grupos_acesso_validations import DesabilitarGrupoAcessoSerializer

        query = DesabilitarGrupoAcessoSerializer(data=request.data)
        query.is_valid(raise_exception=True)

        usuario = User.objects.get(username=request.data.get('username'))
        grupo = Grupo.objects.get(id=request.data.get('id_grupo'))

        usuario.desabilita_grupo_acesso(group_id=grupo.id)

        response = {
            "mensagem": "Grupo de acesso desabiltiado para o usuario."
        }

        return Response(response, status=status.HTTP_200_OK)
