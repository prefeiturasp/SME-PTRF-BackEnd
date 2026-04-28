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
    monta_estrutura_associacao,
    barra_status
)

from drf_spectacular.utils import extend_schema_view
from .docs.valores_reprogramados_docs import DOCS


@extend_schema_view(**DOCS)
class ValoresReprogramadosViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = FechamentoPeriodo.objects.all()
    serializer_class = ValoresReprogramadosListSerializer

    def get_queryset(self):
        dre_uuid = self.request.query_params.get("dre_uuid")
        recurso = self.request.recurso if hasattr(self.request, 'recurso') else None

        if dre_uuid:
            try:
                dre = Unidade.dres.get(uuid=dre_uuid)
            except Unidade.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
                }

                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

            qs = FechamentoPeriodo.objects.filter(
                associacao__unidade__dre=dre,
                status='IMPLANTACAO'
            )

            if recurso:
                qs = qs.filter(periodo__recurso=recurso)
                if recurso.legado:
                    qs = qs.filter(
                        Q(associacao__periodos_iniciais__recurso=recurso) |
                        Q(associacao__periodo_inicial__recurso=recurso)
                    )
                else:
                    qs = qs.filter(associacao__periodos_iniciais__recurso=recurso)
            else:
                qs = qs.exclude(associacao__periodo_inicial=None)

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
                if recurso:
                    if recurso.legado:
                        associacao_ids = set()
                        for fechamento in qs.select_related("associacao").all():
                            if fechamento.associacao.get_status_valores_reprogramados(recurso=recurso) in status_list:
                                associacao_ids.add(fechamento.associacao_id)
                        qs = qs.filter(associacao_id__in=associacao_ids)
                    else:
                        qs = qs.filter(
                            associacao__periodos_iniciais__recurso=recurso,
                            associacao__periodos_iniciais__status_valores_reprogramados__in=status_list
                        )
                else:
                    qs = qs.filter(associacao__periodos_iniciais__status_valores_reprogramados__in=status_list)

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
        associacoes_dre = Associacao.objects.filter(unidade__dre=dre).order_by('nome')

        recurso = self.request.recurso if hasattr(self.request, 'recurso') else None

        if recurso:
            associacoes_dre = Associacao.filter_by_recurso(
                queryset=associacoes_dre,
                recurso=recurso,
                considerar_legado=bool(recurso.legado)
            )
        else:
            associacoes_dre = associacoes_dre.exclude(periodo_inicial=None)

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
            if recurso:
                if recurso.legado:
                    associacao_ids = []
                    for associacao in associacoes_dre.all():
                        if associacao.get_status_valores_reprogramados(recurso=recurso) in status_list:
                            associacao_ids.append(associacao.id)
                    associacoes_dre = associacoes_dre.filter(id__in=associacao_ids)
                else:
                    associacoes_dre = associacoes_dre.filter(
                        periodos_iniciais__recurso=recurso,
                        periodos_iniciais__status_valores_reprogramados__in=status_list
                    )
            else:
                associacoes_dre = associacoes_dre.filter(periodos_iniciais__status_valores_reprogramados__in=status_list)

        valores_reprogramados = lista_valores_reprogramados(associacoes_dre, recurso=recurso)

        if valores_reprogramados == "Nenhum tipo de conta definida em Parâmetro DRE":
            erro = {
                'erro': 'Tipo de conta não definida.',
                'mensagem': "Nenhum tipo de conta definida em Parâmetro DRE."
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
        recurso = self.request.recurso if hasattr(self.request, 'recurso') else None

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associacao para o uuid {associacao_uuid} não foi encontrado na base."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        periodo_inicial_associacao = associacao.get_periodo_inicial_associacao(recurso=recurso)
        periodo = periodo_inicial_associacao.periodo_inicial if periodo_inicial_associacao else None
        if not periodo and recurso and recurso.legado and associacao.periodo_inicial:
            if associacao.periodo_inicial.recurso_id == recurso.id:
                periodo = associacao.periodo_inicial
        if not periodo:
            erro = {
                'erro': 'Período inicial não encontrado.',
                'mensagem': "Não foi encontrado período inicial para o recurso selecionado."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        dados = self.request.data.get('dadosForm', None)

        if not dados:
            erro = {
                'erro': 'Dados não informados.',
                'mensagem': "Os dados necessários não foram informados."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        visao_selecionada = self.request.data.get('visao', None)

        if not visao_selecionada:
            erro = {
                'erro': 'Visão não informada.',
                'mensagem': "A visão não foi informada."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        resultado = salvar_e_concluir_valores_reprogramados(
            associacao,
            periodo,
            dados,
            visao_selecionada,
            recurso=recurso
        )

        if not resultado.get("saldo_salvo", False):
            erro = {
                "erro": resultado.get("codigo_erro", "erro_ao_salvar_valores_reprogramados"),
                "mensagem": resultado.get("mensagem", "Não foi possível salvar os valores reprogramados."),
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = {
            "contas": monta_estrutura_valores_reprogramados(associacao, recurso=recurso),
            "associacao": monta_estrutura_associacao(associacao, recurso=recurso)["associacao"]
        }

        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'], url_path='concluir-valores-reprogramados',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def concluir(self, request):
        associacao_uuid = self.request.data.get('associacao_uuid', None)
        recurso = self.request.recurso if hasattr(self.request, 'recurso') else None

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associacao para o uuid {associacao_uuid} não foi encontrado na base."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        periodo_inicial_associacao = associacao.get_periodo_inicial_associacao(recurso=recurso)
        periodo = periodo_inicial_associacao.periodo_inicial if periodo_inicial_associacao else None
        if not periodo and recurso and recurso.legado and associacao.periodo_inicial:
            if associacao.periodo_inicial.recurso_id == recurso.id:
                periodo = associacao.periodo_inicial
        if not periodo:
            erro = {
                'erro': 'Período inicial não encontrado.',
                'mensagem': "Não foi encontrado período inicial para o recurso selecionado."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        dados = self.request.data.get('dadosForm', None)

        if not dados:
            erro = {
                'erro': 'Dados não informados.',
                'mensagem': "Os dados necessários não foram informados."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        visao_selecionada = self.request.data.get('visao', None)

        if not visao_selecionada:
            erro = {
                'erro': 'Visão não informada.',
                'mensagem': "A visão não foi informada."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        resultado = salvar_e_concluir_valores_reprogramados(
            associacao,
            periodo,
            dados,
            visao_selecionada,
            recurso=recurso,
            concluir=True
        )

        if not resultado.get("saldo_salvo", False):
            erro = {
                "erro": resultado.get("codigo_erro", "erro_ao_concluir_valores_reprogramados"),
                "mensagem": resultado.get("mensagem", "Não foi possível concluir os valores reprogramados."),
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = {
            "contas": monta_estrutura_valores_reprogramados(associacao, recurso=recurso),
            "associacao": monta_estrutura_associacao(associacao, recurso=recurso)["associacao"]
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

        recurso = self.request.recurso if hasattr(self.request, 'recurso') else None

        result = {
            "contas": monta_estrutura_valores_reprogramados(associacao, recurso=recurso),
            "associacao": monta_estrutura_associacao(associacao, recurso=recurso)["associacao"]
        }

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='get-status-valores-reprogramados',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def get_status_valores_reprogramados(self, request):
        associacao_uuid = self.request.query_params.get("associacao_uuid")

        recurso = self.request.recurso if hasattr(self.request, 'recurso') else None

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associacao para o uuid {associacao_uuid} não foi encontrado na base."
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = {
            "status": barra_status(associacao, recurso=recurso)
        }

        return Response(result, status=status.HTTP_200_OK)
