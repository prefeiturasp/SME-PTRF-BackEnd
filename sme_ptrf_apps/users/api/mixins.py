from rest_framework import status
from rest_framework.response import Response

from sme_ptrf_apps.users.services.unidades_acessiveis_service import (
    filtrar_queryset_pelo_contexto_selecionado,
    unidades_acessiveis_do_usuario,
)


class EscopoPorUnidadesDoUsuarioMixin:
    """Recorta o queryset às unidades que o usuário pode acessar.

    Se associacao uuid vier no retrieve/update/destroy, restringe também à
    UE/associação selecionada no menu

    No list, exige associacao uuid para não listar o PTRF inteiro. A associação
    pedida ainda precisa ser de uma UE acessível — caso contrário a lista vem vazia.
    """

    associacao_unidade_filter = 'associacao__unidade__in'
    exigir_associacao_uuid_no_list = True
    acoes_com_contexto_selecionado = ('retrieve', 'update', 'partial_update', 'destroy')

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(**{
            self.associacao_unidade_filter: unidades_acessiveis_do_usuario(self.request.user),
        })
        if self.action in self.acoes_com_contexto_selecionado:
            contexto_uuid = (
                self.request.query_params.get('associacao__uuid') or
                self.request.query_params.get('associacao_uuid')
            )
            if contexto_uuid:
                qs = filtrar_queryset_pelo_contexto_selecionado(
                    qs, contexto_uuid, self.request.user
                )
        return qs

    def list(self, request, *args, **kwargs):
        if self.exigir_associacao_uuid_no_list:
            associacao_uuid = (
                request.query_params.get('associacao__uuid') or
                request.query_params.get('associacao_uuid')
            )
            if not associacao_uuid:
                return Response(
                    {
                        'erro': 'parametros_requerido',
                        'mensagem': (
                            'É necessário enviar o uuid da associação '
                            '(associacao__uuid) como parâmetro.'
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return super().list(request, *args, **kwargs)
