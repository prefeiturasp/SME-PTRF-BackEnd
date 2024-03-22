import pytest

from ...services.gestao_usuario_service import GestaoUsuarioService
from ...services.login_usuario_service import LoginUsuarioService
from unittest.mock import patch

pytestmark = pytest.mark.django_db


def test_get_unidades_que_usuario_tem_acesso_nao_servidor(
    usuario_nao_servidor_service_gestao_usuario,
    membro_associacao_nao_servidor_a,
    membro_associacao_nao_servidor_b
):
    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_service_gestao_usuario)
    login_service = LoginUsuarioService(
        usuario=usuario_nao_servidor_service_gestao_usuario,
        gestao_usuario=gestao_usuario
    )

    result = login_service.unidades_que_usuario_tem_acesso

    assert len(result) == 1


def test_get_unidades_que_usuario_tem_acesso_servidor(
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

        path_dados_unidade = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
        with patch(path_dados_unidade) as mock_get_dados_unidade:
            data = {
                "tipoUnidadeAdm": "1"
            }

            mock_get_dados_unidade.return_value = data

            gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)

            login_service = LoginUsuarioService(
                usuario=usuario_servidor_service_gestao_usuario,
                gestao_usuario=gestao_usuario
            )
            result = login_service.unidades_que_usuario_tem_acesso

            assert len(result) == 1


def test_get_unidades_que_usuario_tem_acesso_servidor_com_sme(
    usuario_servidor_service_gestao_usuario,
    tipo_unidade_administrativa,
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

            login_service = LoginUsuarioService(
                usuario=usuario_servidor_service_gestao_usuario,
                gestao_usuario=gestao_usuario
            )

            result = login_service.unidades_que_usuario_tem_acesso

            assert len(result) == 2


def test_valida_unidades_usuario_nao_deve_remover_unidades_flag_false(
    usuario_nao_servidor_sem_visao_dre_service_gestao_usuario,
    parametros_sme_valida_unidades_login_falso,
    membro_associacao_nao_servidor_a,
    membro_associacao_nao_servidor_b
):
    assert usuario_nao_servidor_sem_visao_dre_service_gestao_usuario.unidades.count() == 2

    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_sem_visao_dre_service_gestao_usuario)

    # A função valida_unidades_usuario() é chamada internamente no serviço
    LoginUsuarioService(
        usuario=usuario_nao_servidor_sem_visao_dre_service_gestao_usuario,
        gestao_usuario=gestao_usuario
    )

    assert usuario_nao_servidor_sem_visao_dre_service_gestao_usuario.unidades.count() == 2


def test_valida_unidades_usuario_nao_servidor_nao_deve_remover_unidades_flag_true(
    usuario_nao_servidor_sem_visao_dre_service_gestao_usuario,
    parametros_sme,
    membro_associacao_nao_servidor_a,
    membro_associacao_nao_servidor_b
):
    assert usuario_nao_servidor_sem_visao_dre_service_gestao_usuario.unidades.count() == 2

    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_sem_visao_dre_service_gestao_usuario)

    # A função valida_unidades_usuario() é chamada internamente no serviço
    LoginUsuarioService(
        usuario=usuario_nao_servidor_sem_visao_dre_service_gestao_usuario,
        gestao_usuario=gestao_usuario
    )

    assert usuario_nao_servidor_sem_visao_dre_service_gestao_usuario.unidades.count() == 2


def test_valida_unidades_usuario_servidor_nao_deve_remover_unidades_flag_true(
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
            data = {
                "tipoUnidadeAdm": "1"
            }

            mock_get_dados_unidade.return_value = data

            assert usuario_servidor_sem_visao_sme_service_gestao_usuario.unidades.count() == 1

            gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_sem_visao_sme_service_gestao_usuario)

            # A função valida_unidades_usuario() é chamada internamente no serviço
            LoginUsuarioService(
                usuario=usuario_servidor_sem_visao_sme_service_gestao_usuario,
                gestao_usuario=gestao_usuario
            )

            assert usuario_servidor_sem_visao_sme_service_gestao_usuario.unidades.count() == 1


def test_valida_unidades_usuario_deve_remover_unidade(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a,
    unidade_gestao_usuario_b,
    parametros_sme
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
            data = {
                "tipoUnidadeAdm": "1"
            }

            mock_get_dados_unidade.return_value = data

            assert usuario_servidor_service_gestao_usuario.unidades.count() == 2

            gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)

            # A função valida_unidades_usuario() é chamada internamente no serviço
            LoginUsuarioService(
                usuario=usuario_servidor_service_gestao_usuario,
                gestao_usuario=gestao_usuario
            )

            assert usuario_servidor_service_gestao_usuario.unidades.count() == 1


def test_valida_unidades_usuario_nao_deve_remover_unidade_suporte(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a,
    unidade_gestao_usuario_b,
    unidade_em_suporte_gestao_usuarios,
    parametros_sme
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
            data = {
                "tipoUnidadeAdm": "1"
            }

            mock_get_dados_unidade.return_value = data

            assert usuario_servidor_service_gestao_usuario.unidades.count() == 2
            assert usuario_servidor_service_gestao_usuario.acessos_de_suporte.count() == 1

            gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)

            # A função valida_unidades_usuario() é chamada internamente no serviço
            LoginUsuarioService(
                usuario=usuario_servidor_service_gestao_usuario,
                gestao_usuario=gestao_usuario
            )

            assert usuario_servidor_service_gestao_usuario.unidades.count() == 2
            assert usuario_servidor_service_gestao_usuario.acessos_de_suporte.count() == 1


def test_valida_unidades_usuario_deve_remover_sme_e_unidade(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a,
    unidade_gestao_usuario_b,
    visao_sme_gestao_usuario,
    parametros_sme
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
            data = {
                "tipoUnidadeAdm": "1"
            }

            mock_get_dados_unidade.return_value = data

            assert usuario_servidor_service_gestao_usuario.unidades.count() == 2
            assert visao_sme_gestao_usuario in usuario_servidor_service_gestao_usuario.visoes.all()

            gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)

            # A função valida_unidades_usuario() é chamada internamente no serviço
            LoginUsuarioService(
                usuario=usuario_servidor_service_gestao_usuario,
                gestao_usuario=gestao_usuario
            )

            assert usuario_servidor_service_gestao_usuario.unidades.count() == 1
            assert visao_sme_gestao_usuario not in usuario_servidor_service_gestao_usuario.visoes.all()


def test_lista_unidades_que_perdeu_acesso(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a,
    unidade_gestao_usuario_b,
    visao_sme_gestao_usuario,
    parametros_sme
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
            data = {
                "tipoUnidadeAdm": "1"
            }

            mock_get_dados_unidade.return_value = data

            assert usuario_servidor_service_gestao_usuario.unidades.count() == 2
            assert visao_sme_gestao_usuario in usuario_servidor_service_gestao_usuario.visoes.all()

            gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)

            # A função valida_unidades_usuario() é chamada internamente no serviço
            login_service = LoginUsuarioService(
                usuario=usuario_servidor_service_gestao_usuario,
                gestao_usuario=gestao_usuario
            )

            assert usuario_servidor_service_gestao_usuario.unidades.count() == 1
            assert visao_sme_gestao_usuario not in usuario_servidor_service_gestao_usuario.visoes.all()

            assert len(login_service.unidades_que_perdeu_acesso) == 2


def test_get_mensagem_perdeu_acesso(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a,
    unidade_gestao_usuario_b,
    visao_sme_gestao_usuario,
    parametros_sme
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
            data = {
                "tipoUnidadeAdm": "1"
            }

            mock_get_dados_unidade.return_value = data

            assert usuario_servidor_service_gestao_usuario.unidades.count() == 2
            assert visao_sme_gestao_usuario in usuario_servidor_service_gestao_usuario.visoes.all()

            gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)

            # A função valida_unidades_usuario() é chamada internamente no serviço
            login_service = LoginUsuarioService(
                usuario=usuario_servidor_service_gestao_usuario,
                gestao_usuario=gestao_usuario
            )

            assert usuario_servidor_service_gestao_usuario.unidades.count() == 1
            assert visao_sme_gestao_usuario not in usuario_servidor_service_gestao_usuario.visoes.all()

            assert login_service.mensagem_perca_acesso == "Favor entrar em contato com a DRE."
            assert login_service.get_exibe_modal() is True


def test_get_mensagem_perdeu_acesso_tecnico_dre(
    usuario_servidor_service_gestao_usuario,
    tecnico_dre_gestao_usuario,
    unidade_gestao_usuario_a,
    unidade_gestao_usuario_b,
    visao_sme_gestao_usuario,
    parametros_sme
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
            data = {
                "tipoUnidadeAdm": "1"
            }

            mock_get_dados_unidade.return_value = data

            assert usuario_servidor_service_gestao_usuario.unidades.count() == 2
            assert visao_sme_gestao_usuario in usuario_servidor_service_gestao_usuario.visoes.all()

            gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)

            # A função valida_unidades_usuario() é chamada internamente no serviço
            login_service = LoginUsuarioService(
                usuario=usuario_servidor_service_gestao_usuario,
                gestao_usuario=gestao_usuario
            )

            assert usuario_servidor_service_gestao_usuario.unidades.count() == 1
            assert visao_sme_gestao_usuario not in usuario_servidor_service_gestao_usuario.visoes.all()

            assert login_service.mensagem_perca_acesso == "Favor entrar em contato com a SME."
            assert login_service.get_exibe_modal() is True


def test_get_mensagem_perdeu_acesso_deve_retornar_none(
    usuario_nao_servidor_sem_visao_dre_service_gestao_usuario,
    parametros_sme,
    membro_associacao_nao_servidor_a,
    membro_associacao_nao_servidor_b
):
    assert usuario_nao_servidor_sem_visao_dre_service_gestao_usuario.unidades.count() == 2

    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_sem_visao_dre_service_gestao_usuario)

    # A função valida_unidades_usuario() é chamada internamente no serviço
    login_service = LoginUsuarioService(
        usuario=usuario_nao_servidor_sem_visao_dre_service_gestao_usuario,
        gestao_usuario=gestao_usuario
    )

    assert usuario_nao_servidor_sem_visao_dre_service_gestao_usuario.unidades.count() == 2

    assert login_service.mensagem_perca_acesso is None
    assert login_service.get_exibe_modal() is False
    assert len(login_service.unidades_que_perdeu_acesso) == 0

