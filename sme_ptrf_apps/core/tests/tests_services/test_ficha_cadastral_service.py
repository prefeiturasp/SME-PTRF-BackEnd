from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

from sme_ptrf_apps.core.services import ficha_cadastral_service as servico
from sme_ptrf_apps.mandatos.models import CargoComposicaoVacancia, ComposicaoVacancia


DADOS_PRESIDENTE = {
    "nome": "VITOR YOSHI YASHINAGA",
    "cargo_educacao": "DIRETOR DE ESCOLA",
    "telefone": "(11)99550-9090",
    "email": "victoryoshinaga@gmail.com",
    "endereco": "RUA BARRA DE GUABIRABA, 97 - Apto 11",
    "complemento": "Apto 11",
    "bairro": "ITAQUERA",
    "cep": "08210-010",
    "municipio": "SAO PAULO",
    "uf": "SP",
}


def test_anonimiza_telefone_mantendo_ddd_e_as_extremidades_do_numero():
    assert servico.anonimizar_telefone("(11)99550-9090") == "(11)99XXX-XX90"
    assert servico.anonimizar_telefone("(11) 99550-9090") == "(11) 99XXX-XX90"
    assert servico.anonimizar_telefone("(11)3333-4444") == "(11)33XX-XX44"
    assert servico.anonimizar_telefone("") == ""
    assert servico.anonimizar_telefone(None) == ""


def test_anonimiza_endereco_complemento_bairro_cep_e_municipio_e_preserva_uf():
    endereco = DADOS_PRESIDENTE["endereco"]
    anonimizado = servico.anonimizar_dados_presidente(DADOS_PRESIDENTE)

    assert anonimizado["nome"] == "VITOR YOSHI YASHINAGA"
    assert anonimizado["cargo_educacao"] == "DIRETOR DE ESCOLA"
    assert anonimizado["telefone"] == "(11)99XXX-XX90"
    assert anonimizado["email"] == "vi" + ("X" * 21) + "om"
    assert anonimizado["endereco"] == "RU" + ("X" * (len(endereco) - 4)) + "11"
    assert anonimizado["complemento"] == "ApXXX11"
    assert anonimizado["bairro"] == "IXXXXXXA"
    assert anonimizado["cep"] == "082XX-XXX"
    assert anonimizado["municipio"] == "SAXXXXXLO"
    assert anonimizado["uf"] == "SP"


def test_email_sme_permanece_visivel_na_ficha():
    dados = {
        **DADOS_PRESIDENTE,
        "email": "anderson.mendes@sme.prefeitura.sp.gov.br",
    }

    anonimizado = servico.anonimizar_dados_presidente(dados)

    assert anonimizado["email"] == "anderson.mendes@sme.prefeitura.sp.gov.br"


def test_campos_vazios_permanecem_vazios():
    anonimizado = servico.anonimizar_dados_presidente({
        "nome": "",
        "cargo_educacao": None,
        "telefone": "",
        "email": "",
        "endereco": "",
        "complemento": "",
        "bairro": "",
        "cep": "",
        "municipio": "",
        "uf": "",
    })

    assert anonimizado["telefone"] == ""
    assert anonimizado["email"] == ""
    assert anonimizado["endereco"] == ""
    assert anonimizado["bairro"] == ""
    assert anonimizado["cep"] == ""
    assert anonimizado["uf"] == ""


def test_sem_flags_usa_presidente_da_lista_de_membros_atual():
    associacao = MagicMock()
    associacao.presidente_associacao = {
        "nome": "Presidente da lista",
        "cargo_educacao": "Diretor",
        "telefone": "(11)98888-7777",
        "email": "presidente@email.com",
        "endereco": "Rua Atual",
        "bairro": "Centro",
        "cep": "01001000",
    }
    request = MagicMock()

    with patch.object(servico, "flag_is_active", return_value=False):
        dados = servico.dados_presidente_para_ficha(associacao, request)

    assert dados["nome"] == "Presidente da lista"
    assert dados["telefone"] == "(11)98888-7777"
    assert dados["uf"] == ""
    associacao.dados_presidente_composicao_vigente_vacancia.assert_not_called()
    associacao.dados_presidente_composicao_vigente.assert_not_called()


def test_flag_v2_tem_prioridade_sobre_historico_v1():
    associacao = MagicMock()
    associacao.dados_presidente_composicao_vigente_vacancia.return_value = {"nome": "Atual v2"}
    request = MagicMock()

    def flag_is_active(_request, nome):
        return nome in {"historico-de-membros-v2", "historico-de-membros"}

    with patch.object(servico, "flag_is_active", side_effect=flag_is_active):
        dados = servico.dados_presidente_para_ficha(associacao, request)

    assert dados == {"nome": "Atual v2"}
    associacao.dados_presidente_composicao_vigente.assert_not_called()


def test_usuario_com_permissao_recebe_dados_completos():
    associacao = MagicMock()
    associacao.dados_presidente_composicao_vigente_vacancia.return_value = dict(DADOS_PRESIDENTE)
    request = MagicMock()

    def flag_v2(_request, nome):
        return nome == "historico-de-membros-v2"

    with patch.object(servico, "flag_is_active", side_effect=flag_v2), \
            patch.object(servico.PermissaoCRUD, "has_perm", return_value=True) as has_perm:
        dados = servico.dados_presidente_ficha_para_usuario(associacao, request)

    has_perm.assert_called_once_with(servico.PERMISSAO_FICHA_CADASTRAL_SEM_ANONIMIZACAO, request.user)
    assert dados["telefone"] == "(11)99550-9090"
    assert dados["email"] == "victoryoshinaga@gmail.com"
    assert dados["cep"] == "08210-010"


def test_usuario_sem_permissao_recebe_dados_anonimizados():
    associacao = MagicMock()
    associacao.dados_presidente_composicao_vigente_vacancia.return_value = dict(DADOS_PRESIDENTE)
    request = MagicMock()

    def flag_v2(_request, nome):
        return nome == "historico-de-membros-v2"

    with patch.object(servico, "flag_is_active", side_effect=flag_v2), \
            patch.object(servico.PermissaoCRUD, "has_perm", return_value=False):
        dados = servico.dados_presidente_ficha_para_usuario(associacao, request)

    assert dados["nome"] == "VITOR YOSHI YASHINAGA"
    assert dados["telefone"] == "(11)99XXX-XX90"
    assert dados["bairro"] == "IXXXXXXA"
    assert dados["cep"] == "082XX-XXX"
    assert dados["uf"] == "SP"


@pytest.mark.django_db
@freeze_time("2026-10-07")
def test_ficha_v2_usa_presidente_da_composicao_atual_do_mandato_vigente(
    associacao_factory, mandato_factory, ocupante_cargo_factory
):
    associacao = associacao_factory.create()
    mandato = mandato_factory.create(
        data_inicial=date(2026, 1, 1),
        data_final=date(2026, 12, 31),
    )
    composicao = ComposicaoVacancia.objects.create(associacao=associacao, mandato=mandato)
    presidente_anterior = ocupante_cargo_factory.create(nome="Presidente Anterior")
    presidente_atual = ocupante_cargo_factory.create(
        nome="Vitor Yoshi Yashinaga",
        cargo_educacao="DIRETOR DE ESCOLA",
        telefone="(11)99550-9090",
        email="victoryoshinaga@gmail.com",
        endereco="RUA BARRA DE GUABIRABA, 97 - Apto 11",
        bairro="ITAQUERA",
        cep="08210-010",
    )
    CargoComposicaoVacancia.objects.create(
        composicao=composicao,
        ocupante_do_cargo=presidente_anterior,
        cargo_associacao="PRESIDENTE_DIRETORIA_EXECUTIVA",
        data_inicio_no_cargo=date(2026, 1, 1),
        data_fim_no_cargo=date(2026, 6, 30),
    )
    CargoComposicaoVacancia.objects.create(
        composicao=composicao,
        ocupante_do_cargo=presidente_atual,
        cargo_associacao="PRESIDENTE_DIRETORIA_EXECUTIVA",
        data_inicio_no_cargo=date(2026, 7, 1),
        data_fim_no_cargo=date(2026, 12, 31),
    )

    dados = associacao.dados_presidente_composicao_vigente_vacancia()

    assert dados["nome"] == "Vitor Yoshi Yashinaga"
    assert dados["cargo_educacao"] == "DIRETOR DE ESCOLA"
    assert dados["telefone"] == "(11)99550-9090"
    assert dados["email"] == "victoryoshinaga@gmail.com"
    assert dados["bairro"] == "ITAQUERA"
    assert dados["cep"] == "08210-010"
