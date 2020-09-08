from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sme_ptrf_apps.core.api.serializers import NotificacaoSerializer
from sme_ptrf_apps.core.api.serializers.notificacao_serializer import TipoNotificacaoSerializer, RemetenteNotificacaoSerializer, CategoriatificacaoSerializer
from sme_ptrf_apps.core.models import Notificacao
from sme_ptrf_apps.core.services import formata_data


class NotificacaoViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"
    permission_classes = (IsAuthenticated,)
    queryset = Notificacao.objects.all()
    serializer_class = NotificacaoSerializer

    def get_queryset(self):
        qs = Notificacao.objects.all()

        if self.request.query_params.get('lido'):
            qs = qs.filter(lido=(self.request.query_params.get('lido') == 'True'))

        if self.request.query_params.get('tipo'):
            qs = qs.filter(tipo__id=self.request.query_params.get('tipo'))

        if self.request.query_params.get('remetente'):
            qs = qs.filter(remetente__id=self.request.query_params.get('remetente'))

        if self.request.query_params.get('categoria'):
            qs = qs.filter(categoria__id=self.request.query_params.get('categoria'))

        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')
        if data_inicio is not None and data_fim is not None:
            qs = qs.filter(criado_em__range=[data_inicio, data_fim])

        return qs

    def list(self, request, *args, **kwargs):
        datas = sorted(self.get_queryset().dates("criado_em", "day"), reverse=True)
        lista = []
        for data in datas:
            d = {"data": formata_data(data), "infos": NotificacaoSerializer(self.get_queryset().filter(criado_em__year=data.year,
                                                                                                       criado_em__month=data.month,
                                                                                                       criado_em__day=data.day), many=True).data}
            lista.append(d)

        return Response(lista)

    @action(detail=False, methods=['get'], url_path='quantidade-nao-lidos')
    def quantidade_de_nao_lidos(self, request):
        quantidade_nao = Notificacao.objects.filter(lido=False).count()
        data = {
            "quantidade_nao_lidos": quantidade_nao
        }
        return Response(data)

    @action(detail=False, url_path='tabelas')
    def tabelas(self, _):
        def get_valores_from(serializer):
            valores = serializer.Meta.model.get_valores()
            return serializer(valores, many=True).data if valores else []

        result = {
            'tipos_notificacao': get_valores_from(TipoNotificacaoSerializer),
            'remetentes': get_valores_from(RemetenteNotificacaoSerializer),
            'categorias': get_valores_from(CategoriatificacaoSerializer)
        }

        return Response(result)
