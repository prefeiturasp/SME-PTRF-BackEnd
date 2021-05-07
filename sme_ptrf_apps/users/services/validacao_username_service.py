from brazilnum.cpf import validate_cpf

def validar_username(username, e_servidor=True):
    if not e_servidor:
        username_e_valido = validate_cpf(username)
        mensagem = "O id de um usuário não servidor deve ser um CPF válido (apenas dígitos)." if not username_e_valido else ""
    else:
        username_e_valido = True
        mensagem = ""

    return {
        'username_e_valido': username_e_valido,
        'mensagem': mensagem,
    }
