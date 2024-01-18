from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sme_ptrf_apps.core.tasks import simular_logs_async
from sme_ptrf_apps.logging.simulador_de_logs import simular_logs


class SimuladorDeLogsAsyncView(APIView):
    def get(self, request, format=None):
        simular_logs_async.delay()
        return Response({"message": "Iniciado o simulador de logs de forma assíncrona."}, status=status.HTTP_202_ACCEPTED)


class SimuladorDeLogsView(APIView):
    def get(self, request, format=None):
        simular_logs()
        return Response({"message": "Executado o simulador de logs."}, status=status.HTTP_202_ACCEPTED)
