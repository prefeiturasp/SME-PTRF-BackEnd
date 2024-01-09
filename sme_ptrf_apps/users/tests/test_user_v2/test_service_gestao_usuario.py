import pytest

from ...services.gestao_usuario_service import GestaoUsuarioService
from unittest.mock import patch

pytestmark = pytest.mark.django_db


def test_retorna_lista_unidades_nao_servidor_visao_sme(
    usuario_nao_servidor_service_gestao_usuario,
    membro_associacao_nao_servidor_a,
    membro_associacao_nao_servidor_b
):
    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_service_gestao_usuario)
    result = gestao_usuario.retorna_lista_unidades_nao_servidor('SME', 'SME')

    assert len(result) == 2


def test_retorna_lista_unidades_nao_servidor_visao_dre(
    usuario_nao_servidor_service_gestao_usuario,
    membro_associacao_nao_servidor_a,
    membro_associacao_nao_servidor_b,
    dre
):
    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_service_gestao_usuario)
    result = gestao_usuario.retorna_lista_unidades_nao_servidor(unidade_base=dre, visao_base='DRE')

    assert len(result) == 1


def test_get_unidade_exercicio_quando_existe(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_b,
    unidade_gestao_usuario_c
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeLotacao": {
                "codigo": f"{unidade_gestao_usuario_b.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_b.nome}"
            },
            "unidadeExercicio": {
                "codigo": f"{unidade_gestao_usuario_c.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_c.nome}"
            }
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.get_info_unidade()

        assert data["unidadeExercicio"]["codigo"] == result["codigo"]
        assert data["unidadeExercicio"]["nomeUnidade"] == result["nomeUnidade"]


def test_get_unidade_lotacao_quando_unidade_exercicio_nao_existe(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_b,
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeLotacao": {
                "codigo": f"{unidade_gestao_usuario_b.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_b.nome}"
            },
            "unidadeExercicio": None
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.get_info_unidade()

        assert data["unidadeLotacao"]["codigo"] == result["codigo"]
        assert data["unidadeLotacao"]["nomeUnidade"] == result["nomeUnidade"]


def test_get_unidade_quando_unidade_exercicio_e_unidade_lotacao_nao_existe(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_b,
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeLotacao": None,
            "unidadeExercicio": None
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.get_info_unidade()

        assert result is None


def test_retorna_lista_unidades_servidor_sem_membro_associacao_visao_sme(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_c

):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeExercicio": {
                "codigo": f"{unidade_gestao_usuario_c.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_c.nome}"
            }
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.retorna_lista_unidades_servidor('SME', 'SME')

        assert len(result) == 1


def test_retorna_lista_unidades_servidor_sem_membro_associacao_e_unidade_exercicio_nao_pertence_a_dre_visao_sme(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_c,
    dre
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeExercicio": {
                "codigo": f"{unidade_gestao_usuario_c.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_c.nome}"
            }
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.retorna_lista_unidades_servidor('SME', 'SME')

        assert len(result) == 1


def test_retorna_lista_unidades_servidor_sem_membro_associacao_visao_dre(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_c,
    dre_ipiranga
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeExercicio": {
                "codigo": f"{unidade_gestao_usuario_c.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_c.nome}"
            }
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.retorna_lista_unidades_servidor(dre_ipiranga, 'DRE')

        assert len(result) == 1


def test_retorna_lista_unidades_servidor_sem_membro_associacao_e_unidade_exercicio_nao_pertence_a_dre_visao_dre(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_c,
    dre
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeExercicio": {
                "codigo": f"{unidade_gestao_usuario_c.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_c.nome}"
            }
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.retorna_lista_unidades_servidor(dre, 'DRE')

        assert len(result) == 0


def test_retorna_lista_unidades_servidor_com_membro_associacao_visao_sme(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_c,
    membro_associacao_servidor_a
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeExercicio": {
                "codigo": f"{unidade_gestao_usuario_c.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_c.nome}"
            }
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.retorna_lista_unidades_servidor('SME', 'SME')

        assert len(result) == 2


def test_retorna_lista_unidades_servidor_apenas_com_membro_associacao_visao_sme(
    usuario_servidor_service_gestao_usuario,
    membro_associacao_servidor_a,
    membro_associacao_servidor_b
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeExercicio": {}
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.retorna_lista_unidades_servidor('SME', 'SME')

        assert len(result) == 2


def test_retorna_lista_unidades_servidor_com_membro_associacao_visao_dre(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_c,
    membro_associacao_servidor_a,
    membro_associacao_servidor_b,
    dre
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeExercicio": {
                "codigo": f"{unidade_gestao_usuario_c.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_c.nome}"
            }
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.retorna_lista_unidades_servidor(dre, 'DRE')

        assert len(result) == 1


def test_retorna_lista_unidades_servidor_apenas_com_membro_associacao_visao_dre(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_c,
    membro_associacao_servidor_a,
    membro_associacao_servidor_b,
    dre_ipiranga
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeExercicio": {
                "codigo": f"{unidade_gestao_usuario_c.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_c.nome}"
            }
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.retorna_lista_unidades_servidor(dre_ipiranga, 'DRE')

        assert len(result) == 2


def test_habilita_acesso_ue(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_c,
    visao_ue_gestao_usuario
):
    assert unidade_gestao_usuario_c not in usuario_servidor_service_gestao_usuario.unidades.all()

    gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
    result = gestao_usuario.habilitar_acesso(unidade=unidade_gestao_usuario_c)

    assert "Acesso ativado para unidade selecionada" == result["mensagem"]
    assert unidade_gestao_usuario_c in usuario_servidor_service_gestao_usuario.unidades.all()
    assert visao_ue_gestao_usuario in usuario_servidor_service_gestao_usuario.visoes.all()


def test_habilita_acesso_dre(
    usuario_servidor_service_gestao_usuario,
    dre,
    visao_dre_gestao_usuario
):
    assert dre not in usuario_servidor_service_gestao_usuario.unidades.all()

    gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
    result = gestao_usuario.habilitar_acesso(unidade=dre)

    assert "Acesso ativado para unidade selecionada" == result["mensagem"]
    assert dre in usuario_servidor_service_gestao_usuario.unidades.all()
    assert visao_dre_gestao_usuario in usuario_servidor_service_gestao_usuario.visoes.all()


def test_habilita_acesso_sme(
    usuario_servidor_sem_visao_sme_service_gestao_usuario,
    visao_sme_gestao_usuario
):
    assert visao_sme_gestao_usuario not in usuario_servidor_sem_visao_sme_service_gestao_usuario.visoes.all()

    gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_sem_visao_sme_service_gestao_usuario)
    result = gestao_usuario.habilitar_acesso(unidade="SME")

    assert "Acesso ativado para unidade selecionada" == result["mensagem"]
    assert visao_sme_gestao_usuario in usuario_servidor_sem_visao_sme_service_gestao_usuario.visoes.all()


def test_desabilita_acesso_ue(
    usuario_nao_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a,
):
    assert unidade_gestao_usuario_a in usuario_nao_servidor_service_gestao_usuario.unidades.all()

    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_service_gestao_usuario)
    result = gestao_usuario.desabilitar_acesso(unidade=unidade_gestao_usuario_a)

    assert "Acesso desativado para unidade selecionada" == result["mensagem"]
    assert unidade_gestao_usuario_a not in usuario_nao_servidor_service_gestao_usuario.unidades.all()


def test_desabilita_acesso_dre(
    usuario_nao_servidor_service_gestao_usuario,
    dre,
):
    assert dre in usuario_nao_servidor_service_gestao_usuario.unidades.all()

    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_service_gestao_usuario)
    result = gestao_usuario.desabilitar_acesso(unidade=dre)

    assert "Acesso desativado para unidade selecionada" == result["mensagem"]
    assert dre not in usuario_nao_servidor_service_gestao_usuario.unidades.all()


def test_desabilita_acesso_sme(
    usuario_servidor_service_gestao_usuario,
    visao_sme_gestao_usuario,
):
    assert visao_sme_gestao_usuario in usuario_servidor_service_gestao_usuario.visoes.all()

    gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
    result = gestao_usuario.desabilitar_acesso(unidade="SME")

    assert "Acesso desativado para unidade selecionada" == result["mensagem"]
    assert visao_sme_gestao_usuario not in usuario_servidor_service_gestao_usuario.visoes.all()


def test_desabilita_acesso_e_remove_visao_ue(
    usuario_nao_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a,
    dre,
    visao_dre_gestao_usuario,
    visao_ue_gestao_usuario
):
    assert dre in usuario_nao_servidor_service_gestao_usuario.unidades.all()
    assert unidade_gestao_usuario_a in usuario_nao_servidor_service_gestao_usuario.unidades.all()

    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_service_gestao_usuario)
    result = gestao_usuario.desabilitar_acesso(unidade=unidade_gestao_usuario_a)

    assert "Acesso desativado para unidade selecionada" == result["mensagem"]
    assert dre in usuario_nao_servidor_service_gestao_usuario.unidades.all()
    assert unidade_gestao_usuario_a not in usuario_nao_servidor_service_gestao_usuario.unidades.all()

    assert visao_dre_gestao_usuario in usuario_nao_servidor_service_gestao_usuario.visoes.all()
    assert visao_ue_gestao_usuario not in usuario_nao_servidor_service_gestao_usuario.visoes.all()


def test_desabilita_acesso_e_remove_visao_dre(
    usuario_nao_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a,
    dre,
    visao_dre_gestao_usuario,
    visao_ue_gestao_usuario
):
    assert dre in usuario_nao_servidor_service_gestao_usuario.unidades.all()
    assert unidade_gestao_usuario_a in usuario_nao_servidor_service_gestao_usuario.unidades.all()

    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_service_gestao_usuario)
    result = gestao_usuario.desabilitar_acesso(unidade=dre)

    assert "Acesso desativado para unidade selecionada" == result["mensagem"]
    assert dre not in usuario_nao_servidor_service_gestao_usuario.unidades.all()
    assert unidade_gestao_usuario_a in usuario_nao_servidor_service_gestao_usuario.unidades.all()

    assert visao_dre_gestao_usuario not in usuario_nao_servidor_service_gestao_usuario.visoes.all()
    assert visao_ue_gestao_usuario in usuario_nao_servidor_service_gestao_usuario.visoes.all()


def test_desabilita_acesso_e_nao_remove_visao_ue(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a,
    unidade_gestao_usuario_b,
    visao_ue_gestao_usuario
):
    assert unidade_gestao_usuario_a in usuario_servidor_service_gestao_usuario.unidades.all()
    assert unidade_gestao_usuario_b in usuario_servidor_service_gestao_usuario.unidades.all()
    assert visao_ue_gestao_usuario in usuario_servidor_service_gestao_usuario.visoes.all()

    gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
    result = gestao_usuario.desabilitar_acesso(unidade=unidade_gestao_usuario_a)

    assert "Acesso desativado para unidade selecionada" == result["mensagem"]
    assert unidade_gestao_usuario_a not in usuario_servidor_service_gestao_usuario.unidades.all()
    assert unidade_gestao_usuario_b in usuario_servidor_service_gestao_usuario.unidades.all()
    assert visao_ue_gestao_usuario in usuario_servidor_service_gestao_usuario.visoes.all()


def test_servidor_membro_associacao_na_unidade(
    usuario_servidor_service_gestao_usuario,
    membro_associacao_servidor_a,
    unidade_gestao_usuario_a
):
    gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
    result = gestao_usuario.usuario_membro_associacao_na_unidade(unidade=unidade_gestao_usuario_a)

    assert result is True


def test_servidor_nao_e_membro_associacao_na_unidade(
    usuario_servidor_service_gestao_usuario,
    membro_associacao_servidor_a,
    membro_associacao_servidor_b,
    unidade_gestao_usuario_c
):
    gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
    result = gestao_usuario.usuario_membro_associacao_na_unidade(unidade=unidade_gestao_usuario_c)

    assert result is False


def test_usuario_possui_acesso_a_unidade(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a
):
    gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
    result = gestao_usuario.usuario_possui_acesso_a_unidade(unidade=unidade_gestao_usuario_a)

    assert result is True


def test_usuario_nao_possui_acesso_a_unidade(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_c
):
    gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
    result = gestao_usuario.usuario_possui_acesso_a_unidade(unidade=unidade_gestao_usuario_c)

    assert result is False


def test_unidades_do_usuario_do_servidor(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_c,
    membro_associacao_servidor_a,
    dre
):

    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeExercicio": {
                "codigo": f"{unidade_gestao_usuario_c.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_c.nome}"
            }
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.unidades_do_usuario(dre, 'SME')

        assert len(result) == 2


def test_unidades_do_usuario_do_nao_servidor(
    usuario_nao_servidor_service_gestao_usuario,
    unidade_gestao_usuario_c,
    membro_associacao_nao_servidor_a,
    dre
):

    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeExercicio": {
                "codigo": f"{unidade_gestao_usuario_c.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_c.nome}"
            }
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_service_gestao_usuario)
        result = gestao_usuario.unidades_do_usuario(dre, 'SME')

        assert len(result) == 1


def test_usuario_possui_visao(
    usuario_servidor_service_gestao_usuario
):
    gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
    result = gestao_usuario.usuario_possui_visao(visao="SME")

    assert result is True


def test_usuario_nao_possui_visao(
    usuario_servidor_service_gestao_usuario
):
    gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
    result = gestao_usuario.usuario_possui_visao(visao="DRE")

    assert result is False


def test_permite_tipo_unidade_administrativa(
    usuario_servidor_service_gestao_usuario,
    parametros_sme
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
    with patch(path) as mock_get:
        data = {
            "tipoUnidadeAdm": "1"
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.permite_tipo_unidade_administrativa("000000")

        assert result is True


def test_nao_permite_tipo_unidade_administrativa(
    usuario_servidor_service_gestao_usuario,
    parametros_sme
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
    with patch(path) as mock_get:
        data = {
            "tipoUnidadeAdm": "65"
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.permite_tipo_unidade_administrativa("000000")

        assert result is False


def test_retorno_get_dados_unidade_eol_sem_tipo_unidade_adm(
    usuario_servidor_service_gestao_usuario,
    parametros_sme
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
    with patch(path) as mock_get:
        data = {
            "teste": None
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.permite_tipo_unidade_administrativa("000000")

        assert result is False


# TODO Débito técnico: Rever mocks da api SMEIntegração. Teste quebrando após alterações na API.
# def test_retorna_lista_unidades_servidor_com_direito_sme(
#     usuario_servidor_service_gestao_usuario,
#     parametros_sme
# ):
#     path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
#     with patch(path) as mock_get:
#         data = {
#             "tipoUnidadeAdm": "1"
#         }
#
#         mock_get.return_value = data
#
#         gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
#         result = gestao_usuario.retorna_lista_unidades_servidor('SME', 'SME')
#
#         assert len(result) == 1


def test_retorna_lista_unidades_servidor_com_direito_sme_e_unidades(
    usuario_servidor_service_gestao_usuario,
    parametros_sme,
    unidade_gestao_usuario_c
):

    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeExercicio": {
                "codigo": f"{unidade_gestao_usuario_c.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_c.nome}"
            }
        }

        mock_get.return_value = data

        path_dados_unidade = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
        with patch(path_dados_unidade) as mock_get_dados_unidade:
            data_dados_unidade = {
                "tipoUnidadeAdm": "1"
            }

            mock_get_dados_unidade.return_value = data_dados_unidade

            gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
            result = gestao_usuario.retorna_lista_unidades_servidor('SME', 'SME')

            assert len(result) == 2


def test_retorna_lista_unidades_sme_no_topo(
    usuario_servidor_service_gestao_usuario,
    parametros_sme,
    unidade_gestao_usuario_c,
    membro_associacao_servidor_a
):

    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeExercicio": {
                "codigo": f"{unidade_gestao_usuario_c.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_c.nome}"
            }
        }

        mock_get.return_value = data

        path_dados_unidade = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
        with patch(path_dados_unidade) as mock_get_dados_unidade:
            data_dados_unidade = {
                "tipoUnidadeAdm": "1"
            }

            mock_get_dados_unidade.return_value = data_dados_unidade

            gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
            result = gestao_usuario.retorna_lista_unidades_servidor('SME', 'SME')

            assert len(result) == 3
            assert result[0]["uuid_unidade"] == "SME"


def test_retorna_lista_unidades_nao_servidor_com_flag_pode_acessar_sme(
    usuario_nao_servidor_sem_visao_dre_service_gestao_usuario,
):
    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_sem_visao_dre_service_gestao_usuario)
    result = gestao_usuario.retorna_lista_unidades_nao_servidor('SME', 'SME')

    assert len(result) == 1
    assert result[0]["uuid_unidade"] == 'SME'


def test_retorna_lista_unidades_nao_servidor_sem_flag_pode_acessar_sme(
    usuario_nao_servidor_service_gestao_usuario,
):
    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_service_gestao_usuario)
    result = gestao_usuario.retorna_lista_unidades_nao_servidor('SME', 'SME')

    assert len(result) == 0


def test_retorna_lista_unidades_servidor_sem_direito_sme_mas_com_flag_pode_acessar_sme(
    usuario_servidor_sem_visao_sme_service_gestao_usuario,
    parametros_sme,
    unidade_gestao_usuario_a
):

    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeExercicio": {
                "codigo": f"{unidade_gestao_usuario_a.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_a.nome}"
            }
        }

        mock_get.return_value = data

        path_dados_unidade = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
        with patch(path_dados_unidade) as mock_get_dados_unidade:
            data_dados_unidade = {
                "tipoUnidadeAdm": "4"
            }

            mock_get_dados_unidade.return_value = data_dados_unidade

            gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_sem_visao_sme_service_gestao_usuario)
            result = gestao_usuario.retorna_lista_unidades_servidor('SME', 'SME')

            assert len(result) == 2
            assert result[0]["uuid_unidade"] == 'SME'


def test_retorna_lista_unidades_servidor_sem_direito_sme_e_sem_flag_pode_acessar_sme(
    usuario_servidor_service_gestao_usuario,
    parametros_sme,
    unidade_gestao_usuario_c
):

    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor'
    with patch(path) as mock_get:
        data = {
            "unidadeExercicio": {
                "codigo": f"{unidade_gestao_usuario_c.codigo_eol}",
                "nomeUnidade": f"{unidade_gestao_usuario_c.nome}"
            }
        }

        mock_get.return_value = data

        path_dados_unidade = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
        with patch(path_dados_unidade) as mock_get_dados_unidade:
            data_dados_unidade = {
                "tipoUnidadeAdm": "4"
            }

            mock_get_dados_unidade.return_value = data_dados_unidade

            gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
            result = gestao_usuario.retorna_lista_unidades_servidor('SME', 'SME')

            assert len(result) == 1
            assert result[0]["uuid_unidade"] == f'{unidade_gestao_usuario_c.uuid}'
