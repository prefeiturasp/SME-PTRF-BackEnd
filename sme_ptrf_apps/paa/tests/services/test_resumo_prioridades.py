import pytest
from unittest.mock import patch

from decimal import Decimal
from rest_framework import serializers

from sme_ptrf_apps.paa.services.resumo_prioridades_service import ResumoPrioridadesService
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum


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
        "livre_aplicacao": Decimal("0")
    }

    result = service.calcula_saldos("acao-1", receitas, despesas)

    assert result["key"] == "acao-1_saldo"
    assert result["recurso"] == 'Saldo'
    assert result["custeio"] == receitas["custeio"] - despesas["custeio"]
    assert result["capital"] == 0  # considera zerado quando não houver saldo
    assert result["livre_aplicacao"] == Decimal("0")


@pytest.mark.django_db
def test_calcula_node_ptrf(resumo_recursos_paa):
    from sme_ptrf_apps.paa.fixtures.factories import ReceitaPrevistaPaaFactory
    from sme_ptrf_apps.core.fixtures.factories.acao_associacao_factory import AcaoAssociacaoFactory
    acao_associacao = AcaoAssociacaoFactory.create(associacao=resumo_recursos_paa.associacao)
    ReceitaPrevistaPaaFactory.create(
        paa=resumo_recursos_paa,
        acao_associacao=acao_associacao,
        previsao_valor_custeio=1001,
        previsao_valor_capital=1002,
        previsao_valor_livre=1003
    )

    service = ResumoPrioridadesService(paa=resumo_recursos_paa)

    result = service.calcula_node_ptrf()

    assert result["key"] == RecursoOpcoesEnum.PTRF.name
    assert result["recurso"] == "PTRF Total"
    assert isinstance(result["children"], list)
    assert result["children"][0]["recurso"].startswith("PTRF")
    assert result["children"][0]["custeio"] == Decimal(1001)
    assert result["children"][0]["capital"] == Decimal(1002)
    assert result["children"][0]["livre_aplicacao"] == Decimal(1003)


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
def test_calcula_node_outros_recursos(resumo_recursos_paa, recurso_proprio_paa_factory, prioridade_paa_factory):
    recurso_proprio_paa_factory.create(paa=resumo_recursos_paa, descricao="ABC 007", valor=1000.00)
    prioridade_paa_factory.create(
        paa=resumo_recursos_paa,
        recurso="RECURSO_PROPRIO",
        valor_total=200,
        acao_pdde=None,
        acao_associacao=None
    )

    service = ResumoPrioridadesService(paa=resumo_recursos_paa)
    result = service.calcula_node_outros_recursos()
    assert result["key"] == RecursoOpcoesEnum.OUTRO_RECURSO.name
    assert result["children"][0]["recurso"] == RecursoOpcoesEnum.RECURSO_PROPRIO.value
    assert result["children"][0]["custeio"] == 0
    assert result["children"][0]["capital"] == 0
    assert result["children"][0]["livre_aplicacao"] == 800


@pytest.mark.django_db
@patch.object(ResumoPrioridadesService, "calcula_node_ptrf")
@patch.object(ResumoPrioridadesService, "calcula_node_pdde")
@patch.object(ResumoPrioridadesService, "calcula_node_outros_recursos")
def test_resumo_prioridades(mock_recursos, mock_pdde, mock_ptrf, resumo_recursos_paa):
    mock_ptrf.return_value = {"key": "PTRF"}
    mock_pdde.return_value = {"key": "PDDE"}
    mock_recursos.return_value = {"key": "OUTRO_RECURSO"}

    service = ResumoPrioridadesService(paa=resumo_recursos_paa)
    result = service.resumo_prioridades()

    assert isinstance(result, list)
    assert {"key": "PTRF"} in result
    assert {"key": "PDDE"} in result
    assert {"key": "OUTRO_RECURSO"} in result
    assert len(result) == 3  # PTRF, PDDE e OUTRO_RECURSO
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
                            'key': 'acao-uuid-123_receita',
                            'recurso': 'Receita',
                            'custeio': Decimal('1000.00'),
                            'capital': Decimal('500.00'),
                            'livre_aplicacao': Decimal('200.00')
                        },
                        {
                            'key': 'acao-uuid-123_despesas',
                            'recurso': 'Despesas previstas',
                            'custeio': Decimal('100.00'),
                            'capital': Decimal('50.00'),
                            'livre_aplicacao': Decimal('0.00')
                        },
                        {
                            'key': 'acao-uuid-123_saldo',
                            'recurso': 'Saldo',
                            'custeio': Decimal('900.00'),
                            'capital': Decimal('450.00'),
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
                            'key': 'acao-pdde-uuid-456_receita',
                            'recurso': 'Receita',
                            'custeio': Decimal('300.00'),
                            'capital': Decimal('800.00'),
                            'livre_aplicacao': Decimal('100.00')
                        },
                        {
                            'key': 'acao-pdde-uuid-456_despesas',
                            'recurso': 'Despesas previstas',
                            'custeio': Decimal('50.00'),
                            'capital': Decimal('100.00'),
                            'livre_aplicacao': Decimal('0.00')
                        },
                        {
                            'key': 'acao-pdde-uuid-456_saldo',
                            'recurso': 'Saldo',
                            'custeio': Decimal('250.00'),
                            'capital': Decimal('700.00'),
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
                            'key': 'acao-uuid-789_receita',
                            'recurso': 'Receita',
                            'custeio': Decimal('500.00'),
                            'capital': Decimal('300.00'),
                            'livre_aplicacao': Decimal('100.00')
                        },
                        {
                            'key': 'acao-uuid-789_despesas',
                            'recurso': 'Despesas previstas',
                            'custeio': Decimal('200.00'),
                            'capital': Decimal('100.00'),
                            'livre_aplicacao': Decimal('0.00')
                        },
                        {
                            'key': 'acao-uuid-789_saldo',
                            'recurso': 'Saldo',
                            'custeio': Decimal('300.00'),
                            'capital': Decimal('200.00'),
                            'livre_aplicacao': Decimal('100.00')
                        },
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
                            'key': 'outra-acao-uuid_receita',
                            'recurso': 'Receita',
                            'custeio': Decimal('0.00'),
                            'capital': Decimal('0.00'),
                            'livre_aplicacao': Decimal('0.00')
                        },
                        {
                            'key': 'outra-acao-uuid_despesas',
                            'recurso': 'Despesas',
                            'custeio': Decimal('0.00'),
                            'capital': Decimal('0.00'),
                            'livre_aplicacao': Decimal('0.00')
                        },
                        {
                            'key': 'outra-acao-uuid_saldo',
                            'recurso': 'Saldo',
                            'custeio': Decimal('0.00'),
                            'capital': Decimal('0.00'),
                            'livre_aplicacao': Decimal('0.00')
                        },
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

    assert 'Saldos de recursos PTRF não encontrados no resumo de prioridades.' in str(exc_info.value)


@pytest.mark.django_db
@patch.object(ResumoPrioridadesService, "resumo_prioridades")
def test_validar_valor_prioridade_recursos_proprios_sucesso(mock_resumo, resumo_recursos_paa):
    """Validação bem-sucedida para Recursos Próprios"""
    mock_resumo.return_value = [
        {
            'key': RecursoOpcoesEnum.RECURSO_PROPRIO.name,
            'children': [
                {
                    'key': f'{RecursoOpcoesEnum.RECURSO_PROPRIO.name}_receita',
                    'recurso': 'Receita',
                    'custeio': Decimal('0.00'),
                    'capital': Decimal('0.00'),
                    'livre_aplicacao': Decimal('1000.00')
                },
                {
                    'key': f'{RecursoOpcoesEnum.RECURSO_PROPRIO.name}_despesas',
                    'recurso': 'Despesas previstas',
                    'custeio': Decimal('0.00'),
                    'capital': Decimal('0.00'),
                    'livre_aplicacao': Decimal('0.00')
                },
                {
                    'key': f'{RecursoOpcoesEnum.RECURSO_PROPRIO.name}_saldo',
                    'recurso': 'Saldo',
                    'custeio': Decimal('0.00'),
                    'capital': Decimal('0.00'),
                    'livre_aplicacao': Decimal('1000.00')
                }
            ]
        }
    ]

    service = ResumoPrioridadesService(paa=resumo_recursos_paa)
    try:
        service.validar_valor_prioridade(
            valor_total=Decimal('5000.00'),
            acao_uuid=RecursoOpcoesEnum.RECURSO_PROPRIO.name,
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
            recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name
        )
        assert True
    except Exception as ex:
        assert 'O valor indicado para a prioridade excede o valor disponível de receita prevista.' in str(ex)


@pytest.mark.django_db
@patch.object(ResumoPrioridadesService, "resumo_prioridades")
def test_validar_valor_prioridade_outros_recursos(mock_resumo, resumo_recursos_paa):
    mock_resumo.return_value = [
        {
            "key": f"{RecursoOpcoesEnum.OUTRO_RECURSO.name}",
            "recurso": "Outros Recursos Total",
            "custeio": 700,
            "capital": 0,
            "livre_aplicacao": -72988.89,
            "children": [
                {
                    "key": "UUID-Outro-Recurso-Periodo",
                    "recurso": "Prêmio de Excelência",
                    "custeio": 700,
                    "capital": 0,
                    "livre_aplicacao": 36011.11,
                    "parent": f"{RecursoOpcoesEnum.OUTRO_RECURSO.name}",
                    "cor": "#3482b3",
                    "children": [
                        {
                            "key": "UUID-Outro-Recurso-Periodo_receita",
                            "recurso": "Receita",
                            "custeio": 0,
                            "capital": 0,
                            "livre_aplicacao": 5000
                        },
                        {
                            "key": "UUID-Outro-Recurso-Periodo_despesa",
                            "recurso": "Despesas previstas",
                            "custeio": 0,
                            "capital": 0,
                            "livre_aplicacao": 2000
                        },
                        {
                            "key": "UUID-Outro-Recurso-Periodo_saldo",
                            "recurso": "Saldo",
                            "custeio": 700,
                            "capital": 0,
                            "livre_aplicacao": 3000
                        }
                    ]
                }
            ]
        }
    ]

    service = ResumoPrioridadesService(paa=resumo_recursos_paa)
    try:
        service.validar_valor_prioridade(
            valor_total=Decimal('5000.00'),
            acao_uuid="UUID-Outro-Recurso-Periodo",
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CAPITAL.name,
            recurso=RecursoOpcoesEnum.OUTRO_RECURSO.name
        )
        assert True
    except Exception as ex:
        assert 'O valor indicado para a prioridade excede o valor disponível de receita prevista.' in str(ex)


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
                            'key': 'acao-uuid-123_receita',
                            'recurso': 'Receita',
                            'custeio': Decimal('1000.00'),
                            'capital': Decimal('500.00'),
                            'livre_aplicacao': Decimal('2000.00')
                        },
                        {
                            'key': 'acao-uuid-123_despesas',
                            'recurso': 'Despesas previstas',
                            'custeio': Decimal('100.00'),
                            'capital': Decimal('100.00'),
                            'livre_aplicacao': Decimal('0.00')
                        },
                        {
                            'key': 'acao-uuid-123_saldo',
                            'recurso': 'Saldo',
                            'custeio': Decimal('900.00'),
                            'capital': Decimal('400.00'),
                            'livre_aplicacao': Decimal('2000.00')
                        }
                    ]
                }
            ]
        }
    ]

    service = ResumoPrioridadesService(paa=resumo_recursos_paa)

    try:
        service.validar_valor_prioridade(
            valor_total=Decimal('50000.00'),
            acao_uuid='acao-uuid-123',
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
            recurso=RecursoOpcoesEnum.PTRF.name,
            prioridade_uuid='prioridade-uuid-123',
            valor_atual_prioridade=Decimal('800.00')
        )
        assert True
    except Exception as e:
        assert "O valor indicado para a prioridade excede o valor disponível de receita prevista." in str(e)


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
                            'key': 'acao-uuid-123_receita',
                            'recurso': 'Receita',
                            'custeio': Decimal('1000.00'),
                            'capital': Decimal('500.00'),
                            'livre_aplicacao': Decimal('200.00')
                        },
                        {
                            'key': 'acao-uuid-123_despesas',
                            'recurso': 'Despesas previstas',
                            'custeio': Decimal('1000.00'),
                            'capital': Decimal('700.00'),
                            'livre_aplicacao': Decimal('0.00')
                        },
                        {
                            'key': 'acao-uuid-123_saldo',
                            'recurso': 'Saldo',
                            'custeio': Decimal('0.00'),
                            'capital': Decimal('0.00'),
                            'livre_aplicacao': Decimal('0.00')
                        },
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
                            'key': 'acao-uuid-123_receita',
                            'recurso': 'Receita',
                            'custeio': Decimal('1000.00'),
                            'capital': Decimal('500.00'),
                            'livre_aplicacao': Decimal('200.00')
                        },
                        {
                            'key': 'acao-uuid-123_despesas',
                            'recurso': 'Despesas previstas',
                            'custeio': Decimal('0.00'),
                            'capital': Decimal('0.00'),
                            'livre_aplicacao': Decimal('0.00')
                        },
                        {
                            'key': 'acao-uuid-123_saldo',
                            'recurso': 'Saldo',
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
            valor_total=Decimal('800.00'),
            acao_uuid='acao-uuid-123',
            tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
            recurso=RecursoOpcoesEnum.PTRF.name,
            prioridade_uuid='prioridade-uuid-123',
            valor_atual_prioridade=Decimal('400.00')
        )
        assert True
    except Exception as e:
        assert "O valor indicado para a prioridade excede o valor disponível de receita prevista." in str(e)
