import pytest

from sme_ptrf_apps.paa.services.acoes_paa_service import AcoesPaaService


@pytest.fixture
def acao_ptrf_exibir_paa(acao_factory):
    """Ação PTRF com recurso legado=True e exibir_paa=True."""
    return acao_factory.create(exibir_paa=True)


@pytest.fixture
def acao_ptrf_nao_exibir_paa(acao_factory):
    """Ação PTRF com recurso legado=True e exibir_paa=False."""
    return acao_factory.create(exibir_paa=False)


@pytest.fixture
def recurso_nao_legado(recurso_factory):
    """Recurso com legado=False."""
    return recurso_factory.create(legado=False, cor='#3982AC')


@pytest.fixture
def acao_recurso_nao_legado(acao_factory, recurso_nao_legado):
    """Ação com recurso legado=False e exibir_paa=True."""
    return acao_factory.create(exibir_paa=True, recurso=recurso_nao_legado)


@pytest.fixture
def acao_assoc_exibir_paa(acao_associacao_factory, paa, acao_ptrf_exibir_paa):
    """AcaoAssociacao da associação do PAA com acao exibir_paa=True e recurso legado."""
    return acao_associacao_factory.create(associacao=paa.associacao, acao=acao_ptrf_exibir_paa)


@pytest.fixture
def acao_assoc_nao_exibir_paa(acao_associacao_factory, paa, acao_ptrf_nao_exibir_paa):
    """AcaoAssociacao da associação do PAA com acao exibir_paa=False e recurso legado."""
    return acao_associacao_factory.create(associacao=paa.associacao, acao=acao_ptrf_nao_exibir_paa)


@pytest.fixture
def acao_assoc_recurso_nao_legado(acao_associacao_factory, paa, acao_recurso_nao_legado):
    """AcaoAssociacao da associação do PAA com acao cujo recurso não é legado."""
    return acao_associacao_factory.create(associacao=paa.associacao, acao=acao_recurso_nao_legado)


@pytest.fixture
def acao_assoc_outra_associacao(acao_associacao_factory, acao_ptrf_exibir_paa):
    """AcaoAssociacao de outra associação (não vinculada ao PAA)."""
    return acao_associacao_factory.create(acao=acao_ptrf_exibir_paa)


@pytest.mark.django_db
def test_retorna_acao_associacao_com_recurso_legado_e_exibir_paa_true(
        paa, acao_assoc_exibir_paa, acao_assoc_nao_exibir_paa):
    """Ação com recurso legado=True e exibir_paa=True deve ser retornada."""
    resultado = AcoesPaaService(paa).obter_ptrf()

    assert acao_assoc_exibir_paa in resultado
    assert acao_assoc_nao_exibir_paa not in resultado


@pytest.mark.django_db
def test_nao_retorna_acao_associacao_com_exibir_paa_false_fora_de_acoes_conclusao(
    paa, acao_assoc_nao_exibir_paa
):
    """Ação com exibir_paa=False que não está em acoes_conclusao não deve ser retornada."""
    resultado = AcoesPaaService(paa).obter_ptrf()

    assert acao_assoc_nao_exibir_paa not in resultado


@pytest.mark.django_db
def test_nao_retorna_acao_associacao_com_recurso_nao_legado(paa, acao_assoc_recurso_nao_legado):
    """Ação com recurso legado=False não deve ser retornada, mesmo com exibir_paa=True."""
    resultado = AcoesPaaService(paa).obter_ptrf()

    assert acao_assoc_recurso_nao_legado not in resultado


@pytest.mark.django_db
def test_retorna_acao_associacao_de_acoes_conclusao_mesmo_com_exibir_paa_false(
    paa, acao_assoc_nao_exibir_paa, flag_paa_retificacao
):
    """Com flag, ação em acoes_conclusao é retornada mesmo com exibir_paa=False."""
    paa.acoes_conclusao.add(acao_assoc_nao_exibir_paa.acao)

    resultado = AcoesPaaService(paa).obter_ptrf()

    assert acao_assoc_nao_exibir_paa in resultado


@pytest.mark.django_db
def test_nao_retorna_duplicatas_quando_acao_em_acoes_conclusao_e_exibir_paa_true(
    paa, acao_assoc_exibir_paa, flag_paa_retificacao
):
    """Com flag, ação em acoes_conclusao E com exibir_paa=True não deve aparecer duplicada."""
    paa.acoes_conclusao.add(acao_assoc_exibir_paa.acao)

    resultado = AcoesPaaService(paa).obter_ptrf()

    uuids = [aa.uuid for aa in resultado]
    assert len(uuids) == len(set(uuids))
    assert acao_assoc_exibir_paa in resultado


@pytest.mark.django_db
def test_retorna_queryset_vazio_sem_acoes_validas(paa):
    """Sem AcaoAssociacao elegíveis, o resultado deve ser vazio."""
    resultado = AcoesPaaService(paa).obter_ptrf()

    assert resultado.count() == 0


@pytest.mark.django_db
def test_nao_retorna_acoes_de_outra_associacao(paa, acao_assoc_outra_associacao):
    """Ações de outra associação não devem aparecer no resultado."""
    resultado = AcoesPaaService(paa).obter_ptrf()

    assert acao_assoc_outra_associacao not in resultado


# ---------------------------------------------------------------------------
# obter_pdde
# ---------------------------------------------------------------------------

@pytest.fixture
def acao_pdde_ativa(acao_pdde_factory):
    """AcaoPdde com status=ATIVA."""
    return acao_pdde_factory.create(status='ATIVA')


@pytest.fixture
def acao_pdde_inativa(acao_pdde_factory):
    """AcaoPdde com status=INATIVA."""
    return acao_pdde_factory.create(status='INATIVA')


@pytest.mark.django_db
def test_obter_pdde_retorna_acao_com_status_ativa(paa, acao_pdde_ativa):
    """AcaoPdde com status=ATIVA deve ser retornada."""
    resultado = AcoesPaaService(paa).obter_pdde()

    assert acao_pdde_ativa in resultado


@pytest.mark.django_db
def test_obter_pdde_nao_retorna_acao_inativa_fora_de_acoes_pdde_conclusao(
    paa, acao_pdde_inativa
):
    """AcaoPdde com status=INATIVA que não está em acoes_pdde_conclusao não deve ser retornada."""
    resultado = AcoesPaaService(paa).obter_pdde()

    assert acao_pdde_inativa not in resultado


@pytest.mark.django_db
def test_obter_pdde_retorna_acao_inativa_em_acoes_pdde_conclusao(paa, acao_pdde_inativa, flag_paa_retificacao):
    """Com flag, AcaoPdde em acoes_pdde_conclusao é retornada mesmo com status=INATIVA."""
    paa.acoes_pdde_conclusao.add(acao_pdde_inativa)

    resultado = AcoesPaaService(paa).obter_pdde()

    assert acao_pdde_inativa in resultado


@pytest.mark.django_db
def test_obter_pdde_nao_retorna_duplicatas(paa, acao_pdde_ativa):
    """AcaoPdde em acoes_pdde_conclusao E com status=ATIVA não deve aparecer duplicada."""
    paa.acoes_pdde_conclusao.add(acao_pdde_ativa)

    resultado = AcoesPaaService(paa).obter_pdde()

    uuids = [a.uuid for a in resultado]
    assert len(uuids) == len(set(uuids))
    assert acao_pdde_ativa in resultado


@pytest.mark.django_db
def test_obter_pdde_retorna_queryset_vazio_sem_acoes_validas(paa, acao_pdde_inativa):
    """Sem AcaoPdde elegíveis, o resultado deve ser vazio."""
    resultado = AcoesPaaService(paa).obter_pdde()

    assert resultado.count() == 0


# ---------------------------------------------------------------------------
# obter_outros_recursos_periodo
# ---------------------------------------------------------------------------

@pytest.fixture
def flag_paa_retificacao(flag_factory):
    """Flag 'paa-retificacao' ativa para todos."""
    return flag_factory.create(name='paa-retificacao', everyone=True)


@pytest.fixture
def outro_recurso_disponivel(outro_recurso_periodo_factory, paa):
    """OutroRecursoPeriodoPaa ativo, mesmo período, sem unidade vinculada (disponível para todos)."""
    return outro_recurso_periodo_factory.create(periodo_paa=paa.periodo_paa, ativo=True)


@pytest.fixture
def outro_recurso_disponivel_por_unidade(outro_recurso_periodo_factory, paa):
    """OutroRecursoPeriodoPaa ativo, mesmo período, vinculado à unidade da associação do PAA."""
    recurso = outro_recurso_periodo_factory.create(periodo_paa=paa.periodo_paa, ativo=True)
    recurso.unidades.add(paa.associacao.unidade)
    return recurso


@pytest.fixture
def outro_recurso_inativo(outro_recurso_periodo_factory, paa):
    """OutroRecursoPeriodoPaa inativo no mesmo período."""
    return outro_recurso_periodo_factory.create(periodo_paa=paa.periodo_paa, ativo=False)


@pytest.fixture
def outro_recurso_outro_periodo(outro_recurso_periodo_factory, periodo_paa_factory):
    """OutroRecursoPeriodoPaa ativo em outro período."""
    return outro_recurso_periodo_factory.create(periodo_paa=periodo_paa_factory.create(), ativo=True)


@pytest.mark.django_db
def test_obter_outros_recursos_periodo_sem_flag_retorna_disponiveis(
    paa, outro_recurso_disponivel
):
    """Sem flag, retorna recursos disponíveis via manager disponiveis_para_paa."""
    resultado = AcoesPaaService(paa).obter_outros_recursos_periodo()

    assert outro_recurso_disponivel in resultado


@pytest.mark.django_db
def test_obter_outros_recursos_periodo_sem_flag_retorna_recurso_vinculado_a_unidade(
    paa, outro_recurso_disponivel_por_unidade
):
    """Sem flag, retorna recursos vinculados à unidade da associação do PAA."""
    resultado = AcoesPaaService(paa).obter_outros_recursos_periodo()

    assert outro_recurso_disponivel_por_unidade in resultado


@pytest.mark.django_db
def test_obter_outros_recursos_periodo_sem_flag_nao_retorna_recurso_inativo(
    paa, outro_recurso_inativo
):
    """Sem flag, recursos inativos não são retornados, mesmo estando no período correto."""
    resultado = AcoesPaaService(paa).obter_outros_recursos_periodo()

    assert outro_recurso_inativo not in resultado


@pytest.mark.django_db
def test_obter_outros_recursos_periodo_sem_flag_nao_retorna_recursos_da_conclusao(
    paa, outro_recurso_inativo
):
    """Sem flag, recursos em outros_recursos_periodo_conclusao não são concatenados."""
    paa.outros_recursos_periodo_conclusao.add(outro_recurso_inativo)

    resultado = AcoesPaaService(paa).obter_outros_recursos_periodo()

    assert outro_recurso_inativo not in resultado


@pytest.mark.django_db
def test_obter_outros_recursos_periodo_com_flag_retorna_disponiveis(
    paa, outro_recurso_disponivel, flag_paa_retificacao
):
    """Com flag, ainda retorna os recursos disponíveis pelo manager."""
    resultado = AcoesPaaService(paa).obter_outros_recursos_periodo()

    assert outro_recurso_disponivel in resultado


@pytest.mark.django_db
def test_obter_outros_recursos_periodo_com_flag_retorna_recurso_da_conclusao_mesmo_inativo(
    paa, outro_recurso_inativo, flag_paa_retificacao
):
    """Com flag, recurso inativo em outros_recursos_periodo_conclusao é retornado."""
    paa.outros_recursos_periodo_conclusao.add(outro_recurso_inativo)

    resultado = AcoesPaaService(paa).obter_outros_recursos_periodo()

    assert outro_recurso_inativo in resultado


@pytest.mark.django_db
def test_obter_outros_recursos_periodo_com_flag_nao_retorna_duplicatas(
    paa, outro_recurso_disponivel, flag_paa_retificacao
):
    """Com flag, recurso em conclusao E disponível não aparece duplicado."""
    paa.outros_recursos_periodo_conclusao.add(outro_recurso_disponivel)

    resultado = AcoesPaaService(paa).obter_outros_recursos_periodo()

    uuids = [r.uuid for r in resultado]
    assert len(uuids) == len(set(uuids))
    assert outro_recurso_disponivel in resultado


@pytest.mark.django_db
def test_obter_outros_recursos_periodo_com_flag_nao_retorna_recurso_de_outro_periodo_sem_conclusao(
    paa, outro_recurso_outro_periodo, flag_paa_retificacao
):
    """Com flag, recurso de outro período que não está na conclusão não é retornado."""
    resultado = AcoesPaaService(paa).obter_outros_recursos_periodo()

    assert outro_recurso_outro_periodo not in resultado
