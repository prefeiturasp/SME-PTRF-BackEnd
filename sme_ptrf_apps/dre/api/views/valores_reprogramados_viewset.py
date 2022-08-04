from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ....core.models import FechamentoPeriodo
from ....core.models import Unidade, Associacao
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from ....utils.choices_to_json import choices_to_json
from ..serializers.valores_reprogramados_serializer import ValoresReprogramadosListSerializer
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre, PermissaoAPITodosComLeituraOuGravacao
)
from ...services import (
    lista_valores_reprogramados,
    salvar_e_concluir_valores_reprogramados,
    monta_estrutura_valores_reprogramados,
    barra_status
)


class ValoresReprogramadosViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = FechamentoPeriodo.objects.all()
    serializer_class = ValoresReprogramadosListSerializer

    def get_queryset(self):
        dre_uuid = self.request.query_params.get("dre_uuid")

        if dre_uuid:
            try:
                dre = Unidade.dres.get(uuid=dre_uuid)
            except Unidade.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
                }

                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

            qs = FechamentoPeriodo.objects.filter(associacao__unidade__dre=dre).filter(
                status='IMPLANTACAO').exclude(associacao__periodo_inicial=None)

            qs = qs.distinct("associacao__uuid")

            # Filtros
            search = self.request.query_params.get('search')
            if search:
                qs = qs.filter(
                    Q(associacao__nome__unaccent__icontains=search) |
                    Q(associacao__unidade__nome__unaccent__icontains=search) |
                    Q(associacao__unidade__codigo_eol=search)
                )

            tipo_unidade = self.request.query_params.get('tipo_unidade')
            if tipo_unidade:
                qs = qs.filter(associacao__unidade__tipo_unidade=tipo_unidade)

            status_valores_reprogramados = self.request.query_params.get('status')
            status_list = status_valores_reprogramados.split(',') if status_valores_reprogramados else []
            if status_list:
                qs = qs.filter(associacao__status_valores_reprogramados__in=status_list)

            return qs

    @action(detail=False, url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoApiDre])
    def tabelas(self, request):
        result = {
            "status": choices_to_json(Associacao.STATUS_VALORES_REPROGRAMADOS_CHOICES)
        }

        return Response(result)

    @action(detail=False, url_path='lista-associacoes',
            permission_classes=[IsAuthenticated & PermissaoApiDre])
    def lista_associacoes(self, request):
        dre_uuid = self.request.query_params.get("dre_uuid")

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except Unidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # query principal
        associacoes_dre = Associacao.objects.filter(unidade__dre=dre).exclude(
            periodo_inicial=None).order_by('nome')

        # filtros
        search = self.request.query_params.get('search')
        if search:
            associacoes_dre = associacoes_dre.filter(
                Q(nome__unaccent__icontains=search) |
                Q(unidade__nome__unaccent__icontains=search) |
                Q(unidade__codigo_eol=search)
            )

        tipo_unidade = self.request.query_params.get('tipo_unidade')
        if tipo_unidade:
            associacoes_dre = associacoes_dre.filter(unidade__tipo_unidade=tipo_unidade)

        status_valores_reprogramados = self.request.query_params.get('status')
        status_list = status_valores_reprogramados.split(',') if status_valores_reprogramados else []
        if status_list:
            associacoes_dre = associacoes_dre.filter(status_valores_reprogramados__in=status_list)

        valores_reprogramados = lista_valores_reprogramados(associacoes_dre)

        if valores_reprogramados == "Nenhum tipo de conta definida em Parâmetro DRE":
            erro = {
                'erro': 'Tipo de conta não definida.',
                'mensagem': f"Nenhum tipo de conta definida em Parâmetro DRE."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = {
            "valores_reprogramados": valores_reprogramados
        }

        return Response(result)

    @action(detail=False, methods=['patch'], url_path='salvar-valores-reprogramados',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def salvar_valores_reprogramados(self, request):
        associacao_uuid = self.request.data.get('associacao_uuid', None)

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
            periodo = associacao.periodo_inicial
        except Associacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associacao para o uuid {associacao_uuid} não foi encontrado na base."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        dados = self.request.data.get('dadosForm', None)

        if not dados:
            erro = {
                'erro': 'Dados não informados.',
                'mensagem': f"Os dados necessários não foram informados."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        visao_selecionada = self.request.data.get('visao', None)

        if not visao_selecionada:
            erro = {
                'erro': 'Visão não informada.',
                'mensagem': f"A visão não foi informada."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        retorno = salvar_e_concluir_valores_reprogramados(associacao, periodo, dados, visao_selecionada)

        result = {
            "contas": monta_estrutura_valores_reprogramados(associacao),
            "associacao": {
                "uuid": f"{associacao.uuid}",
                "status_valores_reprogramados": associacao.status_valores_reprogramados
            }
        }

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'], url_path='concluir-valores-reprogramados',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def concluir(self, request):
        associacao_uuid = self.request.data.get('associacao_uuid', None)

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
            periodo = associacao.periodo_inicial
        except Associacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associacao para o uuid {associacao_uuid} não foi encontrado na base."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        dados = self.request.data.get('dadosForm', None)

        if not dados:
            erro = {
                'erro': 'Dados não informados.',
                'mensagem': f"Os dados necessários não foram informados."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        visao_selecionada = self.request.data.get('visao', None)

        if not visao_selecionada:
            erro = {
                'erro': 'Visão não informada.',
                'mensagem': f"A visão não foi informada."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        retorno = salvar_e_concluir_valores_reprogramados(associacao, periodo, dados, visao_selecionada, concluir=True)

        result = {
            "contas": monta_estrutura_valores_reprogramados(associacao),
            "associacao": {
                "uuid": f"{associacao.uuid}",
                "status_valores_reprogramados": associacao.status_valores_reprogramados
            }
        }

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='get-valores-reprogramados',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def get_valores_reprogramados(self, request):
        associacao_uuid = self.request.query_params.get("associacao_uuid")

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associacao para o uuid {associacao_uuid} não foi encontrado na base."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = {
            "contas": monta_estrutura_valores_reprogramados(associacao),
            "associacao": {
                "uuid": f"{associacao.uuid}",
                "status_valores_reprogramados": associacao.status_valores_reprogramados
            }
        }

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='get-status-valores-reprogramados',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def get_status_valores_reprogramados(self, request):
        associacao_uuid = self.request.query_params.get("associacao_uuid")

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associacao para o uuid {associacao_uuid} não foi encontrado na base."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = {
            "status": barra_status(associacao)
        }

        return Response(result, status=status.HTTP_200_OK)
