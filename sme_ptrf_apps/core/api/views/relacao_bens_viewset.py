from io import BytesIO
from tempfile import NamedTemporaryFile

from django.core.files import File
from django.http import HttpResponse
from openpyxl.writer.excel import save_virtual_workbook
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.models import (
    ContaAssociacao,
    Periodo,
    PrestacaoConta,
    RelacaoBens,
)
from sme_ptrf_apps.core.services.relacao_bens import gerar


class RelacaoBensViewSet(GenericViewSet):
    permission_classes = [AllowAny]
    queryset = RelacaoBens.objects.all()

    @action(detail=False, methods=['get'])
    def previa(self, request):
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')
        periodo_uuid = self.request.query_params.get('periodo')

        if not conta_associacao_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período e o uuid da conta da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        xlsx = self._gerar_planilha(periodo_uuid, conta_associacao_uuid, previa=True)

        result = BytesIO(save_virtual_workbook(xlsx))

        filename = 'relacao_bens.xlsx'
        response = HttpResponse(
            result,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response


    @action(detail=False, methods=['get'], url_path='documento-final')
    def documento_final(self, request):
        #TODO O endpoint docomento-final da relação de bens não deve mais gerar o documento, apenas baixa-lo.
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')
        periodo_uuid = self.request.query_params.get('periodo')

        if not conta_associacao_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período e o uuid da conta da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        conta_associacao = ContaAssociacao.objects.filter(uuid=conta_associacao_uuid).get()
        periodo = Periodo.objects.filter(uuid=periodo_uuid).get()

        prestacao_conta = PrestacaoConta.objects.filter(conta_associacao=conta_associacao, periodo=periodo).first()
        relacao_bens = RelacaoBens.objects.filter(conta_associacao=conta_associacao, prestacao_conta=prestacao_conta).first()

        if not relacao_bens:
            xlsx = self._gerar_planilha(periodo_uuid, conta_associacao_uuid)

            with NamedTemporaryFile() as tmp:
                xlsx.save(tmp.name)

                relacao_bens, _ = RelacaoBens.objects.update_or_create(conta_associacao=conta_associacao, prestacao_conta=prestacao_conta)
                relacao_bens.arquivo.save(name='relacao_bens.xlsx', content=File(tmp))

        filename = 'relacao_bens.xlsx'
        response = HttpResponse(
            open(relacao_bens.arquivo.path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

    @action(detail=False, methods=['get'], url_path='relacao-bens-info')
    def relacao_bens_info(self, request):
        conta_associacao_uuid = self.request.query_params.get('conta-associacao')
        periodo_uuid = self.request.query_params.get('periodo')
        prestacao_conta = PrestacaoConta.objects.filter(conta_associacao__uuid=conta_associacao_uuid, periodo__uuid=periodo_uuid).first()
        relacao_bens = RelacaoBens.objects.filter(conta_associacao__uuid=conta_associacao_uuid, prestacao_conta=prestacao_conta).first()

        msg = str(relacao_bens) if relacao_bens else 'Documento pendente de geração'
        return Response(msg)

    def _gerar_planilha(self, periodo_uuid, conta_associacao_uuid, previa=False):
        #TODO Remover quando retirar a geração da relação de bens do viewset
        conta_associacao = ContaAssociacao.objects.filter(uuid=conta_associacao_uuid).get()
        periodo = Periodo.objects.filter(uuid=periodo_uuid).get()

        xlsx = gerar(periodo, conta_associacao, previa=previa)
        return xlsx
