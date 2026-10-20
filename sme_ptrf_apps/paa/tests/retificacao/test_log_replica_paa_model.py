import pytest
from sme_ptrf_apps.paa.models import LogReplicaPaa

pytestmark = pytest.mark.django_db


@pytest.fixture
def log_replica(paa_retificacao):
    return LogReplicaPaa.objects.create(
        paa=paa_retificacao,
        origem=LogReplicaPaa.CANCELAMENTO,
        numero_versao_documento=1,
        replica={'texto_introducao': 'Intro', 'objetivos': []}
    )


class TestLogReplicaPaaModel:

    def test_criacao_log_replica(self, paa_retificacao):
        log = LogReplicaPaa.objects.create(
            paa=paa_retificacao,
            origem=LogReplicaPaa.CANCELAMENTO,
            replica={'texto': 'snapshot'}
        )
        assert log.id is not None
        assert log.paa == paa_retificacao
        assert log.origem == LogReplicaPaa.CANCELAMENTO
        assert log.replica == {'texto': 'snapshot'}

    def test_origem_default_e_cancelamento(self, paa_retificacao):
        log = LogReplicaPaa.objects.create(paa=paa_retificacao, replica={})
        assert log.origem == LogReplicaPaa.CANCELAMENTO

    def test_str_retorna_formato_correto(self, log_replica, paa_retificacao):
        expected = "Log Réplica do PAA %s (%s) originado por %s" % (
            paa_retificacao.periodo_paa.referencia,
            paa_retificacao.associacao,
            LogReplicaPaa.CANCELAMENTO,
        )
        assert str(log_replica) == expected

    def test_str_com_origem_conclusao(self, paa_retificacao):
        log = LogReplicaPaa.objects.create(
            paa=paa_retificacao,
            origem=LogReplicaPaa.CONCLUSAO,
            replica={}
        )
        assert LogReplicaPaa.CONCLUSAO in str(log)

    def test_origem_nomes_disponiveis(self):
        assert LogReplicaPaa.CANCELAMENTO in LogReplicaPaa.ORIGEM_NOMES
        assert LogReplicaPaa.CONCLUSAO in LogReplicaPaa.ORIGEM_NOMES

    def test_numero_versao_documento_pode_ser_nulo(self, paa_retificacao):
        log = LogReplicaPaa.objects.create(
            paa=paa_retificacao,
            replica={},
            numero_versao_documento=None,
        )
        assert log.numero_versao_documento is None

    def test_numero_versao_documento_com_valor(self, log_replica):
        assert log_replica.numero_versao_documento == 1


class TestFormattedJsonReplica:

    def test_formatted_json_replica_com_dados(self, log_replica):
        resultado = log_replica.formatted_json_replica()
        assert 'texto_introducao' in resultado
        assert '<pre>' in resultado

    def test_formatted_json_replica_sem_dados(self, paa_retificacao):
        log = LogReplicaPaa(
            paa=paa_retificacao,
            origem=LogReplicaPaa.CANCELAMENTO,
            replica=None,
        )
        resultado = log.formatted_json_replica()
        assert resultado == '-'

    def test_formatted_json_replica_vazio(self, paa_retificacao):
        log = LogReplicaPaa.objects.create(
            paa=paa_retificacao,
            origem=LogReplicaPaa.CANCELAMENTO,
            replica={},
        )
        resultado = log.formatted_json_replica()
        assert '<pre>' in resultado

    def test_multiplos_logs_por_paa(self, paa_retificacao):
        LogReplicaPaa.objects.create(paa=paa_retificacao, origem=LogReplicaPaa.CANCELAMENTO, replica={})
        LogReplicaPaa.objects.create(paa=paa_retificacao, origem=LogReplicaPaa.CONCLUSAO, replica={})
        assert LogReplicaPaa.objects.filter(paa=paa_retificacao).count() == 2
