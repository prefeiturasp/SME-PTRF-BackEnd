
import pytest
from model_bakery import baker
from sme_ptrf_apps.core.fixtures.factories.periodo_factory import PeriodoFactory
from sme_ptrf_apps.core.fixtures.factories.unidade_factory import DreFactory
from sme_ptrf_apps.dre.models import AtaParecerTecnicoSnapshot

from sme_ptrf_apps.dre.fixtures.factories import (
    AtaParecerTecnicoFactory,
    AtaParecerTecnicoSnapshotFactory
)

pytestmark = pytest.mark.django_db


def test_info_ata_retorna_presentes_por_recurso(
    jwt_authenticated_client_dre,
    recurso_factory,
):
    dre = DreFactory()
    periodo = PeriodoFactory()

    ata = AtaParecerTecnicoFactory(
        dre=dre,
        periodo=periodo,
    )

    recurso_ptrf = recurso_factory(
        nome='PTRF',
        nome_exibicao='PTRF Exibição',
    )

    recurso_premio = recurso_factory(
        nome='PREMIO',
        nome_exibicao='PREMIO Exibição',
    )

    comissao_recurso_ptrf = baker.make(
        'Comissao',
        nome='Exame de Contas PTRF',
        recursos=[recurso_ptrf],
        responsavel_analise_pc=True,
    )

    comissao_recurso_premio = baker.make(
        'Comissao',
        nome='Exame de Contas PREMIO',
        recursos=[recurso_premio],
        responsavel_analise_pc=True,
    )

    membro_comissao_ptrf_1 = baker.make(
        'MembroComissao',
        rf='123456',
        nome='João',
        cargo='teste',
        email='joao@teste.com',
        dre=dre,
        comissoes=[comissao_recurso_ptrf],
    )

    membro_comissao_ptrf_2 = baker.make(
        'MembroComissao',
        rf='234567',
        nome='Pedro',
        cargo='teste',
        email='pedro@teste.com',
        dre=dre,
        comissoes=[comissao_recurso_ptrf],
    )

    membro_comissao_premio_1 = baker.make(
        'MembroComissao',
        rf='345678',
        nome='Tiago',
        cargo='teste',
        email='tiago@teste.com',
        dre=dre,
        comissoes=[comissao_recurso_premio],
    )

    membro_comissao_premio_2 = baker.make(
        'MembroComissao',
        rf='456789',
        nome='Matias',
        cargo='teste',
        email='matias@teste.com',
        dre=dre,
        comissoes=[comissao_recurso_premio],
    )

    # Presentes do recurso PTRF
    baker.make(
        'PresenteAtaDre',
        ata=ata,
        rf=membro_comissao_ptrf_1.rf,
        nome=membro_comissao_ptrf_1.nome,
        cargo=membro_comissao_ptrf_1.cargo,
    )

    baker.make(
        'PresenteAtaDre',
        ata=ata,
        rf=membro_comissao_ptrf_2.rf,
        nome=membro_comissao_ptrf_2.nome,
        cargo=membro_comissao_ptrf_2.cargo,
    )

    # Presentes do recurso PREMIO
    baker.make(
        'PresenteAtaDre',
        ata=ata,
        rf=membro_comissao_premio_1.rf,
        nome=membro_comissao_premio_1.nome,
        cargo=membro_comissao_premio_1.cargo,
    )

    baker.make(
        'PresenteAtaDre',
        ata=ata,
        rf=membro_comissao_premio_2.rf,
        nome=membro_comissao_premio_2.nome,
        cargo=membro_comissao_premio_2.cargo,
    )

    presentes = [
        {           
            'nome': 'João',
            'rf': '123456',
            'cargo': 'teste',
        },
        {            
            'nome': 'Pedro',
            'rf': '234567',
            'cargo': 'teste',           
        },
    ]

    AtaParecerTecnicoSnapshotFactory(
        ata=ata,
        dados={'presentes_na_ata': {'presentes': presentes}},
        origem=AtaParecerTecnicoSnapshot.ORIGEM_PUBLICACAO,
    )

    response = jwt_authenticated_client_dre.get(
        f"/api/ata-parecer-tecnico/info-ata/?dre={ata.dre.uuid}&periodo={periodo.uuid}&ata={ata.uuid}",
        content_type="application/json",
        HTTP_X_RECURSO_SELECIONADO=str(recurso_ptrf.uuid),
    )

    assert response.status_code == 200

    presentes_na_ata = response.json()['presentes_na_ata']['presentes']

    assert len(presentes_na_ata) == 2

    assert presentes_na_ata == presentes


def test_info_ata_retorna_lista_vazia_quando_nao_ha_presentes_do_recurso(
    jwt_authenticated_client_dre,
    recurso_factory,
):
    dre = DreFactory()
    periodo = PeriodoFactory()
    ata = AtaParecerTecnicoFactory(
        dre=dre,
        periodo=periodo,
    )

    recurso_ptrf = recurso_factory(
        nome='PTRF',
        nome_exibicao='PTRF Exibição',
    )

    recurso_premio = recurso_factory(
        nome='PREMIO',
        nome_exibicao='PREMIO Exibição',
    )

    comissao_premio = baker.make(
        'Comissao',
        nome='Exame de Contas PREMIO',
        recursos=[recurso_premio],
        responsavel_analise_pc=True,
    )

    membro_premio = baker.make(
        'MembroComissao',
        rf='345678',
        nome='Tiago',
        cargo='teste',
        dre=dre,
        comissoes=[comissao_premio],
    )

    baker.make(
        'PresenteAtaDre',
        ata=ata,
        rf=membro_premio.rf,
        nome=membro_premio.nome,
        cargo=membro_premio.cargo,
    )

    response = jwt_authenticated_client_dre.get(
        f"/api/ata-parecer-tecnico/info-ata/?dre={ata.dre.uuid}&periodo={periodo.uuid}&ata={ata.uuid}",
        content_type="application/json",
        HTTP_X_RECURSO_SELECIONADO=str(recurso_ptrf.uuid),
    )

    assert response.status_code == 200

    presentes_na_ata = response.json()['presentes_na_ata']['presentes']

    assert presentes_na_ata == []
