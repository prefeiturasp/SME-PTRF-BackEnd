import pytest
from django.db.models import Q

from sme_ptrf_apps.paa.enums import PaaStatusAndamentoEnum
from sme_ptrf_apps.paa.models import Paa
from sme_ptrf_apps.paa.paa_querysets.status_andamento_cases import CaseDefinition


class TestCaseDefinition:

    def test_campos_nomeados(self):
        case = CaseDefinition(Q(pk=1), PaaStatusAndamentoEnum.GERADO.name, 'Label')

        assert case.condicao == Q(pk=1)
        assert case.status == PaaStatusAndamentoEnum.GERADO.name
        assert case.label == 'Label'

    def test_permite_desempacotar_como_tupla(self):
        condicao, status, label = CaseDefinition(Q(pk=1), PaaStatusAndamentoEnum.GERADO.name, 'Label')

        assert condicao == Q(pk=1)
        assert status == PaaStatusAndamentoEnum.GERADO.name
        assert label == 'Label'


class TestGetCaseDefinitions:

    def test_retorna_lista_de_case_definition(self, case_definitions):
        cases = case_definitions

        assert isinstance(cases, list)
        assert len(cases) == 17
        assert all(isinstance(case, CaseDefinition) for case in cases)

    def test_condicoes_sao_expressoes_q(self, case_definitions):
        assert all(isinstance(case.condicao, Q) for case in case_definitions)

    def test_status_sao_valores_validos_do_enum(self, case_definitions):
        status_validos = {status.name for status in PaaStatusAndamentoEnum}

        assert all(case.status in status_validos for case in case_definitions)

    def test_labels_preenchidos_e_unicos(self, labels_case_definitions):
        labels = labels_case_definitions

        assert all(labels)
        assert len(labels) == len(set(labels))

    def test_contem_regras_de_retificado(self, case_definitions, titulo_label):
        status_por_label = {titulo_label(case.label): case.status for case in case_definitions}

        assert status_por_label['Retificado + Doc Final Retificação + Ata Retificação'] == \
            PaaStatusAndamentoEnum.GERADO.name
        assert status_por_label['Retificado + sem Documento final de retificação'] == \
            PaaStatusAndamentoEnum.FORA_FLUXO.name
        assert status_por_label['Retificado + sem Ata de retificação'] == \
            PaaStatusAndamentoEnum.FORA_FLUXO.name

    def test_regras_fora_fluxo_de_retificado_antes_do_retificado_completo(self, labels_case_definitions):
        """O Case retorna a primeira condição satisfeita: as regras de Fora de Fluxo devem vir antes."""
        labels = labels_case_definitions
        idx_completo = labels.index('Retificado + Doc Final Retificação + Ata Retificação')

        assert labels.index('Retificado + sem Documento final de retificação') < idx_completo
        assert labels.index('Retificado + sem Ata de retificação') < idx_completo

    def test_regras_fora_fluxo_de_gerado_antes_do_gerado_completo(self, labels_case_definitions):
        labels = labels_case_definitions
        idx_completo = labels.index('Gerado + Doc Final + Ata')

        assert labels.index('Gerado + sem Documento final') < idx_completo
        assert labels.index('Gerado + sem Ata') < idx_completo
        assert labels.index('Gerado + Doc Final + Ata + Réplica') < idx_completo

    def test_gerado_com_doc_e_ata_de_retificacao_e_fora_fluxo(self, case_definitions, titulo_label):
        """Gerado com doc final e ata de retificação concluídos deveria estar RETIFICADO."""
        status_por_label = {titulo_label(case.label): case.status for case in case_definitions}

        assert status_por_label['Gerado + Doc Final Retificação + Ata Retificação'] == \
            PaaStatusAndamentoEnum.FORA_FLUXO.name

    def test_gerado_com_doc_e_ata_de_retificacao_antes_do_gerado_completo(self, labels_case_definitions):
        """Esse PAA também tem doc final + ata originais, então a regra deve vir antes do Gerado completo."""
        labels = labels_case_definitions

        assert labels.index('Gerado + Doc Final Retificação + Ata Retificação') < \
            labels.index('Gerado + Doc Final + Ata')

    def test_retificacao_gerada_parcialmente_antes_da_retificacao_iniciada(self, labels_case_definitions):
        """Com doc de retificação gerado, deve prevalecer GERADO_PARCIALMENTE sobre EM_RETIFICACAO."""
        labels = labels_case_definitions
        idx_gerado_parcialmente = labels.index('Em retificação + com Réplica + Doc Retificação gerado + Ata iniciada')
        idx_em_retificacao = labels.index('Em retificação + com Réplica + Ata iniciada')

        assert idx_gerado_parcialmente < idx_em_retificacao

    def test_ultima_regra_e_nao_iniciado_fora_fluxo(self, case_definitions):
        ultima = case_definitions[-1]

        assert ultima.condicao == Q(status='NAO_INICIADO')
        assert ultima.status == PaaStatusAndamentoEnum.FORA_FLUXO.name


@pytest.mark.django_db
class TestRegrasStatusAndamentoNoQueryset:
    """Avalia as regras no banco, via PaaQuerySet.annotate_status_geracao."""

    def test_status_andamento_paa_retificado(self, paa_retificado_cenario_status_andamento):
        cenario = paa_retificado_cenario_status_andamento

        paa = Paa.objects.get(pk=cenario['paa'].pk)

        assert paa.status_andamento == cenario['status_andamento_esperado']
        assert cenario['label_esperado'] in paa._debug_case

    def test_status_andamento_gerado_com_doc_final_e_ata_de_retificacao(
        self, paa_gerado_com_doc_final_e_ata_de_retificacao
    ):
        paa = Paa.objects.get(pk=paa_gerado_com_doc_final_e_ata_de_retificacao.pk)

        assert paa.status_andamento == PaaStatusAndamentoEnum.FORA_FLUXO.name
        assert 'Gerado + Doc Final Retificação + Ata Retificação' in paa._debug_case

    def test_status_andamento_em_retificacao_com_replica_e_ata_iniciada(
        self, paa_em_retificacao_com_replica_e_ata_iniciada
    ):
        paa = Paa.objects.get(pk=paa_em_retificacao_com_replica_e_ata_iniciada.pk)

        assert paa.status_andamento == PaaStatusAndamentoEnum.EM_RETIFICACAO.name
        assert 'Em retificação + com Réplica + Ata iniciada' in paa._debug_case
