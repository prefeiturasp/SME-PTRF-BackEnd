from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sme_ptrf_apps.logging.tasks import simular_logs_async
from sme_ptrf_apps.logging.tasks import simular_logs_secundario_async
from sme_ptrf_apps.logging.simulador_de_logs.simulador_de_logs import simular_logs
from sme_ptrf_apps.logging.simulador_de_logs.simulador_de_logs_secundario import simular_logs_secundario


class SimuladorDeLogsAsyncView(APIView):
    def get(self, request, format=None):
        simular_logs_async.delay()
        return Response({"message": "Iniciado o simulador de logs de forma assíncrona."}, status=status.HTTP_202_ACCEPTED)


class SimuladorDeLogsView(APIView):
    def get(self, request, format=None):
        simular_logs()
        return Response({"message": "Executado o simulador de logs."}, status=status.HTTP_202_ACCEPTED)


class SimuladorDeLogsSecundarioAsyncView(APIView):
    def get(self, request, format=None):
        simular_logs_secundario_async.delay()
        return Response({"message": "Iniciado o simulador de logs secundário de forma assíncrona."}, status=status.HTTP_202_ACCEPTED)


class SimuladorDeLogsSecudarioView(APIView):
    def get(self, request, format=None):
        simular_logs_secundario()
        return Response({"message": "Executado o simulador de logs secundário."}, status=status.HTTP_202_ACCEPTED)
