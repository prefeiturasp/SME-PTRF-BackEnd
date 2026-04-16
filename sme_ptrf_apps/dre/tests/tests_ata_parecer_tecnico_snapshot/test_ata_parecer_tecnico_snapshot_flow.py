from unittest.mock import patch

import pytest
from datetime import date

from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.periodo_factory import PeriodoFactory
from sme_ptrf_apps.core.fixtures.factories.prestacao_conta_factory import PrestacaoContaFactory
from sme_ptrf_apps.core.fixtures.factories.unidade_factory import DreFactory, UnidadeFactory
from sme_ptrf_apps.core.models import PrestacaoConta
from sme_ptrf_apps.dre.fixtures.factories import (
    AtaParecerTecnicoFactory,
    AtaParecerTecnicoSnapshotFactory,
    ConsolidadoDREFactory,
    MotivoAprovacaoRessalvaFactory,
    MotivoReprovacaoFactory,
)
from sme_ptrf_apps.dre.models import AtaParecerTecnicoSnapshot
from sme_ptrf_apps.dre.services.ata_parecer_tecnico_service import (
    gerar_arquivo_ata_parecer_tecnico,
    obter_payload_ata,
)

pytestmark = pytest.mark.django_db


def _contar_status(payload):
    return {
        "APROVADA": len(payload["aprovadas"]["contas"][0]["info"]) if payload["aprovadas"]["contas"] else 0,
        "APROVADA_RESSALVA": len(payload["aprovadas_ressalva"]["contas"][0]["info"]) if payload["aprovadas_ressalva"]["contas"] else 0,
        "REPROVADA": len(payload["reprovadas"]["contas"][0]["info"]) if payload["reprovadas"]["contas"] else 0,
    }


def _montar_publicacao_com_tres_pcs():
    dre = DreFactory()
    periodo = PeriodoFactory()
    consolidado = ConsolidadoDREFactory(
        dre=dre,
        periodo=periodo,
        versao="FINAL",
        sequencia_de_publicacao=1,
        sequencia_de_retificacao=0,
    )
    ata = AtaParecerTecnicoFactory(
        dre=dre,
        periodo=periodo,
        consolidado_dre=consolidado,
        sequencia_de_publicacao=consolidado.sequencia_de_publicacao,
    )

    unidade_a = UnidadeFactory(dre=dre, tipo_unidade="EMEI")
    unidade_b = UnidadeFactory(dre=dre, tipo_unidade="EMEF")
    unidade_c = UnidadeFactory(dre=dre, tipo_unidade="CEI")

    associacao_a = AssociacaoFactory(unidade=unidade_a)
    associacao_b = AssociacaoFactory(unidade=unidade_b)
    associacao_c = AssociacaoFactory(unidade=unidade_c)

    pc_aprovada = PrestacaoContaFactory(
        periodo=periodo,
        associacao=associacao_a,
        status=PrestacaoConta.STATUS_APROVADA,
        publicada=True,
        consolidado_dre=consolidado,
    )
    pc_aprovada_ressalva = PrestacaoContaFactory(
        periodo=periodo,
        associacao=associacao_b,
        status=PrestacaoConta.STATUS_APROVADA_RESSALVA,
        publicada=True,
        consolidado_dre=consolidado,
        recomendacoes="Recomendacao original",
    )
    pc_reprovada = PrestacaoContaFactory(
        periodo=periodo,
        associacao=associacao_c,
        status=PrestacaoConta.STATUS_REPROVADA,
        publicada=True,
        consolidado_dre=consolidado,
    )

    pc_aprovada_ressalva.motivos_aprovacao_ressalva.add(MotivoAprovacaoRessalvaFactory())
    pc_reprovada.motivos_reprovacao.add(MotivoReprovacaoFactory())

    consolidado.pcs_do_consolidado.add(pc_aprovada, pc_aprovada_ressalva, pc_reprovada)

    return dre, periodo, ata, consolidado, pc_aprovada, pc_aprovada_ressalva, pc_reprovada


@patch("sme_ptrf_apps.dre.services.ata_parecer_tecnico_service.gerar_arquivo_ata_parecer_tecnico_pdf")
def test_snapshot_e_criado_na_publicacao_e_congelado(mock_pdf):
    dre, periodo, ata, _, _, pc_aprovada_ressalva, pc_reprovada = _montar_publicacao_com_tres_pcs()

    gerar_arquivo_ata_parecer_tecnico(
        ata=ata,
        dre=dre,
        periodo=periodo,
        usuario="usuario.publicacao",
        parcial={"parcial": True, "sequencia_de_publicacao_atual": 1},
        congelar_snapshot=True,
        origem=AtaParecerTecnicoSnapshot.ORIGEM_PUBLICACAO,
    )

    snapshot = AtaParecerTecnicoSnapshot.objects.get(ata=ata)
    status_no_snapshot = _contar_status(snapshot.dados)
    assert status_no_snapshot == {"APROVADA": 1, "APROVADA_RESSALVA": 1, "REPROVADA": 1}

    # Simula alteracoes posteriores apos retificacao.
    pc_aprovada_ressalva.status = PrestacaoConta.STATUS_REPROVADA
    pc_aprovada_ressalva.recomendacoes = "Recomendacao alterada apos publicacao"
    pc_aprovada_ressalva.save(update_fields=["status", "recomendacoes"])
    pc_aprovada_ressalva.motivos_aprovacao_ressalva.clear()
    pc_aprovada_ressalva.motivos_reprovacao.add(MotivoReprovacaoFactory())

    pc_reprovada.status = PrestacaoConta.STATUS_APROVADA
    pc_reprovada.save(update_fields=["status"])
    pc_reprovada.motivos_reprovacao.clear()

    payload_em_tela = obter_payload_ata(
        dre=dre,
        periodo=periodo,
        ata_de_parecer_tecnico=ata,
        usuario="usuario.tela",
        usar_snapshot=True,
        congelar_snapshot=False,
    )

    assert payload_em_tela == snapshot.dados
    assert _contar_status(payload_em_tela) == {"APROVADA": 1, "APROVADA_RESSALVA": 1, "REPROVADA": 1}
    assert mock_pdf.called


@patch("sme_ptrf_apps.dre.services.ata_parecer_tecnico_service.gerar_arquivo_ata_parecer_tecnico_pdf")
def test_snapshots_de_publicacao_e_retificacao_sao_independentes(mock_pdf):
    dre, periodo, ata_publicacao, consolidado_publicacao, pc_aprovada, _, _ = _montar_publicacao_com_tres_pcs()

    # Fluxo real: ao existir retificacao, a publicacao original ja passou pelo D.O.
    consolidado_publicacao.data_publicacao = date(2026, 4, 10)
    consolidado_publicacao.save(update_fields=["data_publicacao"])

    gerar_arquivo_ata_parecer_tecnico(
        ata=ata_publicacao,
        dre=dre,
        periodo=periodo,
        usuario="usuario.publicacao",
        parcial={"parcial": True, "sequencia_de_publicacao_atual": 1},
        congelar_snapshot=True,
        origem=AtaParecerTecnicoSnapshot.ORIGEM_PUBLICACAO,
    )

    consolidado_retificacao = ConsolidadoDREFactory(
        dre=dre,
        periodo=periodo,
        versao="FINAL",
        sequencia_de_publicacao=consolidado_publicacao.sequencia_de_publicacao,
        sequencia_de_retificacao=1,
        consolidado_retificado=consolidado_publicacao,
        eh_parcial=True,
    )
    ata_retificacao = AtaParecerTecnicoFactory(
        dre=dre,
        periodo=periodo,
        consolidado_dre=consolidado_retificacao,
        sequencia_de_publicacao=consolidado_retificacao.sequencia_de_publicacao,
        sequencia_de_retificacao=consolidado_retificacao.sequencia_de_retificacao,
    )

    pc_aprovada.status = PrestacaoConta.STATUS_REPROVADA
    pc_aprovada.publicada = False
    pc_aprovada.consolidado_dre = consolidado_retificacao
    pc_aprovada.save(update_fields=["status", "publicada", "consolidado_dre"])
    pc_aprovada.motivos_reprovacao.add(MotivoReprovacaoFactory())
    consolidado_retificacao.pcs_do_consolidado.add(pc_aprovada)

    gerar_arquivo_ata_parecer_tecnico(
        ata=ata_retificacao,
        dre=dre,
        periodo=periodo,
        usuario="usuario.retificacao",
        parcial={"parcial": True, "sequencia_de_publicacao_atual": 1},
        congelar_snapshot=True,
        origem=AtaParecerTecnicoSnapshot.ORIGEM_PUBLICACAO,
    )

    # Simula uma nova alteracao apos a retificacao.
    pc_aprovada.status = PrestacaoConta.STATUS_APROVADA_RESSALVA
    pc_aprovada.save(update_fields=["status"])
    pc_aprovada.motivos_aprovacao_ressalva.add(MotivoAprovacaoRessalvaFactory())

    payload_publicacao = obter_payload_ata(
        dre=dre,
        periodo=periodo,
        ata_de_parecer_tecnico=ata_publicacao,
        usar_snapshot=True,
    )
    payload_retificacao = obter_payload_ata(
        dre=dre,
        periodo=periodo,
        ata_de_parecer_tecnico=ata_retificacao,
        usar_snapshot=True,
    )

    assert _contar_status(payload_publicacao) == {"APROVADA": 1, "APROVADA_RESSALVA": 1, "REPROVADA": 1}
    assert _contar_status(payload_retificacao) == {"APROVADA": 0, "APROVADA_RESSALVA": 0, "REPROVADA": 1}
    assert mock_pdf.call_count == 2


def test_obter_payload_ata_prioriza_snapshot_existente():
    dre = DreFactory()
    periodo = PeriodoFactory()
    ata = AtaParecerTecnicoFactory(dre=dre, periodo=periodo)
    payload_snapshot = {
        "cabecalho": {"titulo": "SNAPSHOT_FIXO"},
        "aprovadas": {"contas": [{"info": [{"status_prestacao_contas": "APROVADA"}]}]},
        "aprovadas_ressalva": {"contas": [], "motivos": []},
        "reprovadas": {"contas": [], "motivos": []},
    }
    AtaParecerTecnicoSnapshotFactory(
        ata=ata,
        dados=payload_snapshot,
        origem=AtaParecerTecnicoSnapshot.ORIGEM_PUBLICACAO,
    )

    payload = obter_payload_ata(
        dre=dre,
        periodo=periodo,
        ata_de_parecer_tecnico=ata,
        usuario="usuario.tela",
        usar_snapshot=True,
        congelar_snapshot=False,
    )

    assert payload == payload_snapshot


def test_info_ata_retorna_snapshot_quando_existente(jwt_authenticated_client_dre):
    dre = DreFactory()
    periodo = PeriodoFactory()
    ata = AtaParecerTecnicoFactory(dre=dre, periodo=periodo)
    payload_snapshot = {
        "cabecalho": {"titulo": "PAYLOAD_SNAPSHOT"},
        "aprovadas": {"contas": []},
        "aprovadas_ressalva": {"contas": [], "motivos": []},
        "reprovadas": {"contas": [], "motivos": []},
    }
    AtaParecerTecnicoSnapshotFactory(
        ata=ata,
        dados=payload_snapshot,
        origem=AtaParecerTecnicoSnapshot.ORIGEM_PUBLICACAO,
    )

    response = jwt_authenticated_client_dre.get(
        f"/api/ata-parecer-tecnico/info-ata/?dre={dre.uuid}&periodo={periodo.uuid}&ata={ata.uuid}",
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json() == payload_snapshot


def test_criar_se_nao_existir_retorna_snapshot_existente_sem_duplicar():
    dre = DreFactory()
    periodo = PeriodoFactory()
    ata = AtaParecerTecnicoFactory(dre=dre, periodo=periodo)

    payload_original = {
        "cabecalho": {"titulo": "ORIGINAL"},
        "aprovadas": {"contas": []},
        "aprovadas_ressalva": {"contas": [], "motivos": []},
        "reprovadas": {"contas": [], "motivos": []},
    }

    snapshot_existente = AtaParecerTecnicoSnapshotFactory(
        ata=ata,
        dados=payload_original,
        origem=AtaParecerTecnicoSnapshot.ORIGEM_PUBLICACAO,
    )

    payload_novo = {
        "cabecalho": {"titulo": "NOVO"},
        "aprovadas": {"contas": [{"info": [{"status_prestacao_contas": "APROVADA"}]}]},
        "aprovadas_ressalva": {"contas": [], "motivos": []},
        "reprovadas": {"contas": [], "motivos": []},
    }

    snapshot_retorno, criado = AtaParecerTecnicoSnapshot.criar_se_nao_existir(
        ata=ata,
        dados=payload_novo,
        origem=AtaParecerTecnicoSnapshot.ORIGEM_MANUAL,
    )

    assert criado is False
    assert snapshot_retorno.pk == snapshot_existente.pk
    assert AtaParecerTecnicoSnapshot.objects.filter(ata=ata).count() == 1
    assert snapshot_retorno.dados == payload_original
