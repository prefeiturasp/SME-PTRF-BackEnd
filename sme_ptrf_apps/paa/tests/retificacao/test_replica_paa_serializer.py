import pytest

from sme_ptrf_apps.paa.api.serializers.replica_paa_serializer import (
    HistoricoPaaSerializer,
    ReplicaPaaSerializer,
)
from sme_ptrf_apps.paa.models import ReplicaPaa

pytestmark = pytest.mark.django_db


HISTORICO_VALIDO = {
    'texto_introducao': 'Texto de introdução.',
    'texto_conclusao': 'Texto de conclusão.',
    'objetivos': {
        'uuid-obj-1': {'nome': 'Objetivo A'},
    },
    'receitas_ptrf': {
        'uuid-ptrf-1': {
            'previsao_valor_capital': '100.00',
            'previsao_valor_custeio': '200.00',
            'previsao_valor_livre': '50.00',
        },
    },
    'receitas_pdde': {},
    'receitas_outros_recursos': {},
    'prioridades': {
        'uuid-prio-1': {
            'recurso': 'PTRF',
            'prioridade': 1,
            'tipo_aplicacao': 'CUSTEIO',
            'valor_total': '1000.00',
            'acao_associacao_uuid': None,
            'programa_pdde_uuid': None,
            'acao_pdde_uuid': None,
            'outro_recurso_uuid': None,
            'tipo_despesa_custeio_uuid': None,
            'especificacao_material_uuid': None,
        },
    },
}


class TestHistoricoPaaSerializer:

    def test_historico_valido_passa_validacao(self):
        serializer = HistoricoPaaSerializer(data=HISTORICO_VALIDO)
        assert serializer.is_valid(), serializer.errors

    def test_historico_vazio_e_invalido(self):
        serializer = HistoricoPaaSerializer(data={})
        assert not serializer.is_valid()
        for campo in HistoricoPaaSerializer.CAMPOS_OBRIGATORIOS:
            assert campo in serializer.errors, f"Campo '{campo}' deveria estar nos erros"

    def test_campo_obrigatorio_ausente_invalida(self):
        """
        Testa se um historico de PAA sem um campo obrigatório e inválido.
        """
        for campo in HistoricoPaaSerializer.CAMPOS_OBRIGATORIOS:
            historico = {k: v for k, v in HISTORICO_VALIDO.items() if k != campo}
            serializer = HistoricoPaaSerializer(data=historico)
            assert not serializer.is_valid(), f"Deveria ser inválido sem o campo '{campo}'"
            assert campo in serializer.errors, f"Campo '{campo}' deveria estar nos erros"

    def test_objetivo_sem_campo_nome_invalida(self):
        historico = {
            **HISTORICO_VALIDO,
            'objetivos': {'uuid-obj-1': {'descricao': 'sem nome'}},
        }
        serializer = HistoricoPaaSerializer(data=historico)
        assert not serializer.is_valid()
        assert 'objetivos' in serializer.errors

    def test_objetivo_sem_nome_mensagem_de_erro(self):
        historico = {**HISTORICO_VALIDO, 'objetivos': {'uuid-obj-1': {}}}
        serializer = HistoricoPaaSerializer(data=historico)
        serializer.is_valid()
        assert 'objetivos' in serializer.errors

    def test_receita_ptrf_sem_campos_obrigatorios_invalida(self):
        historico = {
            **HISTORICO_VALIDO,
            'receitas_ptrf': {
                'uuid-ptrf-1': {'previsao_valor_capital': '100.00'},
            },
        }
        serializer = HistoricoPaaSerializer(data=historico)
        assert not serializer.is_valid()
        assert 'receitas_ptrf' in serializer.errors

    def test_receita_pdde_sem_campos_obrigatorios_invalida(self):
        historico = {
            **HISTORICO_VALIDO,
            'receitas_pdde': {
                'uuid-pdde-1': {'saldo_custeio': '0.00'},
            },
        }
        serializer = HistoricoPaaSerializer(data=historico)
        assert not serializer.is_valid()
        assert 'receitas_pdde' in serializer.errors

    def test_receita_outros_recursos_sem_campos_obrigatorios_invalida(self):
        historico = {
            **HISTORICO_VALIDO,
            'receitas_outros_recursos': {
                'uuid-outro-1': {},
            },
        }
        serializer = HistoricoPaaSerializer(data=historico)
        assert not serializer.is_valid()
        assert 'receitas_outros_recursos' in serializer.errors

    def test_campos_opcionais_de_receita_sao_aceitos(self):
        historico = {
            **HISTORICO_VALIDO,
            'receitas_ptrf': {
                'uuid-ptrf-1': {
                    'previsao_valor_capital': '0.00',
                    'previsao_valor_custeio': '500.00',
                    'previsao_valor_livre': '0.00',
                    'saldo_congelado_custeio': '100.00',
                    'saldo_congelado_capital': '0.00',
                    'saldo_congelado_livre': '0.00',
                },
            },
        }
        serializer = HistoricoPaaSerializer(data=historico)
        assert serializer.is_valid(), serializer.errors

    def test_texto_nulo_e_aceito(self):
        historico = {**HISTORICO_VALIDO, 'texto_introducao': None, 'texto_conclusao': None}
        serializer = HistoricoPaaSerializer(data=historico)
        assert serializer.is_valid(), serializer.errors


class TestReplicaPaaSerializer:

    def test_serializer_retorna_campo_uuid(self, paa_retificacao, replica_paa_factory):
        replica = replica_paa_factory(paa=paa_retificacao, historico=HISTORICO_VALIDO)
        serializer = ReplicaPaaSerializer(replica)
        assert 'uuid' in serializer.data

    def test_serializer_retorna_paa_como_uuid(self, paa_retificacao, replica_paa_factory):
        replica = replica_paa_factory(paa=paa_retificacao, historico=HISTORICO_VALIDO)
        serializer = ReplicaPaaSerializer(replica)
        assert str(serializer.data['paa']) == str(paa_retificacao.uuid)

    def test_serializer_retorna_historico(self, paa_retificacao, replica_paa_factory):
        replica = replica_paa_factory(paa=paa_retificacao, historico=HISTORICO_VALIDO)
        serializer = ReplicaPaaSerializer(replica)
        assert 'historico' in serializer.data

    def test_serializer_retorna_campos_de_data(self, paa_retificacao, replica_paa_factory):
        replica = replica_paa_factory(paa=paa_retificacao, historico=HISTORICO_VALIDO)
        serializer = ReplicaPaaSerializer(replica)
        assert 'criado_em' in serializer.data
        assert 'alterado_em' in serializer.data

    def test_cria_replica_via_serializer(self, paa_retificacao):
        payload = {
            'paa': str(paa_retificacao.uuid),
            'historico': HISTORICO_VALIDO,
        }
        serializer = ReplicaPaaSerializer(data=payload)
        assert serializer.is_valid(), serializer.errors

        replica = serializer.save()

        assert isinstance(replica, ReplicaPaa)
        assert replica.paa == paa_retificacao

    def test_historico_invalido_falha_na_criacao(self, paa_retificacao):
        payload = {
            'paa': str(paa_retificacao.uuid),
            'historico': {
                **HISTORICO_VALIDO,
                'objetivos': {'uuid-1': {'sem_nome': True}},
            },
        }
        serializer = ReplicaPaaSerializer(data=payload)
        assert not serializer.is_valid()
        assert 'historico' in serializer.errors
