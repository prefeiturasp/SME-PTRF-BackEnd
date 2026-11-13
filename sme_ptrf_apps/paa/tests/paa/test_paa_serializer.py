import pytest
from datetime import date
from unittest.mock import patch

from django.db import IntegrityError

from rest_framework import serializers

from sme_ptrf_apps.paa.api.serializers import PaaSerializer
from sme_ptrf_apps.paa.api.serializers.paa_serializer import (
    PaaRetificacaoComparativoSerializer, PaaDreSerializer, PaaUpdateSerializer)
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum
from sme_ptrf_apps.paa.models import ObjetivoPaa, AtividadeEstatutaria, AtividadeEstatutariaPaa

pytestmark = pytest.mark.django_db


def test_paa_retriever_serializer(paa):
    serializer = PaaSerializer(paa)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'periodo_paa' in serializer.data
    assert 'associacao' in serializer.data
    assert 'periodo_paa_objeto' in serializer.data
    assert 'saldo_congelado_em' in serializer.data
    assert 'texto_introducao' in serializer.data
    assert 'texto_conclusao' in serializer.data
    assert 'status' in serializer.data
    assert 'atividades_previstas_preenchidas' in serializer.data


def test_paa_model_tem_campos_acoes_conclusao(paa):
    """Testa que o modelo PAA tem os campos ManyToMany para ações na conclusão"""
    assert hasattr(paa, 'acoes_conclusao')
    assert hasattr(paa, 'acoes_pdde_conclusao')
    assert hasattr(paa, 'outros_recursos_periodo_conclusao')
    assert paa.acoes_conclusao.count() == 0
    assert paa.acoes_pdde_conclusao.count() == 0
    assert paa.outros_recursos_periodo_conclusao.count() == 0


def test_paa_serializer_status_andamento(paa):
    serializer = PaaSerializer(paa)
    assert 'status_andamento' in serializer.data


def test_paa_serializer_tem_documento_final_sem_retificacao(paa):
    serializer = PaaSerializer(paa)
    assert 'tem_documento_final_concluido' in serializer.data
    assert serializer.data['tem_documento_final_concluido'] is False


def test_paa_serializer_tem_documento_final_com_retificacao(paa_factory, documento_paa_factory):
    paa = paa_factory()
    paa.set_paa_status_em_retificacao()
    serializer = PaaSerializer(paa)
    assert 'tem_documento_final_concluido' in serializer.data


def test_paa_serializer_tem_ata_concluida_sem_retificacao(paa):
    serializer = PaaSerializer(paa)
    assert 'tem_ata_concluida' in serializer.data
    assert serializer.data['tem_ata_concluida'] is False


def test_paa_serializer_tem_ata_concluida_com_retificacao(paa_factory):
    paa = paa_factory()
    paa.set_paa_status_em_retificacao()
    serializer = PaaSerializer(paa)
    assert 'tem_ata_concluida' in serializer.data


def test_paa_serializer_validate_sem_periodo_vigente(paa_factory, associacao):
    paa_factory()
    data = {'associacao': str(associacao.uuid)}
    serializer = PaaSerializer(data=data)
    with patch('sme_ptrf_apps.paa.services.paa_service.PaaService.pode_elaborar_novo_paa'):
        with patch('sme_ptrf_apps.paa.api.serializers.paa_serializer.PeriodoPaa.periodo_vigente', return_value=None):
            assert not serializer.is_valid()
            assert 'non_field_errors' in serializer.errors


def test_paa_serializer_validate_paa_service_exception(paa_factory, associacao):
    paa_factory()
    data = {'associacao': str(associacao.uuid)}
    serializer = PaaSerializer(data=data)
    with patch('sme_ptrf_apps.paa.services.paa_service.PaaService.pode_elaborar_novo_paa',
               side_effect=Exception('Não pode elaborar')):
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors


class TestPaaRetificacaoComparativoSerializer:

    def test_campos_adicionais_retificacao(self, paa):
        serializer = PaaRetificacaoComparativoSerializer(paa, context={'alteracoes': {'prioridades': {}}})
        assert 'alteracoes' in serializer.data
        assert 'ata_elaboracao' in serializer.data
        assert 'ata_retificacao' in serializer.data

    def test_get_alteracoes_retorna_context(self, paa):
        alteracoes = {'prioridades': {'uuid': {'acao': 'modificado'}}}
        serializer = PaaRetificacaoComparativoSerializer(paa, context={'alteracoes': alteracoes})
        assert serializer.data['alteracoes'] == alteracoes

    def test_get_alteracoes_sem_context_retorna_vazio(self, paa):
        serializer = PaaRetificacaoComparativoSerializer(paa)
        assert serializer.data['alteracoes'] == {}


class TestPaaDreSerializer:

    def test_campos_paa_dre_serializer(self, paa):
        serializer = PaaDreSerializer(paa)
        assert 'uuid' in serializer.data
        assert 'periodo_paa' in serializer.data
        assert 'unidade' in serializer.data
        assert 'status' in serializer.data
        assert 'status_display' in serializer.data
        assert 'tem_documentos' in serializer.data

    def test_tem_documentos_false_sem_documentos(self, paa):
        serializer = PaaDreSerializer(paa)
        assert serializer.data['tem_documentos'] is False


class TestPaaUpdateSerializerGerenciarObjetivos:

    def test_atualiza_nome_de_objetivo_do_proprio_paa(self, paa, objetivo_do_paa):
        """Objetivo existente do próprio PAA tem o nome atualizado e permanece vinculado"""
        PaaUpdateSerializer()._generenciar_objetivos(paa, [
            {'objetivo': objetivo_do_paa, 'nome': 'Nome Atualizado'},
        ])

        objetivo_do_paa.refresh_from_db()
        assert objetivo_do_paa.nome == 'Nome Atualizado'
        assert list(paa.objetivos.all()) == [objetivo_do_paa]

    def test_vincula_objetivo_nao_pertencente_ao_paa_sem_alterar_nome(self, paa, objetivo_nao_pertencente_ao_paa):
        """Objetivo global ou de outro PAA é vinculado, mas o nome não é alterado"""
        PaaUpdateSerializer()._generenciar_objetivos(paa, [
            {'objetivo': objetivo_nao_pertencente_ao_paa, 'nome': 'Nome Ignorado'},
        ])

        objetivo_nao_pertencente_ao_paa.refresh_from_db()
        assert objetivo_nao_pertencente_ao_paa.nome == 'Objetivo Original'
        assert list(paa.objetivos.all()) == [objetivo_nao_pertencente_ao_paa]

    def test_destroy_exclui_objetivo(self, paa, objetivo_do_paa):
        """Objetivo marcado com _destroy é excluído e desvinculado do PAA"""
        objetivo_id = objetivo_do_paa.id

        PaaUpdateSerializer()._generenciar_objetivos(paa, [
            {'objetivo': objetivo_do_paa, 'nome': objetivo_do_paa.nome, '_destroy': True},
        ])

        assert not ObjetivoPaa.objects.filter(id=objetivo_id).exists()
        assert paa.objetivos.count() == 0

    def test_destroy_false_mantem_objetivo(self, paa, objetivo_do_paa):
        """Objetivo com _destroy falso não é excluído e permanece vinculado"""
        PaaUpdateSerializer()._generenciar_objetivos(paa, [
            {'objetivo': objetivo_do_paa, 'nome': objetivo_do_paa.nome, '_destroy': False},
        ])

        assert ObjetivoPaa.objects.filter(id=objetivo_do_paa.id).exists()
        assert list(paa.objetivos.all()) == [objetivo_do_paa]

    def test_cria_novo_objetivo_pelo_nome(self, paa):
        """Item somente com nome cria um novo objetivo vinculado ao PAA"""
        PaaUpdateSerializer()._generenciar_objetivos(paa, [{'nome': 'Novo Objetivo'}])

        novo_objetivo = ObjetivoPaa.objects.get(nome='Novo Objetivo')
        assert novo_objetivo.paa == paa
        assert list(paa.objetivos.all()) == [novo_objetivo]

    def test_nome_duplicado_levanta_validation_error(self, paa, objetivo_do_paa, nome_objetivo_duplicado):
        """Criar objetivo com nome já existente no PAA (case-insensitive) levanta ValidationError"""
        serializer = PaaUpdateSerializer()
        objetivos_data = [{'nome': nome_objetivo_duplicado}]

        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer._generenciar_objetivos(paa, objetivos_data)

        assert excinfo.value.detail == {'mensagem': ['Já existe um objetivo cadastrado com este nome.']}
        assert ObjetivoPaa.objects.filter(paa=paa).count() == 1

    def test_nome_existente_em_outro_paa_nao_e_duplicado(self, paa, paa_factory, objetivo_paa_factory):
        """A verificação de duplicidade considera apenas os objetivos do próprio PAA"""
        objetivo_paa_factory.create(nome='Objetivo Compartilhado', paa=paa_factory.create())

        PaaUpdateSerializer()._generenciar_objetivos(paa, [{'nome': 'Objetivo Compartilhado'}])

        assert paa.objetivos.filter(nome='Objetivo Compartilhado').count() == 1

    def test_objetivos_nao_enviados_sao_desvinculados(self, paa, objetivo_do_paa, objetivo_paa_factory):
        """Objetivos vinculados que não vieram nos dados são desvinculados, mas não excluídos"""
        objetivo_mantido = objetivo_paa_factory.create(nome='Objetivo Mantido', paa=paa)
        paa.objetivos.add(objetivo_mantido)

        PaaUpdateSerializer()._generenciar_objetivos(paa, [
            {'objetivo': objetivo_mantido, 'nome': objetivo_mantido.nome},
        ])

        assert list(paa.objetivos.all()) == [objetivo_mantido]
        assert ObjetivoPaa.objects.filter(id=objetivo_do_paa.id).exists()

    def test_lista_vazia_desvincula_todos_os_objetivos(self, paa, objetivo_do_paa):
        """Lista vazia remove todos os vínculos de objetivos do PAA"""
        PaaUpdateSerializer()._generenciar_objetivos(paa, [])

        assert paa.objetivos.count() == 0
        assert ObjetivoPaa.objects.filter(id=objetivo_do_paa.id).exists()

    def test_item_sem_objetivo_e_sem_nome_e_ignorado(self, paa, objetivo_do_paa):
        """Item sem 'objetivo' e sem 'nome' não cria nem mantém objetivos"""
        PaaUpdateSerializer()._generenciar_objetivos(paa, [{}])

        assert paa.objetivos.count() == 0
        assert ObjetivoPaa.objects.filter(paa=paa).count() == 1

    def test_combina_atualizacao_criacao_e_exclusao(self, paa, objetivo_do_paa, objetivo_paa_factory):
        """Atualização, criação e exclusão no mesmo envio resultam nos vínculos corretos"""
        objetivo_excluido = objetivo_paa_factory.create(nome='Objetivo Excluído', paa=paa)
        paa.objetivos.add(objetivo_excluido)

        PaaUpdateSerializer()._generenciar_objetivos(paa, [
            {'objetivo': objetivo_do_paa, 'nome': 'Objetivo Atualizado'},
            {'objetivo': objetivo_excluido, 'nome': objetivo_excluido.nome, '_destroy': True},
            {'nome': 'Objetivo Novo'},
        ])

        nomes_vinculados = set(paa.objetivos.values_list('nome', flat=True))
        assert nomes_vinculados == {'Objetivo Atualizado', 'Objetivo Novo'}
        assert not ObjetivoPaa.objects.filter(id=objetivo_excluido.id).exists()

    def test_erro_de_validacao_reverte_alteracoes(self, paa, objetivo_do_paa):
        """Com ValidationError no meio do processamento, as alterações anteriores são revertidas"""
        serializer = PaaUpdateSerializer()
        objetivos_data = [
            {'objetivo': objetivo_do_paa, 'nome': 'Nome Que Será Revertido'},
            {'nome': 'Nome Que Será Revertido'},
        ]

        with pytest.raises(serializers.ValidationError):
            serializer._generenciar_objetivos(paa, objetivos_data)

        objetivo_do_paa.refresh_from_db()
        assert objetivo_do_paa.nome == 'Objetivo do PAA'
        assert list(paa.objetivos.all()) == [objetivo_do_paa]


class TestPaaUpdateSerializerGerenciarAtividadesEstatutarias:

    ORDINARIA = TipoAtividadeEstatutariaEnum.ORDINARIA.name
    EXTRAORDINARIA = TipoAtividadeEstatutariaEnum.EXTRAORDINARIA.name
    MENSAGEM_DUPLICADA = "Já existe uma atividade com mesmo nome, tipo, mês e data para este PAA."

    def test_destroy_exclui_atividade_do_paa_e_seus_vinculos(self, paa, atividade_do_paa):
        """Atividade do próprio PAA com _destroy é excluída junto com seus vínculos"""
        atividade_id = atividade_do_paa.id

        PaaUpdateSerializer()._gerenciar_atividades_estatutarias(paa, [
            {'atividade_estatutaria': atividade_do_paa, '_destroy': True},
        ])

        assert not AtividadeEstatutaria.objects.filter(id=atividade_id).exists()
        assert not AtividadeEstatutariaPaa.objects.filter(atividade_estatutaria_id=atividade_id).exists()

    def test_atualiza_nome_tipo_e_mes_da_atividade_do_paa(self, paa, atividade_do_paa):
        """Nome, tipo e mês (derivado da data) são atualizados na atividade do próprio PAA"""
        nova_data = date(2025, 8, 20)

        PaaUpdateSerializer()._gerenciar_atividades_estatutarias(paa, [
            {'atividade_estatutaria': atividade_do_paa, 'nome': 'Nome Atualizado',
             'tipo': self.EXTRAORDINARIA, 'data': nova_data},
        ])

        atividade_do_paa.refresh_from_db()
        assert atividade_do_paa.nome == 'Nome Atualizado'
        assert atividade_do_paa.tipo == self.EXTRAORDINARIA
        assert atividade_do_paa.mes == 8

    def test_atualiza_somente_nome_mantem_tipo_e_mes(self, paa, atividade_do_paa):
        """Somente o nome informado é alterado; tipo e mês permanecem quando não há tipo nem data"""
        PaaUpdateSerializer()._gerenciar_atividades_estatutarias(paa, [
            {'atividade_estatutaria': atividade_do_paa, 'nome': 'Somente Nome'},
        ])

        atividade_do_paa.refresh_from_db()
        assert atividade_do_paa.nome == 'Somente Nome'
        assert atividade_do_paa.tipo == self.ORDINARIA
        assert atividade_do_paa.mes == 3

    def test_atualiza_somente_tipo_mantem_nome(self, paa, atividade_do_paa):
        """Somente o tipo informado é alterado; o nome permanece"""
        PaaUpdateSerializer()._gerenciar_atividades_estatutarias(paa, [
            {'atividade_estatutaria': atividade_do_paa, 'tipo': self.EXTRAORDINARIA},
        ])

        atividade_do_paa.refresh_from_db()
        assert atividade_do_paa.nome == 'Assembleia do PAA'
        assert atividade_do_paa.tipo == self.EXTRAORDINARIA

    def test_sem_nome_e_sem_tipo_nao_altera_atividade(self, paa, atividade_do_paa, data_atividade):
        """Sem nome e sem tipo, a atividade não é alterada, mesmo com data de outro mês"""
        PaaUpdateSerializer()._gerenciar_atividades_estatutarias(paa, [
            {'atividade_estatutaria': atividade_do_paa, 'data': date(2025, 11, 5)},
        ])

        atividade_do_paa.refresh_from_db()
        assert atividade_do_paa.nome == 'Assembleia do PAA'
        assert atividade_do_paa.mes == data_atividade.month

    def test_atualizacao_duplicada_levanta_validation_error(
            self, paa, atividade_do_paa, atividade_estatutaria_factory, data_atividade):
        """Atualizar para nome, tipo, mês e data iguais aos de outra atividade do PAA levanta ValidationError"""
        outra_atividade = atividade_estatutaria_factory.create(
            nome='Outra Atividade', tipo=self.ORDINARIA, mes=data_atividade.month, paa=paa)

        serializer = PaaUpdateSerializer()
        atividades_data = [
            {'atividade_estatutaria': outra_atividade, 'nome': atividade_do_paa.nome,
             'tipo': atividade_do_paa.tipo, 'data': data_atividade},
        ]

        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer._gerenciar_atividades_estatutarias(paa, atividades_data)

        assert excinfo.value.detail == {'mensagem': self.MENSAGEM_DUPLICADA}
        outra_atividade.refresh_from_db()
        assert outra_atividade.nome == 'Outra Atividade'

    def test_atualizacao_da_propria_atividade_nao_e_duplicada(self, paa, atividade_do_paa, data_atividade):
        """Reenviar os mesmos dados da própria atividade não é considerado duplicidade"""
        PaaUpdateSerializer()._gerenciar_atividades_estatutarias(paa, [
            {'atividade_estatutaria': atividade_do_paa, 'nome': atividade_do_paa.nome,
             'tipo': atividade_do_paa.tipo, 'data': data_atividade},
        ])

        assert AtividadeEstatutariaPaa.objects.filter(atividade_estatutaria=atividade_do_paa, paa=paa).count() == 1

    def test_vinculo_existente_tem_data_atualizada(self, paa, atividade_do_paa):
        """Vínculo já existente com o PAA tem a data atualizada quando informada"""
        nova_data = date(2025, 3, 28)

        PaaUpdateSerializer()._gerenciar_atividades_estatutarias(paa, [
            {'atividade_estatutaria': atividade_do_paa, 'data': nova_data},
        ])

        vinculo = AtividadeEstatutariaPaa.objects.get(atividade_estatutaria=atividade_do_paa, paa=paa)
        assert vinculo.data == nova_data

    def test_vinculo_existente_sem_data_mantem_data(self, paa, atividade_do_paa, data_atividade):
        """Vínculo já existente mantém a data quando nenhuma data é informada"""
        PaaUpdateSerializer()._gerenciar_atividades_estatutarias(paa, [
            {'atividade_estatutaria': atividade_do_paa},
        ])

        vinculo = AtividadeEstatutariaPaa.objects.get(atividade_estatutaria=atividade_do_paa, paa=paa)
        assert vinculo.data == data_atividade

    def test_destroy_de_atividade_nao_pertencente_levanta_validation_error(
            self, paa, atividade_nao_pertencente_ao_paa):
        """Não é permitido excluir atividade global ou de outro PAA"""
        serializer = PaaUpdateSerializer()
        atividades_data = [{'atividade_estatutaria': atividade_nao_pertencente_ao_paa, '_destroy': True}]

        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer._gerenciar_atividades_estatutarias(paa, atividades_data)

        assert excinfo.value.detail == {
            'mensagem': 'Não é possível excluir atividade estatutária que não pertece ao PAA.'}
        assert AtividadeEstatutaria.objects.filter(id=atividade_nao_pertencente_ao_paa.id).exists()

    def test_vincula_atividade_nao_pertencente_sem_alterar_dados(
            self, paa, atividade_nao_pertencente_ao_paa, data_atividade):
        """Atividade global ou de outro PAA é vinculada na data, sem alterar nome ou tipo"""
        PaaUpdateSerializer()._gerenciar_atividades_estatutarias(paa, [
            {'atividade_estatutaria': atividade_nao_pertencente_ao_paa, 'nome': 'Nome Ignorado',
             'tipo': self.EXTRAORDINARIA, 'data': data_atividade},
        ])

        atividade_nao_pertencente_ao_paa.refresh_from_db()
        assert atividade_nao_pertencente_ao_paa.nome == 'Atividade Original'
        assert atividade_nao_pertencente_ao_paa.tipo == self.ORDINARIA
        vinculo = AtividadeEstatutariaPaa.objects.get(atividade_estatutaria=atividade_nao_pertencente_ao_paa, paa=paa)
        assert vinculo.data == data_atividade

    def test_cria_nova_atividade_e_vinculo(self, paa, data_atividade):
        """Item sem atividade_estatutaria cria uma nova atividade do PAA e o vínculo na data"""
        PaaUpdateSerializer()._gerenciar_atividades_estatutarias(paa, [
            {'nome': 'Nova Atividade', 'tipo': self.EXTRAORDINARIA, 'data': data_atividade},
        ])

        nova_atividade = AtividadeEstatutaria.objects.get(nome='Nova Atividade', paa=paa)
        assert nova_atividade.tipo == self.EXTRAORDINARIA
        assert nova_atividade.mes == data_atividade.month
        vinculo = AtividadeEstatutariaPaa.objects.get(atividade_estatutaria=nova_atividade, paa=paa)
        assert vinculo.data == data_atividade

    def test_nova_atividade_incompleta_levanta_validation_error(self, paa, dados_nova_atividade_incompletos):
        """Nova atividade sem nome, tipo ou data levanta ValidationError"""
        serializer = PaaUpdateSerializer()
        atividades_data = [dados_nova_atividade_incompletos]

        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer._gerenciar_atividades_estatutarias(paa, atividades_data)

        assert excinfo.value.detail == {'mensagem': 'Nova atividade precisa de nome, tipo e data.'}
        assert not AtividadeEstatutaria.objects.filter(nome='Nova Atividade').exists()

    def test_nova_atividade_duplicada_levanta_validation_error(self, paa, atividade_do_paa, data_atividade):
        """Nova atividade com nome, tipo, mês e data iguais a uma existente do PAA levanta ValidationError"""
        serializer = PaaUpdateSerializer()
        atividades_data = [{'nome': atividade_do_paa.nome, 'tipo': atividade_do_paa.tipo, 'data': data_atividade}]

        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer._gerenciar_atividades_estatutarias(paa, atividades_data)

        assert excinfo.value.detail == {'mensagem': self.MENSAGEM_DUPLICADA}
        assert AtividadeEstatutaria.objects.filter(nome=atividade_do_paa.nome, paa=paa).count() == 1

    def test_integrity_error_no_vinculo_levanta_validation_error(self, monkeypatch, paa, data_atividade):
        """IntegrityError ao criar o vínculo da nova atividade é convertido em ValidationError"""
        def _create_com_integrity_error(**kwargs):
            raise IntegrityError

        monkeypatch.setattr(AtividadeEstatutariaPaa.objects, 'create', _create_com_integrity_error)

        serializer = PaaUpdateSerializer()
        atividades_data = [{'nome': 'Nova Atividade', 'tipo': self.EXTRAORDINARIA, 'data': data_atividade}]

        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer._gerenciar_atividades_estatutarias(paa, atividades_data)

        assert excinfo.value.detail == {'mensagem': 'Já existe uma atividade paa com esse paa e data.'}

    def test_lista_vazia_nao_altera_nada(self, paa, atividade_do_paa):
        """Lista vazia não altera atividades nem vínculos"""
        PaaUpdateSerializer()._gerenciar_atividades_estatutarias(paa, [])

        assert AtividadeEstatutaria.objects.filter(id=atividade_do_paa.id).exists()
        assert AtividadeEstatutariaPaa.objects.filter(atividade_estatutaria=atividade_do_paa, paa=paa).exists()

    def test_erro_de_validacao_reverte_alteracoes(self, paa, atividade_do_paa, data_atividade):
        """Com ValidationError no meio do processamento, as alterações anteriores são revertidas"""
        atividade_id = atividade_do_paa.id
        serializer = PaaUpdateSerializer()
        atividades_data = [
            {'nome': 'Atividade Criada', 'tipo': self.EXTRAORDINARIA, 'data': data_atividade},
            {'atividade_estatutaria': atividade_do_paa, '_destroy': True},
            {'nome': 'Incompleta'},
        ]

        with pytest.raises(serializers.ValidationError):
            serializer._gerenciar_atividades_estatutarias(paa, atividades_data)

        assert not AtividadeEstatutaria.objects.filter(nome='Atividade Criada').exists()
        assert AtividadeEstatutaria.objects.filter(id=atividade_id).exists()
        assert AtividadeEstatutariaPaa.objects.filter(atividade_estatutaria_id=atividade_id, paa=paa).exists()
