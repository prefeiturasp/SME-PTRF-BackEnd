from ...services.get_usuarios_servidores_por_visao import get_usuarios_servidores_por_visao
import pytest

pytestmark = pytest.mark.django_db


def test_get_usuarios_servidores_por_visao_nao_deve_retornar_nada_nao_eh_servidor(
    usuario__nao_eh_servidor_para_teste_teste_get_usuarios_servidores_por_visao,
    visao_ue_teste_get_usuarios_servidores_por_visao
):
    usuarios = get_usuarios_servidores_por_visao(visao_ue_teste_get_usuarios_servidores_por_visao)

    resultado_esperado = []

    assert usuarios == resultado_esperado


def test_get_usuarios_servidores_por_visao_nao_deve_retornar_nada_nao_tem_visao_sme(
    usuario__eh_servidor_para_teste_teste_get_usuarios_servidores_por_visao,
    visao_sme_teste_get_usuarios_servidores_por_visao
):
    usuarios = get_usuarios_servidores_por_visao(visao_sme_teste_get_usuarios_servidores_por_visao)

    resultado_esperado = []

    assert usuarios == resultado_esperado


def test_get_usuarios_servidores_por_visao(
    usuario__eh_servidor_para_teste_teste_get_usuarios_servidores_por_visao,
    visao_ue_teste_get_usuarios_servidores_por_visao
):
    usuarios = get_usuarios_servidores_por_visao(visao_ue_teste_get_usuarios_servidores_por_visao)

    resultado_esperado = [
        {
            "usuario": "7210418 - Usuario Servidor com Visao UE",
            "username": "7210418",
            "nome": "Usuario Servidor com Visao UE",
        }
    ]

    assert usuarios == resultado_esperado
