import pytest

from .....dre.services.valores_reprogramados_dre_service import (
    salvar_e_concluir_valores_reprogramados,
    calcula_novo_status,
    possui_diferenca,
    monta_estrutura_valores_reprogramados,
    barra_status
)
from decimal import Decimal

pytestmark = pytest.mark.django_db


def test_salvar_valores_reprogramados(
    jwt_authenticated_client_a,
    associacao,
    conta_associacao,
    acao_associacao
):
    periodo = associacao.periodo_inicial
    visao_selecionada = "UE"

    dados = {
        "associacao": {
            "status_valores_reprogramados": associacao.status_valores_reprogramados,
            "uuid": f"{associacao.uuid}"
        },
        "contas": [{
            "conta": {
                "acoes": [{
                    "custeio": {
                        "nome": "custeio",
                        "status_conferencia": None,
                        "valor_dre": None,
                        "valor_ue": None
                    },
                    "nome": acao_associacao.acao.nome,
                    "uuid": f"{acao_associacao.uuid}"
                }],
                "tipo_conta": conta_associacao.tipo_conta.nome,
                "uuid": f"{conta_associacao.uuid}"
            }
        }]
    }

    resultado_esperado = {
        'saldo_salvo': True,
        'codigo_erro': None,
        'mensagem': 'Saldo salvo com sucesso'
    }

    retorno = salvar_e_concluir_valores_reprogramados(associacao, periodo, dados, visao_selecionada)

    assert retorno == resultado_esperado


def test_salvar_valores_reprogramados_sem_periodo_inicial(
    jwt_authenticated_client_a,
    associacao,
    conta_associacao,
    acao_associacao
):
    periodo = associacao.periodo_inicial
    visao_selecionada = "UE"

    associacao.periodo_inicial = None

    dados = {
        "associacao": {
            "status_valores_reprogramados": associacao.status_valores_reprogramados,
            "uuid": f"{associacao.uuid}"
        },
        "contas": [{
            "conta": {
                "acoes": [{
                    "custeio": {
                        "nome": "custeio",
                        "status_conferencia": None,
                        "valor_dre": None,
                        "valor_ue": None
                    },
                    "nome": acao_associacao.acao.nome,
                    "uuid": f"{acao_associacao.uuid}"
                }],
                "tipo_conta": conta_associacao.tipo_conta.nome,
                "uuid": f"{conta_associacao.uuid}"
            }
        }]
    }

    resultado_esperado = {
        'saldo_salvo': False,
        'codigo_erro': 'periodo_inicial_nao_definido',
        'mensagem': 'Período inicial não foi definido para essa associação. Verifique com o administrador.',
    }

    retorno = salvar_e_concluir_valores_reprogramados(associacao, periodo, dados, visao_selecionada)

    assert retorno == resultado_esperado


def test_salvar_valores_reprogramados_sem_contas(
    jwt_authenticated_client_a,
    associacao,
    conta_associacao,
    acao_associacao
):
    periodo = associacao.periodo_inicial
    visao_selecionada = "UE"

    dados = {
        "associacao": {
            "status_valores_reprogramados": associacao.status_valores_reprogramados,
            "uuid": f"{associacao.uuid}"
        },
        "contas": []
    }

    resultado_esperado = {
        'saldo_salvo': False,
        'codigo_erro': 'contas_nao_informadas',
        'mensagem': 'É necessário informar as contas',
    }

    retorno = salvar_e_concluir_valores_reprogramados(associacao, periodo, dados, visao_selecionada)

    assert retorno == resultado_esperado


def test_concluir_valores_reprogramados(
    jwt_authenticated_client_a,
    associacao,
    conta_associacao,
    acao_associacao
):
    periodo = associacao.periodo_inicial
    visao_selecionada = "DRE"

    dados = {
        "associacao": {
            "status_valores_reprogramados": associacao.status_valores_reprogramados,
            "uuid": f"{associacao.uuid}"
        },
        "contas": [{
            "conta": {
                "acoes": [{
                    "custeio": {
                        "nome": "custeio",
                        "status_conferencia": None,
                        "valor_dre": 0.10,
                        "valor_ue": 0.20
                    },
                    "nome": acao_associacao.acao.nome,
                    "uuid": f"{acao_associacao.uuid}"
                }],
                "tipo_conta": conta_associacao.tipo_conta.nome,
                "uuid": f"{conta_associacao.uuid}"
            }
        }]
    }

    resultado_esperado = {
        'saldo_salvo': True,
        'codigo_erro': None,
        'mensagem': 'Saldo salvo com sucesso'
    }

    retorno = salvar_e_concluir_valores_reprogramados(associacao, periodo, dados, visao_selecionada, concluir=True)

    assert retorno == resultado_esperado


def test_concluir_valores_reprogramados_sem_periodo_inicial(
    jwt_authenticated_client_a,
    associacao,
    conta_associacao,
    acao_associacao
):
    periodo = associacao.periodo_inicial
    visao_selecionada = "DRE"

    associacao.periodo_inicial = None

    dados = {
        "associacao": {
            "status_valores_reprogramados": associacao.status_valores_reprogramados,
            "uuid": f"{associacao.uuid}"
        },
        "contas": [{
            "conta": {
                "acoes": [{
                    "custeio": {
                        "nome": "custeio",
                        "status_conferencia": None,
                        "valor_dre": None,
                        "valor_ue": None
                    },
                    "nome": acao_associacao.acao.nome,
                    "uuid": f"{acao_associacao.uuid}"
                }],
                "tipo_conta": conta_associacao.tipo_conta.nome,
                "uuid": f"{conta_associacao.uuid}"
            }
        }]
    }

    resultado_esperado = {
        'saldo_salvo': False,
        'codigo_erro': 'periodo_inicial_nao_definido',
        'mensagem': 'Período inicial não foi definido para essa associação. Verifique com o administrador.',
    }

    retorno = salvar_e_concluir_valores_reprogramados(associacao, periodo, dados, visao_selecionada)

    assert retorno == resultado_esperado


def test_concluir_valores_reprogramados_sem_contas(
    jwt_authenticated_client_a,
    associacao,
    conta_associacao,
    acao_associacao
):
    periodo = associacao.periodo_inicial
    visao_selecionada = "DRE"

    dados = {
        "associacao": {
            "status_valores_reprogramados": associacao.status_valores_reprogramados,
            "uuid": f"{associacao.uuid}"
        },
        "contas": []
    }

    resultado_esperado = {
        'saldo_salvo': False,
        'codigo_erro': 'contas_nao_informadas',
        'mensagem': 'É necessário informar as contas',
    }

    retorno = salvar_e_concluir_valores_reprogramados(associacao, periodo, dados, visao_selecionada)

    assert retorno == resultado_esperado


def test_calcula_novo_status_ue_nao_finalizado(
    jwt_authenticated_client_a,
    associacao_status_nao_finalizado,
    valores_reprogramados_nao_finalizado
):
    visao_selecionada = "UE"

    novo_status = calcula_novo_status(associacao_status_nao_finalizado, visao_selecionada)

    assert novo_status == "EM_CONFERENCIA_DRE"


def test_calcula_novo_status_ue_correcao_ue_valores_diferentes(
    jwt_authenticated_client_a,
    associacao_status_correcao_ue,
    valores_reprogramados_correcao_ue
):
    visao_selecionada = "UE"

    novo_status = calcula_novo_status(associacao_status_correcao_ue, visao_selecionada)

    assert novo_status == "EM_CONFERENCIA_DRE"


def test_calcula_novo_status_ue_correcao_ue_valores_iguais(
    jwt_authenticated_client_a,
    associacao_status_correcao_ue,
    valores_reprogramados_correcao_ue_com_valores_iguais
):
    visao_selecionada = "UE"

    novo_status = calcula_novo_status(associacao_status_correcao_ue, visao_selecionada)

    assert novo_status == "VALORES_CORRETOS"


def test_calcula_novo_status_ue_conferencia_dre(
    jwt_authenticated_client_a,
    associacao_status_conferencia_dre,
    valores_reprogramados_conferencia_dre
):
    visao_selecionada = "DRE"

    novo_status = calcula_novo_status(associacao_status_conferencia_dre, visao_selecionada)

    assert novo_status == "EM_CORRECAO_UE"


def test_calcula_novo_status_ue_conferencia_dre_valores_iguais(
    jwt_authenticated_client_a,
    associacao_status_conferencia_dre,
    valores_reprogramados_conferencia_dre_com_valores_iguais
):
    visao_selecionada = "DRE"

    novo_status = calcula_novo_status(associacao_status_conferencia_dre, visao_selecionada)

    assert novo_status == "VALORES_CORRETOS"


def test_calcula_novo_status_ue_valores_corretos(
    jwt_authenticated_client_a,
    associacao,
    valores_reprogramados_valores_corretos
):
    visao_selecionada = "DRE"

    novo_status = calcula_novo_status(associacao, visao_selecionada)

    assert novo_status == "EM_CORRECAO_UE"


def test_calcula_novo_status_ue_valores_corretos_valores_iguais(
    jwt_authenticated_client_a,
    associacao,
    valores_reprogramados_valores_corretos_com_valores_iguais
):
    visao_selecionada = "DRE"

    novo_status = calcula_novo_status(associacao, visao_selecionada)

    assert novo_status == "VALORES_CORRETOS"


def test_nao_tem_diferenca_nos_valores(
    associacao,
    valores_reprogramados_valores_corretos_com_valores_iguais,
    valores_reprogramados_valores_corretos_com_valores_iguais_2
):
    valores_iguais = possui_diferenca(associacao)

    assert valores_iguais is True


def test_tem_diferenca_nos_valores(
    associacao,
    valores_reprogramados_valores_corretos,
    valores_reprogramados_valores_corretos_com_valores_iguais
):
    valores_iguais = possui_diferenca(associacao)

    assert valores_iguais is False


def test_monta_estrutura_valores_reprogramados(
    associacao,
    conta_associacao,
    acao_associacao_aceita_custeio,
    valores_reprogramados_valores_corretos
):

    esperado = [{
        "conta": {
            "uuid": f"{conta_associacao.uuid}",
            "tipo_conta": conta_associacao.tipo_conta.nome,
            "acoes": [{
                "nome": acao_associacao_aceita_custeio.acao.nome,
                "uuid": f"{acao_associacao_aceita_custeio.uuid}",
                "custeio": {
                    "nome": "custeio",
                    "valor_ue": Decimal('0.10'),
                    "valor_dre": Decimal('0.20'),
                    "status_conferencia": "incorreto"
                }
            }]
        }
    }]

    resultado = monta_estrutura_valores_reprogramados(associacao)

    assert resultado == esperado


def test_barra_status_nao_finalizado(
    associacao_status_nao_finalizado
):
    esperado = {
        "texto": 'Não finalizado pela Associação',
        "cor": 1,
        "periodo_fechado": None
    }

    resultado = barra_status(associacao_status_nao_finalizado)

    assert esperado == resultado


def test_barra_status_conferencia_dre(
    associacao_status_conferencia_dre
):
    esperado = {
        "texto": 'Aguardando conferência da DRE',
        "cor": 2,
        "periodo_fechado": None
    }

    resultado = barra_status(associacao_status_conferencia_dre)

    assert esperado == resultado


def test_barra_status_correcao_ue(
    associacao_status_correcao_ue
):
    esperado = {
        "texto": 'Aguardando correção pela Associação',
        "cor": 3,
        "periodo_fechado": None
    }

    resultado = barra_status(associacao_status_correcao_ue)

    assert esperado == resultado


def test_barra_status_valores_corretos(
    associacao,
):
    esperado = {
        "texto": 'Análise concluída: valores corretos',
        "cor": 4,
        "periodo_fechado": None
    }

    resultado = barra_status(associacao)

    assert esperado == resultado


def test_barra_status_periodo_fechado(
    associacao,
    prestacao_conta_iniciada
):
    esperado = {
        "texto": 'Análise concluída: valores corretos **Período fechado**',
        "cor": 4,
        "periodo_fechado": True
    }

    resultado = barra_status(associacao)

    assert esperado == resultado
