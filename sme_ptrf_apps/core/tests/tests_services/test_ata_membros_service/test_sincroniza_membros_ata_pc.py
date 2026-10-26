from datetime import date

import pytest
from model_bakery import baker
from waffle import get_waffle_flag_model

from sme_ptrf_apps.core.models import Ata, Participante
from sme_ptrf_apps.core.services.ata_membros_service import ServicoAtualizacaoMembrosAtas
from sme_ptrf_apps.mandatos.choices import CargoComposicaoVacanciaChoices as Cargos


pytestmark = pytest.mark.django_db

INICIO = date(2026, 1, 1)
FIM = date(2028, 12, 31)
PRESIDENTE = Cargos.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
SECRETARIO = Cargos.CARGO_ASSOCIACAO_SECRETARIO
CONSELHEIRO = Cargos.CARGO_ASSOCIACAO_CONSELHEIRO_1

"""Testes da sincronização de membros do histórico v2 com as atas de PC."""

@pytest.fixture
def contexto_atas(associacao, periodo_factory):
    periodo = periodo_factory.create()
    mandato = baker.make(
        "mandatos.Mandato",
        referencia_mandato="2026 a 2028",
        data_inicial=INICIO,
        data_final=FIM,
    )
    composicao = baker.make(
        "mandatos.ComposicaoVacancia",
        associacao=associacao,
        mandato=mandato,
    )
    return {
        "associacao": associacao,
        "periodo": periodo,
        "composicao": composicao,
    }


@pytest.fixture
def historico_v2_ativo():
    get_waffle_flag_model().objects.update_or_create(
        name="historico-de-membros-v2",
        defaults={"everyone": True},
    )


def definir_flag(nome, ativa):
    get_waffle_flag_model().objects.update_or_create(
        name=nome,
        defaults={"everyone": ativa},
    )


def criar_ata(contexto, data_reuniao, **campos):
    return baker.make(
        Ata,
        associacao=campos.pop("associacao", contexto["associacao"]),
        periodo=contexto["periodo"],
        data_reuniao=data_reuniao,
        status_geracao_pdf=campos.pop("status_geracao_pdf", Ata.STATUS_NAO_GERADO),
        tipo_ata=campos.pop("tipo_ata", Ata.ATA_APRESENTACAO),
        **campos,
    )


def criar_registro(
    contexto,
    nome="Maria",
    identificacao="1234567",
    cargo=PRESIDENTE,
    data_inicio=INICIO,
    data_fim=FIM,
):
    ocupante = None
    if nome is not None:
        ocupante = baker.make(
            "mandatos.OcupanteCargo",
            nome=nome,
            codigo_identificacao=identificacao,
        )

    return baker.make(
        "mandatos.CargoComposicaoVacancia",
        composicao=contexto["composicao"],
        cargo_associacao=cargo,
        ocupante_do_cargo=ocupante,
        data_inicio_no_cargo=data_inicio,
        data_fim_no_cargo=data_fim,
    )


def criar_participante(ata, nome="João", identificacao="000", cargo=PRESIDENTE, **campos):
    return baker.make(
        Participante,
        ata=ata,
        cargo=Cargos(cargo).label,
        membro=campos.pop("membro", True),
        nome=nome,
        identificacao=identificacao,
        **campos,
    )


def sincronizar(contexto, cargo=PRESIDENTE, inicio=INICIO, fim=FIM):
    ServicoAtualizacaoMembrosAtas.atualizar_atas_por_periodo(
        composicao_vacancia=contexto["composicao"],
        cargo_associacao=cargo,
        data_inicio=inicio,
        data_fim=fim,
    )


def test_nao_sincroniza_quando_flag_historico_v2_desativada(contexto_atas):
    definir_flag("historico-de-membros-v2", False)
    definir_flag("historico-de-membros", True)
    criar_registro(contexto_atas, nome="Maria")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    participante = criar_participante(ata, nome="João")

    sincronizar(contexto_atas)

    participante.refresh_from_db()
    assert participante.nome == "João"
    assert Participante.objects.filter(ata=ata, membro=True).count() == 1


def test_nao_sincroniza_quando_intervalo_e_invalido(contexto_atas, historico_v2_ativo):
    criar_registro(contexto_atas)
    ata = criar_ata(contexto_atas, date(2026, 3, 10))

    sincronizar(contexto_atas, inicio=date(2026, 4, 1), fim=date(2026, 3, 1))

    assert not Participante.objects.filter(ata=ata).exists()


@pytest.mark.parametrize("tipo_ata", [Ata.ATA_APRESENTACAO, Ata.ATA_RETIFICACAO])
def test_cria_participante_nas_atas_de_apresentacao_e_retificacao(
    contexto_atas, historico_v2_ativo, tipo_ata,
):
    criar_registro(contexto_atas, nome="Maria", identificacao="7654321")
    ata = criar_ata(contexto_atas, date(2026, 5, 10), tipo_ata=tipo_ata)

    sincronizar(contexto_atas)

    participante = Participante.objects.get(ata=ata, membro=True)
    assert participante.nome == "Maria"
    assert participante.identificacao == "7654321"
    assert participante.cargo == Cargos(PRESIDENTE).label
    assert participante.conselho_fiscal is False


def test_respeita_a_timeline_de_ocupacao_e_vacancia(contexto_atas, historico_v2_ativo):
    criar_registro(contexto_atas, nome="Maria", data_fim=date(2026, 3, 10))
    criar_registro(
        contexto_atas,
        nome=None,
        data_inicio=date(2026, 3, 11),
        data_fim=date(2026, 3, 15),
    )
    criar_registro(contexto_atas, nome="João", data_inicio=date(2026, 3, 16))
    ata_maria = criar_ata(contexto_atas, date(2026, 3, 10))
    ata_vacancia = criar_ata(contexto_atas, date(2026, 3, 11))
    ata_joao = criar_ata(contexto_atas, date(2026, 3, 16))
    participante_antigo = criar_participante(ata_vacancia, nome="Maria")

    sincronizar(contexto_atas)

    assert Participante.objects.get(ata=ata_maria, membro=True).nome == "Maria"
    assert not Participante.objects.filter(pk=participante_antigo.pk).exists()
    assert not Participante.objects.filter(ata=ata_vacancia, membro=True).exists()
    assert Participante.objects.get(ata=ata_joao, membro=True).nome == "João"


def test_remove_membro_quando_nao_existe_registro_na_data(contexto_atas, historico_v2_ativo):
    criar_registro(contexto_atas, nome="Maria", data_inicio=date(2026, 4, 1))
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    participante = criar_participante(ata, nome="João")

    sincronizar(contexto_atas)

    assert not Participante.objects.filter(pk=participante.pk).exists()


def test_sincroniza_apenas_atas_elegiveis(
    contexto_atas, historico_v2_ativo, associacao_factory,
):
    criar_registro(contexto_atas, nome="Maria")
    ata_valida = criar_ata(contexto_atas, date(2026, 3, 10))
    ata_sem_data = criar_ata(contexto_atas, None)
    ata_pdf_concluido = criar_ata(
        contexto_atas, date(2026, 3, 10), status_geracao_pdf=Ata.STATUS_CONCLUIDO,
    )
    ata_em_processamento = criar_ata(
        contexto_atas, date(2026, 3, 10), status_geracao_pdf=Ata.STATUS_EM_PROCESSAMENTO,
    )
    outra_associacao = associacao_factory.create()
    ata_outra_associacao = criar_ata(
        contexto_atas, date(2026, 3, 10), associacao=outra_associacao,
    )
    ata_fora_intervalo = criar_ata(contexto_atas, date(2026, 6, 1))

    sincronizar(contexto_atas, inicio=date(2026, 3, 1), fim=date(2026, 3, 31))

    assert Participante.objects.filter(ata=ata_valida, nome="Maria", membro=True).exists()
    for ata in (
        ata_sem_data, ata_pdf_concluido, ata_em_processamento,
        ata_outra_associacao, ata_fora_intervalo,
    ):
        assert not Participante.objects.filter(ata=ata, membro=True).exists()


def test_atualiza_participante_sem_duplicar_e_preserva_presenca(
    contexto_atas, historico_v2_ativo,
):
    criar_registro(contexto_atas, nome="Maria", identificacao="7654321")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    antigo = criar_participante(
        ata, nome="João", identificacao="1234567", presente=False,
    )

    sincronizar(contexto_atas)

    antigo.refresh_from_db()
    assert antigo.nome == "Maria"
    assert antigo.identificacao == "7654321"
    assert antigo.presente is False
    assert Participante.objects.filter(ata=ata, membro=True).count() == 1


@pytest.mark.parametrize("v1_ativa", [True, False])
def test_substituicao_limpa_fk_presidente_sem_alterar_secretario(
    contexto_atas, historico_v2_ativo, v1_ativa,
):
    definir_flag("historico-de-membros", v1_ativa)
    criar_registro(contexto_atas, nome="Maria")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    antigo = criar_participante(ata, nome="João")
    secretario = criar_participante(ata, nome="Carlos", cargo=SECRETARIO)
    ata.presidente_da_reuniao = antigo
    ata.secretario_da_reuniao = secretario
    ata.save(update_fields=["presidente_da_reuniao", "secretario_da_reuniao"])

    sincronizar(contexto_atas)

    ata.refresh_from_db()
    antigo.refresh_from_db()
    assert ata.presidente_da_reuniao is None
    assert ata.secretario_da_reuniao_id == secretario.pk
    assert antigo.nome == "Maria"
    assert Participante.objects.filter(ata=ata, membro=True).count() == 2


def test_vacancia_limpa_fk_secretario_e_exclui_apenas_membro_do_cargo(
    contexto_atas, historico_v2_ativo,
):
    criar_registro(contexto_atas, nome=None, cargo=SECRETARIO)
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    presidente = criar_participante(ata, nome="Maria", cargo=PRESIDENTE)
    antigo_secretario = criar_participante(ata, nome="João", cargo=SECRETARIO)
    ata.presidente_da_reuniao = presidente
    ata.secretario_da_reuniao = antigo_secretario
    ata.save(update_fields=["presidente_da_reuniao", "secretario_da_reuniao"])

    sincronizar(contexto_atas, cargo=SECRETARIO)

    ata.refresh_from_db()
    assert ata.secretario_da_reuniao is None
    assert ata.presidente_da_reuniao_id == presidente.pk
    assert not Participante.objects.filter(pk=antigo_secretario.pk).exists()
    assert Participante.objects.filter(pk=presidente.pk).exists()


def test_substituicao_limpa_campos_legados_de_presidente_com_cargo_maiusculo(
    contexto_atas, historico_v2_ativo,
):
    definir_flag("historico-de-membros", True)
    criar_registro(contexto_atas, nome="Maria")
    ata = criar_ata(
        contexto_atas,
        date(2026, 3, 10),
        presidente_reuniao="João",
        cargo_presidente_reuniao=Cargos(PRESIDENTE).label.upper(),
        secretario_reuniao="Carlos",
        cargo_secretaria_reuniao="Secretário",
    )
    criar_participante(ata, nome="João")

    sincronizar(contexto_atas)

    ata.refresh_from_db()
    assert ata.presidente_reuniao == ""
    assert ata.cargo_presidente_reuniao == ""
    assert ata.secretario_reuniao == "Carlos"
    assert ata.cargo_secretaria_reuniao == "Secretário"


def test_vacancia_limpa_campos_legados_de_secretario_mesmo_com_v1_desativada(
    contexto_atas, historico_v2_ativo,
):
    definir_flag("historico-de-membros", False)
    criar_registro(contexto_atas, nome=None, cargo=SECRETARIO)
    ata = criar_ata(
        contexto_atas,
        date(2026, 3, 10),
        secretario_reuniao="João",
        cargo_secretaria_reuniao=Cargos(SECRETARIO).label.upper(),
    )
    criar_participante(ata, nome="João", cargo=SECRETARIO)

    sincronizar(contexto_atas, cargo=SECRETARIO)

    ata.refresh_from_db()
    assert ata.secretario_reuniao == ""
    assert ata.cargo_secretaria_reuniao == ""
    assert not Participante.objects.filter(ata=ata, cargo=Cargos(SECRETARIO).label, membro=True).exists()


def test_substituicao_limpa_fk_e_campos_legados_quando_ambos_estao_preenchidos(
    contexto_atas, historico_v2_ativo,
):
    criar_registro(contexto_atas, nome="Maria")
    ata = criar_ata(
        contexto_atas,
        date(2026, 3, 10),
        presidente_reuniao="João",
        cargo_presidente_reuniao=Cargos(PRESIDENTE).label,
    )
    antigo = criar_participante(ata, nome="João")
    ata.presidente_da_reuniao = antigo
    ata.save(update_fields=["presidente_da_reuniao"])

    sincronizar(contexto_atas)

    ata.refresh_from_db()
    assert ata.presidente_da_reuniao is None
    assert ata.presidente_reuniao == ""
    assert ata.cargo_presidente_reuniao == ""


def test_nao_limpa_presidencia_quando_nome_e_identificacao_nao_mudam(
    contexto_atas, historico_v2_ativo,
):
    criar_registro(
        contexto_atas, nome="Maria", identificacao="1234567", cargo=CONSELHEIRO,
    )
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    participante = criar_participante(
        ata, nome="Maria", identificacao="1234567", cargo=CONSELHEIRO,
        conselho_fiscal=False,
    )
    ata.presidente_da_reuniao = participante
    ata.save(update_fields=["presidente_da_reuniao"])

    sincronizar(contexto_atas, cargo=CONSELHEIRO)

    ata.refresh_from_db()
    participante.refresh_from_db()
    assert participante.conselho_fiscal is True
    assert ata.presidente_da_reuniao_id == participante.pk


def test_alteracao_apenas_da_identificacao_limpa_referencia_do_secretario(
    contexto_atas, historico_v2_ativo,
):
    criar_registro(contexto_atas, nome="João", identificacao="222", cargo=SECRETARIO)
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    participante = criar_participante(
        ata, nome="João", identificacao="111", cargo=SECRETARIO,
    )
    ata.secretario_da_reuniao = participante
    ata.save(update_fields=["secretario_da_reuniao"])

    sincronizar(contexto_atas, cargo=SECRETARIO)

    ata.refresh_from_db()
    participante.refresh_from_db()
    assert participante.nome == "João"
    assert participante.identificacao == "222"
    assert ata.secretario_da_reuniao is None


def test_nao_limpa_campos_legados_de_outro_participante(
    contexto_atas, historico_v2_ativo,
):
    criar_registro(contexto_atas, nome=None)
    ata = criar_ata(
        contexto_atas,
        date(2026, 3, 10),
        presidente_reuniao="Carlos",
        cargo_presidente_reuniao=Cargos(PRESIDENTE).label,
    )
    antigo = criar_participante(ata, nome="João")

    sincronizar(contexto_atas)

    ata.refresh_from_db()
    assert not Participante.objects.filter(pk=antigo.pk).exists()
    assert ata.presidente_reuniao == "Carlos"
    assert ata.cargo_presidente_reuniao == Cargos(PRESIDENTE).label


def test_vacancia_nao_exclui_participante_que_nao_e_membro(
    contexto_atas, historico_v2_ativo,
):
    criar_registro(contexto_atas, nome=None)
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    membro = criar_participante(ata, nome="João")
    convidado = criar_participante(ata, nome="Convidado", membro=False)

    sincronizar(contexto_atas)

    assert not Participante.objects.filter(pk=membro.pk).exists()
    assert Participante.objects.filter(pk=convidado.pk, membro=False).exists()


def test_sincronizacao_repetida_nao_duplica_participantes(
    contexto_atas, historico_v2_ativo,
):
    criar_registro(contexto_atas, nome="Maria")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))

    sincronizar(contexto_atas)
    primeiro_id = Participante.objects.get(ata=ata, membro=True).pk
    sincronizar(contexto_atas)

    assert Participante.objects.filter(ata=ata, membro=True).count() == 1
    assert Participante.objects.get(ata=ata, membro=True).pk == primeiro_id


def test_sincronizacao_de_um_cargo_nao_altera_participante_de_outro_cargo(
    contexto_atas, historico_v2_ativo,
):
    criar_registro(contexto_atas, nome="Maria", cargo=PRESIDENTE)
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    secretario = criar_participante(
        ata, nome="Carlos", identificacao="888", cargo=SECRETARIO,
    )

    sincronizar(contexto_atas, cargo=PRESIDENTE)

    secretario.refresh_from_db()
    assert secretario.nome == "Carlos"
    assert secretario.identificacao == "888"
    assert Participante.objects.get(
        ata=ata, cargo=Cargos(PRESIDENTE).label, membro=True,
    ).nome == "Maria"


def test_remove_nao_membro_com_mesma_identificacao_ao_sincronizar(
    contexto_atas, historico_v2_ativo,
):
    identificacao = "1234567"

    criar_registro(
        contexto_atas,
        nome="Maria",
        identificacao=identificacao,
    )
    ata = criar_ata(contexto_atas, date(2026, 3, 10))

    nao_membro = criar_participante(
        ata,
        nome="Maria",
        identificacao=identificacao,
        membro=False,
    )
    outro_nao_membro = criar_participante(
        ata,
        nome="Convidado",
        identificacao="9999999",
        membro=False,
    )

    sincronizar(contexto_atas)

    assert not Participante.objects.filter(pk=nao_membro.pk).exists()
    assert Participante.objects.filter(pk=outro_nao_membro.pk).exists()

    participante = Participante.objects.get(
        ata=ata,
        membro=True,
        identificacao=identificacao,
    )
    assert participante.nome == "Maria"
