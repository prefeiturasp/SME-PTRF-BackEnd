import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from sme_ptrf_apps.paa.services import OutroRecursoPeriodoBaseService
from sme_ptrf_apps.paa.fixtures.factories import (
    PaaFactory,
    ReceitaPrevistaOutroRecursoPeriodoFactory,
    PrioridadePaaFactory
)
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.core.fixtures.factories import UnidadeFactory


@pytest.fixture
def periodo_paa_1(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='P 2020.1',
        data_inicial=date(2020, 1, 1),
        data_final=date(2020, 4, 30),
    )


@pytest.fixture
def periodo_paa_2(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='P 2020.2',
        data_inicial=date(2020, 5, 1),
        data_final=date(2020, 9, 30),
    )


@pytest.fixture
def paa1(paa_factory, periodo_paa_1):
    return paa_factory.create(periodo_paa=periodo_paa_1)


@pytest.fixture
def paa2(paa_factory, periodo_paa_2):
    return paa_factory.create(periodo_paa=periodo_paa_2)


@pytest.fixture
def outros_recursos_periodo(periodo_paa_1, outro_recurso_factory, outro_recurso_periodo_factory):
    outro_recurso = outro_recurso_factory.create(nome='Teste 2020')
    return outro_recurso_periodo_factory.create(
        outro_recurso=outro_recurso,
        periodo_paa=periodo_paa_1,
        ativo=True
    )


@pytest.fixture
def base_service(outros_recursos_periodo):
    """Fixture que retorna instância do base service"""
    return OutroRecursoPeriodoBaseService(outros_recursos_periodo)


@pytest.mark.django_db
def test_init_service_com_sucesso(outros_recursos_periodo):
    """Testa inicialização do service com sucesso"""
    service = OutroRecursoPeriodoBaseService(outros_recursos_periodo)

    assert service.outro_recurso_periodo == outros_recursos_periodo
    assert isinstance(service, OutroRecursoPeriodoBaseService)


@pytest.mark.django_db
def test_init_service_armazena_referencia(outros_recursos_periodo):
    """Testa que service armazena referência correta ao objeto"""
    service = OutroRecursoPeriodoBaseService(outros_recursos_periodo)

    assert service.outro_recurso_periodo.uuid == outros_recursos_periodo.uuid
    assert service.outro_recurso_periodo.ativo == outros_recursos_periodo.ativo


@pytest.mark.django_db
def test_tinha_todas_unidades_sem_vinculo(base_service):
    """Testa que retorna True quando não há unidades vinculadas"""
    resultado = base_service._tinha_todas_unidades()

    assert resultado is True


@pytest.mark.django_db
def test_tinha_todas_unidades_com_vinculo(base_service):
    """Testa que retorna False quando há unidades vinculadas"""
    unidade = UnidadeFactory.create()
    base_service.outro_recurso_periodo.unidades.add(unidade)

    resultado = base_service._tinha_todas_unidades()

    assert resultado is False


@pytest.mark.django_db
def test_tinha_todas_unidades_multiplas_unidades(base_service):
    """Testa com múltiplas unidades vinculadas"""
    unidades = UnidadeFactory.create_batch(3)
    base_service.outro_recurso_periodo.unidades.add(*unidades)

    resultado = base_service._tinha_todas_unidades()

    assert resultado is False


@pytest.mark.django_db
def test_obtem_paas_afetados_sem_paas(base_service):
    """Testa quando não há PAAs no período"""
    paas = base_service._obtem_paas_afetados()

    assert paas.count() == 0


@pytest.mark.django_db
def test_obtem_paas_afetados_com_paas(base_service, paa1, paa2):
    """Testa obtenção de PAAs do período"""

    paas = base_service._obtem_paas_afetados()

    assert paas.count() == 1
    assert paa1 in paas
    assert paa2 not in paas


@pytest.mark.django_db
def test_obtem_paas_afetados_select_related(base_service, periodo_paa):
    """Testa que select_related é aplicado corretamente"""
    PaaFactory.create(periodo_paa=periodo_paa)

    with patch('sme_ptrf_apps.paa.models.Paa.objects.filter') as mock_filter:
        mock_queryset = MagicMock()
        mock_filter.return_value = mock_queryset

        base_service._obtem_paas_afetados()

        mock_queryset.select_related.assert_called_once_with(
            'associacao', 'associacao__unidade', 'periodo_paa'
        )


@pytest.mark.django_db
def test_paas_afetados_em_elaboracao(base_service, periodo_paa_1):
    """Testa filtro de PAAs em elaboração"""
    paa_elaboracao = PaaFactory.create(
        periodo_paa=periodo_paa_1,
        status=PaaStatusEnum.EM_ELABORACAO.name
    )
    PaaFactory.create(
        periodo_paa=periodo_paa_1,
        status=PaaStatusEnum.GERADO.name
    )

    paas = base_service._paas_afetados_em_elaboracao()

    assert paas.count() == 1
    assert paa_elaboracao in paas


@pytest.mark.django_db
def test_paas_afetados_gerado_retificado(base_service, periodo_paa_1):
    """Testa filtro de PAAs gerados ou em retificação"""
    paa_gerado = PaaFactory.create(
        periodo_paa=periodo_paa_1,
        status=PaaStatusEnum.GERADO.name
    )
    paa_retificacao = PaaFactory.create(
        periodo_paa=periodo_paa_1,
        status=PaaStatusEnum.EM_RETIFICACAO.name
    )
    PaaFactory.create(
        periodo_paa=periodo_paa_1,
        status=PaaStatusEnum.EM_ELABORACAO.name
    )

    paas = base_service._paas_afetados_gerado_retificado()

    assert paas.count() == 2
    assert paa_gerado in paas
    assert paa_retificacao in paas


@pytest.mark.django_db
def test_paa_em_elaboracao_true(base_service, periodo_paa):
    """Testa verificação quando PAA está em elaboração"""
    paa = PaaFactory.create(
        periodo_paa=periodo_paa,
        status=PaaStatusEnum.EM_ELABORACAO.name
    )

    assert base_service._paa_em_elaboracao(paa) is True


@pytest.mark.django_db
def test_paa_em_elaboracao_false(base_service, periodo_paa):
    """Testa verificação quando PAA não está em elaboração"""
    paa = PaaFactory.create(
        periodo_paa=periodo_paa,
        status=PaaStatusEnum.GERADO.name
    )

    assert base_service._paa_em_elaboracao(paa) is False


@pytest.mark.django_db
def test_paa_gerado_retificado_gerado(base_service, periodo_paa):
    """Testa verificação para PAA gerado"""
    paa = PaaFactory.create(
        periodo_paa=periodo_paa,
        status=PaaStatusEnum.GERADO.name
    )
    assert base_service._paa_gerado_retificado(paa) is True


@pytest.mark.django_db
def test_paa_gerado_retificado_retificacao(base_service, periodo_paa):
    """Testa verificação para PAA em retificação"""
    paa = PaaFactory.create(
        periodo_paa=periodo_paa,
        status=PaaStatusEnum.EM_RETIFICACAO.name
    )
    assert base_service._paa_gerado_retificado(paa) is True


@pytest.mark.django_db
def test_paa_gerado_retificado_false(base_service, periodo_paa):
    """Testa verificação quando PAA não está gerado nem em retificação"""
    paa = PaaFactory.create(
        periodo_paa=periodo_paa,
        status=PaaStatusEnum.EM_ELABORACAO.name
    )

    assert base_service._paa_gerado_retificado(paa) is False


@pytest.mark.django_db
def test_paa_retificado_true(base_service, periodo_paa):
    """Testa verificação quando PAA está em retificação"""
    paa = PaaFactory.create(
        periodo_paa=periodo_paa,
        status=PaaStatusEnum.EM_RETIFICACAO.name
    )

    assert base_service._paa_retificado(paa) is True


@pytest.mark.django_db
def test_paa_retificado_false(base_service, periodo_paa):
    """Testa verificação quando PAA não está em retificação"""
    paa = PaaFactory.create(
        periodo_paa=periodo_paa,
        status=PaaStatusEnum.GERADO.name
    )

    assert base_service._paa_retificado(paa) is False


@pytest.mark.django_db
def test_paa_gerado_true(base_service, periodo_paa):
    """Testa verificação quando PAA está gerado"""
    paa = PaaFactory.create(
        periodo_paa=periodo_paa,
        status=PaaStatusEnum.GERADO.name
    )

    assert base_service._paa_gerado(paa) is True


@pytest.mark.django_db
def test_paa_gerado_false(base_service, periodo_paa):
    """Testa verificação quando PAA não está gerado"""
    paa = PaaFactory.create(
        periodo_paa=periodo_paa,
        status=PaaStatusEnum.EM_ELABORACAO.name
    )

    assert base_service._paa_gerado(paa) is False


@pytest.mark.django_db
def test_receitas_previstas_afetadas_sem_receitas(base_service, periodo_paa):
    """Testa quando não há receitas previstas"""
    paa = PaaFactory.create(periodo_paa=periodo_paa)

    receitas = base_service._receitas_previstas_outro_recurso_periodo_afetadas(paa)

    assert receitas.count() == 0


@pytest.mark.django_db
def test_receitas_previstas_afetadas_com_receitas(base_service, periodo_paa):
    """Testa obtenção de receitas previstas"""
    paa = PaaFactory.create(periodo_paa=periodo_paa)

    receita1 = ReceitaPrevistaOutroRecursoPeriodoFactory.create(
        paa=paa,
        outro_recurso_periodo=base_service.outro_recurso_periodo
    )

    receitas = base_service._receitas_previstas_outro_recurso_periodo_afetadas(paa)

    assert receitas.count() == 1
    assert receita1 in receitas


@pytest.mark.django_db
def test_receitas_previstas_afetadas_filtra_por_recurso(
    base_service,
    periodo_paa,
    outro_recurso_factory
):
    """Testa que filtra apenas receitas do recurso específico"""
    paa = PaaFactory.create(periodo_paa=periodo_paa)

    # Receita do recurso correto
    receita_correta = ReceitaPrevistaOutroRecursoPeriodoFactory.create(
        paa=paa,
        outro_recurso_periodo=base_service.outro_recurso_periodo
    )

    # Receita de outro recurso (não deve ser retornada)
    from sme_ptrf_apps.paa.fixtures.factories import OutroRecursoPeriodoFactory
    outro_recurso_periodo = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa,
        outro_recurso=outro_recurso_factory.create(nome="Outro Recurso")
    )
    ReceitaPrevistaOutroRecursoPeriodoFactory.create(
        paa=paa,
        outro_recurso_periodo=outro_recurso_periodo
    )

    receitas = base_service._receitas_previstas_outro_recurso_periodo_afetadas(paa)

    assert receitas.count() == 1
    assert receita_correta in receitas


@pytest.mark.django_db
def test_remover_receitas_previstas_com_sucesso(base_service, periodo_paa):
    """Testa remoção de receitas previstas com sucesso"""
    paa = PaaFactory.create(periodo_paa=periodo_paa)

    ReceitaPrevistaOutroRecursoPeriodoFactory.create(
        paa=paa,
        outro_recurso_periodo=base_service.outro_recurso_periodo
    )

    count = base_service._remover_receitas_previstas_outro_recurso_periodo(paa)

    assert count == 1
    assert base_service._receitas_previstas_outro_recurso_periodo_afetadas(paa).count() == 0


@pytest.mark.django_db
def test_remover_receitas_previstas_sem_receitas(base_service, periodo_paa):
    """Testa remoção quando não há receitas"""
    paa = PaaFactory.create(periodo_paa=periodo_paa)

    count = base_service._remover_receitas_previstas_outro_recurso_periodo(paa)

    assert count == 0


@pytest.mark.django_db
def test_remover_receitas_previstas_erro(base_service, periodo_paa):
    """Testa que exceção é levantada em caso de erro"""
    paa = PaaFactory.create(periodo_paa=periodo_paa)

    with patch.object(
        base_service,
        '_receitas_previstas_outro_recurso_periodo_afetadas',
        side_effect=Exception("Erro de banco")
    ):
        with pytest.raises(Exception) as excinfo:
            base_service._remover_receitas_previstas_outro_recurso_periodo(paa)

        assert "Erro ao remover receitas previstas" in str(excinfo.value)


@pytest.mark.django_db
def test_prioridades_afetadas_sem_prioridades(base_service, periodo_paa):
    """Testa quando não há prioridades"""
    paa = PaaFactory.create(periodo_paa=periodo_paa)

    prioridades = base_service._prioridades_afetadas(paa)

    assert prioridades.count() == 0


@pytest.mark.django_db
def test_prioridades_afetadas_com_prioridades(base_service, periodo_paa):
    """Testa obtenção de prioridades"""
    paa = PaaFactory.create(periodo_paa=periodo_paa)

    prioridade1 = PrioridadePaaFactory.create(
        paa=paa,
        outro_recurso=base_service.outro_recurso_periodo.outro_recurso
    )
    prioridade2 = PrioridadePaaFactory.create(
        paa=paa,
        outro_recurso=base_service.outro_recurso_periodo.outro_recurso
    )
    prioridades = base_service._prioridades_afetadas(paa)
    assert prioridades.count() == 2
    assert prioridade1 in prioridades
    assert prioridade2 in prioridades


@pytest.mark.django_db
def test_prioridades_afetadas_filtra_por_recurso(
    base_service,
    periodo_paa,
    outro_recurso_factory
):
    """Testa que filtra apenas prioridades do recurso específico"""
    paa = PaaFactory.create(periodo_paa=periodo_paa)
    # Prioridade do recurso correto
    prioridade_correta = PrioridadePaaFactory.create(
        paa=paa,
        outro_recurso=base_service.outro_recurso_periodo.outro_recurso
    )
    # Prioridade de outro recurso (não deve ser retornada)
    outro_recurso = outro_recurso_factory.create(nome="Outro Recurso")
    PrioridadePaaFactory.create(
        paa=paa,
        outro_recurso=outro_recurso
    )
    prioridades = base_service._prioridades_afetadas(paa)
    assert prioridades.count() == 1
    assert prioridade_correta in prioridades


@pytest.mark.django_db
def test_remover_prioridades_com_sucesso(base_service, periodo_paa):
    """Testa remoção (deixar em branco) de prioridades com sucesso"""
    paa = PaaFactory.create(periodo_paa=periodo_paa)
    prioridades = PrioridadePaaFactory.create_batch(
        3,
        paa=paa,
        outro_recurso=base_service.outro_recurso_periodo.outro_recurso
    )
    count = base_service._remover_prioridades_outro_recurso_periodo(paa)
    assert count == 3
    # Verifica que prioridades foram atualizadas para None
    for prioridade in prioridades:
        prioridade.refresh_from_db()
        assert prioridade.outro_recurso is None


@pytest.mark.django_db
def test_remover_prioridades_sem_prioridades(base_service, periodo_paa):
    """Testa remoção quando não há prioridades"""
    paa = PaaFactory.create(periodo_paa=periodo_paa)
    count = base_service._remover_prioridades_outro_recurso_periodo(paa)

    assert count == 0


@pytest.mark.django_db
def test_remover_prioridades_nao_deleta_registro(base_service, periodo_paa):
    """Testa que registros de prioridades não são deletados, apenas atualizados"""
    paa = PaaFactory.create(periodo_paa=periodo_paa)

    prioridade = PrioridadePaaFactory.create(
        paa=paa,
        outro_recurso=base_service.outro_recurso_periodo.outro_recurso
    )
    prioridade_id = prioridade.id

    base_service._remover_prioridades_outro_recurso_periodo(paa)

    # Verifica que o registro ainda existe
    from sme_ptrf_apps.paa.models import PrioridadePaa
    prioridade_atualizada = PrioridadePaa.objects.get(id=prioridade_id)
    assert prioridade_atualizada is not None
    assert prioridade_atualizada.outro_recurso is None


@pytest.mark.django_db
def test_outro_recurso_periodo_ativo_true(base_service):
    """Testa quando recurso está ativo"""
    base_service.outro_recurso_periodo.ativo = True
    base_service.outro_recurso_periodo.save()

    assert base_service._outro_recurso_periodo_ativo() is True


@pytest.mark.django_db
def test_outro_recurso_periodo_ativo_false(base_service):
    """Testa quando recurso está inativo"""
    base_service.outro_recurso_periodo.ativo = False
    base_service.outro_recurso_periodo.save()

    assert base_service._outro_recurso_periodo_ativo() is False


@pytest.mark.django_db
def test_outro_recurso_periodo_ativo_default(outros_recursos_periodo):
    """Testa valor default ao criar recurso"""
    service = OutroRecursoPeriodoBaseService(outros_recursos_periodo)

    # Assume que o default é True
    assert service._outro_recurso_periodo_ativo() is True
