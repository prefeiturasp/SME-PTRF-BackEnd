import pytest

from ...services.gestao_usuario_service import GestaoUsuarioService
from unittest.mock import patch
from datetime import datetime, timedelta
from sme_ptrf_apps.mandatos.models.cargo_composicao import CargoComposicao
from brazilnum.cpf import format_cpf
from waffle.testutils import override_flag

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

        path_dados_unidade = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
        with patch(path_dados_unidade) as mock_get_dados_unidade:
            data = {
                "tipoUnidadeAdm": "1"
            }

            mock_get_dados_unidade.return_value = data

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

        path_dados_unidade = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
        with patch(path_dados_unidade) as mock_get_dados_unidade:
            data = {
                "tipoUnidadeAdm": "1"
            }

            mock_get_dados_unidade.return_value = data

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

        path_dados_unidade = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
        with patch(path_dados_unidade) as mock_get_dados_unidade:
            data = {
                "tipoUnidadeAdm": "1"
            }

            mock_get_dados_unidade.return_value = data

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

        path_dados_unidade = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
        with patch(path_dados_unidade) as mock_get_dados_unidade:
            data = {
                "tipoUnidadeAdm": "1"
            }

            mock_get_dados_unidade.return_value = data

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
    tipo_unidade_administrativa
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
    tipo_unidade_administrativa
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
    tipo_unidade_administrativa
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


def test_retorna_lista_unidades_servidor_com_direito_sme(
    usuario_servidor_service_gestao_usuario,
    tipo_unidade_administrativa,
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


def test_retorna_lista_unidades_servidor_com_direito_sme_e_unidades(
    usuario_servidor_service_gestao_usuario,
    tipo_unidade_administrativa,
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
    tipo_unidade_administrativa,
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
    tipo_unidade_administrativa,
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


def test_permite_tipo_unidade_administrativa_nao_encontrado_deve_retornar_false(
    usuario_servidor_service_gestao_usuario,
    tipo_unidade_administrativa
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
    with patch(path) as mock_get:
        data = {
            "tipoUnidadeAdm": "65"
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.permite_tipo_unidade_administrativa("120000")

        assert result is False


def test_permite_tipo_unidade_administrativa_encontrado_sem_codigo_eol_deve_retornar_true(
    usuario_servidor_service_gestao_usuario,
    tipo_unidade_administrativa
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
    with patch(path) as mock_get:
        data = {
            "tipoUnidadeAdm": "1"
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.permite_tipo_unidade_administrativa("120000")

        assert result is True


def test_permite_tipo_unidade_administrativa_encontrado_com_codigo_eol_deve_retornar_true(
    usuario_servidor_service_gestao_usuario,
    tipo_unidade_administrativa_com_codigo_eol
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
    with patch(path) as mock_get:
        data = {
            "tipoUnidadeAdm": "2"
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)
        result = gestao_usuario.permite_tipo_unidade_administrativa("120000")

        assert result is True


def test_permite_tipo_unidade_administrativa_encontrado_com_codigo_eol_deve_retornar_false(
    usuario_servidor_service_gestao_usuario,
    tipo_unidade_administrativa_com_codigo_eol
):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
    with patch(path) as mock_get:
        data = {
            "tipoUnidadeAdm": "2"
        }

        mock_get.return_value = data

        gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)

        # Codigo eol informado diferente do gravado em tipo_unidade_administrativa_com_codigo_eol
        result = gestao_usuario.permite_tipo_unidade_administrativa("130000")

        assert result is False


def test_retorna_unidades_membros_v2_usuario_servidor(
    mandato_factory,
    composicao_factory,
    cargo_composicao_factory,
    ocupante_cargo_factory,
    usuario_servidor_service_gestao_usuario
):

    mandato_2024 = mandato_factory.create(data_inicial=datetime.now(
    ) - timedelta(days=91), data_final=datetime.now() + timedelta(days=365))

    # Composição vigente de uma associacao
    composicao_vigente_1 = composicao_factory.create(
        mandato=mandato_2024, data_inicial=mandato_2024.data_inicial, data_final=mandato_2024.data_final)

    # Composição vigente de outra associacao
    composicao_vigente_2 = composicao_factory.create(
        mandato=mandato_2024, data_inicial=mandato_2024.data_inicial, data_final=mandato_2024.data_final)

    presidente_executiva = ocupante_cargo_factory.create(
        codigo_identificacao=usuario_servidor_service_gestao_usuario.username
    )

    secretario = ocupante_cargo_factory.create(
        codigo_identificacao=usuario_servidor_service_gestao_usuario.username
    )

    cargo_composicao_1 = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_vigente_1.data_inicial,
        data_fim_no_cargo=composicao_vigente_1.data_final,
        composicao=composicao_vigente_1,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )

    cargo_composicao_2 = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_vigente_2.data_inicial,
        data_fim_no_cargo=composicao_vigente_2.data_final,
        composicao=composicao_vigente_2,
        ocupante_do_cargo=secretario,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO
    )

    gestao_usuario = GestaoUsuarioService(usuario=usuario_servidor_service_gestao_usuario)

    unidades = [
        composicao_vigente_1.associacao.unidade.codigo_eol,
        composicao_vigente_2.associacao.unidade.codigo_eol
    ]

    result = gestao_usuario.retorna_unidades_membros_v2(unidades=unidades)

    assert len(result) == 2


def test_retorna_unidades_membros_v2(
    mandato_factory,
    composicao_factory,
    cargo_composicao_factory,
    ocupante_cargo_factory,
    usuario_nao_servidor_service_gestao_usuario
):
    codigo_membro = format_cpf(usuario_nao_servidor_service_gestao_usuario.username)

    mandato_2024 = mandato_factory.create(data_inicial=datetime.now(
    ) - timedelta(days=91), data_final=datetime.now() + timedelta(days=365))

    # Composição vigente de uma associacao
    composicao_vigente_1 = composicao_factory.create(
        mandato=mandato_2024, data_inicial=mandato_2024.data_inicial, data_final=mandato_2024.data_final)

    # Composição vigente de outra associacao
    composicao_vigente_2 = composicao_factory.create(
        mandato=mandato_2024, data_inicial=mandato_2024.data_inicial, data_final=mandato_2024.data_final)

    presidente_executiva = ocupante_cargo_factory.create(
        cpf_responsavel=codigo_membro
    )

    secretario = ocupante_cargo_factory.create(
        cpf_responsavel=codigo_membro
    )

    cargo_composicao_1 = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_vigente_1.data_inicial,
        data_fim_no_cargo=composicao_vigente_1.data_final,
        composicao=composicao_vigente_1,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )

    cargo_composicao_2 = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_vigente_2.data_inicial,
        data_fim_no_cargo=composicao_vigente_2.data_final,
        composicao=composicao_vigente_2,
        ocupante_do_cargo=secretario,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO
    )

    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_service_gestao_usuario)

    unidades = [
        composicao_vigente_1.associacao.unidade.codigo_eol,
        composicao_vigente_2.associacao.unidade.codigo_eol
    ]

    result = gestao_usuario.retorna_unidades_membros_v2(unidades=unidades)

    assert len(result) == 2


def test_retorna_unidades_membros_v2_sem_composicao_vigente(
    mandato_factory,
    composicao_factory,
    cargo_composicao_factory,
    ocupante_cargo_factory,
    usuario_nao_servidor_service_gestao_usuario
):
    codigo_membro = format_cpf(usuario_nao_servidor_service_gestao_usuario.username)

    mandato_2024 = mandato_factory.create(data_inicial=datetime.now(
    ) - timedelta(days=91), data_final=datetime.now() + timedelta(days=365))

    finaliza_apos_30_dias = mandato_2024.data_inicial + timedelta(days=30)

    # Composicao inicial de uma escola (Não é composição vigente)
    composicao_inicial = composicao_factory.create(
        mandato=mandato_2024,
        data_inicial=mandato_2024.data_inicial,
        data_final=finaliza_apos_30_dias
    )

    presidente_executiva = ocupante_cargo_factory.create(
        cpf_responsavel=codigo_membro
    )

    cargo_composicao = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_inicial.data_inicial,
        data_fim_no_cargo=composicao_inicial.data_final,
        composicao=composicao_inicial,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )

    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_service_gestao_usuario)

    unidades = [
        composicao_inicial.associacao.unidade.codigo_eol,
    ]

    result = gestao_usuario.retorna_unidades_membros_v2(unidades=unidades)

    # Este usuario não é membro de nenhuma composição vigente
    assert len(result) == 0


def test_retorna_unidades_membros_v2_com_apenas_uma_composicao_vigente(
    mandato_factory,
    composicao_factory,
    cargo_composicao_factory,
    ocupante_cargo_factory,
    usuario_nao_servidor_service_gestao_usuario
):
    codigo_membro = format_cpf(usuario_nao_servidor_service_gestao_usuario.username)

    mandato_2024 = mandato_factory.create(data_inicial=datetime.now(
    ) - timedelta(days=91), data_final=datetime.now() + timedelta(days=365))

    finaliza_apos_30_dias = mandato_2024.data_inicial + timedelta(days=30)

    # Composicao inicial de uma escola (Não é composição vigente)
    composicao_inicial = composicao_factory.create(
        mandato=mandato_2024,
        data_inicial=mandato_2024.data_inicial,
        data_final=finaliza_apos_30_dias
    )

    # Composicao vigente de outra escola
    composicao_vigente = composicao_factory.create(
        mandato=mandato_2024,
        data_inicial=mandato_2024.data_inicial,
        data_final=mandato_2024.data_final
    )

    presidente_executiva = ocupante_cargo_factory.create(
        cpf_responsavel=codigo_membro
    )

    secretario = ocupante_cargo_factory.create(
        cpf_responsavel=codigo_membro
    )

    cargo_da_composicao_inicial = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_inicial.data_inicial,
        data_fim_no_cargo=composicao_inicial.data_final,
        composicao=composicao_inicial,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )

    cargo_da_composicao_vigente = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_vigente.data_inicial,
        data_fim_no_cargo=composicao_vigente.data_final,
        composicao=composicao_vigente,
        ocupante_do_cargo=secretario,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_SECRETARIO
    )

    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_service_gestao_usuario)

    unidades = [
        composicao_inicial.associacao.unidade.codigo_eol,
        composicao_vigente.associacao.unidade.codigo_eol,
    ]

    result = gestao_usuario.retorna_unidades_membros_v2(unidades=unidades)

    # Este usuario é membro de apenas uma composição vigente
    assert len(result) == 1
    assert result[0]["uuid_unidade"] == f"{composicao_vigente.associacao.unidade.uuid}"


@override_flag('historico-de-membros', active=True)
def test_retorna_unidades_que_eh_membro_associacao_com_flag_ativa(
    mandato_factory,
    composicao_factory,
    cargo_composicao_factory,
    ocupante_cargo_factory,
    usuario_nao_servidor_service_gestao_usuario
):
    codigo_membro = format_cpf(usuario_nao_servidor_service_gestao_usuario.username)

    mandato_2024 = mandato_factory.create(data_inicial=datetime.now(
    ) - timedelta(days=91), data_final=datetime.now() + timedelta(days=365))

    composicao_vigente = composicao_factory.create(
        mandato=mandato_2024,
        data_inicial=mandato_2024.data_inicial,
        data_final=mandato_2024.data_final
    )

    presidente_executiva = ocupante_cargo_factory.create(
        cpf_responsavel=codigo_membro
    )

    cargo_composicao = cargo_composicao_factory.create(
        data_inicio_no_cargo=composicao_vigente.data_inicial,
        data_fim_no_cargo=composicao_vigente.data_final,
        composicao=composicao_vigente,
        ocupante_do_cargo=presidente_executiva,
        cargo_associacao=CargoComposicao.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    )

    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_service_gestao_usuario)

    unidades = [
        composicao_vigente.associacao.unidade.codigo_eol,
    ]

    result = gestao_usuario.retorna_unidades_que_eh_membro_associacao(unidades=unidades)

    assert len(result) == 1


@override_flag('historico-de-membros', active=False)
def test_retorna_unidades_que_eh_membro_associacao_com_flag_nao_ativa(
    usuario_nao_servidor_service_gestao_usuario,
    membro_associacao_nao_servidor_a,
    membro_associacao_nao_servidor_b
):
    gestao_usuario = GestaoUsuarioService(usuario=usuario_nao_servidor_service_gestao_usuario)

    unidades = [
        membro_associacao_nao_servidor_a.associacao.unidade.codigo_eol,
        membro_associacao_nao_servidor_b.associacao.unidade.codigo_eol,
    ]

    result = gestao_usuario.retorna_unidades_que_eh_membro_associacao(unidades=unidades)

    assert len(result) == 2


def test_valida_unidades_do_usuario_deve_remover_unidade_e_retornar_lista_de_removidas(
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
            result = gestao_usuario.valida_unidades_do_usuario()

            assert usuario_servidor_service_gestao_usuario.unidades.count() == 1
            assert visao_sme_gestao_usuario not in usuario_servidor_service_gestao_usuario.visoes.all()

            # Foram removidas uma unidade e a visão SME
            assert len(result) == 2


def test_valida_unidades_do_usuario_nao_deve_remover_unidade_e_deve_retornar_lista_de_unidades_que_seriam_removidas(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a,
    unidade_gestao_usuario_b,
    visao_sme_gestao_usuario,
    parametros_sme_valida_unidades_login_falso
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
            result = gestao_usuario.valida_unidades_do_usuario()

            assert usuario_servidor_service_gestao_usuario.unidades.count() == 2
            assert visao_sme_gestao_usuario in usuario_servidor_service_gestao_usuario.visoes.all()

            # Foram removidas uma unidade e a visão SME
            assert len(result) == 2
