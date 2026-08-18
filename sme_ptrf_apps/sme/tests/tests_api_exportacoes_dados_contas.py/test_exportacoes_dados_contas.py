import datetime
import json
import pytest

from unittest.mock import Mock

from rest_framework.status import HTTP_201_CREATED
from waffle.models import Flag

from sme_ptrf_apps.sme.tasks import exportar_dados_conta_async
from sme_ptrf_apps.sme.services.exporta_dados_contas_service import ExportacaoDadosContasService
import sme_ptrf_apps.sme.tasks.exportar_dados_contas as exportar_dados_contas_module
import sme_ptrf_apps.sme.services.bb_accountability_client as bb_accountability_client_module

pytestmark = pytest.mark.django_db

DATAS = (datetime.date(2020, 3, 26), datetime.date(2020, 4, 26))
FLAG_INTEGRACAO_API_BB = "premio-excelencia-integracao-api-bb"


def test_exportacoes_dados_contas(jwt_authenticated_client_sme, usuario_permissao_sme, monkeypatch):
    url = f'/api/exportacoes-dados/contas-associacao/?data_inicio={DATAS[0]}&data_final={DATAS[1]}'
    resultado_esperado = {
        'response': 'O arquivo está sendo gerado e será enviado para a central de download após conclusão.'
    }

    # Mock da função exportar_receitas_async
    mock_exportar_dados_conta_async = Mock()
    monkeypatch.setattr(exportar_dados_conta_async, 'delay', mock_exportar_dados_conta_async)

    response = jwt_authenticated_client_sme.get(
        url,
        content_type='multipart/form-data')

    result = json.loads(response.content)

    # Testa o resultado da requisição
    assert response.status_code == HTTP_201_CREATED
    assert result == resultado_esperado

    # Testa se a função mockada foi chamada com os parâmetros corretos
    mock_exportar_dados_conta_async.assert_called_once_with(
        data_inicio='2020-03-26',
        data_final='2020-04-26',
        username=usuario_permissao_sme.username,
        dre_uuid=None
    )


class ExportacaoDadosContasServiceFake:
    instancias = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.exporta_contas_principal_chamado = False
        self.instancias.append(self)

    def exporta_contas_principal(self):
        self.exporta_contas_principal_chamado = True


def _mock_exportacao_dados_contas_service(monkeypatch):
    ExportacaoDadosContasServiceFake.instancias.clear()
    monkeypatch.setattr(
        exportar_dados_contas_module,
        "ExportacaoDadosContasService",
        ExportacaoDadosContasServiceFake,
    )


def test_exportar_dados_conta_async_com_flag_integracao_bb_ativa_passa_usar_integracao_bb_true(monkeypatch):
    Flag.objects.filter(name=FLAG_INTEGRACAO_API_BB).delete()
    Flag.objects.create(name=FLAG_INTEGRACAO_API_BB, everyone=True)
    _mock_exportacao_dados_contas_service(monkeypatch)

    exportar_dados_conta_async.run(
        data_inicio='2020-03-26',
        data_final='2020-04-26',
        username='1235678',
        dre_uuid=None,
    )

    assert len(ExportacaoDadosContasServiceFake.instancias) == 1
    instancia = ExportacaoDadosContasServiceFake.instancias[0]
    assert instancia.kwargs["usar_integracao_bb"] is True
    assert instancia.kwargs["nome_arquivo"] == "dados_contas.csv"
    assert instancia.exporta_contas_principal_chamado is True


def test_exportar_dados_conta_async_com_flag_integracao_bb_inativa_passa_usar_integracao_bb_false(monkeypatch):
    Flag.objects.filter(name=FLAG_INTEGRACAO_API_BB).delete()
    _mock_exportacao_dados_contas_service(monkeypatch)

    exportar_dados_conta_async.run(
        data_inicio='2020-03-26',
        data_final='2020-04-26',
        username='1235678',
        dre_uuid=None,
    )

    assert len(ExportacaoDadosContasServiceFake.instancias) == 1
    instancia = ExportacaoDadosContasServiceFake.instancias[0]
    assert instancia.kwargs["usar_integracao_bb"] is False
    assert instancia.kwargs["nome_arquivo"] == "dados_contas.csv"
    assert instancia.exporta_contas_principal_chamado is True


def test_exportacao_dados_contas_service_com_integracao_bb_usa_cliente_bb(monkeypatch):
    class BBAccountabilityClientFake:
        def __init__(self):
            self.chamadas = []

        def obter_saldo_total(self, agencia, numero_conta):
            self.chamadas.append((agencia, numero_conta))
            return "R$ 1.234,56"

    monkeypatch.setattr(
        bb_accountability_client_module,
        "BBAccountabilityClient",
        BBAccountabilityClientFake,
    )

    service = ExportacaoDadosContasService(usar_integracao_bb=True)
    conta = Mock(id=1, agencia="2801-X", numero_conta="000097935-X")

    cabecalho = [coluna for coluna, _ in service.cabecalho]
    saldo = service._obter_saldo_bancario(conta)

    assert "Saldo_atual_SIG-Escola" in cabecalho
    assert "Saldo Atual do Banco¹" in cabecalho
    assert saldo == "R$ 1.234,56"
    assert service._bb_client.chamadas == [("2801-X", "000097935-X")]
