import pytest

from sme_ptrf_apps.paa.services.registrar_acoes_conclusao_paa_service import (
    RegistrarAcoesPtrfConclusaoPaaService,
    RegistrarAcoesPddeConclusaoPaaService,
    RegistrarAcoesOutrosRecursosConclusaoPaaService
)


@pytest.mark.django_db
def test_registrar_acoes_ptrf_conclusao_paa_registra_acoes_com_exibir_paa_true(
    paa_factory, periodo_paa_1
):
    """Testa que apenas ações com exibir_paa=True são registradas"""
    from sme_ptrf_apps.core.models import Acao
    
    paa = paa_factory.create(periodo_paa=periodo_paa_1)
    
    # Obtém ações existentes com exibir_paa=True
    acoes_com_exibir_paa = list(Acao.objects.filter(exibir_paa=True))
    quantidade_antes = len(acoes_com_exibir_paa)
    
    if quantidade_antes == 0:
        acao_existente = Acao.objects.first()
        if acao_existente:
            acao_existente.exibir_paa = True
            acao_existente.save()
            acoes_com_exibir_paa = [acao_existente]
    
    quantidade = RegistrarAcoesPtrfConclusaoPaaService.registrar(paa)
    
    # Verifica que as ações foram registradas
    assert quantidade == len(acoes_com_exibir_paa)
    assert paa.acoes_conclusao.count() == quantidade
    
    # Verifica que apenas ações com exibir_paa=True foram registradas
    acoes_registradas = paa.acoes_conclusao.all()
    for acao in acoes_registradas:
        assert acao.exibir_paa is True


@pytest.mark.django_db
def test_registrar_acoes_ptrf_conclusao_paa_retorna_zero_quando_nao_ha_acoes(
    paa_factory, periodo_paa_1
):
    """Testa que retorna 0 quando não há ações com exibir_paa=True"""
    paa = paa_factory.create(periodo_paa=periodo_paa_1)
    
    quantidade = RegistrarAcoesPtrfConclusaoPaaService.registrar(paa)
    
    assert quantidade == 0
    assert paa.acoes_conclusao.count() == 0


@pytest.mark.django_db
def test_registrar_acoes_pdde_conclusao_paa_registra_acoes_com_status_ativa(
    paa_factory, acao_pdde_factory, periodo_paa_1
):
    """Testa que apenas ações PDDE com status ATIVA são registradas"""
    paa = paa_factory.create(periodo_paa=periodo_paa_1)
    
    # Cria ações PDDE com status ATIVA
    acao_pdde1 = acao_pdde_factory.create(status='ATIVA', nome="Ação PDDE 1")
    acao_pdde2 = acao_pdde_factory.create(status='ATIVA', nome="Ação PDDE 2")
    
    # Cria ação PDDE com status INATIVA (não deve ser registrada)
    acao_pdde3 = acao_pdde_factory.create(status='INATIVA', nome="Ação PDDE 3")
    
    quantidade = RegistrarAcoesPddeConclusaoPaaService.registrar(paa)
    
    # Verifica que apenas as ações com status ATIVA foram registradas
    assert quantidade == 2
    assert acao_pdde1 in paa.acoes_pdde_conclusao.all()
    assert acao_pdde2 in paa.acoes_pdde_conclusao.all()
    assert acao_pdde3 not in paa.acoes_pdde_conclusao.all()


@pytest.mark.django_db
def test_registrar_acoes_pdde_conclusao_paa_retorna_zero_quando_nao_ha_acoes_ativas(
    paa_factory, periodo_paa_1
):
    """Testa que retorna 0 quando não há ações PDDE com status ATIVA"""
    paa = paa_factory.create(periodo_paa=periodo_paa_1)
    
    quantidade = RegistrarAcoesPddeConclusaoPaaService.registrar(paa)
    
    assert quantidade == 0
    assert paa.acoes_pdde_conclusao.count() == 0


@pytest.mark.django_db
def test_registrar_acoes_outros_recursos_conclusao_paa_registra_recursos_disponiveis(
    paa_factory, outro_recurso_periodo_factory, periodo_paa_1
):
    """Testa que apenas outros recursos disponíveis para o PAA são registrados"""
    paa = paa_factory.create(periodo_paa=periodo_paa_1)
    unidade = paa.associacao.unidade
    
    # Cria outro recurso disponível para o PAA (mesmo período e unidade, ativo=True)
    outro_recurso1 = outro_recurso_periodo_factory.create(
        periodo_paa=paa.periodo_paa,
        ativo=True
    )
    outro_recurso1.unidades.add(unidade)
    
    # Cria outro recurso disponível sem unidades específicas (disponível para todas)
    outro_recurso2 = outro_recurso_periodo_factory.create(
        periodo_paa=paa.periodo_paa,
        ativo=True
    )
    
    # Cria outro recurso inativo (não deve ser registrado)
    outro_recurso3 = outro_recurso_periodo_factory.create(
        periodo_paa=paa.periodo_paa,
        ativo=False
    )
    
    quantidade = RegistrarAcoesOutrosRecursosConclusaoPaaService.registrar(paa)
    
    # Verifica que apenas os recursos disponíveis foram registrados
    assert quantidade == 2
    assert outro_recurso1 in paa.outros_recursos_periodo_conclusao.all()
    assert outro_recurso2 in paa.outros_recursos_periodo_conclusao.all()
    assert outro_recurso3 not in paa.outros_recursos_periodo_conclusao.all()


@pytest.mark.django_db
def test_registrar_acoes_outros_recursos_conclusao_paa_retorna_zero_quando_nao_ha_recursos(
    paa_factory, periodo_paa_1
):
    """Testa que retorna 0 quando não há outros recursos disponíveis"""
    paa = paa_factory.create(periodo_paa=periodo_paa_1)
    
    quantidade = RegistrarAcoesOutrosRecursosConclusaoPaaService.registrar(paa)
    
    assert quantidade == 0
    assert paa.outros_recursos_periodo_conclusao.count() == 0


@pytest.mark.django_db
def test_registrar_acoes_outros_recursos_conclusao_paa_nao_registra_recursos_de_outro_periodo(
    paa_factory, outro_recurso_periodo_factory, periodo_paa_factory, unidade_factory
):
    """Testa que não registra recursos de outro período"""
    periodo_paa_1 = periodo_paa_factory.create()
    periodo_paa_2 = periodo_paa_factory.create()
    
    paa = paa_factory.create(periodo_paa=periodo_paa_1)
    unidade = paa.associacao.unidade
    
    # Cria recurso do período correto
    outro_recurso1 = outro_recurso_periodo_factory.create(
        periodo_paa=periodo_paa_1,
        ativo=True
    )
    outro_recurso1.unidades.add(unidade)
    
    # Cria recurso de outro período (não deve ser registrado)
    outro_recurso2 = outro_recurso_periodo_factory.create(
        periodo_paa=periodo_paa_2,
        ativo=True
    )
    outro_recurso2.unidades.add(unidade)
    
    quantidade = RegistrarAcoesOutrosRecursosConclusaoPaaService.registrar(paa)
    
    # Verifica que apenas o recurso do período correto foi registrado
    assert quantidade == 1
    assert outro_recurso1 in paa.outros_recursos_periodo_conclusao.all()
    assert outro_recurso2 not in paa.outros_recursos_periodo_conclusao.all()
