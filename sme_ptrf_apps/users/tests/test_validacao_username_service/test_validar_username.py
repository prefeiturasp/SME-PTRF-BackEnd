import pytest

from ...services.validacao_username_service import validar_username

def test_validar_username_servidor():
    """ Para usuários servidores o username pode ser qualquer número.
    """
    username = '123456'
    e_servidor = True
    validacao_esperada = {
        'username_e_valido': True,
        'mensagem': "",
    }
    validacao = validar_username(username=username, e_servidor=e_servidor)

    assert validacao == validacao_esperada, "Deveria ser considerado um username válido."

def test_validar_username_nao_servidor_cpf_invalido():
    """ Para usuários não servidores o username tem que ser um CPF válido (apenas dígitos).
    """
    validacao_esperada = {
        'username_e_valido': False,
        'mensagem': "O id de um usuário não servidor deve ser um CPF válido (apenas dígitos).",
    }
    cpf_invalido = '123456'
    validacao = validar_username(username=cpf_invalido, e_servidor=False)

    assert validacao == validacao_esperada, "Deveria ser considerado um username inválido."


def test_validar_username_nao_servidor_cpf_valido():
    """ Para usuários não servidores o username tem que ser um CPF válido (apenas dígitos).
    """
    validacao_esperada = {
        'username_e_valido': True,
        'mensagem': "",
    }
    cpf_valido = '00746198701'
    validacao = validar_username(username=cpf_valido, e_servidor=False)

    assert validacao == validacao_esperada, "Deveria ser considerado um username válido."
