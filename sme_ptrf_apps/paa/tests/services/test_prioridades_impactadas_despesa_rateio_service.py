import pytest
from unittest.mock import Mock, patch
from django.db import models

from sme_ptrf_apps.paa.services import (
    PrioridadesPaaImpactadasDespesaRateioService,
    ValidacaoSaldoIndisponivel,
)
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum

pytestmark = pytest.mark.django_db

SERVICE_MODULE = 'sme_ptrf_apps.paa.services.prioridades_impactadas_despesa_rateio_service'


@pytest.fixture
def mock_acao_associacao():
    acao = Mock()
    acao.uuid = 'acao-uuid-123'
    return acao


@pytest.fixture
def mock_associacao():
    associacao = Mock()
    associacao.uuid = 'associacao-uuid-123'
    return associacao


@pytest.fixture
def rateio_attrs(mock_acao_associacao, mock_associacao):
    return {
        'acao_associacao': mock_acao_associacao,
        'associacao': mock_associacao,
        'aplicacao_recurso': TipoAplicacaoOpcoesEnum.CUSTEIO.name,
        'valor_rateio': '500.00',
        'uuid': 'rateio-uuid-123',
    }


@pytest.fixture
def rateio_attrs_sem_tipo_aplicacao(mock_acao_associacao, mock_associacao):
    return {
        'acao_associacao': mock_acao_associacao,
        'associacao': mock_associacao,
        'aplicacao_recurso': None,
        'valor_rateio': '500.00',
        'uuid': 'rateio-uuid-123',
    }


@pytest.fixture
def mock_prioridade():
    prioridade = Mock()
    prioridade.uuid = 'prioridade-uuid-456'
    prioridade.valor_total = 1000.00
    prioridade.tipo_aplicacao = TipoAplicacaoOpcoesEnum.CUSTEIO.name
    prioridade.paa = Mock()
    return prioridade


@pytest.fixture
def mock_qs_vazio():
    mock_qs = Mock(spec=models.QuerySet)
    mock_qs.filter.return_value = mock_qs
    mock_qs.exists.return_value = False
    mock_qs.count.return_value = 0
    mock_qs.values_list.return_value = []
    return mock_qs


class TestInit:

    def test_init_sem_instance(self, rateio_attrs, mock_acao_associacao, mock_associacao):
        """Testa inicialização sem instância de despesa"""
        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)

        assert service.instance_despesa is None
        assert service.rateio == rateio_attrs
        assert service.acao_associacao == mock_acao_associacao
        assert service.associacao == mock_associacao
        assert service.tipo_aplicacao == TipoAplicacaoOpcoesEnum.CUSTEIO.name

    def test_init_com_instance(self, rateio_attrs):
        """Testa inicialização com instância de despesa"""
        mock_despesa = Mock()
        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs, mock_despesa)

        assert service.instance_despesa == mock_despesa

    def test_init_sem_acao_associacao(self, mock_associacao):
        """Testa inicialização quando rateio não tem acao_associacao"""
        rateio = {'acao_associacao': None, 'associacao': mock_associacao, 'aplicacao_recurso': None}
        service = PrioridadesPaaImpactadasDespesaRateioService(rateio)

        assert service.acao_associacao is None

    def test_init_sem_associacao(self, mock_acao_associacao):
        """Testa inicialização quando rateio não tem associacao"""
        rateio = {'acao_associacao': mock_acao_associacao, 'associacao': None, 'aplicacao_recurso': None}
        service = PrioridadesPaaImpactadasDespesaRateioService(rateio)

        assert service.associacao is None

    def test_init_sem_tipo_aplicacao(self, rateio_attrs_sem_tipo_aplicacao):
        """Testa inicialização quando rateio não tem tipo_aplicacao"""
        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs_sem_tipo_aplicacao)

        assert service.tipo_aplicacao is None


class TestValidarPreCondicoes:

    def test_sem_acao_associacao_retorna_false(self, mock_associacao):
        """Testa que retorna False quando acao_associacao é None"""
        rateio = {'acao_associacao': None, 'associacao': mock_associacao, 'aplicacao_recurso': None}
        service = PrioridadesPaaImpactadasDespesaRateioService(rateio)

        assert service._validar_pre_condicoes() is False

    def test_sem_associacao_retorna_false(self, mock_acao_associacao):
        """Testa que retorna False quando associacao é None"""
        rateio = {'acao_associacao': mock_acao_associacao, 'associacao': None, 'aplicacao_recurso': None}
        service = PrioridadesPaaImpactadasDespesaRateioService(rateio)

        assert service._validar_pre_condicoes() is False

    def test_com_todos_atributos_retorna_true(self, rateio_attrs):
        """Testa que retorna True quando todas pré-condições são satisfeitas"""
        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)

        assert service._validar_pre_condicoes() is True


class TestVerificarPrioridadesImpactadas:

    def test_sem_acao_associacao_retorna_lista_vazia(self, mock_associacao):
        """Testa que retorna lista vazia quando pré-condições não são atendidas"""
        rateio = {'acao_associacao': None, 'associacao': mock_associacao, 'aplicacao_recurso': None}
        service = PrioridadesPaaImpactadasDespesaRateioService(rateio)

        result = service.verificar_prioridades_impactadas()

        assert result == []

    def test_sem_associacao_retorna_lista_vazia(self, mock_acao_associacao):
        """Testa que retorna lista vazia quando associacao é None"""
        rateio = {'acao_associacao': mock_acao_associacao, 'associacao': None, 'aplicacao_recurso': None}
        service = PrioridadesPaaImpactadasDespesaRateioService(rateio)

        result = service.verificar_prioridades_impactadas()

        assert result == []

    @patch.object(PrioridadesPaaImpactadasDespesaRateioService, '_buscar_prioridades_impactadas')
    def test_com_pre_condicoes_validas_chama_values(self, mock_buscar, rateio_attrs):
        """Testa que chama values() com os campos corretos"""
        expected = [
            {'uuid': 'prioridade-uuid-456', 'valor_total': 1000.00, 'tipo_aplicacao': 'CUSTEIO'}
        ]
        mock_qs = Mock()
        mock_qs.values.return_value = expected
        mock_buscar.return_value = mock_qs

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        result = service.verificar_prioridades_impactadas()

        mock_qs.values.assert_called_once_with('uuid', 'valor_total', 'tipo_aplicacao')
        assert result == expected

    @patch.object(PrioridadesPaaImpactadasDespesaRateioService, '_buscar_prioridades_impactadas')
    def test_retorna_lista_com_valores(self, mock_buscar, rateio_attrs):
        """Testa que retorna uma lista (não um queryset)"""
        mock_qs = Mock()
        mock_qs.values.return_value = [{'uuid': 'uuid-1', 'valor_total': 100.0, 'tipo_aplicacao': 'CUSTEIO'}]
        mock_buscar.return_value = mock_qs

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        result = service.verificar_prioridades_impactadas()

        assert isinstance(result, list)


class TestLimparValorPrioridadesImpactadas:

    def test_sem_acao_associacao_retorna_lista_vazia(self, mock_associacao):
        """Testa que retorna lista vazia quando pré-condições não são atendidas"""
        rateio = {'acao_associacao': None, 'associacao': mock_associacao, 'aplicacao_recurso': None}
        service = PrioridadesPaaImpactadasDespesaRateioService(rateio)

        result = service.limpar_valor_prioridades_impactadas()

        assert result == []

    @patch.object(PrioridadesPaaImpactadasDespesaRateioService, '_buscar_prioridades_impactadas')
    def test_com_prioridades_impactadas_chama_update(self, mock_buscar, rateio_attrs):
        """Testa que chama update(valor_total=None) nas prioridades impactadas"""
        mock_qs = Mock()
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 2
        mock_qs.values_list.return_value = ['uuid-1', 'uuid-2']
        mock_buscar.return_value = mock_qs

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        service.limpar_valor_prioridades_impactadas()

        mock_qs.update.assert_called_once_with(valor_total=None)

    @patch.object(PrioridadesPaaImpactadasDespesaRateioService, '_buscar_prioridades_impactadas')
    def test_com_prioridades_impactadas_retorna_lista_de_uuids(self, mock_buscar, rateio_attrs):
        """Testa que retorna lista de UUIDs das prioridades impactadas"""
        mock_qs = Mock()
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 2
        mock_qs.values_list.return_value = ['uuid-1', 'uuid-2']
        mock_buscar.return_value = mock_qs

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        result = service.limpar_valor_prioridades_impactadas()

        mock_qs.values_list.assert_called_once_with('uuid', flat=True)
        assert result == ['uuid-1', 'uuid-2']

    @patch.object(PrioridadesPaaImpactadasDespesaRateioService, '_buscar_prioridades_impactadas')
    def test_sem_prioridades_impactadas_nao_chama_update(self, mock_buscar, rateio_attrs):
        """Testa que não chama update quando não há prioridades impactadas"""
        mock_qs = Mock()
        mock_qs.exists.return_value = False
        mock_qs.values_list.return_value = []
        mock_buscar.return_value = mock_qs

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        service.limpar_valor_prioridades_impactadas()

        mock_qs.update.assert_not_called()

    @patch.object(PrioridadesPaaImpactadasDespesaRateioService, '_buscar_prioridades_impactadas')
    def test_sem_prioridades_retorna_lista_vazia(self, mock_buscar, rateio_attrs):
        """Testa que retorna lista vazia quando não há prioridades impactadas"""
        mock_qs = Mock()
        mock_qs.exists.return_value = False
        mock_qs.values_list.return_value = []
        mock_buscar.return_value = mock_qs

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        result = service.limpar_valor_prioridades_impactadas()

        assert result == []


# ============================================================
# Testes de _buscar_prioridades_impactadas
# ============================================================

class TestBuscarPrioridadesImpactadas:

    @patch(f'{SERVICE_MODULE}.Paa')
    @patch(f'{SERVICE_MODULE}.PrioridadePaa.objects')
    def test_filtro_principal_usa_exists_com_paa_em_elaboracao(
        self, mock_queryset, mock_paa_class, rateio_attrs, mock_qs_vazio
    ):
        """Testa que o filtro principal inclui models.Exists com paas_em_elaboracao"""
        mock_queryset.filter.return_value = mock_qs_vazio

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        service._buscar_prioridades_impactadas()

        call_args = mock_queryset.filter.call_args
        assert isinstance(call_args.args[0], models.Exists)

    @patch(f'{SERVICE_MODULE}.Paa')
    @patch(f'{SERVICE_MODULE}.PrioridadePaa.objects')
    def test_com_tipo_aplicacao_aplica_filtro_adicional(
        self, mock_queryset, mock_paa_class, rateio_attrs, mock_qs_vazio
    ):
        """Testa que filtro de tipo_aplicacao é aplicado quando definido"""
        mock_queryset.filter.return_value = mock_qs_vazio

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        service._buscar_prioridades_impactadas()

        mock_qs_vazio.filter.assert_called_once_with(
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name
        )

    @patch(f'{SERVICE_MODULE}.Paa')
    @patch(f'{SERVICE_MODULE}.PrioridadePaa.objects')
    def test_sem_tipo_aplicacao_nao_aplica_filtro_adicional(
        self, mock_queryset, mock_paa_class, rateio_attrs_sem_tipo_aplicacao, mock_qs_vazio
    ):
        """Testa que filtro de tipo_aplicacao NÃO é aplicado quando não definido"""
        mock_queryset.filter.return_value = mock_qs_vazio

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs_sem_tipo_aplicacao)
        service._buscar_prioridades_impactadas()

        # Quando tipo_aplicacao é None e exists() é False, qs.filter não é chamado
        mock_qs_vazio.filter.assert_not_called()

    @patch(f'{SERVICE_MODULE}.ResumoPrioridadesService')
    @patch(f'{SERVICE_MODULE}.Paa')
    @patch(f'{SERVICE_MODULE}.PrioridadePaa.objects')
    def test_com_saldo_insuficiente_prioridade_inclusa_na_lista_afetados(
        self, mock_queryset, mock_paa_class, mock_resumo_service,
        rateio_attrs, mock_prioridade
    ):
        """Testa que prioridade com ValidacaoSaldoIndisponivel é adicionada aos afetados"""
        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 1
        mock_qs.__iter__ = Mock(return_value=iter([mock_prioridade]))

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        mock_resumo_instance = Mock()
        mock_resumo_instance.validar_valor_prioridade.side_effect = ValidacaoSaldoIndisponivel(
            "Saldo insuficiente"
        )
        mock_resumo_service.return_value = mock_resumo_instance

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        service._buscar_prioridades_impactadas()

        mock_qs.filter.assert_any_call(uuid__in=[str(mock_prioridade.uuid)])

    @patch(f'{SERVICE_MODULE}.ResumoPrioridadesService')
    @patch(f'{SERVICE_MODULE}.Paa')
    @patch(f'{SERVICE_MODULE}.PrioridadePaa.objects')
    def test_com_saldo_suficiente_prioridade_nao_inclusa_na_lista_afetados(
        self, mock_queryset, mock_paa_class, mock_resumo_service,
        rateio_attrs, mock_prioridade
    ):
        """Testa que prioridade com saldo suficiente NÃO é adicionada aos afetados"""
        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 1
        mock_qs.__iter__ = Mock(return_value=iter([mock_prioridade]))

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        mock_resumo_instance = Mock()
        mock_resumo_instance.validar_valor_prioridade.return_value = None
        mock_resumo_service.return_value = mock_resumo_instance

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        service._buscar_prioridades_impactadas()

        # Lista de afetados deve estar vazia
        mock_qs.filter.assert_any_call(uuid__in=[])

    @patch(f'{SERVICE_MODULE}.ResumoPrioridadesService')
    @patch(f'{SERVICE_MODULE}.Paa')
    @patch(f'{SERVICE_MODULE}.PrioridadePaa.objects')
    def test_excecao_generica_nao_inclui_prioridade_nos_afetados(
        self, mock_queryset, mock_paa_class, mock_resumo_service,
        rateio_attrs, mock_prioridade
    ):
        """Testa que exceção genérica não adiciona prioridade à lista de afetados"""
        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 1
        mock_qs.__iter__ = Mock(return_value=iter([mock_prioridade]))

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        mock_resumo_instance = Mock()
        mock_resumo_instance.validar_valor_prioridade.side_effect = Exception("Erro inesperado")
        mock_resumo_service.return_value = mock_resumo_instance

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        service._buscar_prioridades_impactadas()

        mock_qs.filter.assert_any_call(uuid__in=[])

    @patch(f'{SERVICE_MODULE}.ResumoPrioridadesService')
    @patch(f'{SERVICE_MODULE}.Paa')
    @patch(f'{SERVICE_MODULE}.PrioridadePaa.objects')
    def test_resumo_prioridades_instanciado_com_paa_da_prioridade(
        self, mock_queryset, mock_paa_class, mock_resumo_service,
        rateio_attrs, mock_prioridade
    ):
        """Testa que ResumoPrioridadesService é instanciado com o paa da prioridade"""
        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 1
        mock_qs.__iter__ = Mock(return_value=iter([mock_prioridade]))

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        mock_resumo_service.return_value = Mock()

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        service._buscar_prioridades_impactadas()

        mock_resumo_service.assert_called_once_with(mock_prioridade.paa)

    @patch(f'{SERVICE_MODULE}.ResumoPrioridadesService')
    @patch(f'{SERVICE_MODULE}.Paa')
    @patch(f'{SERVICE_MODULE}.PrioridadePaa.objects')
    def test_validar_valor_prioridade_chamado_com_parametros_corretos(
        self, mock_queryset, mock_paa_class, mock_resumo_service,
        rateio_attrs, mock_prioridade, mock_acao_associacao
    ):
        """Testa que validar_valor_prioridade é chamado com os parâmetros corretos"""
        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 1
        mock_qs.__iter__ = Mock(return_value=iter([mock_prioridade]))

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        mock_resumo_instance = Mock()
        mock_resumo_service.return_value = mock_resumo_instance

        # Sem instance_despesa (criação) para simplificar
        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        service._buscar_prioridades_impactadas()

        mock_resumo_instance.validar_valor_prioridade.assert_called_once_with(
            valor_total='500.00',
            acao_uuid=mock_acao_associacao.uuid,
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
            recurso=RecursoOpcoesEnum.PTRF.name,
            prioridade_uuid=mock_prioridade.uuid,
            valor_atual_prioridade=0,
        )

    @patch(f'{SERVICE_MODULE}.ResumoPrioridadesService')
    @patch(f'{SERVICE_MODULE}.Paa')
    @patch(f'{SERVICE_MODULE}.PrioridadePaa.objects')
    def test_criacao_despesa_usa_valor_integral_do_rateio(
        self, mock_queryset, mock_paa_class, mock_resumo_service,
        rateio_attrs, mock_prioridade
    ):
        """Testa que em criação (sem instance_despesa) usa o valor integral do rateio"""
        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 1
        mock_qs.__iter__ = Mock(return_value=iter([mock_prioridade]))

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        mock_resumo_instance = Mock()
        mock_resumo_instance.validar_valor_prioridade.side_effect = ValidacaoSaldoIndisponivel(
            "Saldo insuficiente"
        )
        mock_resumo_service.return_value = mock_resumo_instance

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        service._buscar_prioridades_impactadas()

        call_kwargs = mock_resumo_instance.validar_valor_prioridade.call_args.kwargs
        assert call_kwargs['valor_total'] == '500.00'

    @patch(f'{SERVICE_MODULE}.ResumoPrioridadesService')
    @patch(f'{SERVICE_MODULE}.Paa')
    @patch(f'{SERVICE_MODULE}.PrioridadePaa.objects')
    def test_edicao_despesa_calcula_diferenca_entre_novo_e_antigo_rateio(
        self, mock_queryset, mock_paa_class, mock_resumo_service,
        rateio_attrs, mock_prioridade
    ):
        """Testa que em edição o valor = novo_valor_rateio - valor_rateio_antigo"""
        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 1
        mock_qs.__iter__ = Mock(return_value=iter([mock_prioridade]))

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        mock_resumo_instance = Mock()
        mock_resumo_instance.validar_valor_prioridade.side_effect = ValidacaoSaldoIndisponivel(
            "Saldo insuficiente"
        )
        mock_resumo_service.return_value = mock_resumo_instance

        # Rateio existente com valor antigo = 300.00
        mock_rateio_existente = Mock()
        mock_rateio_existente.valor_rateio = '300.00'
        mock_despesa = Mock()
        mock_despesa.rateios.get.return_value = mock_rateio_existente

        # rateio_attrs tem valor_rateio='500.00'
        # diff esperada = 500.00 - 300.00 = 200.0
        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs, mock_despesa)
        service._buscar_prioridades_impactadas()

        call_kwargs = mock_resumo_instance.validar_valor_prioridade.call_args.kwargs
        assert call_kwargs['valor_total'] == 200.0

    @patch(f'{SERVICE_MODULE}.ResumoPrioridadesService')
    @patch(f'{SERVICE_MODULE}.Paa')
    @patch(f'{SERVICE_MODULE}.PrioridadePaa.objects')
    def test_edicao_sem_rateio_correspondente_usa_valor_integral(
        self, mock_queryset, mock_paa_class, mock_resumo_service,
        rateio_attrs, mock_prioridade
    ):
        """Testa que quando o rateio não é encontrado na edição, usa o valor integral"""
        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 1
        mock_qs.__iter__ = Mock(return_value=iter([mock_prioridade]))

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        mock_resumo_instance = Mock()
        mock_resumo_instance.validar_valor_prioridade.side_effect = ValidacaoSaldoIndisponivel(
            "Saldo insuficiente"
        )
        mock_resumo_service.return_value = mock_resumo_instance

        # instance_despesa presente, mas rateio não encontrado
        mock_despesa = Mock()
        mock_despesa.rateios.get.side_effect = Exception("Rateio não encontrado")

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs, mock_despesa)
        service._buscar_prioridades_impactadas()

        call_kwargs = mock_resumo_instance.validar_valor_prioridade.call_args.kwargs
        assert call_kwargs['valor_total'] == '500.00'

    @patch(f'{SERVICE_MODULE}.ResumoPrioridadesService')
    @patch(f'{SERVICE_MODULE}.Paa')
    @patch(f'{SERVICE_MODULE}.PrioridadePaa.objects')
    def test_multiplas_prioridades_afetadas(
        self, mock_queryset, mock_paa_class, mock_resumo_service, rateio_attrs
    ):
        """Testa que múltiplas prioridades com saldo insuficiente são todas incluídas"""
        mock_prioridade_1 = Mock()
        mock_prioridade_1.uuid = 'prioridade-uuid-1'
        mock_prioridade_1.paa = Mock()

        mock_prioridade_2 = Mock()
        mock_prioridade_2.uuid = 'prioridade-uuid-2'
        mock_prioridade_2.paa = Mock()

        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 2
        mock_qs.__iter__ = Mock(return_value=iter([mock_prioridade_1, mock_prioridade_2]))

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        mock_resumo_instance = Mock()
        mock_resumo_instance.validar_valor_prioridade.side_effect = ValidacaoSaldoIndisponivel(
            "Saldo insuficiente"
        )
        mock_resumo_service.return_value = mock_resumo_instance

        service = PrioridadesPaaImpactadasDespesaRateioService(rateio_attrs)
        service._buscar_prioridades_impactadas()

        mock_qs.filter.assert_any_call(
            uuid__in=[str(mock_prioridade_1.uuid), str(mock_prioridade_2.uuid)]
        )
