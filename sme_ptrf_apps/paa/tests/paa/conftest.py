from datetime import date

import pytest
from django.db.models import Q

from sme_ptrf_apps.paa.enums import PaaStatusEnum, PaaStatusAndamentoEnum, TipoAtividadeEstatutariaEnum
from sme_ptrf_apps.paa.models import AtaPaa, DocumentoPaa
from sme_ptrf_apps.paa.paa_querysets.status_andamento_cases import get_case_definitions


@pytest.fixture
def periodo_paa_2024(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia="Periodo 2024", data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))


@pytest.fixture
def periodo_paa_2025(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))


@pytest.fixture
def cria_paa_gerado(paa_factory, ata_paa_factory, documento_paa_factory):
    """
    Cria um PAA GERADO: documento final original + ata de apresentação concluídos.
    """
    def _cria(**kwargs):
        paa = paa_factory.create(status=PaaStatusEnum.GERADO.name, **kwargs)
        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
            retificacao=False,
        )
        ata_paa_factory.create(
            paa=paa,
            tipo_ata=AtaPaa.ATA_APRESENTACAO,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )
        return paa
    return _cria


@pytest.fixture
def cria_paa_retificado(cria_paa_gerado, ata_paa_factory, documento_paa_factory):
    """
    Cria um PAA RETIFICADO. Um PAA retificado também passou pelo GERADO, então possui:
        - documento final original + ata de apresentação concluídos;
        - documento final de retificação + ata de retificação concluídos.
    """
    def _cria(**kwargs):
        paa = cria_paa_gerado(**kwargs)
        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
            retificacao=True,
        )
        ata_paa_factory.create(
            paa=paa,
            tipo_ata=AtaPaa.ATA_RETIFICACAO,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
            pdf_gerado_previamente=True,
        )
        paa.set_paa_status_retificado()
        return paa
    return _cria


@pytest.fixture
def paa_vigente_retificado_e_anterior_gerado(associacao, periodo_paa_2024, periodo_paa_2025,
                                             cria_paa_gerado, cria_paa_retificado):
    """PAA vigente (2025) RETIFICADO e PAA anterior (2024) GERADO, da mesma associação."""
    return {
        'paa_vigente': cria_paa_retificado(periodo_paa=periodo_paa_2025, associacao=associacao),
        'paa_anterior': cria_paa_gerado(periodo_paa=periodo_paa_2024, associacao=associacao),
    }


@pytest.fixture
def paa_vigente_gerado_e_anterior_retificado(associacao, periodo_paa_2024, periodo_paa_2025,
                                             cria_paa_gerado, cria_paa_retificado):
    """PAA vigente (2025) GERADO e PAA anterior (2024) RETIFICADO, da mesma associação."""
    return {
        'paa_vigente': cria_paa_gerado(periodo_paa=periodo_paa_2025, associacao=associacao),
        'paa_anterior': cria_paa_retificado(periodo_paa=periodo_paa_2024, associacao=associacao),
    }


@pytest.fixture(
    params=[
        # (tem_doc_final_retificacao, tem_ata_retificacao, status_andamento_esperado, label_esperado)
        (True, True, PaaStatusAndamentoEnum.GERADO.name,
         'Retificado + Doc Final Retificação + Ata Retificação'),
        (False, True, PaaStatusAndamentoEnum.FORA_FLUXO.name,
         'Retificado + sem Documento final de retificação'),
        (True, False, PaaStatusAndamentoEnum.FORA_FLUXO.name,
         'Retificado + sem Ata de retificação'),
    ],
    ids=['completo', 'sem_doc_final_retificacao', 'sem_ata_retificacao'],
)
def paa_retificado_cenario_status_andamento(request, cria_paa_gerado, ata_paa_factory, documento_paa_factory):
    """
    Cenários de PAA RETIFICADO para as regras de status_andamento (status_andamento_cases).

    O PAA sempre possui o original gerado (doc final + ata de apresentação) e, conforme o
    cenário, o documento final e/ou a ata de retificação concluídos.

    Retorna um dict com: paa, status_andamento_esperado, label_esperado.
    """
    tem_doc_final_retificacao, tem_ata_retificacao, status_esperado, label_esperado = request.param

    paa = cria_paa_gerado()

    if tem_doc_final_retificacao:
        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
            retificacao=True,
        )
    if tem_ata_retificacao:
        ata_paa_factory.create(
            paa=paa,
            tipo_ata=AtaPaa.ATA_RETIFICACAO,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
            pdf_gerado_previamente=True,
        )

    paa.set_paa_status_retificado()

    return {
        'paa': paa,
        'status_andamento_esperado': status_esperado,
        'label_esperado': label_esperado,
    }


@pytest.fixture
def paa_gerado_com_doc_final_e_ata_de_retificacao(cria_paa_gerado, ata_paa_factory, documento_paa_factory):
    """
    PAA que concluiu a retificação (doc final + ata de retificação concluídos),
    mas permaneceu com status GERADO (Fora de Fluxo).
    """
    paa = cria_paa_gerado()
    documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        retificacao=True,
    )
    ata_paa_factory.create(
        paa=paa,
        tipo_ata=AtaPaa.ATA_RETIFICACAO,
        status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        pdf_gerado_previamente=True,
    )
    return paa


@pytest.fixture
def paa_em_retificacao_com_replica_e_ata_iniciada(cria_paa_gerado, ata_paa_factory, replica_paa_factory):
    """PAA EM_RETIFICACAO com réplica e ata de retificação iniciada (ainda sem documento de retificação)."""
    paa = cria_paa_gerado()
    replica_paa_factory.create(paa=paa, historico={})
    ata_paa_factory.create(
        paa=paa,
        tipo_ata=AtaPaa.ATA_RETIFICACAO,
        status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO,
    )
    paa.set_paa_status_em_retificacao()
    return paa


@pytest.fixture
def case_definitions():
    """
    Regras de status_andamento montadas com expressões Q no lugar das subqueries Exists.
    A função apenas combina as expressões (&, ~), então Q é suficiente para testar a estrutura.
    """
    return get_case_definitions(
        doc_final_original=Q(pk=1),
        doc_final_retificacao=Q(pk=2),
        ata_apresentacao=Q(pk=3),
        ata_retificacao=Q(pk=4),
        ata_retificacao_iniciada=Q(pk=5),
    )


@pytest.fixture
def titulo_label():
    """
    Retorna uma função que extrai a primeira linha do label
    (os labels de Fora de Fluxo trazem instruções nas linhas seguintes).
    """
    def _titulo(label):
        return label.strip().splitlines()[0].strip()
    return _titulo


@pytest.fixture
def labels_case_definitions(case_definitions, titulo_label):
    """Títulos (primeira linha do label) das regras de status_andamento, na ordem de avaliação."""
    return [titulo_label(case.label) for case in case_definitions]


@pytest.fixture
def objetivo_do_paa(objetivo_paa_factory, paa):
    """Objetivo criado pelo próprio PAA e vinculado a ele."""
    objetivo = objetivo_paa_factory.create(nome='Objetivo do PAA', paa=paa)
    paa.objetivos.add(objetivo)
    return objetivo


@pytest.fixture(params=['global', 'outro_paa'])
def objetivo_nao_pertencente_ao_paa(request, objetivo_paa_factory, paa_factory):
    """Objetivo que não pertence ao PAA: global (sem PAA) ou criado por outro PAA."""
    paa_do_objetivo = None if request.param == 'global' else paa_factory.create()
    return objetivo_paa_factory.create(nome='Objetivo Original', paa=paa_do_objetivo)


@pytest.fixture(params=['Objetivo do PAA', 'objetivo do paa', 'OBJETIVO DO PAA'],
                ids=['mesmo_nome', 'minusculo', 'maiusculo'])
def nome_objetivo_duplicado(request):
    """Variações de nome que conflitam (case-insensitive) com o objetivo_do_paa."""
    return request.param


@pytest.fixture
def data_atividade():
    """Data padrão de realização das atividades estatutárias nos testes."""
    return date(2025, 3, 15)


@pytest.fixture
def atividade_do_paa(atividade_estatutaria_factory, atividade_estatutaria_paa_factory, paa, data_atividade):
    """Atividade estatutária criada pelo próprio PAA e vinculada a ele na data_atividade."""
    atividade = atividade_estatutaria_factory.create(
        nome='Assembleia do PAA',
        tipo=TipoAtividadeEstatutariaEnum.ORDINARIA.name,
        mes=data_atividade.month,
        paa=paa,
    )
    atividade_estatutaria_paa_factory.create(atividade_estatutaria=atividade, paa=paa, data=data_atividade)
    return atividade


@pytest.fixture(params=['global', 'outro_paa'])
def atividade_nao_pertencente_ao_paa(request, atividade_estatutaria_factory, paa_factory):
    """Atividade estatutária que não pertence ao PAA: global (sem PAA) ou criada por outro PAA."""
    paa_da_atividade = None if request.param == 'global' else paa_factory.create()
    return atividade_estatutaria_factory.create(
        nome='Atividade Original',
        tipo=TipoAtividadeEstatutariaEnum.ORDINARIA.name,
        mes=1,
        paa=paa_da_atividade,
    )


@pytest.fixture(params=['nome', 'tipo', 'data'], ids=['sem_nome', 'sem_tipo', 'sem_data'])
def dados_nova_atividade_incompletos(request, data_atividade):
    """Dados de nova atividade estatutária sem um dos campos obrigatórios (nome, tipo ou data)."""
    dados = {
        'nome': 'Nova Atividade',
        'tipo': TipoAtividadeEstatutariaEnum.EXTRAORDINARIA.name,
        'data': data_atividade,
    }
    dados.pop(request.param)
    return dados
