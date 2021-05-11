def unidades_do_usuario_e_permissoes_na_visao(usuario, visao, unidade_logada=None):
    """ Retorna lista de unidades do usuário, com campo calculando informando se, na visão passada
    por parâmetro, o vínculo do usuário com a unidade pode ou não ser excluido.

    Regra de negócio:

    O vinculo unidade x usuario so pode ser excluido nas seguintes situações:

    1) Visão == SME

    2) Visão == DRE e Unidade.DRE == Unidade Logada

    3) Visão == UE e Unidade == Unidade Logada

    """

    unidades_e_permissoes = []
    for unidade in usuario.unidades.all():
        pode_excluir = False

        if (
            visao == "SME" or
            visao == "DRE" and (unidade.dre == unidade_logada or unidade == unidade_logada) or
            (visao == "UE" and unidade == unidade_logada)
        ):
            pode_excluir = True

        unidades_e_permissoes.append(
            {
                'uuid': f'{unidade.uuid}',
                'nome': unidade.nome,
                'codigo_eol': unidade.codigo_eol,
                'tipo_unidade': unidade.tipo_unidade,
                'pode_excluir': pode_excluir
            }
        )
    return unidades_e_permissoes
