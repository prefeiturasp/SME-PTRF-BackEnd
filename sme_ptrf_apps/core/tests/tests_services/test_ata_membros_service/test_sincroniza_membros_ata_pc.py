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

# Testes da sincronização de membros do histórico v2 com as atas de PC.


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


# Nome específico evita conflito com helpers antigos chamados criar_registro.
def criar_registro_cargo_ata(
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
    criar_registro_cargo_ata(contexto_atas, nome="Maria")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    participante = criar_participante(ata, nome="João")

    sincronizar(contexto_atas)
    participante.refresh_from_db()

    assert participante.nome == "João"
    assert Participante.objects.filter(ata=ata, membro=True).count() == 1


def test_nao_sincroniza_quando_intervalo_e_invalido(contexto_atas, historico_v2_ativo):
    criar_registro_cargo_ata(contexto_atas)
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    participante = criar_participante(ata, nome="João")

    sincronizar(contexto_atas, inicio=date(2026, 4, 1), fim=date(2026, 3, 1))

    participante.refresh_from_db()
    assert participante.nome == "João"
    assert Participante.objects.filter(ata=ata, membro=True).count() == 1


@pytest.mark.parametrize("tipo_ata", [Ata.ATA_APRESENTACAO, Ata.ATA_RETIFICACAO])
def test_cria_participante_nas_atas_de_apresentacao_e_retificacao(
    contexto_atas, historico_v2_ativo, tipo_ata,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria", identificacao="7654321")
    ata = criar_ata(contexto_atas, date(2026, 5, 10), tipo_ata=tipo_ata)
    # Uma ata sem nenhum membro é ignorada. Outro cargo já a torna elegível.
    secretario = criar_participante(ata, nome="Carlos", cargo=SECRETARIO)

    sincronizar(contexto_atas)
    participante = Participante.objects.get(
        ata=ata, membro=True, cargo=Cargos(PRESIDENTE).label,
    )

    assert participante.nome == "Maria"
    assert participante.identificacao == "7654321"
    assert participante.conselho_fiscal is False
    assert participante.presente is True
    assert participante.vago is False
    assert Participante.objects.filter(ata=ata, membro=True).count() == 2
    assert Participante.objects.filter(pk=secretario.pk).exists()


def test_respeita_a_timeline_de_ocupacao_e_vacancia(contexto_atas, historico_v2_ativo):
    criar_registro_cargo_ata(contexto_atas, nome="Maria", data_fim=date(2026, 3, 10))
    criar_registro_cargo_ata(
        contexto_atas,
        nome=None,
        data_inicio=date(2026, 3, 11),
        data_fim=date(2026, 3, 15),
    )
    criar_registro_cargo_ata(contexto_atas, nome="João", data_inicio=date(2026, 3, 16))
    ata_maria = criar_ata(contexto_atas, date(2026, 3, 10))
    ata_vacancia = criar_ata(contexto_atas, date(2026, 3, 11))
    ata_joao = criar_ata(contexto_atas, date(2026, 3, 16))
    criar_participante(ata_maria, nome="Carlos", cargo=SECRETARIO)
    criar_participante(ata_joao, nome="Carlos", cargo=SECRETARIO)
    participante_antigo = criar_participante(ata_vacancia, nome="Maria")

    sincronizar(contexto_atas)
    maria = Participante.objects.get(ata=ata_maria, cargo=Cargos(PRESIDENTE).label)
    joao = Participante.objects.get(ata=ata_joao, cargo=Cargos(PRESIDENTE).label)
    participante_antigo.refresh_from_db()

    assert maria.nome == "Maria"
    assert maria.presente is True
    assert joao.nome == "João"
    assert joao.presente is True
    # A vacância atualiza o registro existente, sem excluí-lo.
    assert participante_antigo.nome == ""
    assert participante_antigo.identificacao == ""
    assert participante_antigo.vago is True
    assert participante_antigo.presente is False
    assert participante_antigo.membro is True
    assert participante_antigo.data_inicio_no_cargo == date(2026, 3, 11)


def test_mantem_membro_quando_nao_existe_registro_na_data(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria", data_inicio=date(2026, 4, 1))
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    participante = criar_participante(ata, nome="João", identificacao="111")

    sincronizar(contexto_atas)
    participante.refresh_from_db()

    assert participante.nome == "João"
    assert participante.identificacao == "111"
    assert Participante.objects.filter(ata=ata, membro=True).count() == 1


def test_sincroniza_apenas_atas_elegiveis(
    contexto_atas, historico_v2_ativo, associacao_factory,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria")
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
    atas_nao_elegiveis = (
        ata_sem_data,
        ata_pdf_concluido,
        ata_em_processamento,
        ata_outra_associacao,
        ata_fora_intervalo,
    )
    for ata in (ata_valida, *atas_nao_elegiveis):
        criar_participante(ata, nome="João", identificacao="111")

    sincronizar(contexto_atas, inicio=date(2026, 3, 1), fim=date(2026, 3, 31))

    assert Participante.objects.get(ata=ata_valida, membro=True).nome == "Maria"
    for ata in atas_nao_elegiveis:
        participantes = Participante.objects.filter(ata=ata, membro=True)

        assert participantes.count() == 1
        assert participantes.get().nome == "João"


def test_atualiza_participante_sem_duplicar_e_marca_presente_ao_substituir(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria", identificacao="7654321")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    antigo = criar_participante(
        ata, nome="João", identificacao="1234567", presente=False, vago=False,
    )

    sincronizar(contexto_atas)
    antigo.refresh_from_db()

    assert antigo.nome == "Maria"
    assert antigo.identificacao == "7654321"
    assert antigo.presente is True
    assert antigo.vago is False
    assert Participante.objects.filter(ata=ata, membro=True).count() == 1


@pytest.mark.parametrize("v1_ativa", [True, False])
def test_substituicao_limpa_fk_presidente_sem_alterar_secretario(
    contexto_atas, historico_v2_ativo, v1_ativa,
):
    definir_flag("historico-de-membros", v1_ativa)
    criar_registro_cargo_ata(contexto_atas, nome="Maria")
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


def test_vacancia_limpa_fk_secretario_e_mantem_membro_vago(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome=None, cargo=SECRETARIO)
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    presidente = criar_participante(ata, nome="Maria", cargo=PRESIDENTE)
    antigo_secretario = criar_participante(ata, nome="João", cargo=SECRETARIO)
    ata.presidente_da_reuniao = presidente
    ata.secretario_da_reuniao = antigo_secretario
    ata.save(update_fields=["presidente_da_reuniao", "secretario_da_reuniao"])

    sincronizar(contexto_atas, cargo=SECRETARIO)
    ata.refresh_from_db()
    antigo_secretario.refresh_from_db()

    assert ata.secretario_da_reuniao is None
    assert ata.presidente_da_reuniao_id == presidente.pk
    assert antigo_secretario.vago is True
    assert antigo_secretario.presente is False
    assert antigo_secretario.nome == ""
    assert antigo_secretario.identificacao == ""
    assert antigo_secretario.membro is True
    assert Participante.objects.filter(pk=presidente.pk).exists()


def test_substituicao_limpa_campos_legados_de_presidente_com_cargo_maiusculo(
    contexto_atas, historico_v2_ativo,
):
    definir_flag("historico-de-membros", True)
    criar_registro_cargo_ata(contexto_atas, nome="Maria")
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
    criar_registro_cargo_ata(contexto_atas, nome=None, cargo=SECRETARIO)
    ata = criar_ata(
        contexto_atas,
        date(2026, 3, 10),
        secretario_reuniao="João",
        cargo_secretaria_reuniao=Cargos(SECRETARIO).label.upper(),
    )
    antigo = criar_participante(ata, nome="João", cargo=SECRETARIO)

    sincronizar(contexto_atas, cargo=SECRETARIO)
    ata.refresh_from_db()
    antigo.refresh_from_db()

    assert ata.secretario_reuniao == ""
    assert ata.cargo_secretaria_reuniao == ""
    assert antigo.vago is True
    assert antigo.presente is False
    assert antigo.membro is True


def test_substituicao_limpa_fk_e_campos_legados_quando_ambos_estao_preenchidos(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria")
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
    criar_registro_cargo_ata(
        contexto_atas, nome="Maria", identificacao="1234567", cargo=CONSELHEIRO,
    )
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    participante = criar_participante(
        ata,
        nome="Maria",
        identificacao="1234567",
        cargo=CONSELHEIRO,
        conselho_fiscal=True,
        presente=False,
        vago=False,
    )
    ata.presidente_da_reuniao = participante
    ata.save(update_fields=["presidente_da_reuniao"])

    sincronizar(contexto_atas, cargo=CONSELHEIRO)
    ata.refresh_from_db()
    participante.refresh_from_db()

    assert participante.conselho_fiscal is True
    # Com a mesma pessoa, o serviço mantém a presença anterior.

    assert participante.presente is False
    assert ata.presidente_da_reuniao_id == participante.pk
    assert participante.data_inicio_no_cargo == INICIO


def test_alteracao_apenas_da_identificacao_limpa_referencia_do_secretario(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome="João", identificacao="222", cargo=SECRETARIO)
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
    criar_registro_cargo_ata(contexto_atas, nome=None)
    ata = criar_ata(
        contexto_atas,
        date(2026, 3, 10),
        presidente_reuniao="Carlos",
        cargo_presidente_reuniao=Cargos(PRESIDENTE).label,
    )
    antigo = criar_participante(ata, nome="João")

    sincronizar(contexto_atas)
    ata.refresh_from_db()
    antigo.refresh_from_db()

    assert antigo.vago is True
    assert antigo.nome == ""
    assert ata.presidente_reuniao == "Carlos"
    assert ata.cargo_presidente_reuniao == Cargos(PRESIDENTE).label


def test_vacancia_nao_exclui_participante_que_nao_e_membro(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome=None)
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    membro = criar_participante(ata, nome="João")
    convidado = criar_participante(ata, nome="Convidado", membro=False)

    sincronizar(contexto_atas)
    membro.refresh_from_db()

    assert membro.vago is True
    assert membro.presente is False
    assert Participante.objects.filter(pk=convidado.pk, membro=False).exists()


def test_sincronizacao_repetida_nao_duplica_participantes(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    antigo = criar_participante(ata, nome="João")

    sincronizar(contexto_atas)
    primeiro_id = Participante.objects.get(ata=ata, membro=True).pk

    sincronizar(contexto_atas)

    assert primeiro_id == antigo.pk
    assert Participante.objects.filter(ata=ata, membro=True).count() == 1
    assert Participante.objects.get(ata=ata, membro=True).pk == primeiro_id
    assert Participante.objects.get(pk=primeiro_id).nome == "Maria"


def test_sincronizacao_de_um_cargo_nao_altera_participante_de_outro_cargo(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria", cargo=PRESIDENTE)
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
    criar_registro_cargo_ata(contexto_atas, nome="Maria", identificacao=identificacao)
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    criar_participante(ata, nome="Carlos", cargo=SECRETARIO)
    nao_membro = criar_participante(
        ata, nome="Maria", identificacao=identificacao, membro=False,
    )
    outro_nao_membro = criar_participante(
        ata, nome="Convidado", identificacao="9999999", membro=False,
    )

    sincronizar(contexto_atas)

    assert not Participante.objects.filter(pk=nao_membro.pk).exists()
    assert Participante.objects.filter(pk=outro_nao_membro.pk).exists()
    participante = Participante.objects.get(
        ata=ata, membro=True, identificacao=identificacao,
    )

    assert participante.nome == "Maria"


def test_ignora_ata_sem_membros_mas_com_convidados(contexto_atas, historico_v2_ativo):
    criar_registro_cargo_ata(contexto_atas, nome="Maria")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    convidado = criar_participante(
        ata, nome="Maria", identificacao="1234567", membro=False,
    )

    sincronizar(contexto_atas)

    assert not Participante.objects.filter(ata=ata, membro=True).exists()
    assert Participante.objects.filter(pk=convidado.pk, membro=False).exists()


def test_ignora_ata_totalmente_vazia(contexto_atas, historico_v2_ativo):
    criar_registro_cargo_ata(contexto_atas, nome="Maria")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))

    sincronizar(contexto_atas)

    assert not Participante.objects.filter(ata=ata).exists()


def test_cria_membro_vago_quando_cargo_ainda_nao_tem_participante(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome=None)
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    criar_participante(ata, nome="Carlos", cargo=SECRETARIO)

    sincronizar(contexto_atas)

    vago = Participante.objects.get(ata=ata, cargo=Cargos(PRESIDENTE).label)
    assert vago.membro is True
    assert vago.vago is True
    assert vago.presente is False
    assert vago.nome == ""
    assert vago.identificacao == ""
    assert vago.data_inicio_no_cargo == INICIO


def test_cria_conselheiro_com_indicacao_de_conselho_fiscal(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria", cargo=CONSELHEIRO)
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    criar_participante(ata, nome="Carlos", cargo=SECRETARIO)

    sincronizar(contexto_atas, cargo=CONSELHEIRO)

    conselheiro = Participante.objects.get(ata=ata, cargo=Cargos(CONSELHEIRO).label)
    assert conselheiro.nome == "Maria"
    assert conselheiro.conselho_fiscal is True


def test_reativa_membro_ao_sair_de_vacancia(
    contexto_atas, historico_v2_ativo,
):
    registro = criar_registro_cargo_ata(contexto_atas, nome="Maria", identificacao="1234567")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    participante = criar_participante(
        ata, nome="", identificacao="", vago=True, presente=False,
    )

    sincronizar(contexto_atas)

    participante.refresh_from_db()
    assert participante.vago is False
    assert participante.presente is True
    assert participante.nome == registro.ocupante_do_cargo.nome
    assert participante.identificacao == "1234567"


def test_usa_cpf_responsavel_quando_codigo_identificacao_esta_vazio(
    contexto_atas, historico_v2_ativo,
):
    registro = criar_registro_cargo_ata(contexto_atas, nome="Maria", identificacao="")
    ocupante = registro.ocupante_do_cargo
    ocupante.cpf_responsavel = "12345678909"
    ocupante.save(update_fields=["cpf_responsavel"])
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    criar_participante(ata, nome="Carlos", cargo=SECRETARIO)

    sincronizar(contexto_atas)

    presidente = Participante.objects.get(ata=ata, cargo=Cargos(PRESIDENTE).label)
    assert presidente.nome == "Maria"
    assert presidente.identificacao == "12345678909"


def test_remove_nao_membro_pelo_nome_com_espacos_e_caixa_diferente(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria", identificacao="1234567")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    criar_participante(ata, nome="Carlos", cargo=SECRETARIO)
    convidada_duplicada = criar_participante(
        ata, nome="  mArIa  ", identificacao="2222222", membro=False,
    )

    sincronizar(contexto_atas)

    assert not Participante.objects.filter(pk=convidada_duplicada.pk).exists()
    assert Participante.objects.filter(
        ata=ata, membro=True, cargo=Cargos(PRESIDENTE).label, nome="Maria",
    ).exists()


@pytest.mark.parametrize("referencia", ["presidente_da_reuniao", "secretario_da_reuniao"])
def test_transfere_referencia_de_nao_membro_para_membro_do_cargo(
    contexto_atas, historico_v2_ativo, referencia,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria", identificacao="1234567")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    criar_participante(ata, nome="Carlos", cargo=SECRETARIO)
    nao_membro = criar_participante(
        ata, nome="Maria", identificacao="1234567", membro=False,
    )
    setattr(ata, referencia, nao_membro)
    ata.save(update_fields=[referencia])

    sincronizar(contexto_atas)

    ata.refresh_from_db()
    presidente_membro = Participante.objects.get(
        ata=ata, membro=True, cargo=Cargos(PRESIDENTE).label,
    )
    assert getattr(ata, f"{referencia}_id") == presidente_membro.pk
    assert not Participante.objects.filter(pk=nao_membro.pk).exists()


def test_remove_nao_membro_por_cpf_responsavel(
    contexto_atas, historico_v2_ativo,
):
    registro = criar_registro_cargo_ata(contexto_atas, nome="Maria", identificacao="7654321")
    ocupante = registro.ocupante_do_cargo
    ocupante.cpf_responsavel = "12345678909"
    ocupante.save(update_fields=["cpf_responsavel"])
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    criar_participante(ata, nome="Carlos", cargo=SECRETARIO)
    nao_membro = criar_participante(
        ata, nome="Nome Diferente", identificacao="12345678909", membro=False,
    )

    sincronizar(contexto_atas)

    assert not Participante.objects.filter(pk=nao_membro.pk).exists()
    assert Participante.objects.filter(
        ata=ata, membro=True, cargo=Cargos(PRESIDENTE).label,
        identificacao="7654321",
    ).exists()


def test_marca_ata_como_atualizada_pelo_historico_ao_sincronizar(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    criar_participante(ata, nome="João")
    assert ata.atualizado_historico is False

    sincronizar(contexto_atas)
    ata.refresh_from_db()

    assert ata.atualizado_historico is True


def test_mantem_ata_marcada_como_atualizada_ao_sincronizar_novamente(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria")
    ata = criar_ata(contexto_atas, date(2026, 3, 10), atualizado_historico=True)
    criar_participante(ata, nome="João")

    sincronizar(contexto_atas)
    ata.refresh_from_db()

    assert ata.atualizado_historico is True


def test_nao_marca_ata_como_atualizada_quando_flag_historico_v2_desativada(contexto_atas):
    definir_flag("historico-de-membros-v2", False)
    criar_registro_cargo_ata(contexto_atas, nome="Maria")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    criar_participante(ata, nome="João")

    sincronizar(contexto_atas)
    ata.refresh_from_db()

    assert ata.atualizado_historico is False


def test_nao_marca_ata_como_atualizada_quando_ata_nao_tem_membros(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria")
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    criar_participante(ata, nome="Convidado", membro=False)

    sincronizar(contexto_atas)
    ata.refresh_from_db()

    assert ata.atualizado_historico is False


def test_nao_marca_ata_como_atualizada_quando_nao_existe_registro_na_data(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria", data_inicio=date(2026, 4, 1))
    ata = criar_ata(contexto_atas, date(2026, 3, 10))
    criar_participante(ata, nome="João")

    sincronizar(contexto_atas)
    ata.refresh_from_db()

    assert ata.atualizado_historico is False


def test_nao_marca_ata_nao_elegivel_como_atualizada(
    contexto_atas, historico_v2_ativo,
):
    criar_registro_cargo_ata(contexto_atas, nome="Maria")
    ata_valida = criar_ata(contexto_atas, date(2026, 3, 10))
    ata_pdf_concluido = criar_ata(
        contexto_atas, date(2026, 3, 10), status_geracao_pdf=Ata.STATUS_CONCLUIDO,
    )
    for ata in (ata_valida, ata_pdf_concluido):
        criar_participante(ata, nome="João")

    sincronizar(contexto_atas)
    ata_valida.refresh_from_db()
    ata_pdf_concluido.refresh_from_db()

    assert ata_valida.atualizado_historico is True
    assert ata_pdf_concluido.atualizado_historico is False
