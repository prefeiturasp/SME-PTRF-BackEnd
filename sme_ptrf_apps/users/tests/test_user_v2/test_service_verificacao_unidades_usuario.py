import pytest

from ...services.verificar_unidades_usuarios_service import VerificaUnidadesUsuariosService
from unittest.mock import patch

pytestmark = pytest.mark.django_db


def test_unidade_em_suporte_deve_retornar_verdadeiro(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_b,
    unidade_em_suporte_gestao_usuarios,
):

    em_suporte = VerificaUnidadesUsuariosService().unidade_em_suporte(
        unidade_gestao_usuario_b,
        usuario_servidor_service_gestao_usuario
    )

    assert em_suporte is True


def test_unidade_em_suporte_deve_retornar_falso(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a,
    unidade_em_suporte_gestao_usuarios,
):

    em_suporte = VerificaUnidadesUsuariosService().unidade_em_suporte(
        unidade_gestao_usuario_a,
        usuario_servidor_service_gestao_usuario
    )

    assert em_suporte is False


def test_lista_usuarios(
    usuario_nao_servidor_service_gestao_usuario,
    usuario_servidor_service_gestao_usuario,
):

    lista = VerificaUnidadesUsuariosService().usuarios
    assert len(lista) == 2


def test_valida_unidades_nao_deve_remover_nenhuma_unidade_usuario_nao_servidor(
    usuario_nao_servidor_sem_visao_dre_service_gestao_usuario,
    membro_associacao_nao_servidor_a,
    membro_associacao_nao_servidor_b
):

    assert usuario_nao_servidor_sem_visao_dre_service_gestao_usuario.unidades.count() == 2

    VerificaUnidadesUsuariosService().iniciar_processo()

    assert usuario_nao_servidor_sem_visao_dre_service_gestao_usuario.unidades.count() == 2


def test_valida_unidades_nao_deve_remover_nenhuma_unidade_usuario_servidor(
    usuario_servidor_sem_visao_sme_service_gestao_usuario,
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

        assert usuario_servidor_sem_visao_sme_service_gestao_usuario.unidades.count() == 1

        VerificaUnidadesUsuariosService().iniciar_processo()

        assert usuario_servidor_sem_visao_sme_service_gestao_usuario.unidades.count() == 1


def test_valida_unidades_deve_remover_unidade(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a,
    unidade_gestao_usuario_b
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

        assert usuario_servidor_service_gestao_usuario.unidades.count() == 2

        VerificaUnidadesUsuariosService().iniciar_processo()

        assert usuario_servidor_service_gestao_usuario.unidades.count() == 1


def test_valida_unidades_deve_remover_sme_e_unidade(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a,
    unidade_gestao_usuario_b,
    visao_sme_gestao_usuario
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

        assert usuario_servidor_service_gestao_usuario.unidades.count() == 2
        assert visao_sme_gestao_usuario in usuario_servidor_service_gestao_usuario.visoes.all()

        VerificaUnidadesUsuariosService().iniciar_processo()

        assert usuario_servidor_service_gestao_usuario.unidades.count() == 1
        assert visao_sme_gestao_usuario not in usuario_servidor_service_gestao_usuario.visoes.all()


def test_valida_unidades_nao_deve_remover_unidade_suporte(
    usuario_servidor_service_gestao_usuario,
    unidade_gestao_usuario_a,
    unidade_gestao_usuario_b,
    unidade_em_suporte_gestao_usuarios,
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

        assert usuario_servidor_service_gestao_usuario.unidades.count() == 2
        assert usuario_servidor_service_gestao_usuario.acessos_de_suporte.count() == 1

        VerificaUnidadesUsuariosService().iniciar_processo()

        assert usuario_servidor_service_gestao_usuario.unidades.count() == 2
        assert usuario_servidor_service_gestao_usuario.acessos_de_suporte.count() == 1

