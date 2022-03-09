import pytest

from ....services.membro_associacao_service import seleciona_cargo_servidor

pytestmark = pytest.mark.django_db


def test_seleciona_cargo_servidor_diretor():
    result_info_servidor = [
        {
            "nm_pessoa": "ANA PAULA FRANCA REBOUCAS GUIDOTTI ROCHA",
            "cd_cpf_pessoa": "27456232814",
            "cargo": "PROF.ENS.FUND.II E MED.-MATEMATICA",
            "cd_divisao": "019277",
            "divisao": "VILA ATLANTICA",
            "cd_coord": "109000",
            "coord": "DIRETORIA REGIONAL DE EDUCACAO PIRITUBA/JARAGUA"
        },
        {
            "nm_pessoa": "ANA PAULA FRANCA REBOUCAS GUIDOTTI ROCHA",
            "cd_cpf_pessoa": "27456232814",
            "cargo": "DIRETOR DE ESCOLA",
            "cd_divisao": "019296",
            "divisao": "VILA ATLANTICA",
            "cd_coord": "109000",
            "coord": "DIRETORIA REGIONAL DE EDUCACAO PIRITUBA/JARAGUA"
        }
    ]
    resultado_esperado = [
        {
            "nm_pessoa": "ANA PAULA FRANCA REBOUCAS GUIDOTTI ROCHA",
            "cd_cpf_pessoa": "27456232814",
            "cargo": "DIRETOR DE ESCOLA",
            "cd_divisao": "019296",
            "divisao": "VILA ATLANTICA",
            "cd_coord": "109000",
            "coord": "DIRETORIA REGIONAL DE EDUCACAO PIRITUBA/JARAGUA"
        },
    ]
    resultado = seleciona_cargo_servidor(result_info_servidor)

    assert resultado == resultado_esperado


def test_seleciona_cargo_servidor_coordenador():
    result_info_servidor = [
        {
            "nm_pessoa": "ANA PAULA FRANCA REBOUCAS GUIDOTTI ROCHA",
            "cd_cpf_pessoa": "27456232814",
            "cargo": "PROF.ENS.FUND.II E MED.-MATEMATICA",
            "cd_divisao": "019277",
            "divisao": "VILA ATLANTICA",
            "cd_coord": "109000",
            "coord": "DIRETORIA REGIONAL DE EDUCACAO PIRITUBA/JARAGUA"
        },
        {
            "nm_pessoa": "ANA PAULA FRANCA REBOUCAS GUIDOTTI ROCHA",
            "cd_cpf_pessoa": "27456232814",
            "cargo": "COORDENADOR PEDAGOGICO",
            "cd_divisao": "019296",
            "divisao": "VILA ATLANTICA",
            "cd_coord": "109000",
            "coord": "DIRETORIA REGIONAL DE EDUCACAO PIRITUBA/JARAGUA"
        }
    ]
    resultado_esperado = [
        {
            "nm_pessoa": "ANA PAULA FRANCA REBOUCAS GUIDOTTI ROCHA",
            "cd_cpf_pessoa": "27456232814",
            "cargo": "COORDENADOR PEDAGOGICO",
            "cd_divisao": "019296",
            "divisao": "VILA ATLANTICA",
            "cd_coord": "109000",
            "coord": "DIRETORIA REGIONAL DE EDUCACAO PIRITUBA/JARAGUA"
        },
    ]
    resultado = seleciona_cargo_servidor(result_info_servidor)

    assert resultado == resultado_esperado


def test_seleciona_cargo_servidor_assistente():
    result_info_servidor = [
        {
            "nm_pessoa": "ANA PAULA FRANCA REBOUCAS GUIDOTTI ROCHA",
            "cd_cpf_pessoa": "27456232814",
            "cargo": "PROF.ENS.FUND.II E MED.-MATEMATICA",
            "cd_divisao": "019277",
            "divisao": "VILA ATLANTICA",
            "cd_coord": "109000",
            "coord": "DIRETORIA REGIONAL DE EDUCACAO PIRITUBA/JARAGUA"
        },
        {
            "nm_pessoa": "ANA PAULA FRANCA REBOUCAS GUIDOTTI ROCHA",
            "cd_cpf_pessoa": "27456232814",
            "cargo": "ASSISTENTE DE DIRECAO",
            "cd_divisao": "019296",
            "divisao": "VILA ATLANTICA",
            "cd_coord": "109000",
            "coord": "DIRETORIA REGIONAL DE EDUCACAO PIRITUBA/JARAGUA"
        }
    ]
    resultado_esperado = [
        {
            "nm_pessoa": "ANA PAULA FRANCA REBOUCAS GUIDOTTI ROCHA",
            "cd_cpf_pessoa": "27456232814",
            "cargo": "ASSISTENTE DE DIRECAO",
            "cd_divisao": "019296",
            "divisao": "VILA ATLANTICA",
            "cd_coord": "109000",
            "coord": "DIRETORIA REGIONAL DE EDUCACAO PIRITUBA/JARAGUA"
        },
    ]
    resultado = seleciona_cargo_servidor(result_info_servidor)

    assert resultado == resultado_esperado


def test_seleciona_cargo_servidor_primeiro():
    result_info_servidor = [
        {
            "nm_pessoa": "ANA PAULA FRANCA REBOUCAS GUIDOTTI ROCHA",
            "cd_cpf_pessoa": "27456232814",
            "cargo": "PROF.ENS.FUND.II E MED.-MATEMATICA",
            "cd_divisao": "019277",
            "divisao": "VILA ATLANTICA",
            "cd_coord": "109000",
            "coord": "DIRETORIA REGIONAL DE EDUCACAO PIRITUBA/JARAGUA"
        },
        {
            "nm_pessoa": "ANA PAULA FRANCA REBOUCAS GUIDOTTI ROCHA",
            "cd_cpf_pessoa": "27456232814",
            "cargo": "OUTRO CARGO",
            "cd_divisao": "019296",
            "divisao": "VILA ATLANTICA",
            "cd_coord": "109000",
            "coord": "DIRETORIA REGIONAL DE EDUCACAO PIRITUBA/JARAGUA"
        }
    ]
    resultado_esperado = [
        {
            "nm_pessoa": "ANA PAULA FRANCA REBOUCAS GUIDOTTI ROCHA",
            "cd_cpf_pessoa": "27456232814",
            "cargo": "PROF.ENS.FUND.II E MED.-MATEMATICA",
            "cd_divisao": "019277",
            "divisao": "VILA ATLANTICA",
            "cd_coord": "109000",
            "coord": "DIRETORIA REGIONAL DE EDUCACAO PIRITUBA/JARAGUA"
        },
    ]
    resultado = seleciona_cargo_servidor(result_info_servidor)

    assert resultado == resultado_esperado


def test_seleciona_cargo_servidor_apenas_um():
    result_info_servidor = [
        {
            "nm_pessoa": "ANA PAULA FRANCA REBOUCAS GUIDOTTI ROCHA",
            "cd_cpf_pessoa": "27456232814",
            "cargo": "PROF.ENS.FUND.II E MED.-MATEMATICA",
            "cd_divisao": "019277",
            "divisao": "VILA ATLANTICA",
            "cd_coord": "109000",
            "coord": "DIRETORIA REGIONAL DE EDUCACAO PIRITUBA/JARAGUA"
        },
    ]
    resultado_esperado = [
        {
            "nm_pessoa": "ANA PAULA FRANCA REBOUCAS GUIDOTTI ROCHA",
            "cd_cpf_pessoa": "27456232814",
            "cargo": "PROF.ENS.FUND.II E MED.-MATEMATICA",
            "cd_divisao": "019277",
            "divisao": "VILA ATLANTICA",
            "cd_coord": "109000",
            "coord": "DIRETORIA REGIONAL DE EDUCACAO PIRITUBA/JARAGUA"
        },
    ]
    resultado = seleciona_cargo_servidor(result_info_servidor)

    assert resultado == resultado_esperado
