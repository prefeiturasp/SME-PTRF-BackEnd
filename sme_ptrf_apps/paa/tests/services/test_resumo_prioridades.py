import uuid
import pytest
from unittest.mock import patch, MagicMock

from decimal import Decimal
from rest_framework import serializers

from sme_ptrf_apps.paa.services.resumo_prioridades_service import ResumoPrioridadesService
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum


@pytest.mark.django_db
def test_calcula_despesa_livre_aplicacao_sobra(resumo_recursos_paa):
    service = ResumoPrioridadesService(paa=resumo_recursos_paa)

    result = service.calcula_despesa_livre_aplicacao(
        despesa_custeio=Decimal("100"),
        despesa_capital=Decimal("200"),
        receita_custeio=Decimal("50"),
        receita_capital=Decimal("50"),
    )

    # Receitas < Despesas -> deve gerar despesa livre
    assert result == Decimal("200")


@pytest.mark.django_db
def test_calcula_despesa_livre_aplicacao_sem_excedente(resumo_recursos_paa):
    service = ResumoPrioridadesService(paa=resumo_recursos_paa)

    result = service.calcula_despesa_livre_aplicacao(
        despesa_custeio=Decimal("100"),
        despesa_capital=Decimal("200"),
        receita_custeio=Decimal("300"),
        receita_capital=Decimal("400"),
    )

    # Receitas > Despesas -> nada em livre
    assert result == 0


@pytest.mark.django_db
def test_calcula_saldos(resumo_recursos_paa):
    service = ResumoPrioridadesService(paa=resumo_recursos_paa)

    receitas = {
        "custeio": Decimal("300"),
        "capital": Decimal("400"),
        "livre_aplicacao": Decimal("100")
    }
    despesas = {
        "custeio": Decimal("200"),
        "capital": Decimal("500"),
        "livre_aplicacao": Decimal("80")
    }

    result = service.calcula_saldos("acao-1", receitas, despesas)

    assert result["key"] == "acao-1_saldo"
    assert result["recurso"] == 'Saldo'
    assert result["custeio"] == receitas["custeio"] - despesas["custeio"]
    assert result["capital"] == 0  # considera zerado quando não houver saldo
    assert result["livre_aplicacao"] == Decimal("20")  # 100 - 80


@pytest.mark.django_db
@patch("sme_ptrf_apps.core.api.serializers.AcaoAssociacaoRetrieveSerializer")
def test_calcula_node_ptrf(mock_serializer, resumo_recursos_paa):
    mock_serializer.return_value.data = [
        {
            "uuid": str(uuid.uuid4()),
            "acao": {"nome": "PTRF Teste"},
            "receitas_previstas_paa": [],
            "saldos": {}
        }
    ]
    service = ResumoPrioridadesService(paa=resumo_recursos_paa)

    result = service.calcula_node_ptrf()

    assert result["key"] == RecursoOpcoesEnum.PTRF.name
    assert result["recurso"] == "PTRF Total"
    assert isinstance(result["children"], list)
    assert result["children"][0]["recurso"].startswith("PTRF")


@pytest.mark.django_db
def test_calcula_node_pdde(receita_prevista_pdde_resumo_recursos):

    service = ResumoPrioridadesService(paa=receita_prevista_pdde_resumo_recursos.paa)
    result = service.calcula_node_pdde()

    assert result["key"] == RecursoOpcoesEnum.PDDE.name
    assert result["children"][0]["recurso"].startswith("PDDE")

    custeio = sum([
        receita_prevista_pdde_resumo_recursos.previsao_valor_custeio,
        receita_prevista_pdde_resumo_recursos.saldo_custeio
    ])
    assert result["children"][0]["custeio"] == custeio

    capital = sum([
        receita_prevista_pdde_resumo_recursos.previsao_valor_capital,
        receita_prevista_pdde_resumo_recursos.saldo_capital
    ])
    assert result["children"][0]["capital"] == capital

    livre = sum([
        receita_prevista_pdde_resumo_recursos.previsao_valor_livre,
        receita_prevista_pdde_resumo_recursos.saldo_livre
    ])
    assert result["children"][0]["livre_aplicacao"] == livre


@pytest.mark.django_db
@patch("sme_ptrf_apps.paa.api.serializers.RecursoProprioPaaListSerializer")
def test_calcula_node_recursos_proprios(mock_serializer, resumo_recursos_paa):
    mock_serializer.return_value.data = [
        {
            "uuid": "rec-1",
            "descricao": "R1",
            "valor": Decimal("500")
        },
        {
            "uuid": "rec-2",
            "descricao": "R2",
            "valor": Decimal("500")
        }
    ]

    service = ResumoPrioridadesService(paa=resumo_recursos_paa)
    result = service.calcula_node_recursos_proprios()

    assert result["key"] == RecursoOpcoesEnum.RECURSO_PROPRIO.name
    assert result["children"][0]["recurso"] == "Total de Recursos Próprios"
    assert result["children"][0]["custeio"] == 0
    assert result["children"][0]["capital"] == 0
    assert result["children"][0]["livre_aplicacao"] == 1000  # 500 + 500


@pytest.mark.django_db
@patch.object(ResumoPrioridadesService, "calcula_node_ptrf")
@patch.object(ResumoPrioridadesService, "calcula_node_pdde")
@patch.object(ResumoPrioridadesService, "calcula_node_recursos_proprios")
def test_resumo_prioridades(mock_recursos, mock_pdde, mock_ptrf, resumo_recursos_paa):
    mock_ptrf.return_value = {"key": "PTRF"}
    mock_pdde.return_value = {"key": "PDDE"}
    mock_recursos.return_value = {"key": "RECURSO_PROPRIO"}

    service = ResumoPrioridadesService(paa=resumo_recursos_paa)
    result = service.resumo_prioridades()

    assert isinstance(result, list)
    assert {"key": "PTRF"} in result
    assert {"key": "PDDE"} in result
    assert {"key": "RECURSO_PROPRIO"} in result
    assert len(result) == 3  # PTRF, PDDE e RECURSO_PROPRIO
    assert result[0]["key"] == "PTRF"


@pytest.mark.django_db
@patch.object(ResumoPrioridadesService, "resumo_prioridades")
def test_validar_valor_prioridade_sucesso_custeio(mock_resumo, resumo_recursos_paa):
    """Validação bem-sucedida para tipo CUSTEIO"""
    mock_resumo.return_value = [
        {
            'key': RecursoOpcoesEnum.PTRF.name,
            'children': [
                {
                    'key': 'acao-uuid-123',
                    'children': [
                        {
                            'recurso': 'Receita',
                            'custeio': Decimal('1000.00'),
                            'capital': Decimal('500.00'),
                            'livre_aplicacao': Decimal('200.00')
                        },
                        {
                            'recurso': 'Despesas previstas',
                            'custeio': Decimal('100.00'),
                            'capital': Decimal('50.00'),
                            'livre_aplicacao': Decimal('0.00')
                        }
                    ]
                }
            ]
        }
    ]
    
    service = ResumoPrioridadesService(paa=resumo_recursos_paa)
    
    try:
        service.validar_valor_prioridade(
            valor_total=Decimal('800.00'),
            acao_uuid='acao-uuid-123',
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
            recurso=RecursoOpcoesEnum.PTRF.name
        )
        assert True
    except Exception as e:
        pytest.fail(f"Validação deveria ter passado, mas falhou com: {str(e)}")


@pytest.mark.django_db
@patch.object(ResumoPrioridadesService, "resumo_prioridades")
def test_validar_valor_prioridade_sucesso_capital(mock_resumo, resumo_recursos_paa):
    """Validação bem-sucedida para tipo CAPITAL"""
    mock_resumo.return_value = [
        {
            'key': RecursoOpcoesEnum.PDDE.name,
            'children': [
                {
                    'key': 'acao-pdde-uuid-456',
                    'children': [
                        {
                            'recurso': 'Receita',
                            'custeio': Decimal('300.00'),
                            'capital': Decimal('800.00'),
                            'livre_aplicacao': Decimal('100.00')
                        },
                        {
                            'recurso': 'Despesas previstas',
                            'custeio': Decimal('50.00'),
                            'capital': Decimal('100.00'),
                            'livre_aplicacao': Decimal('0.00')
                        }
                    ]
                }
            ]
        }
    ]
    
    service = ResumoPrioridadesService(paa=resumo_recursos_paa)
    
    try:
        service.validar_valor_prioridade(
            valor_total=Decimal('700.00'),
            acao_uuid='acao-pdde-uuid-456',
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CAPITAL.name,
            recurso=RecursoOpcoesEnum.PDDE.name
        )
        assert True
    except Exception as e:
        pytest.fail(f"Validação deveria ter passado, mas falhou com: {str(e)}")


@pytest.mark.django_db
@patch.object(ResumoPrioridadesService, "resumo_prioridades")
def test_validar_valor_prioridade_excede_valor_disponivel(mock_resumo, resumo_recursos_paa):
    """Validação falha quando valor excede o disponível"""
    mock_resumo.return_value = [
        {
            'key': RecursoOpcoesEnum.PTRF.name,
            'children': [
                {
                    'key': 'acao-uuid-789',
                    'children': [
                        {
                            'recurso': 'Receita',
                            'custeio': Decimal('500.00'),
                            'capital': Decimal('300.00'),
                            'livre_aplicacao': Decimal('100.00')
                        },
                        {
                            'recurso': 'Despesas previstas',
                            'custeio': Decimal('200.00'),
                            'capital': Decimal('100.00'),
                            'livre_aplicacao': Decimal('0.00')
                        }
                    ]
                }
            ]
        }
    ]
    
    service = ResumoPrioridadesService(paa=resumo_recursos_paa)
    
    with pytest.raises(serializers.ValidationError) as exc_info:
        service.validar_valor_prioridade(
            valor_total=Decimal('500.00'),
            acao_uuid='acao-uuid-789',
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
            recurso=RecursoOpcoesEnum.PTRF.name
        )
    
    assert 'O valor indicado para a prioridade excede o valor disponível de receita prevista.' in str(exc_info.value)


@pytest.mark.django_db
@patch.object(ResumoPrioridadesService, "resumo_prioridades")
def test_validar_valor_prioridade_acao_nao_encontrada(mock_resumo, resumo_recursos_paa):
    """Validação falha quando ação não é encontrada"""
    mock_resumo.return_value = [
        {
            'key': RecursoOpcoesEnum.PTRF.name,
            'children': [
                {
                    'key': 'outra-acao-uuid',
                    'children': [
                        {
                            'recurso': 'Receita',
                            'custeio': Decimal('1000.00'),
                            'capital': Decimal('500.00'),
                            'livre_aplicacao': Decimal('200.00')
                        }
                    ]
                }
            ]
        }
    ]
    
    service = ResumoPrioridadesService(paa=resumo_recursos_paa)
    
    with pytest.raises(serializers.ValidationError) as exc_info:
        service.validar_valor_prioridade(
            valor_total=Decimal('100.00'),
            acao_uuid='acao-inexistente-uuid',
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
            recurso=RecursoOpcoesEnum.PTRF.name
        )
    
    assert 'Ação não encontrada no resumo de prioridades.' in str(exc_info.value)


@pytest.mark.django_db
@patch.object(ResumoPrioridadesService, "resumo_prioridades")
def test_validar_valor_prioridade_recursos_proprios_sucesso(mock_resumo, resumo_recursos_paa):
    """Validação bem-sucedida para Recursos Próprios"""
    mock_resumo.return_value = [
        {
            'key': RecursoOpcoesEnum.RECURSO_PROPRIO.name,
            'children': [
                {
                    'key': 'item_recursos',
                    'children': [
                        {
                            'recurso': 'Receita',
                            'custeio': Decimal('0.00'),
                            'capital': Decimal('0.00'),
                            'livre_aplicacao': Decimal('1000.00')
                        },
                        {
                            'recurso': 'Despesas previstas',
                            'custeio': Decimal('0.00'),
                            'capital': Decimal('0.00'),
                            'livre_aplicacao': Decimal('200.00')
                        }
                    ]
                }
            ]
        }
    ]
    
    service = ResumoPrioridadesService(paa=resumo_recursos_paa)
    
    try:
        service.validar_valor_prioridade(
            valor_total=Decimal('500.00'),
            acao_uuid=None,
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
            recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name
        )
        assert True
    except Exception as e:
        pytest.fail(f"Validação deveria ter passado, mas falhou com: {str(e)}")


@pytest.mark.django_db
@patch.object(ResumoPrioridadesService, "resumo_prioridades")
def test_validar_valor_prioridade_atualizacao_reducao_permitida(mock_resumo, resumo_recursos_paa):
    """Validação permite redução mesmo com saldo zerado"""
    mock_resumo.return_value = [
        {
            'key': RecursoOpcoesEnum.PTRF.name,
            'children': [
                {
                    'key': 'acao-uuid-123',
                    'children': [
                        {
                            'recurso': 'Receita',
                            'custeio': Decimal('1000.00'),
                            'capital': Decimal('500.00'),
                            'livre_aplicacao': Decimal('200.00')
                        },
                        {
                            'recurso': 'Despesas previstas',
                            'custeio': Decimal('1000.00'),
                            'capital': Decimal('500.00'),
                            'livre_aplicacao': Decimal('200.00')
                        }
                    ]
                }
            ]
        }
    ]
    
    service = ResumoPrioridadesService(paa=resumo_recursos_paa)
    
    try:
        service.validar_valor_prioridade(
            valor_total=Decimal('500.00'),
            acao_uuid='acao-uuid-123',
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
            recurso=RecursoOpcoesEnum.PTRF.name,
            prioridade_uuid='prioridade-uuid-123',
            valor_atual_prioridade=Decimal('800.00')
        )
        assert True
    except Exception as e:
        pytest.fail(f"Redução deveria ter sido permitida, mas falhou com: {str(e)}")


@pytest.mark.django_db
@patch.object(ResumoPrioridadesService, "resumo_prioridades")
def test_validar_valor_prioridade_atualizacao_aumento_bloqueado_saldo_zerado(mock_resumo, resumo_recursos_paa):
    """Validação bloqueia aumento quando saldo está zerado"""
    mock_resumo.return_value = [
        {
            'key': RecursoOpcoesEnum.PTRF.name,
            'children': [
                {
                    'key': 'acao-uuid-123',
                    'children': [
                        {
                            'recurso': 'Receita',
                            'custeio': Decimal('1000.00'),
                            'capital': Decimal('500.00'),
                            'livre_aplicacao': Decimal('200.00')
                        },
                        {
                            'recurso': 'Despesas previstas',
                            'custeio': Decimal('1000.00'),
                            'capital': Decimal('500.00'),
                            'livre_aplicacao': Decimal('200.00')
                        }
                    ]
                }
            ]
        }
    ]
    
    service = ResumoPrioridadesService(paa=resumo_recursos_paa)
    
    with pytest.raises(serializers.ValidationError) as exc_info:
        service.validar_valor_prioridade(
            valor_total=Decimal('1200.00'),
            acao_uuid='acao-uuid-123',
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
            recurso=RecursoOpcoesEnum.PTRF.name,
            prioridade_uuid='prioridade-uuid-123',
            valor_atual_prioridade=Decimal('800.00')
        )
    
    assert 'O valor indicado para a prioridade excede o valor disponível de receita prevista.' in str(exc_info.value)


@pytest.mark.django_db
@patch.object(ResumoPrioridadesService, "resumo_prioridades")
def test_validar_valor_prioridade_atualizacao_aumento_permitido_saldo_positivo(mock_resumo, resumo_recursos_paa):
    """Validação permite aumento quando há saldo positivo"""
    mock_resumo.return_value = [
        {
            'key': RecursoOpcoesEnum.PTRF.name,
            'children': [
                {
                    'key': 'acao-uuid-123',
                    'children': [
                        {
                            'recurso': 'Receita',
                            'custeio': Decimal('1000.00'),
                            'capital': Decimal('500.00'),
                            'livre_aplicacao': Decimal('200.00')
                        },
                        {
                            'recurso': 'Despesas previstas',
                            'custeio': Decimal('500.00'),
                            'capital': Decimal('200.00'),
                            'livre_aplicacao': Decimal('100.00')
                        }
                    ]
                }
            ]
        }
    ]
    
    service = ResumoPrioridadesService(paa=resumo_recursos_paa)
    
    try:
        service.validar_valor_prioridade(
            valor_total=Decimal('800.00'),
            acao_uuid='acao-uuid-123',
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
            recurso=RecursoOpcoesEnum.PTRF.name,
            prioridade_uuid='prioridade-uuid-123',
            valor_atual_prioridade=Decimal('400.00')
        )
        assert True
    except Exception as e:
        pytest.fail(f"Aumento deveria ter sido permitido, mas falhou com: {str(e)}")
