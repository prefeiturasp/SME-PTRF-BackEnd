import pytest
from datetime import date
from unittest.mock import patch
from sme_ptrf_apps.paa.services import (
    OutroRecursoPeriodoDesabilitacaoService,
    DesabilitacaoRecursoException
)
from sme_ptrf_apps.paa.fixtures.factories import PaaFactory


@pytest.fixture
def outros_recursos_periodo(periodo_paa_factory, outro_recurso_factory, outro_recurso_periodo_factory):
    periodo_paa = periodo_paa_factory.create(
        referencia='2000.10',
        data_inicial=date(2000, 1, 1),
        data_final=date(2000, 4, 30),
    )
    outro_recurso = outro_recurso_factory.create(nome='Teste 2000')
    return outro_recurso_periodo_factory.create(
        outro_recurso=outro_recurso,
        periodo_paa=periodo_paa,
        ativo=True
    )


@pytest.fixture
def service_desabilitacao(outros_recursos_periodo):
    """Fixture que retorna instância do service de desabilitação"""
    return OutroRecursoPeriodoDesabilitacaoService(outros_recursos_periodo)


@pytest.fixture
def paa_em_elaboracao(outros_recursos_periodo):
    """Fixture de PAA em elaboração"""
    return PaaFactory.create(
        status='EM_ELABORACAO',
        periodo_paa=outros_recursos_periodo.periodo_paa
    )


@pytest.fixture
def paa_gerado(outros_recursos_periodo):
    """Fixture de PAA gerado"""
    return PaaFactory.create(
        status='GERADO',
        periodo_paa=outros_recursos_periodo.periodo_paa
    )


@pytest.fixture
def paa_em_retificacao(outros_recursos_periodo):
    """Fixture de PAA em retificação"""
    return PaaFactory.create(
        status='EM_RETIFICACAO',
        periodo_paa=outros_recursos_periodo.periodo_paa
    )


@pytest.mark.django_db
def test_init_service_com_sucesso(outros_recursos_periodo):
    """Testa inicialização do service com sucesso"""
    service = OutroRecursoPeriodoDesabilitacaoService(outros_recursos_periodo)

    assert service.outro_recurso_periodo == outros_recursos_periodo
    assert isinstance(service, OutroRecursoPeriodoDesabilitacaoService)


@pytest.mark.django_db
def test_init_service_herda_base_service(outros_recursos_periodo):
    """Testa que service herda de OutroRecursoPeriodoBaseService"""
    from sme_ptrf_apps.paa.services import OutroRecursoPeriodoBaseService

    service = OutroRecursoPeriodoDesabilitacaoService(outros_recursos_periodo)

    assert isinstance(service, OutroRecursoPeriodoBaseService)


@pytest.mark.django_db
def test_aplica_regras_em_elaboracao_remove_receitas_e_prioridades(
    service_desabilitacao,
    paa_em_elaboracao,
):
    """Testa que regras em elaboração removem receitas e prioridades"""
    with patch.object(
            service_desabilitacao,
            '_remover_receitas_previstas_outro_recurso_periodo',
            return_value=3) as mock_receitas:
        with patch.object(
                service_desabilitacao,
                '_remover_prioridades_outro_recurso_periodo',
                return_value=2) as mock_prioridades:
            resultado = service_desabilitacao.aplica_regras_desabilitacao_em_elaboracao(paa_em_elaboracao)

            assert resultado['paa_uuid'] == str(paa_em_elaboracao.uuid)
            assert resultado['status'] == 'EM_ELABORACAO'
            assert resultado['receitas_previstas'] == 3
            assert resultado['prioridades_afetadas'] == 2
            assert 'removido' in resultado['acao'].lower()

            mock_receitas.assert_called_once_with(paa_em_elaboracao)
            mock_prioridades.assert_called_once_with(paa_em_elaboracao)


@pytest.mark.django_db
def test_aplica_regras_em_elaboracao_com_associacao(
    service_desabilitacao,
    paa_em_elaboracao,
):
    """Testa que associação é incluída no resultado"""
    with patch.object(service_desabilitacao, '_remover_receitas_previstas_outro_recurso_periodo', return_value=0):
        with patch.object(service_desabilitacao, '_remover_prioridades_outro_recurso_periodo', return_value=0):
            resultado = service_desabilitacao.aplica_regras_desabilitacao_em_elaboracao(paa_em_elaboracao)

            if paa_em_elaboracao.associacao:
                assert resultado['associacao'] == str(paa_em_elaboracao.associacao.unidade)
            else:
                assert resultado['associacao'] == 'N/A'


@pytest.mark.django_db
def test_aplica_regras_em_elaboracao_sem_receitas_removidas(
    service_desabilitacao,
    paa_em_elaboracao,
):
    """Testa quando não há receitas para remover"""
    with patch.object(service_desabilitacao, '_remover_receitas_previstas_outro_recurso_periodo', return_value=0):
        with patch.object(service_desabilitacao, '_remover_prioridades_outro_recurso_periodo', return_value=0):
            resultado = service_desabilitacao.aplica_regras_desabilitacao_em_elaboracao(paa_em_elaboracao)

            assert resultado['receitas_previstas'] == 0
            assert resultado['prioridades_afetadas'] == 0


@pytest.mark.django_db
def test_aplica_regras_gerado_mantem_receitas_e_prioridades(
    service_desabilitacao,
    paa_gerado,
):
    """Testa que regras para PAA gerado mantêm receitas e prioridades"""
    resultado = service_desabilitacao.aplica_regras_desabilitacao_gerado_retificacao(paa_gerado)

    assert resultado['paa_uuid'] == str(paa_gerado.uuid)
    assert resultado['status'] == 'GERADO'
    assert 'mantido' in resultado['acao'].lower()


@pytest.mark.django_db
def test_aplica_regras_retificacao_mantem_receitas_e_prioridades(
    service_desabilitacao,
    paa_em_retificacao,
):
    """Testa que regras para PAA em retificação mantêm receitas e prioridades"""
    resultado = service_desabilitacao.aplica_regras_desabilitacao_gerado_retificacao(paa_em_retificacao)

    assert resultado['paa_uuid'] == str(paa_em_retificacao.uuid)
    assert resultado['status'] == 'EM_RETIFICACAO'
    assert 'mantido' in resultado['acao'].lower()


@pytest.mark.django_db
def test_aplica_regras_gerado_com_associacao(
    service_desabilitacao,
    paa_gerado,
):
    """Testa que associação é incluída no resultado"""
    resultado = service_desabilitacao.aplica_regras_desabilitacao_gerado_retificacao(paa_gerado)

    if paa_gerado.associacao:
        assert resultado['associacao'] == str(paa_gerado.associacao.unidade)
    else:
        assert resultado['associacao'] == 'N/A'


@pytest.mark.django_db
def test_desabilitar_recurso_ja_desabilitado(
    service_desabilitacao,
):
    """Testa que não é possível desabilitar recurso já desabilitado"""
    service_desabilitacao.outro_recurso_periodo.ativo = False
    service_desabilitacao.outro_recurso_periodo.save()

    with pytest.raises(DesabilitacaoRecursoException) as excinfo:
        service_desabilitacao.desabilitar_outro_recurso_periodo()

    assert "já está desabilitado" in str(excinfo.value)


@pytest.mark.django_db
def test_desabilitar_recurso_com_sucesso_sem_paas(
    service_desabilitacao,
):
    """Testa desabilitação com sucesso quando não há PAAs afetados"""
    with patch.object(service_desabilitacao, '_obtem_paas_afetados', return_value=[]):
        resultado = service_desabilitacao.desabilitar_outro_recurso_periodo()

        assert resultado['sucesso'] is True
        assert resultado['mensagem'] == 'Recurso desabilitado com sucesso.'
        assert resultado['total_paas'] == 0
        assert len(resultado['paas_processados']) == 0

        service_desabilitacao.outro_recurso_periodo.refresh_from_db()
        assert service_desabilitacao.outro_recurso_periodo.ativo is False


@pytest.mark.django_db
def test_desabilitar_recurso_com_paas_em_elaboracao(
    service_desabilitacao,
    paa_em_elaboracao,
):
    """Testa desabilitação com PAAs em elaboração"""
    with patch.object(service_desabilitacao, '_obtem_paas_afetados', return_value=[paa_em_elaboracao]):
        with patch.object(service_desabilitacao, '_paa_em_elaboracao', return_value=True):
            with patch.object(service_desabilitacao, '_paa_gerado_retificado', return_value=False):
                with patch.object(service_desabilitacao, 'aplica_regras_desabilitacao_em_elaboracao') as mock_regras:
                    mock_regras.return_value = {
                        'paa_uuid': str(paa_em_elaboracao.uuid),
                        'acao': 'Recurso removido'
                    }

                    resultado = service_desabilitacao.desabilitar_outro_recurso_periodo()

                    assert resultado['sucesso'] is True
                    assert resultado['total_paas'] == 1
                    assert len(resultado['paas_processados']) == 1
                    mock_regras.assert_called_once_with(paa_em_elaboracao)


@pytest.mark.django_db
def test_desabilitar_recurso_com_paas_gerados(
    service_desabilitacao,
    paa_gerado,
):
    """Testa desabilitação com PAAs gerados"""
    with patch.object(service_desabilitacao, '_obtem_paas_afetados', return_value=[paa_gerado]):
        with patch.object(service_desabilitacao, '_paa_em_elaboracao', return_value=False):
            with patch.object(service_desabilitacao, '_paa_gerado_retificado', return_value=True):
                with patch.object(
                        service_desabilitacao,
                        'aplica_regras_desabilitacao_gerado_retificacao') as mock_regras:
                    mock_regras.return_value = {
                        'paa_uuid': str(paa_gerado.uuid),
                        'acao': 'Recurso mantido'
                    }

                    resultado = service_desabilitacao.desabilitar_outro_recurso_periodo()

                    assert resultado['sucesso'] is True
                    assert resultado['total_paas'] == 1
                    mock_regras.assert_called_once_with(paa_gerado)


@pytest.mark.django_db
def test_desabilitar_recurso_com_paas_mistos(
    service_desabilitacao,
    paa_em_elaboracao,
    paa_gerado,
):
    """Testa desabilitação com PAAs em diferentes status"""
    paas = [paa_em_elaboracao, paa_gerado]

    with patch.object(service_desabilitacao, '_obtem_paas_afetados', return_value=paas):
        def paa_em_elaboracao_side_effect(paa):
            return paa == paa_em_elaboracao

        def paa_gerado_side_effect(paa):
            return paa == paa_gerado

        with patch.object(service_desabilitacao, '_paa_em_elaboracao', side_effect=paa_em_elaboracao_side_effect):
            with patch.object(service_desabilitacao, '_paa_gerado_retificado', side_effect=paa_gerado_side_effect):
                with patch.object(
                        service_desabilitacao, 'aplica_regras_desabilitacao_em_elaboracao') as mock_elaboracao:
                    with patch.object(
                            service_desabilitacao,
                            'aplica_regras_desabilitacao_gerado_retificacao') as mock_gerado:
                        mock_elaboracao.return_value = {'paa_uuid': str(paa_em_elaboracao.uuid)}
                        mock_gerado.return_value = {'paa_uuid': str(paa_gerado.uuid)}

                        resultado = service_desabilitacao.desabilitar_outro_recurso_periodo()

                        assert resultado['sucesso'] is True
                        assert resultado['total_paas'] == 2
                        assert len(resultado['paas_processados']) == 2
                        mock_elaboracao.assert_called_once()
                        mock_gerado.assert_called_once()


@pytest.mark.django_db
def test_desabilitar_recurso_status_nao_tratado(
    service_desabilitacao,
    paa_em_elaboracao,
):
    """Testa comportamento com status de PAA não tratado"""
    paa_em_elaboracao.status = 'STATUS_DESCONHECIDO'

    with patch.object(service_desabilitacao, '_obtem_paas_afetados', return_value=[paa_em_elaboracao]):
        with patch.object(service_desabilitacao, '_paa_em_elaboracao', return_value=False):
            with patch.object(service_desabilitacao, '_paa_gerado_retificado', return_value=False):
                resultado = service_desabilitacao.desabilitar_outro_recurso_periodo()

                assert resultado['sucesso'] is True
                assert resultado['total_paas'] == 1
                assert 'Status não tratado' in resultado['paas_processados'][0]['acao']


@pytest.mark.django_db
def test_desabilitar_recurso_erro_ao_processar(
    service_desabilitacao,
    paa_em_elaboracao,
):
    """Testa que exceção é levantada em caso de erro"""
    with patch.object(service_desabilitacao, '_obtem_paas_afetados', return_value=[paa_em_elaboracao]):
        with patch.object(service_desabilitacao, '_paa_em_elaboracao', side_effect=Exception("Erro de banco")):
            with pytest.raises(DesabilitacaoRecursoException) as excinfo:
                service_desabilitacao.desabilitar_outro_recurso_periodo()

            assert "Erro ao desabilitar recurso" in str(excinfo.value)


@pytest.mark.django_db
def test_desabilitar_recurso_transacao_atomica(
    service_desabilitacao,
    paa_em_elaboracao,
):
    """Testa que operação é realizada em transação atômica"""
    with patch.object(service_desabilitacao, '_obtem_paas_afetados', return_value=[paa_em_elaboracao]):
        with patch.object(service_desabilitacao, '_paa_em_elaboracao', return_value=True):
            with patch.object(service_desabilitacao, 'aplica_regras_desabilitacao_em_elaboracao') as mock_regras:
                mock_regras.side_effect = Exception("Erro durante processamento")

                with pytest.raises(DesabilitacaoRecursoException):
                    service_desabilitacao.desabilitar_outro_recurso_periodo()

                # Verifica que recurso não foi desabilitado (rollback)
                service_desabilitacao.outro_recurso_periodo.refresh_from_db()
                assert service_desabilitacao.outro_recurso_periodo.ativo is True


@pytest.mark.django_db
def test_desabilitar_recurso_resultado_completo(
    service_desabilitacao,
):
    """Testa que resultado contém todas as informações esperadas"""
    with patch.object(service_desabilitacao, '_obtem_paas_afetados', return_value=[]):
        resultado = service_desabilitacao.desabilitar_outro_recurso_periodo()

        assert 'sucesso' in resultado
        assert 'mensagem' in resultado
        assert 'recurso' in resultado
        assert 'periodo' in resultado
        assert 'total_paas' in resultado
        assert 'paas_processados' in resultado


@pytest.mark.django_db
def test_obter_informacoes_sem_paas(
    service_desabilitacao,
):
    """Testa obtenção de informações quando não há PAAs"""
    with patch.object(service_desabilitacao, '_obtem_paas_afetados', return_value=[]):
        resultado = service_desabilitacao.obter_informacoes_para_confirmacao()

        assert resultado['total_paas'] == 0
        assert resultado['paas_em_elaboracao'] == 0
        assert resultado['paas_gerados_ou_retificacao'] == 0
        assert len(resultado['detalhes']['em_elaboracao']) == 0
        assert len(resultado['detalhes']['gerados_ou_retificacao']) == 0


@pytest.mark.django_db
def test_obter_informacoes_com_paas_em_elaboracao(
    service_desabilitacao,
    paa_em_elaboracao,
):
    """Testa obtenção de informações com PAAs em elaboração"""
    with patch.object(service_desabilitacao, '_obtem_paas_afetados', return_value=[paa_em_elaboracao]):
        with patch.object(service_desabilitacao, '_paa_em_elaboracao', return_value=True):
            with patch.object(service_desabilitacao, '_paa_gerado_retificado', return_value=False):
                with patch.object(
                        service_desabilitacao,
                        '_receitas_previstas_outro_recurso_periodo_afetadas', return_value=[1, 2]):
                    with patch.object(service_desabilitacao, '_prioridades_afetadas', return_value=[1]):
                        resultado = service_desabilitacao.obter_informacoes_para_confirmacao()

                        assert resultado['total_paas'] == 1
                        assert resultado['paas_em_elaboracao'] == 1
                        assert resultado['paas_gerados_ou_retificacao'] == 0
                        assert len(resultado['detalhes']['em_elaboracao']) == 1
                        assert resultado['detalhes']['em_elaboracao'][0]['receitas_previstas'] == 2
                        assert resultado['detalhes']['em_elaboracao'][0]['prioridades'] == 1


@pytest.mark.django_db
def test_obter_informacoes_com_paas_gerados(
    service_desabilitacao,
    paa_gerado,
):
    """Testa obtenção de informações com PAAs gerados"""
    with patch.object(service_desabilitacao, '_obtem_paas_afetados', return_value=[paa_gerado]):
        with patch.object(service_desabilitacao, '_paa_em_elaboracao', return_value=False):
            with patch.object(service_desabilitacao, '_paa_gerado_retificado', return_value=True):
                with patch.object(
                        service_desabilitacao,
                        '_receitas_previstas_outro_recurso_periodo_afetadas', return_value=[1, 2, 3]):
                    with patch.object(service_desabilitacao, '_prioridades_afetadas', return_value=[1, 2]):
                        resultado = service_desabilitacao.obter_informacoes_para_confirmacao()

                        assert resultado['total_paas'] == 1
                        assert resultado['paas_em_elaboracao'] == 0
                        assert resultado['paas_gerados_ou_retificacao'] == 1
                        assert len(resultado['detalhes']['gerados_ou_retificacao']) == 1
                        assert resultado['detalhes']['gerados_ou_retificacao'][0]['receitas_previstas'] == 3
                        assert resultado['detalhes']['gerados_ou_retificacao'][0]['prioridades'] == 2


@pytest.mark.django_db
def test_obter_informacoes_com_paas_mistos(
    service_desabilitacao,
    paa_em_elaboracao,
    paa_gerado,
):
    """Testa obtenção de informações com PAAs em diferentes status"""
    paas = [paa_em_elaboracao, paa_gerado]

    with patch.object(service_desabilitacao, '_obtem_paas_afetados', return_value=paas):
        def paa_em_elaboracao_side_effect(paa):
            return paa == paa_em_elaboracao

        def paa_gerado_side_effect(paa):
            return paa == paa_gerado

        with patch.object(service_desabilitacao, '_paa_em_elaboracao', side_effect=paa_em_elaboracao_side_effect):
            with patch.object(service_desabilitacao, '_paa_gerado_retificado', side_effect=paa_gerado_side_effect):
                with patch.object(
                        service_desabilitacao, '_receitas_previstas_outro_recurso_periodo_afetadas', return_value=[1]):
                    with patch.object(service_desabilitacao, '_prioridades_afetadas', return_value=[1]):
                        resultado = service_desabilitacao.obter_informacoes_para_confirmacao()

                        assert resultado['total_paas'] == 2
                        assert resultado['paas_em_elaboracao'] == 1
                        assert resultado['paas_gerados_ou_retificacao'] == 1
                        assert len(resultado['detalhes']['em_elaboracao']) == 1
                        assert len(resultado['detalhes']['gerados_ou_retificacao']) == 1


@pytest.mark.django_db
def test_obter_informacoes_estrutura_completa(
    service_desabilitacao,
):
    """Testa que estrutura de retorno está completa"""
    with patch.object(service_desabilitacao, '_obtem_paas_afetados', return_value=[]):
        resultado = service_desabilitacao.obter_informacoes_para_confirmacao()

        assert 'recurso' in resultado
        assert 'periodo' in resultado
        assert 'total_paas' in resultado
        assert 'paas_em_elaboracao' in resultado
        assert 'paas_gerados_ou_retificacao' in resultado
        assert 'detalhes' in resultado
        assert 'em_elaboracao' in resultado['detalhes']
        assert 'gerados_ou_retificacao' in resultado['detalhes']
