import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from django.db import models

from sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service import (
    PrioridadesPaaImpactadasBaseService,
    ConfirmarExlusaoPrioridadesPaaRecursoProprioService,
)
from sme_ptrf_apps.paa.services import (
    PrioridadesPaaImpactadasReceitasPrevistasPTRFService,
    PrioridadesPaaImpactadasReceitasPrevistasPDDEService,
    PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService,
    PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService,
)
from sme_ptrf_apps.paa.models import (
    ReceitaPrevistaPaa,
    ReceitaPrevistaPdde,
    ReceitaPrevistaOutroRecursoPeriodo,
    RecursoProprioPaa,
)
from sme_ptrf_apps.paa.enums import (
    PaaStatusEnum,
    RecursoOpcoesEnum,
    TipoAplicacaoOpcoesEnum,
)
from sme_ptrf_apps.paa.services import ValidacaoSaldoIndisponivel

pytestmark = pytest.mark.django_db


# Classe concreta para testar a classe base abstrata
class ConcretePrioridadesPaaImpactadasService(PrioridadesPaaImpactadasBaseService):
    """Implementação concreta para testes da classe base"""

    def get_acao_receita(self):
        return self.instance_receita_prevista.acao if self.instance_receita_prevista else None

    def get_recurso(self):
        return RecursoOpcoesEnum.PTRF.name


# Fixtures
@pytest.fixture
def receita_prevista_ptrf_data():
    return {
        'previsao_valor_custeio': '1000.00',
        'previsao_valor_capital': '2000.00',
        'previsao_valor_livre': '500.00',
    }


@pytest.fixture
def receita_prevista_pdde_data():
    return {
        'previsao_valor_custeio': '1500.00',
        'previsao_valor_capital': '2500.00',
        'previsao_valor_livre': '800.00',
        'saldo_custeio': '100.00',
        'saldo_capital': '200.00',
        'saldo_livre': '50.00',
    }


@pytest.fixture
def receita_prevista_outro_recurso_data():
    return {
        'previsao_valor_custeio': '1200.00',
        'previsao_valor_capital': '1800.00',
        'previsao_valor_livre': '600.00',
        'saldo_custeio': '150.00',
        'saldo_capital': '250.00',
        'saldo_livre': '100.00',
    }


@pytest.fixture
def receita_prevista_recurso_proprio_data():
    return {
        'valor': '3000.00',
    }


@pytest.fixture
def mock_acao_associacao():
    acao = Mock()
    acao.uuid = 'acao-uuid-123'
    acao.associacao = Mock()
    acao.associacao.uuid = 'associacao-uuid-123'
    return acao


@pytest.fixture
def mock_acao_pdde():
    acao = Mock()
    acao.uuid = 'acao-pdde-uuid-123'
    acao.programa = Mock()
    acao.programa.uuid = 'programa-uuid-123'
    return acao


@pytest.fixture
def mock_outro_recurso_periodo():
    periodo = Mock()
    periodo.outro_recurso = Mock()
    periodo.outro_recurso.uuid = 'outro-recurso-uuid-123'
    return periodo


@pytest.fixture
def mock_paa():
    paa = Mock()
    paa.uuid = 'paa-uuid-123'
    paa.status = PaaStatusEnum.EM_ELABORACAO.name
    paa.associacao = Mock()
    paa.associacao.uuid = 'associacao-uuid-123'
    return paa


# Testes Base Service (usando classe concreta)
class TestPrioridadesPaaImpactadasBaseService:

    def test_init_sem_instance(self, receita_prevista_ptrf_data):
        """Testa inicialização sem instância de receita prevista"""
        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data)

        assert service.receita_prevista == receita_prevista_ptrf_data
        assert service.instance_receita_prevista is None

    def test_init_com_instance(self, receita_prevista_ptrf_data, mock_acao_associacao, mock_paa):
        """Testa inicialização com instância de receita prevista"""
        instance = Mock()
        instance.acao = mock_acao_associacao
        instance.paa = mock_paa

        service = ConcretePrioridadesPaaImpactadasService(
            receita_prevista_ptrf_data,
            instance
        )

        assert service.instance_receita_prevista == instance

    def test_get_acao_receita_implementado(self, receita_prevista_ptrf_data):
        """Testa que get_acao_receita está implementado na classe concreta"""
        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data)

        # Não deve lançar NotImplementedError
        result = service.get_acao_receita()
        assert result is None

    def test_get_acao_receita_base_lanca_not_implemented(self, receita_prevista_ptrf_data):
        """Testa que a implementação base de get_acao_receita lança NotImplementedError ao ser chamada diretamente"""
        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data)

        with pytest.raises(NotImplementedError):
            PrioridadesPaaImpactadasBaseService.get_acao_receita(service)

    def test__get_valor_custeio_edicao_base_lanca_not_implemented(self, receita_prevista_ptrf_data):
        """Testa que a implementação base de _get_valor_custeio_edicao
            lança NotImplementedError ao ser chamada diretamente"""
        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data)

        with pytest.raises(NotImplementedError):
            PrioridadesPaaImpactadasBaseService._get_valor_custeio_edicao(service)

    def test__get_valor_custeio_atual_base_lanca_not_implemented(self, receita_prevista_ptrf_data):
        """Testa que a implementação base de _get_valor_custeio_atual lança NotImplementedError ao
            ser chamada diretamente"""
        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data)

        with pytest.raises(NotImplementedError):
            PrioridadesPaaImpactadasBaseService._get_valor_custeio_atual(service)

    def test__get_valor_capital_edicao_base_lanca_not_implemented(self, receita_prevista_ptrf_data):
        """Testa que a implementação base de _get_valor_capital_edicao lança NotImplementedError ao
            ser chamada diretamente"""
        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data)

        with pytest.raises(NotImplementedError):
            PrioridadesPaaImpactadasBaseService._get_valor_capital_edicao(service)

    def test__get_valor_capital_atual_base_lanca_not_implemented(self, receita_prevista_ptrf_data):
        """Testa que a implementação base de _get_valor_capital_atual lança NotImplementedError ao
            ser chamada diretamente"""
        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data)

        with pytest.raises(NotImplementedError):
            PrioridadesPaaImpactadasBaseService._get_valor_capital_atual(service)

    def test__get_valor_livre_edicao_base_lanca_not_implemented(self, receita_prevista_ptrf_data):
        """Testa que a implementação base de _get_valor_livre_edicao lança NotImplementedError ao
            ser chamada diretamente"""
        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data)

        with pytest.raises(NotImplementedError):
            PrioridadesPaaImpactadasBaseService._get_valor_livre_edicao(service)

    def test__get_valor_livre_atual_base_lanca_not_implemented(self, receita_prevista_ptrf_data):
        """Testa que a implementação base de _get_valor_livre_atual lança NotImplementedError ao
            ser chamada diretamente"""
        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data)

        with pytest.raises(NotImplementedError):
            PrioridadesPaaImpactadasBaseService._get_valor_livre_atual(service)

    def test_get_recurso_base_lanca_not_implemented(self, receita_prevista_ptrf_data):
        """Testa que a implementação base de get_recurso lança NotImplementedError ao
            ser chamada diretamente"""
        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data)

        with pytest.raises(NotImplementedError):
            PrioridadesPaaImpactadasBaseService.get_recurso(service)

    def test_get_acao_receita_via_super_lanca_not_implemented(self, receita_prevista_ptrf_data):
        """Testa que subclasse que delega get_acao_receita ao super() lança NotImplementedError na inicialização"""
        class ServiceComSuperGetAcaoReceita(PrioridadesPaaImpactadasBaseService):
            def get_acao_receita(self):
                return super().get_acao_receita()

            def get_recurso(self):
                return RecursoOpcoesEnum.PTRF.name

        with pytest.raises(NotImplementedError):
            ServiceComSuperGetAcaoReceita(receita_prevista_ptrf_data)

    def test_get_recurso_implementado(self, receita_prevista_ptrf_data):
        """Testa que get_recurso está implementado na classe concreta"""
        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data)

        # Não deve lançar NotImplementedError
        result = service.get_recurso()
        assert result == RecursoOpcoesEnum.PTRF.name

    def test_classe_base_e_abstrata(self):
        """Testa que a classe base é de fato abstrata"""
        from abc import ABC

        assert issubclass(PrioridadesPaaImpactadasBaseService, ABC)

        # Tentar instanciar diretamente deve falhar
        with pytest.raises(TypeError):
            PrioridadesPaaImpactadasBaseService({})

    def test_validar_pre_condicoes_sem_acao(self, receita_prevista_ptrf_data):
        """Testa validação quando não há ação definida"""

        instance = Mock()
        instance.acao = mock_acao_associacao
        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data, instance)
        service.acao_receita = None
        service.recurso = RecursoOpcoesEnum.PTRF.name

        assert service._validar_pre_condicoes() is False

    def test_validar_pre_condicoes_sem_recurso(self, receita_prevista_ptrf_data, mock_acao_associacao):
        """Testa validação quando não há recurso definido"""
        instance = Mock()
        instance.acao = mock_acao_associacao

        service = ConcretePrioridadesPaaImpactadasService(
            receita_prevista_ptrf_data,
            instance
        )
        service.recurso = None

        assert service._validar_pre_condicoes() is False

    def test_validar_pre_condicoes_com_sucesso(self, receita_prevista_ptrf_data, mock_acao_associacao):
        """Testa validação com sucesso"""
        instance = Mock()
        instance.acao = mock_acao_associacao

        service = ConcretePrioridadesPaaImpactadasService(
            receita_prevista_ptrf_data,
            instance
        )

        assert service._validar_pre_condicoes() is True

    @patch('sme_ptrf_apps.paa.models.Paa')
    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.PrioridadePaa.objects')
    def test_query_base_retorna_queryset_filtrado(
        self,
        mock_queryset,
        mock_paa_class,
        receita_prevista_ptrf_data
    ):
        """Testa que query_base retorna queryset com filtros corretos via Exists(paas_em_elaboracao)"""
        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data)

        result = service._query_base()

        # Verifica que filter foi chamado com Exists como arg posicional e valor_total__isnull=False
        call_args = mock_queryset.filter.call_args
        assert isinstance(call_args.args[0], models.Exists)
        assert call_args.kwargs == {'valor_total__isnull': False}
        assert result == mock_qs

    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.PrioridadePaa.objects')
    def test_verificar_prioridades_impactadas_sem_pre_condicoes(
        self,
        mock_queryset,
        receita_prevista_ptrf_data
    ):
        """Testa verificação quando pré-condições não são atendidas"""
        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data)
        service.acao_receita = None

        result = service.verificar_prioridades_impactadas()

        assert result == []
        mock_queryset.filter.assert_not_called()

    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.PrioridadePaa.objects')
    def test_verificar_prioridades_impactadas_com_pre_condicoes(
        self,
        mock_queryset,
        receita_prevista_ptrf_data,
        mock_acao_associacao
    ):
        """Testa que verificar_prioridades_impactadas retorna lista de dicts com uuid,
        valor_total e tipo_aplicacao quando pré-condições são atendidas"""
        instance = Mock()
        instance.acao = mock_acao_associacao

        service = ConcretePrioridadesPaaImpactadasService(
            receita_prevista_ptrf_data,
            instance
        )

        prioridades_esperadas = [
            {
                'uuid': 'uuid-prioridade-1',
                'valor_total': Decimal('1000.00'),
                'tipo_aplicacao': TipoAplicacaoOpcoesEnum.CUSTEIO.name,
            },
            {
                'uuid': 'uuid-prioridade-2',
                'valor_total': Decimal('500.00'),
                'tipo_aplicacao': TipoAplicacaoOpcoesEnum.CAPITAL.name,
            },
        ]

        mock_qs = Mock(spec=models.QuerySet)
        mock_qs.values.return_value = prioridades_esperadas

        with patch.object(service, '_buscar_prioridades_impactadas', return_value=mock_qs):
            result = service.verificar_prioridades_impactadas()

        assert result == prioridades_esperadas
        mock_qs.values.assert_called_once_with('uuid', 'valor_total', 'tipo_aplicacao')

    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.PrioridadePaa.objects')
    def test_limpar_valor_prioridades_sem_pre_condicoes(
        self,
        mock_queryset,
        receita_prevista_ptrf_data
    ):
        """Testa limpeza quando pré-condições não são atendidas"""

        service = ConcretePrioridadesPaaImpactadasService(receita_prevista_ptrf_data)
        service.acao_receita = None

        result = service.limpar_valor_prioridades_impactadas()

        assert result == []
        mock_queryset.filter.assert_not_called()

    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.PrioridadePaa.objects')
    def test_limpar_valor_prioridades_com_pre_condicoes(
        self,
        mock_queryset,
        receita_prevista_ptrf_data,
        mock_acao_associacao
    ):
        """Testa que limpar_valor_prioridades_impactadas chama update(valor_total=None) e
        retorna lista de uuids quando pré-condições são atendidas e existem prioridades"""
        instance = Mock()
        instance.acao = mock_acao_associacao

        service = ConcretePrioridadesPaaImpactadasService(
            receita_prevista_ptrf_data,
            instance
        )

        uuids_esperados = ['uuid-prioridade-1', 'uuid-prioridade-2']

        mock_qs = Mock(spec=models.QuerySet)
        mock_qs.exists.return_value = True
        mock_qs.values_list.return_value = uuids_esperados

        with patch.object(service, '_buscar_prioridades_impactadas', return_value=mock_qs):
            result = service.limpar_valor_prioridades_impactadas()

        mock_qs.update.assert_called_once_with(valor_total=None)
        mock_qs.values_list.assert_called_once_with('uuid', flat=True)
        assert result == uuids_esperados

    def test_get_acao_uuid_resumo_prioridade_not_implemented(
        self,
        receita_prevista_ptrf_data
    ):
        """Testa que método não implementado lança exceção para tipo desconhecido"""
        # Cria uma instância mock de um tipo não suportado
        instance = Mock()
        # Remove specs para que isinstance falhe
        instance.__class__ = type('UnknownClass', (), {})

        service = ConcretePrioridadesPaaImpactadasService(
            receita_prevista_ptrf_data,
            instance
        )

        with pytest.raises(NotImplementedError):
            service._get_acao_uuid_resumo_prioridade()


# Testes PTRF Service
@pytest.mark.django_db
class TestPrioridadesPaaImpactadasReceitasPrevistasPTRFService:

    def test_get_acao_receita_sem_instance(self, receita_prevista_ptrf_data):
        """Testa get_acao_receita sem instância"""
        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data
        )
        assert service.get_acao_receita() is None

    def test_get_acao_receita_com_instance(
        self,
        receita_prevista_ptrf_data,
        mock_acao_associacao,
        mock_paa
    ):
        """Testa get_acao_receita com instância"""
        instance = Mock(spec=ReceitaPrevistaPaa)
        instance.acao_associacao = mock_acao_associacao
        instance.paa = mock_paa
        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data,
            instance
        )

        assert service.get_acao_receita() == mock_acao_associacao

    def test_get_recurso(self, receita_prevista_ptrf_data):
        """Testa get_recurso retorna PTRF"""
        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data
        )

        assert service.get_recurso() == RecursoOpcoesEnum.PTRF.name

    def test_get_valor_custeio_edicao(
        self,
        receita_prevista_ptrf_data,
        mock_acao_associacao,
        mock_paa
    ):
        """Testa cálculo de valor custeio em edição"""
        instance = Mock(spec=ReceitaPrevistaPaa)
        instance.acao_associacao = mock_acao_associacao
        instance.paa = mock_paa

        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data,
            instance
        )

        valor = service._get_valor_custeio_edicao()
        assert valor == Decimal('1000.00')

    def test_get_valor_custeio_atual(
        self,
        receita_prevista_ptrf_data,
        mock_acao_associacao,
        mock_paa
    ):
        """Testa obtenção de valor custeio atual"""
        instance = Mock(spec=ReceitaPrevistaPaa)
        instance.acao_associacao = mock_acao_associacao
        instance.paa = mock_paa
        instance.previsao_valor_custeio = Decimal('1500.00')

        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data,
            instance
        )

        valor = service._get_valor_custeio_atual()
        assert valor == Decimal('1500.00')

    def test_get_valor_capital_edicao(
        self,
        receita_prevista_ptrf_data,
        mock_acao_associacao,
        mock_paa
    ):
        """Testa cálculo de valor capital em edição"""
        instance = Mock(spec=ReceitaPrevistaPaa)
        instance.acao_associacao = mock_acao_associacao
        instance.paa = mock_paa

        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data,
            instance
        )

        valor = service._get_valor_capital_edicao()
        assert valor == Decimal('2000.00')

    def test_get_valor_livre_edicao(
        self,
        receita_prevista_ptrf_data,
        mock_acao_associacao,
        mock_paa
    ):
        """Testa cálculo de valor livre em edição"""
        instance = Mock(spec=ReceitaPrevistaPaa)
        instance.acao_associacao = mock_acao_associacao
        instance.paa = mock_paa

        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data,
            instance
        )

        valor = service._get_valor_livre_edicao()
        assert valor == Decimal('500.00')

    @patch('sme_ptrf_apps.paa.models.Paa')
    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.PrioridadePaa.objects')
    def test_query_base(
        self,
        mock_queryset,
        mock_paa_class,
        receita_prevista_ptrf_data,
        mock_acao_associacao,
        mock_paa
    ):
        """Testa query base para buscar prioridades"""
        instance = Mock(spec=ReceitaPrevistaPaa)
        instance.acao_associacao = mock_acao_associacao
        instance.paa = mock_paa

        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data,
            instance
        )

        service._query_base()

        assert mock_queryset.filter.called
        assert mock_qs.filter.called

    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.PrioridadePaa.objects')
    def test_verificar_prioridades_impactadas_sem_pre_condicoes(
        self,
        mock_queryset,
        receita_prevista_ptrf_data
    ):
        """Testa verificação quando pré-condições não são atendidas"""
        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data
        )

        result = service.verificar_prioridades_impactadas()

        assert result == []

    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.PrioridadePaa.objects')
    def test_limpar_valor_prioridades_impactadas_sem_pre_condicoes(
        self,
        mock_queryset,
        receita_prevista_ptrf_data
    ):
        """Testa limpeza quando pré-condições não são atendidas"""
        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data
        )

        result = service.limpar_valor_prioridades_impactadas()

        assert result == []


# Testes PDDE Service
@pytest.mark.django_db
class TestPrioridadesPaaImpactadasReceitasPrevistasPDDEService:

    def test_get_recurso(self, receita_prevista_pdde_data):
        """Testa get_recurso retorna PDDE"""
        service = PrioridadesPaaImpactadasReceitasPrevistasPDDEService(
            receita_prevista_pdde_data
        )

        assert service.get_recurso() == RecursoOpcoesEnum.PDDE.name

    def test_get_acao_receita_com_instance(
        self,
        receita_prevista_pdde_data,
        mock_acao_pdde,
        mock_paa
    ):
        """Testa get_acao_receita com instância PDDE"""
        instance = Mock(spec=ReceitaPrevistaPdde)
        instance.acao_pdde = mock_acao_pdde
        instance.paa = mock_paa

        service = PrioridadesPaaImpactadasReceitasPrevistasPDDEService(
            receita_prevista_pdde_data,
            instance
        )

        assert service.get_acao_receita() == mock_acao_pdde

    def test_get_valor_custeio_edicao_com_saldo(
        self,
        receita_prevista_pdde_data,
        mock_acao_pdde,
        mock_paa
    ):
        """Testa cálculo de valor custeio incluindo saldo"""
        instance = Mock(spec=ReceitaPrevistaPdde)
        instance.acao_pdde = mock_acao_pdde
        instance.paa = mock_paa

        service = PrioridadesPaaImpactadasReceitasPrevistasPDDEService(
            receita_prevista_pdde_data,
            instance
        )

        valor = service._get_valor_custeio_edicao()
        # 1500.00 + 100.00 = 1600.00
        assert valor == Decimal('1600.00')

    def test_get_valor_custeio_atual(
        self,
        receita_prevista_pdde_data,
        mock_acao_pdde,
        mock_paa
    ):
        """Testa cálculo de valor custeio incluindo saldo"""
        instance = Mock(spec=ReceitaPrevistaPdde)
        instance.acao_pdde = mock_acao_pdde
        instance.paa = mock_paa
        instance.previsao_valor_custeio = Decimal('2500.00')
        instance.saldo_custeio = Decimal('200.00')

        service = PrioridadesPaaImpactadasReceitasPrevistasPDDEService(
            receita_prevista_pdde_data,
            instance
        )

        valor = service._get_valor_custeio_atual()
        # 2500.00 + 200.00 = 2700.00
        assert valor == Decimal('2700.00')

    def test_get_valor_livre_atual(
        self,
        receita_prevista_pdde_data,
        mock_acao_pdde,
        mock_paa
    ):
        """Testa cálculo de valor livre incluindo saldo"""
        instance = Mock(spec=ReceitaPrevistaPdde)
        instance.acao_pdde = mock_acao_pdde
        instance.paa = mock_paa
        instance.previsao_valor_livre = Decimal('2500.00')
        instance.saldo_livre = Decimal('200.00')

        service = PrioridadesPaaImpactadasReceitasPrevistasPDDEService(
            receita_prevista_pdde_data,
            instance
        )

        valor = service._get_valor_livre_atual()
        # 2500.00 + 200.00 = 2700.00
        assert valor == Decimal('2700.00')

    def test_get_valor_livre_edicao(
        self,
        receita_prevista_pdde_data,
        mock_acao_pdde,
        mock_paa
    ):
        """Testa cálculo de valor livre incluindo saldo"""
        instance = Mock(spec=ReceitaPrevistaPdde)
        instance.acao_pdde = mock_acao_pdde
        instance.paa = mock_paa

        service = PrioridadesPaaImpactadasReceitasPrevistasPDDEService(
            receita_prevista_pdde_data,
            instance
        )

        valor = service._get_valor_livre_edicao()
        # 800.00 + 50.00 = 850.00 (fixture)
        assert valor == Decimal('850.00')

    def test_get_valor_capital_atual_com_saldo(
        self,
        receita_prevista_pdde_data,
        mock_acao_pdde,
        mock_paa
    ):
        """Testa obtenção de valor capital atual incluindo saldo"""
        instance = Mock(spec=ReceitaPrevistaPdde)
        instance.acao_pdde = mock_acao_pdde
        instance.paa = mock_paa
        instance.previsao_valor_capital = Decimal('2500.00')
        instance.saldo_capital = Decimal('200.00')

        service = PrioridadesPaaImpactadasReceitasPrevistasPDDEService(
            receita_prevista_pdde_data,
            instance
        )

        valor = service._get_valor_capital_atual()
        # 2500.00 + 200.00 = 2700.00
        assert valor == Decimal('2700.00')

    def test_get_valor_capital_edicao_com_saldo(
        self,
        receita_prevista_pdde_data,
        mock_acao_pdde,
        mock_paa
    ):
        """Testa obtenção de valor capital atual incluindo saldo"""
        instance = Mock(spec=ReceitaPrevistaPdde)
        instance.acao_pdde = mock_acao_pdde
        instance.paa = mock_paa
        instance.previsao_valor_capital = Decimal('2500.00')
        instance.saldo_capital = Decimal('200.00')

        service = PrioridadesPaaImpactadasReceitasPrevistasPDDEService(
            receita_prevista_pdde_data,
            instance
        )

        valor = service._get_valor_capital_edicao()
        # 2500.00 + 200.00 = 2700.00
        assert valor == Decimal('2700.00')

    @patch('sme_ptrf_apps.paa.models.Paa')
    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.PrioridadePaa.objects')
    def test_query_base(
        self,
        mock_queryset,
        mock_paa_class,
        receita_prevista_pdde_data,
        mock_acao_pdde,
        mock_paa
    ):
        """Testa que _query_base filtra por paa__associacao, acao_pdde, programa_pdde e recurso PDDE"""
        instance = Mock(spec=ReceitaPrevistaPdde)
        instance.acao_pdde = mock_acao_pdde
        instance.paa = mock_paa

        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        service = PrioridadesPaaImpactadasReceitasPrevistasPDDEService(
            receita_prevista_pdde_data,
            instance
        )

        service._query_base()

        assert mock_queryset.filter.called
        assert mock_qs.filter.called
        filter_kwargs = mock_qs.filter.call_args.kwargs
        assert filter_kwargs['paa__associacao'] == mock_paa.associacao
        assert filter_kwargs['acao_pdde'] == mock_acao_pdde
        assert filter_kwargs['programa_pdde'] == mock_acao_pdde.programa
        assert filter_kwargs['recurso'] == RecursoOpcoesEnum.PDDE.name


# Testes Outro Recurso Service
@pytest.mark.django_db
class TestPrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService:

    def test_get_recurso(self, receita_prevista_outro_recurso_data):
        """Testa get_recurso retorna OUTRO_RECURSO"""
        service = PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService(
            receita_prevista_outro_recurso_data
        )

        assert service.get_recurso() == RecursoOpcoesEnum.OUTRO_RECURSO.name

    def test_get_acao_receita_com_instance(
        self,
        receita_prevista_outro_recurso_data,
        mock_outro_recurso_periodo,
        mock_paa
    ):
        """Testa get_acao_receita com instância de outro recurso"""
        instance = Mock(spec=ReceitaPrevistaOutroRecursoPeriodo)
        instance.outro_recurso_periodo = mock_outro_recurso_periodo
        instance.paa = mock_paa

        service = PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService(
            receita_prevista_outro_recurso_data,
            instance
        )

        assert service.get_acao_receita() == mock_outro_recurso_periodo

    def test_get_acao_uuid_resumo_prioridade(
        self,
        receita_prevista_outro_recurso_data,
        mock_outro_recurso_periodo,
        mock_paa
    ):
        """Testa obtenção do UUID para resumo de prioridades"""
        instance = Mock(spec=ReceitaPrevistaOutroRecursoPeriodo)
        instance.outro_recurso_periodo = mock_outro_recurso_periodo
        instance.paa = mock_paa

        service = PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService(
            receita_prevista_outro_recurso_data,
            instance
        )

        uuid = service._get_acao_uuid_resumo_prioridade()
        assert uuid == mock_outro_recurso_periodo.outro_recurso.uuid

    def test_get_valor_custeio_edicao_com_saldo(
        self,
        receita_prevista_outro_recurso_data,
        mock_outro_recurso_periodo,
        mock_paa
    ):
        """Testa _get_valor_custeio_edicao soma previsao_valor_custeio e saldo_custeio
        quando instance_receita_prevista é ReceitaPrevistaOutroRecursoPeriodo"""
        instance = Mock(spec=ReceitaPrevistaOutroRecursoPeriodo)
        instance.outro_recurso_periodo = mock_outro_recurso_periodo
        instance.paa = mock_paa

        service = PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService(
            receita_prevista_outro_recurso_data,
            instance
        )

        valor = service._get_valor_custeio_edicao()
        # 1200.00 + 150.00 = 1350.00
        assert valor == Decimal('1350.00')

    def test_get_valor_custeio_atual_com_saldo(
        self,
        receita_prevista_outro_recurso_data,
        mock_outro_recurso_periodo,
        mock_paa
    ):
        """Testa _get_valor_custeio_atual soma previsao_valor_custeio e saldo_custeio
        quando instance_receita_prevista é ReceitaPrevistaOutroRecursoPeriodo"""
        instance = Mock(spec=ReceitaPrevistaOutroRecursoPeriodo)
        instance.outro_recurso_periodo = mock_outro_recurso_periodo
        instance.paa = mock_paa
        instance.previsao_valor_custeio = Decimal('1200.00')
        instance.saldo_custeio = Decimal('150.00')

        service = PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService(
            receita_prevista_outro_recurso_data,
            instance
        )

        valor = service._get_valor_custeio_atual()
        # 1200.00 + 150.00 = 1350.00
        assert valor == Decimal('1350.00')

    def test_get_valor_capital_edicao_com_saldo(
        self,
        receita_prevista_outro_recurso_data,
        mock_outro_recurso_periodo,
        mock_paa
    ):
        """Testa _get_valor_capital_edicao soma previsao_valor_capital e saldo_capital
        quando instance_receita_prevista é ReceitaPrevistaOutroRecursoPeriodo"""
        instance = Mock(spec=ReceitaPrevistaOutroRecursoPeriodo)
        instance.outro_recurso_periodo = mock_outro_recurso_periodo
        instance.paa = mock_paa

        service = PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService(
            receita_prevista_outro_recurso_data,
            instance
        )

        valor = service._get_valor_capital_edicao()
        # 1800.00 + 250.00 = 2050.00 (fixture)
        assert valor == Decimal('2050.00')

    def test_get_valor_capital_atual_com_saldo(
        self,
        receita_prevista_outro_recurso_data,
        mock_outro_recurso_periodo,
        mock_paa
    ):
        """Testa _get_valor_capital_atual soma previsao_valor_capital e saldo_capital
        quando instance_receita_prevista é ReceitaPrevistaOutroRecursoPeriodo"""
        instance = Mock(spec=ReceitaPrevistaOutroRecursoPeriodo)
        instance.outro_recurso_periodo = mock_outro_recurso_periodo
        instance.paa = mock_paa
        instance.previsao_valor_capital = Decimal('1200.00')
        instance.saldo_capital = Decimal('150.00')

        service = PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService(
            receita_prevista_outro_recurso_data,
            instance
        )

        valor = service._get_valor_capital_atual()
        # 1200.00 + 150.00 = 1350.00
        assert valor == Decimal('1350.00')

    def test_get_valor_livre_atual_com_saldo(
        self,
        receita_prevista_outro_recurso_data,
        mock_outro_recurso_periodo,
        mock_paa
    ):
        """Testa _get_valor_livre_atual soma previsao_valor_custeio e saldo_custeio
        quando instance_receita_prevista é ReceitaPrevistaOutroRecursoPeriodo"""
        instance = Mock(spec=ReceitaPrevistaOutroRecursoPeriodo)
        instance.outro_recurso_periodo = mock_outro_recurso_periodo
        instance.paa = mock_paa
        instance.previsao_valor_livre = Decimal('1200.00')
        instance.saldo_livre = Decimal('150.00')

        service = PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService(
            receita_prevista_outro_recurso_data,
            instance
        )

        valor = service._get_valor_livre_atual()
        # 1200.00 + 150.00 = 1350.00
        assert valor == Decimal('1350.00')

    def test_get_valor_livre_edicao_com_saldo(
        self,
        receita_prevista_outro_recurso_data,
        mock_outro_recurso_periodo,
        mock_paa
    ):
        instance = Mock(spec=ReceitaPrevistaOutroRecursoPeriodo)
        instance.outro_recurso_periodo = mock_outro_recurso_periodo
        instance.paa = mock_paa

        service = PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService(
            receita_prevista_outro_recurso_data,
            instance
        )

        valor = service._get_valor_livre_edicao()
        # 600.00 + 100.00 = 700.00 (fixture)
        assert valor == Decimal('700.00')

    @patch('sme_ptrf_apps.paa.models.Paa')
    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.PrioridadePaa.objects')
    def test_query_base(
        self,
        mock_queryset,
        mock_paa_class,
        receita_prevista_outro_recurso_data,
        mock_outro_recurso_periodo,
        mock_paa
    ):
        """Testa que _query_base filtra por paa__associacao, outro_recurso e recurso OUTRO_RECURSO"""
        instance = Mock(spec=ReceitaPrevistaOutroRecursoPeriodo)
        instance.outro_recurso_periodo = mock_outro_recurso_periodo
        instance.paa = mock_paa

        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        service = PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService(
            receita_prevista_outro_recurso_data,
            instance
        )

        service._query_base()

        assert mock_queryset.filter.called
        assert mock_qs.filter.called
        filter_kwargs = mock_qs.filter.call_args.kwargs
        assert filter_kwargs['paa__associacao'] == mock_paa.associacao
        assert filter_kwargs['outro_recurso'] == mock_outro_recurso_periodo.outro_recurso
        assert filter_kwargs['recurso'] == RecursoOpcoesEnum.OUTRO_RECURSO.name


# Testes Recurso Próprio Service
@pytest.mark.django_db
class TestPrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService:

    def test_get_recurso(self, receita_prevista_recurso_proprio_data):
        """Testa get_recurso retorna RECURSO_PROPRIO"""
        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(
            receita_prevista_recurso_proprio_data
        )

        assert service.get_recurso() == RecursoOpcoesEnum.RECURSO_PROPRIO.name

    def test_get_acao_receita_retorna_enum(
        self,
        receita_prevista_recurso_proprio_data,
        mock_paa
    ):
        """Testa que get_acao_receita retorna o próprio enum para recurso próprio"""
        instance = Mock(spec=RecursoProprioPaa)
        instance.paa = mock_paa
        instance.associacao = mock_paa.associacao

        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(
            receita_prevista_recurso_proprio_data,
            instance
        )

        assert service.get_acao_receita() == RecursoOpcoesEnum.RECURSO_PROPRIO.name

    def test_get_valor_custeio_retorna_zero(
        self,
        receita_prevista_recurso_proprio_data,
        mock_paa
    ):
        """Testa que valores de custeio retornam zero para recurso próprio"""
        instance = Mock(spec=RecursoProprioPaa)
        instance.paa = mock_paa
        instance.associacao = mock_paa.associacao

        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(
            receita_prevista_recurso_proprio_data,
            instance
        )

        assert service._get_valor_custeio_edicao() == 0
        assert service._get_valor_custeio_atual() == 0

    def test_get_valor_capital_retorna_zero(
        self,
        receita_prevista_recurso_proprio_data,
        mock_paa
    ):
        """Testa que valores de capital retornam zero para recurso próprio"""
        instance = Mock(spec=RecursoProprioPaa)
        instance.paa = mock_paa
        instance.associacao = mock_paa.associacao

        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(
            receita_prevista_recurso_proprio_data,
            instance
        )

        assert service._get_valor_capital_edicao() == 0
        assert service._get_valor_capital_atual() == 0

    def test_get_valor_livre_edicao(
        self,
        receita_prevista_recurso_proprio_data,
        mock_paa
    ):
        """Testa obtenção de valor livre em edição"""
        instance = Mock(spec=RecursoProprioPaa)
        instance.paa = mock_paa
        instance.associacao = mock_paa.associacao

        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(
            receita_prevista_recurso_proprio_data,
            instance
        )

        valor = service._get_valor_livre_edicao()
        assert valor == Decimal('3000.00')

    def test_get_valor_livre_atual(
        self,
        receita_prevista_recurso_proprio_data,
        mock_paa
    ):
        """Testa obtenção de valor livre atual"""
        instance = Mock(spec=RecursoProprioPaa)
        instance.paa = mock_paa
        instance.associacao = mock_paa.associacao
        instance.valor = Decimal('2500.00')

        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(
            receita_prevista_recurso_proprio_data,
            instance
        )

        valor = service._get_valor_livre_atual()
        assert valor == Decimal('2500.00')

    @patch('sme_ptrf_apps.paa.models.Paa')
    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.PrioridadePaa.objects')
    def test_query_base(
        self,
        mock_queryset,
        mock_paa_class,
        receita_prevista_recurso_proprio_data,
        mock_paa
    ):
        """Testa que _query_base filtra por paa__associacao e recurso RECURSO_PROPRIO"""
        instance = Mock(spec=RecursoProprioPaa)
        instance.paa = mock_paa
        instance.associacao = mock_paa.associacao

        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(
            receita_prevista_recurso_proprio_data,
            instance
        )

        service._query_base()

        assert mock_queryset.filter.called
        assert mock_qs.filter.called
        filter_kwargs = mock_qs.filter.call_args.kwargs
        assert filter_kwargs['paa__associacao'] == mock_paa.associacao
        assert filter_kwargs['recurso'] == RecursoOpcoesEnum.RECURSO_PROPRIO.name

    def test_limpar_ao_excluir_sem_pre_condicoes(
        self,
        receita_prevista_recurso_proprio_data
    ):
        """Testa que retorna [] quando pré-condições não são atendidas (sem instance)"""
        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(
            receita_prevista_recurso_proprio_data
        )

        mock_qs = Mock(spec=models.QuerySet)
        mock_qs.filter.return_value = mock_qs

        with patch.object(service, '_query_base', return_value=mock_qs):
            result = service.limpar_valor_prioridades_impactadas_ao_excluir_instancia()

        assert result == []
        mock_qs.filter.assert_not_called()

    def test_limpar_ao_excluir_sem_prioridades(
        self,
        receita_prevista_recurso_proprio_data,
        mock_paa
    ):
        """Testa que retorna lista vazia quando não há prioridades de CUSTEIO ou CAPITAL"""
        instance = Mock(spec=RecursoProprioPaa)
        instance.paa = mock_paa
        instance.associacao = mock_paa.associacao

        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(
            receita_prevista_recurso_proprio_data,
            instance
        )

        mock_qs = Mock(spec=models.QuerySet)
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = False
        mock_qs.values_list.return_value = []

        with patch.object(service, '_query_base', return_value=mock_qs):
            result = service.limpar_valor_prioridades_impactadas_ao_excluir_instancia()

        mock_qs.update.assert_not_called()
        assert result == []

    def test_limpar_ao_excluir_sem_confirmacao_lanca_excecao(
        self,
        receita_prevista_recurso_proprio_data,
        mock_paa
    ):
        """Testa que lança ConfirmarExlusaoPrioridadesPaaRecursoProprioService
        quando há prioridades e confirmar=False (padrão)"""
        instance = Mock(spec=RecursoProprioPaa)
        instance.paa = mock_paa
        instance.associacao = mock_paa.associacao

        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(
            receita_prevista_recurso_proprio_data,
            instance
        )

        mock_qs = Mock(spec=models.QuerySet)
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 2

        with patch.object(service, '_query_base', return_value=mock_qs):
            with pytest.raises(ConfirmarExlusaoPrioridadesPaaRecursoProprioService):
                service.limpar_valor_prioridades_impactadas_ao_excluir_instancia(confirmar=False)

        mock_qs.update.assert_not_called()

    def test_limpar_ao_excluir_com_confirmacao(
        self,
        receita_prevista_recurso_proprio_data,
        mock_paa
    ):
        """Testa que chama update(valor_total=None) e retorna lista de uuids
        quando há prioridades e confirmar=True"""
        instance = Mock(spec=RecursoProprioPaa)
        instance.paa = mock_paa
        instance.associacao = mock_paa.associacao

        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(
            receita_prevista_recurso_proprio_data,
            instance
        )

        uuids_esperados = ['uuid-prioridade-1', 'uuid-prioridade-2']

        mock_qs = Mock(spec=models.QuerySet)
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.count.return_value = 2
        mock_qs.values_list.return_value = uuids_esperados

        with patch.object(service, '_query_base', return_value=mock_qs):
            result = service.limpar_valor_prioridades_impactadas_ao_excluir_instancia(confirmar=True)

        mock_qs.update.assert_called_once_with(valor_total=None)
        mock_qs.values_list.assert_called_once_with('uuid', flat=True)
        assert result == uuids_esperados


# Testes de Validação de Saldo
@pytest.mark.django_db
class TestValidacaoSaldo:

    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.ResumoPrioridadesService')
    @patch('sme_ptrf_apps.paa.models.Paa')
    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.PrioridadePaa.objects')
    def test_buscar_prioridades_com_reducao_custeio(
        self,
        mock_queryset,
        mock_paa_class,
        mock_resumo_service,
        receita_prevista_ptrf_data,
        mock_acao_associacao,
        mock_paa
    ):
        """Testa busca de prioridades quando há redução no valor de custeio"""
        # Setup instance
        instance = Mock(spec=ReceitaPrevistaPaa)
        instance.acao_associacao = mock_acao_associacao
        instance.paa = mock_paa
        instance.previsao_valor_custeio = Decimal('2000.00')
        instance.previsao_valor_capital = Decimal('2000.00')
        instance.previsao_valor_livre = Decimal('500.00')

        # Atualiza dados para simular redução
        receita_prevista_ptrf_data['previsao_valor_custeio'] = '1500.00'  # Redução de 500

        # Mock prioridade
        mock_prioridade = Mock()
        mock_prioridade.uuid = 'prioridade-uuid-123'
        mock_prioridade.tipo_aplicacao = TipoAplicacaoOpcoesEnum.CUSTEIO.name

        # Mock queryset
        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = Mock(return_value=iter([mock_prioridade]))

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        # Mock resumo service para simular saldo insuficiente
        mock_resumo_instance = Mock()
        mock_resumo_instance.validar_valor_prioridade.side_effect = ValidacaoSaldoIndisponivel()
        mock_resumo_service.return_value = mock_resumo_instance

        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data,
            instance
        )

        service._buscar_prioridades_impactadas()

        # Verifica que a validação foi chamada
        assert mock_resumo_instance.validar_valor_prioridade.called

    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.ResumoPrioridadesService')
    @patch('sme_ptrf_apps.paa.models.Paa')
    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.PrioridadePaa.objects')
    def test_buscar_prioridades_com_reducao_capital(
        self,
        mock_queryset,
        mock_paa_class,
        mock_resumo_service,
        receita_prevista_ptrf_data,
        mock_acao_associacao,
        mock_paa
    ):
        """Testa busca de prioridades quando há redução no valor de capital:
        deve iterar sobre prioridades de CAPITAL e chamar _verifica_saldo para cada uma"""
        instance = Mock(spec=ReceitaPrevistaPaa)
        instance.acao_associacao = mock_acao_associacao
        instance.paa = mock_paa
        instance.previsao_valor_custeio = Decimal('1000.00')  # sem redução
        instance.previsao_valor_capital = Decimal('2000.00')  # valor atual
        instance.previsao_valor_livre = Decimal('500.00')    # sem redução

        # Mantém custeio e livre iguais ao atual; reduz apenas capital
        receita_prevista_ptrf_data['previsao_valor_custeio'] = '1000.00'
        receita_prevista_ptrf_data['previsao_valor_capital'] = '1500.00'  # Redução de 500
        receita_prevista_ptrf_data['previsao_valor_livre'] = '500.00'

        mock_prioridade = Mock()
        mock_prioridade.uuid = 'prioridade-capital-uuid-123'
        mock_prioridade.tipo_aplicacao = TipoAplicacaoOpcoesEnum.CAPITAL.name
        mock_prioridade.paa = mock_paa

        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = Mock(return_value=iter([mock_prioridade]))

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        mock_resumo_instance = Mock()
        mock_resumo_instance.validar_valor_prioridade.side_effect = ValidacaoSaldoIndisponivel()
        mock_resumo_service.return_value = mock_resumo_instance

        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data,
            instance
        )

        service._buscar_prioridades_impactadas()

        assert mock_resumo_instance.validar_valor_prioridade.called

    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.ResumoPrioridadesService')
    @patch('sme_ptrf_apps.paa.models.Paa')
    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.PrioridadePaa.objects')
    def test_buscar_prioridades_com_reducao_livre(
        self,
        mock_queryset,
        mock_paa_class,
        mock_resumo_service,
        receita_prevista_ptrf_data,
        mock_acao_associacao,
        mock_paa
    ):
        """Testa busca de prioridades quando há redução no valor de livre aplicação:
        deve iterar sobre prioridades de CUSTEIO e CAPITAL e chamar _verifica_saldo
        usando apenas a diferença do valor livre (valor_livre_atual - valor_livre_edicao)"""
        instance = Mock(spec=ReceitaPrevistaPaa)
        instance.acao_associacao = mock_acao_associacao
        instance.paa = mock_paa
        instance.previsao_valor_custeio = Decimal('1000.00')  # sem redução
        instance.previsao_valor_capital = Decimal('2000.00')  # sem redução
        instance.previsao_valor_livre = Decimal('500.00')    # valor atual

        # Mantém custeio e capital iguais ao atual; reduz apenas livre
        receita_prevista_ptrf_data['previsao_valor_custeio'] = '1000.00'
        receita_prevista_ptrf_data['previsao_valor_capital'] = '2000.00'
        receita_prevista_ptrf_data['previsao_valor_livre'] = '300.00'  # Redução de 200

        mock_prioridade_custeio = Mock()
        mock_prioridade_custeio.uuid = 'prioridade-custeio-uuid'
        mock_prioridade_custeio.tipo_aplicacao = TipoAplicacaoOpcoesEnum.CUSTEIO.name
        mock_prioridade_custeio.paa = mock_paa

        mock_prioridade_capital = Mock()
        mock_prioridade_capital.uuid = 'prioridade-capital-uuid'
        mock_prioridade_capital.tipo_aplicacao = TipoAplicacaoOpcoesEnum.CAPITAL.name
        mock_prioridade_capital.paa = mock_paa

        mock_qs = Mock(spec=models.QuerySet)
        mock_queryset.filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = Mock(return_value=iter([mock_prioridade_custeio, mock_prioridade_capital]))

        mock_paa_qs = Mock()
        mock_paa_class.objects.filter.return_value = mock_paa_qs
        mock_paa_qs.paas_em_elaboracao.return_value = Mock()

        mock_resumo_instance = Mock()
        mock_resumo_instance.validar_valor_prioridade.side_effect = ValidacaoSaldoIndisponivel()
        mock_resumo_service.return_value = mock_resumo_instance

        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data,
            instance
        )

        service._buscar_prioridades_impactadas()

        # Deve ter validado saldo para ambas as prioridades (CUSTEIO e CAPITAL)
        assert mock_resumo_instance.validar_valor_prioridade.call_count == 2

    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.ResumoPrioridadesService')
    def test_verifica_saldo_com_saldo_suficiente(
        self,
        mock_resumo_service,
        receita_prevista_ptrf_data,
        mock_acao_associacao,
        mock_paa
    ):
        """Testa verificação de saldo quando há saldo suficiente"""
        instance = Mock(spec=ReceitaPrevistaPaa)
        instance.acao_associacao = mock_acao_associacao
        instance.paa = mock_paa

        mock_prioridade = Mock()
        mock_prioridade.uuid = 'prioridade-uuid'
        mock_prioridade.tipo_aplicacao = TipoAplicacaoOpcoesEnum.CUSTEIO.name
        mock_prioridade.paa = mock_paa

        # Mock resumo service - não lança exceção = saldo suficiente
        mock_resumo_instance = Mock()
        mock_resumo_service.return_value = mock_resumo_instance

        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data,
            instance
        )

        # Não deve lançar exceção
        service._verifica_saldo(mock_prioridade, Decimal('100.00'))

        mock_resumo_instance.validar_valor_prioridade.assert_called_once()

    @patch('sme_ptrf_apps.paa.services.prioridades_impactadas_receitas_previstas_service.ResumoPrioridadesService')
    def test_verifica_saldo_com_saldo_insuficiente(
        self,
        mock_resumo_service,
        receita_prevista_ptrf_data,
        mock_acao_associacao,
        mock_paa
    ):
        """Testa verificação de saldo quando há saldo insuficiente"""
        instance = Mock(spec=ReceitaPrevistaPaa)
        instance.acao_associacao = mock_acao_associacao
        instance.paa = mock_paa
        instance.uuid = 'receita-uuid'

        mock_prioridade = Mock()
        mock_prioridade.uuid = 'prioridade-uuid'
        mock_prioridade.tipo_aplicacao = TipoAplicacaoOpcoesEnum.CUSTEIO.name
        mock_prioridade.paa = mock_paa

        # Mock resumo service - lança exceção = saldo insuficiente
        mock_resumo_instance = Mock()
        mock_resumo_instance.validar_valor_prioridade.side_effect = ValidacaoSaldoIndisponivel()
        mock_resumo_service.return_value = mock_resumo_instance

        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data,
            instance
        )

        # Deve lançar exceção
        with pytest.raises(ValidacaoSaldoIndisponivel):
            service._verifica_saldo(mock_prioridade, Decimal('10000.00'))


# Testes de get_acao_uuid_resumo_prioridade
class TestGetAcaoUuidResumoPrioridade:

    def test_com_receita_prevista_outro_recurso(
        self,
        receita_prevista_outro_recurso_data,
        mock_outro_recurso_periodo,
        mock_paa
    ):
        """Testa UUID para outro recurso"""
        instance = Mock(spec=ReceitaPrevistaOutroRecursoPeriodo)
        instance.outro_recurso_periodo = mock_outro_recurso_periodo
        instance.paa = mock_paa

        service = PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService(
            receita_prevista_outro_recurso_data,
            instance
        )

        uuid = service._get_acao_uuid_resumo_prioridade()
        assert uuid == mock_outro_recurso_periodo.outro_recurso.uuid

    def test_com_receita_prevista_pdde(
        self,
        receita_prevista_pdde_data,
        mock_acao_pdde,
        mock_paa
    ):
        """Testa UUID para PDDE"""
        instance = Mock(spec=ReceitaPrevistaPdde)
        instance.acao_pdde = mock_acao_pdde
        instance.paa = mock_paa

        service = PrioridadesPaaImpactadasReceitasPrevistasPDDEService(
            receita_prevista_pdde_data,
            instance
        )

        uuid = service._get_acao_uuid_resumo_prioridade()
        assert uuid == mock_acao_pdde.uuid

    def test_com_receita_prevista_ptrf(
        self,
        receita_prevista_ptrf_data,
        mock_acao_associacao,
        mock_paa
    ):
        """Testa UUID para PTRF"""
        instance = Mock(spec=ReceitaPrevistaPaa)
        instance.acao_associacao = mock_acao_associacao
        instance.paa = mock_paa

        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(
            receita_prevista_ptrf_data,
            instance
        )

        uuid = service._get_acao_uuid_resumo_prioridade()
        assert uuid == mock_acao_associacao.uuid

    def test_com_recurso_proprio(
        self,
        receita_prevista_recurso_proprio_data,
        mock_paa
    ):
        """Testa UUID para recurso próprio"""
        instance = Mock(spec=RecursoProprioPaa)
        instance.paa = mock_paa
        instance.associacao = mock_paa.associacao

        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(
            receita_prevista_recurso_proprio_data,
            instance
        )

        uuid = service._get_acao_uuid_resumo_prioridade()
        assert uuid == mock_paa.associacao.uuid
