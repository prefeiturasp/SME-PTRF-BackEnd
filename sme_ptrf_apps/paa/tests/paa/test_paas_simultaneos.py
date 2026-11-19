"""PAA vigente e PAA da Próxima Vigência elaborados ao mesmo tempo, sem exigir o PAA vigente gerado."""
import json
from datetime import date

import pytest
from freezegun import freeze_time
from rest_framework import status

from sme_ptrf_apps.paa import constantes
from sme_ptrf_apps.paa.enums import PaaStatusAndamentoEnum
from sme_ptrf_apps.paa.models import AtaPaa, DocumentoPaa, Paa, PrioridadePaa
from sme_ptrf_apps.paa.services.elaboracao_paa_service import (
    ElaboracaoPaaService, PeriodoInvalidoParaElaboracaoException)

pytestmark = pytest.mark.django_db

HOJE = date(2026, 10, 28)


@pytest.fixture(autouse=True)
def parametro_outubro(parametro_paa_factory):
    return parametro_paa_factory.create(mes_elaboracao_paa=10)


@pytest.fixture
def periodo_vigente(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2026', data_inicial=date(2026, 5, 1), data_final=date(2027, 4, 30))


@pytest.fixture
def periodo_proxima_vigencia(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2027', data_inicial=date(2027, 8, 1), data_final=date(2027, 12, 31))


@pytest.fixture
def periodo_antigo(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2025', data_inicial=date(2025, 5, 1), data_final=date(2026, 4, 30))


def _gera_plano(documento_paa_factory, paa):
    documento_paa_factory.create(
        paa=paa, versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO, retificacao=False)


def _gera_ata(ata_paa_factory, paa):
    ata_paa_factory.create(paa=paa, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)
    paa.set_paa_status_gerado()


def _post(cliente, associacao, periodo):
    payload = {'associacao': str(associacao.uuid), 'periodo': str(periodo.uuid)}
    return cliente.post('/api/paa/', content_type='application/json', data=json.dumps(payload))


def _valida(associacao, periodo, habilitada=True):
    ElaboracaoPaaService.validar_periodo_para_criacao(associacao, periodo, habilitada, hoje=HOJE)


class TestCriacaoSimultanea:

    def test_proxima_vigencia_com_vigente_em_elaboracao_e_permitida_por_padrao(
            self, paa_factory, associacao, periodo_vigente, periodo_proxima_vigencia):
        paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao)

        _valida(associacao, periodo_proxima_vigencia)

    def test_proxima_vigencia_sem_paa_no_vigente_e_permitida_por_padrao(
            self, associacao, periodo_vigente, periodo_proxima_vigencia):
        _valida(associacao, periodo_proxima_vigencia)

    def test_exigencia_parametrizada_recusa_vigente_em_elaboracao(
            self, monkeypatch, paa_factory, associacao, periodo_vigente, periodo_proxima_vigencia):
        monkeypatch.setattr(
            constantes, 'STATUS_VIGENTE_EXIGIDOS_PARA_INICIAR_PROXIMA_VIGENCIA', ('GERADO_PARCIALMENTE', 'GERADO'))
        paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao)

        with pytest.raises(PeriodoInvalidoParaElaboracaoException, match='situação exigida'):
            _valida(associacao, periodo_proxima_vigencia)

    def test_exigencia_parametrizada_recusa_vigente_sem_paa(
            self, monkeypatch, associacao, periodo_vigente, periodo_proxima_vigencia):
        monkeypatch.setattr(
            constantes, 'STATUS_VIGENTE_EXIGIDOS_PARA_INICIAR_PROXIMA_VIGENCIA', ('GERADO',))

        with pytest.raises(PeriodoInvalidoParaElaboracaoException, match='ainda não foi iniciado'):
            _valida(associacao, periodo_proxima_vigencia)

    def test_exigencia_parametrizada_recusa_quando_nao_ha_periodo_vigente(self, monkeypatch, associacao):
        monkeypatch.setattr(
            constantes, 'STATUS_VIGENTE_EXIGIDOS_PARA_INICIAR_PROXIMA_VIGENCIA', ('GERADO',))

        with pytest.raises(PeriodoInvalidoParaElaboracaoException, match='ainda não foi iniciado'):
            ElaboracaoPaaService._validar_situacao_exigida_do_paa_vigente(associacao, None)

    def test_sem_exigencia_nao_recusa_quando_nao_ha_periodo_vigente(self, monkeypatch, associacao):
        monkeypatch.setattr(
            constantes, 'STATUS_VIGENTE_EXIGIDOS_PARA_INICIAR_PROXIMA_VIGENCIA', None)

        ElaboracaoPaaService._validar_situacao_exigida_do_paa_vigente(associacao, None)

    def test_exigencia_com_todos_os_status_basta_o_vigente_existir(
            self, monkeypatch, paa_factory, associacao, periodo_vigente, periodo_proxima_vigencia):
        monkeypatch.setattr(
            constantes, 'STATUS_VIGENTE_EXIGIDOS_PARA_INICIAR_PROXIMA_VIGENCIA',
            tuple(status_andamento.name for status_andamento in PaaStatusAndamentoEnum))
        paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao)

        _valida(associacao, periodo_proxima_vigencia)

    def test_exigencia_com_varios_status_aceita_qualquer_um_deles(
            self, monkeypatch, paa_factory, associacao, periodo_vigente, periodo_proxima_vigencia):
        monkeypatch.setattr(
            constantes, 'STATUS_VIGENTE_EXIGIDOS_PARA_INICIAR_PROXIMA_VIGENCIA', ('EM_ELABORACAO', 'GERADO'))
        paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao)

        _valida(associacao, periodo_proxima_vigencia)

    def test_exigencia_parametrizada_aceita_vigente_gerado_parcialmente(
            self, monkeypatch, paa_factory, documento_paa_factory, associacao,
            periodo_vigente, periodo_proxima_vigencia):
        monkeypatch.setattr(
            constantes, 'STATUS_VIGENTE_EXIGIDOS_PARA_INICIAR_PROXIMA_VIGENCIA', ('GERADO_PARCIALMENTE',))
        paa = paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao)
        documento_paa_factory.create(
            paa=paa, versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO, retificacao=False)

        _valida(associacao, periodo_proxima_vigencia)

    @freeze_time('2026-10-28')
    def test_api_cria_os_dois_paas_em_sequencia(
            self, jwt_authenticated_client_sme, flag_paa, flag_paa_proxima_vigencia, associacao,
            periodo_vigente, periodo_proxima_vigencia):
        primeiro = _post(jwt_authenticated_client_sme, associacao, periodo_vigente)
        segundo = _post(jwt_authenticated_client_sme, associacao, periodo_proxima_vigencia)

        assert primeiro.status_code == status.HTTP_201_CREATED, primeiro.content
        assert segundo.status_code == status.HTTP_201_CREATED, segundo.content
        assert set(Paa.objects.values_list('periodo_paa__referencia', flat=True)) == {'2026', '2027'}
        assert {p.get_status_andamento() for p in Paa.objects.all()} == {'EM_ELABORACAO'}

    @freeze_time('2026-10-28')
    def test_api_cria_a_proxima_vigencia_antes_do_vigente(
            self, jwt_authenticated_client_sme, flag_paa, flag_paa_proxima_vigencia, associacao,
            periodo_vigente, periodo_proxima_vigencia):
        segundo = _post(jwt_authenticated_client_sme, associacao, periodo_proxima_vigencia)
        primeiro = _post(jwt_authenticated_client_sme, associacao, periodo_vigente)

        assert segundo.status_code == status.HTTP_201_CREATED, segundo.content
        assert primeiro.status_code == status.HTTP_201_CREATED, primeiro.content

    @freeze_time('2026-10-28')
    def test_api_recusa_a_proxima_vigencia_duplicada(
            self, jwt_authenticated_client_sme, flag_paa, flag_paa_proxima_vigencia, associacao,
            periodo_vigente, periodo_proxima_vigencia):
        _post(jwt_authenticated_client_sme, associacao, periodo_proxima_vigencia)

        response = _post(jwt_authenticated_client_sme, associacao, periodo_proxima_vigencia)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Paa.objects.count() == 1


class TestAcessoPorUuid:
    """Sem um PAA "único em elaboração", cada tela precisa abrir o PAA pelo uuid."""

    def test_cada_paa_e_recuperado_pelo_proprio_uuid(
            self, jwt_authenticated_client_sme, flag_paa, paa_factory, associacao,
            periodo_vigente, periodo_proxima_vigencia):
        vigente = paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao, texto_introducao='V')
        proxima = paa_factory.create(periodo_paa=periodo_proxima_vigencia, associacao=associacao, texto_introducao='P')

        corpo_vigente = jwt_authenticated_client_sme.get(f'/api/paa/{vigente.uuid}/').json()
        corpo_proxima = jwt_authenticated_client_sme.get(f'/api/paa/{proxima.uuid}/').json()

        assert (corpo_vigente['uuid'], corpo_vigente['texto_introducao']) == (str(vigente.uuid), 'V')
        assert (corpo_proxima['uuid'], corpo_proxima['texto_introducao']) == (str(proxima.uuid), 'P')

    @freeze_time('2026-10-28')
    def test_paa_vigente_do_fluxo_antigo_ignora_a_proxima_vigencia(
            self, jwt_authenticated_client_sme, flag_paa, paa_factory, associacao,
            periodo_vigente, periodo_proxima_vigencia):
        """O endpoint legado devolve sempre o vigente: telas que ainda o usam exibem o PAA errado."""
        vigente = paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao)
        paa_factory.create(periodo_paa=periodo_proxima_vigencia, associacao=associacao)

        corpo = jwt_authenticated_client_sme.get(f'/api/associacoes/{associacao.uuid}/paa-vigente/').json()

        assert corpo['uuid'] == str(vigente.uuid)

    @freeze_time('2026-10-28')
    def test_paa_vigente_do_fluxo_antigo_responde_404_se_so_a_proxima_vigencia_existe(
            self, jwt_authenticated_client_sme, flag_paa, paa_factory, associacao,
            periodo_vigente, periodo_proxima_vigencia):
        """Quem elabora apenas a Próxima Vigência não tem PAA vigente: telas legadas quebram com 404."""
        paa_factory.create(periodo_paa=periodo_proxima_vigencia, associacao=associacao)

        response = jwt_authenticated_client_sme.get(f'/api/associacoes/{associacao.uuid}/paa-vigente/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestIndependenciaDeDados:

    def test_prioridades_dos_dois_paas_nao_se_misturam_no_relatorio(
            self, jwt_authenticated_client_sme, flag_paa, paa_factory, prioridade_paa_factory, associacao,
            periodo_vigente, periodo_proxima_vigencia):
        vigente = paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao)
        proxima = paa_factory.create(periodo_paa=periodo_proxima_vigencia, associacao=associacao)
        prioridade_paa_factory.create_batch(2, paa=vigente)
        prioridade_paa_factory.create(paa=proxima)

        resposta_vigente = jwt_authenticated_client_sme.get(
            '/api/prioridades-paa/', {'paa__uuid': vigente.uuid}).json()
        resposta_proxima = jwt_authenticated_client_sme.get(
            '/api/prioridades-paa/', {'paa__uuid': proxima.uuid}).json()

        assert PrioridadePaa.objects.count() == 3
        assert resposta_vigente['count'] == 2
        assert resposta_proxima['count'] == 1

    def test_importar_prioridades_do_vigente_em_elaboracao_para_a_proxima_vigencia(
            self, monkeypatch, jwt_authenticated_client_sme, flag_paa, paa_factory, prioridade_paa_factory,
            associacao, periodo_vigente, periodo_proxima_vigencia):
        """Sem exigência parametrizada, o backend permite importar de um PAA anterior ainda em elaboração."""
        monkeypatch.setattr(constantes, 'STATUS_PAA_ORIGEM_EXIGIDOS_PARA_IMPORTAR_PRIORIDADES', None)
        vigente = paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao)
        proxima = paa_factory.create(periodo_paa=periodo_proxima_vigencia, associacao=associacao)
        prioridade_paa_factory.create(paa=vigente, prioridade=True)

        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{proxima.uuid}/importar-prioridades/{vigente.uuid}/')

        assert response.status_code == status.HTTP_200_OK, response.content
        assert proxima.prioridadepaa_set.count() == 1

    def test_exigencia_parametrizada_recusa_importar_de_paa_em_elaboracao(
            self, monkeypatch, jwt_authenticated_client_sme, flag_paa, paa_factory, prioridade_paa_factory,
            associacao, periodo_vigente, periodo_proxima_vigencia):
        monkeypatch.setattr(
            constantes, 'STATUS_PAA_ORIGEM_EXIGIDOS_PARA_IMPORTAR_PRIORIDADES', ('GERADO_PARCIALMENTE', 'GERADO'))
        vigente = paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao)
        proxima = paa_factory.create(periodo_paa=periodo_proxima_vigencia, associacao=associacao)
        prioridade_paa_factory.create(paa=vigente, prioridade=True)

        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{proxima.uuid}/importar-prioridades/{vigente.uuid}/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            'Só é possível importar prioridades de PAA com '
            'situação andamento:') in response.json()['mensagem']
        assert proxima.prioridadepaa_set.count() == 0

    def test_paas_anteriores_da_proxima_vigencia_listam_o_vigente_em_elaboracao(
            self, monkeypatch, jwt_authenticated_client_sme, flag_paa, paa_factory, associacao,
            periodo_vigente, periodo_proxima_vigencia):
        monkeypatch.setattr(constantes, 'STATUS_PAA_ORIGEM_EXIGIDOS_PARA_IMPORTAR_PRIORIDADES', None)
        vigente = paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao)
        proxima = paa_factory.create(periodo_paa=periodo_proxima_vigencia, associacao=associacao)

        corpo = jwt_authenticated_client_sme.get(f'/api/paa/{proxima.uuid}/paas-anteriores/').json()

        assert [item['uuid'] for item in corpo] == [str(vigente.uuid)]


class TestPaasAnterioresParaImportacao:
    """A lista de PAAs de origem respeita `STATUS_PAA_ORIGEM_EXIGIDOS_PARA_IMPORTAR_PRIORIDADES`."""

    @pytest.fixture
    def paas(self, paa_factory, documento_paa_factory, ata_paa_factory, associacao,
             periodo_antigo, periodo_vigente, periodo_proxima_vigencia):
        """Antigo `GERADO`, vigente com Plano gerado e ata pendente (`GERADO_PARCIALMENTE`) e a Próxima Vigência."""
        antigo = paa_factory.create(periodo_paa=periodo_antigo, associacao=associacao)
        _gera_plano(documento_paa_factory, antigo)
        _gera_ata(ata_paa_factory, antigo)

        vigente = paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao)
        _gera_plano(documento_paa_factory, vigente)

        proxima = paa_factory.create(periodo_paa=periodo_proxima_vigencia, associacao=associacao)
        return {'antigo': antigo, 'vigente': vigente, 'proxima': proxima}

    @staticmethod
    def _uuids_listados(cliente, paa):
        resposta = cliente.get(f'/api/paa/{paa.uuid}/paas-anteriores/')
        assert resposta.status_code == status.HTTP_200_OK, resposta.content
        return [item['uuid'] for item in resposta.json()]

    def test_sem_exigencia_lista_todos_os_anteriores_do_mais_recente_ao_mais_antigo(
            self, monkeypatch, jwt_authenticated_client_sme, flag_paa, paas):
        monkeypatch.setattr(constantes, 'STATUS_PAA_ORIGEM_EXIGIDOS_PARA_IMPORTAR_PRIORIDADES', None)

        uuids = self._uuids_listados(jwt_authenticated_client_sme, paas['proxima'])

        assert uuids == [str(paas['vigente'].uuid), str(paas['antigo'].uuid)]

    def test_sem_exigencia_lista_tambem_o_paa_em_elaboracao(
            self, monkeypatch, jwt_authenticated_client_sme, flag_paa, paa_factory, associacao, paas,
            periodo_paa_factory):
        monkeypatch.setattr(constantes, 'STATUS_PAA_ORIGEM_EXIGIDOS_PARA_IMPORTAR_PRIORIDADES', None)
        periodo_intermediario = periodo_paa_factory.create(
            referencia='2026-2', data_inicial=date(2027, 5, 1), data_final=date(2027, 7, 31))
        em_elaboracao = paa_factory.create(periodo_paa=periodo_intermediario, associacao=associacao)

        uuids = self._uuids_listados(jwt_authenticated_client_sme, paas['proxima'])

        assert str(em_elaboracao.uuid) in uuids

    def test_padrao_atual_exige_paa_gerado(self, jwt_authenticated_client_sme, flag_paa, paas):
        """Garante o valor padrão da constante: muda junto com a decisão do PO."""
        assert constantes.STATUS_PAA_ORIGEM_EXIGIDOS_PARA_IMPORTAR_PRIORIDADES == ('GERADO',)

        uuids = self._uuids_listados(jwt_authenticated_client_sme, paas['proxima'])

        assert uuids == [str(paas['antigo'].uuid)]

    def test_exigindo_gerado_lista_so_os_gerados(
            self, monkeypatch, jwt_authenticated_client_sme, flag_paa, paas):
        monkeypatch.setattr(constantes, 'STATUS_PAA_ORIGEM_EXIGIDOS_PARA_IMPORTAR_PRIORIDADES', ('GERADO',))

        uuids = self._uuids_listados(jwt_authenticated_client_sme, paas['proxima'])

        assert uuids == [str(paas['antigo'].uuid)]

    def test_exigindo_varias_situacoes_lista_as_que_se_enquadram(
            self, monkeypatch, jwt_authenticated_client_sme, flag_paa, paas):
        monkeypatch.setattr(
            constantes, 'STATUS_PAA_ORIGEM_EXIGIDOS_PARA_IMPORTAR_PRIORIDADES', ('GERADO_PARCIALMENTE', 'GERADO'))

        uuids = self._uuids_listados(jwt_authenticated_client_sme, paas['proxima'])

        assert uuids == [str(paas['vigente'].uuid), str(paas['antigo'].uuid)]

    def test_exigindo_situacao_que_nenhum_atende_devolve_lista_vazia(
            self, monkeypatch, jwt_authenticated_client_sme, flag_paa, paas):
        monkeypatch.setattr(constantes, 'STATUS_PAA_ORIGEM_EXIGIDOS_PARA_IMPORTAR_PRIORIDADES', ('EM_RETIFICACAO',))

        assert self._uuids_listados(jwt_authenticated_client_sme, paas['proxima']) == []

    def test_a_exigencia_nao_afeta_paas_de_outra_associacao(
            self, monkeypatch, jwt_authenticated_client_sme, flag_paa, paa_factory, documento_paa_factory,
            ata_paa_factory, associacao_factory, periodo_antigo, paas):
        monkeypatch.setattr(constantes, 'STATUS_PAA_ORIGEM_EXIGIDOS_PARA_IMPORTAR_PRIORIDADES', ('GERADO',))
        de_outra = paa_factory.create(periodo_paa=periodo_antigo, associacao=associacao_factory.create())
        _gera_plano(documento_paa_factory, de_outra)
        _gera_ata(ata_paa_factory, de_outra)

        uuids = self._uuids_listados(jwt_authenticated_client_sme, paas['proxima'])

        assert str(de_outra.uuid) not in uuids

    def test_nao_lista_o_proprio_paa_nem_os_posteriores(
            self, monkeypatch, jwt_authenticated_client_sme, flag_paa, paas):
        monkeypatch.setattr(
            constantes, 'STATUS_PAA_ORIGEM_EXIGIDOS_PARA_IMPORTAR_PRIORIDADES', ('GERADO_PARCIALMENTE', 'GERADO'))

        uuids = self._uuids_listados(jwt_authenticated_client_sme, paas['vigente'])

        assert uuids == [str(paas['antigo'].uuid)]

    def test_o_que_a_lista_oferece_a_importacao_aceita_e_o_que_ela_omite_e_recusado(
            self, monkeypatch, jwt_authenticated_client_sme, flag_paa, prioridade_paa_factory, paas):
        monkeypatch.setattr(constantes, 'STATUS_PAA_ORIGEM_EXIGIDOS_PARA_IMPORTAR_PRIORIDADES', ('GERADO',))
        for origem in (paas['antigo'], paas['vigente']):
            prioridade_paa_factory.create(paa=origem, prioridade=True)
        listados = self._uuids_listados(jwt_authenticated_client_sme, paas['proxima'])

        aceita = jwt_authenticated_client_sme.post(
            f'/api/paa/{paas["proxima"].uuid}/importar-prioridades/{paas["antigo"].uuid}/')
        recusada = jwt_authenticated_client_sme.post(
            f'/api/paa/{paas["proxima"].uuid}/importar-prioridades/{paas["vigente"].uuid}/')

        assert listados == [str(paas['antigo'].uuid)]
        assert aceita.status_code == status.HTTP_200_OK, aceita.content
        assert recusada.status_code == status.HTTP_400_BAD_REQUEST


class TestListagemSemPeriodoVigente:

    @freeze_time('2026-10-28')
    def test_responde_404_e_esconde_o_paa_da_proxima_vigencia_ja_gerado(
            self, jwt_authenticated_client_sme, flag_paa, paa_factory, documento_paa_factory, associacao,
            periodo_paa_factory):
        """Lacuna conhecida: sem período vigente a listagem inteira responde 404."""
        futuro = periodo_paa_factory.create(
            referencia='2027', data_inicial=date(2027, 8, 1), data_final=date(2027, 12, 31))
        paa = paa_factory.create(periodo_paa=futuro, associacao=associacao)
        documento_paa_factory.create(
            paa=paa, versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO, retificacao=False)

        response = jwt_authenticated_client_sme.get(
            '/api/paa/paa-vigente-e-anteriores/', {'associacao_uuid': associacao.uuid})

        assert response.status_code == status.HTTP_404_NOT_FOUND
