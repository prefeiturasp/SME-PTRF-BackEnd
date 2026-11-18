import copy
from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from django.template.loader import get_template
from model_bakery import baker
from waffle import get_waffle_flag_model

from sme_ptrf_apps.core.services.dados_demo_financeiro_service import (
    cria_identificacao_apm as cria_identificacao_demonstrativo,
)
from sme_ptrf_apps.core.models import DadosDemonstrativoFinanceiro
from sme_ptrf_apps.core.services.persistencia_dados_demo_financeiro_service import PersistenciaDadosDemoFinanceiro
from sme_ptrf_apps.core.services.relacao_bens_dados_service import (
    cria_identificacao_apm as cria_identificacao_relacao_bens,
)
from sme_ptrf_apps.core.tests.tests_services.tests_dados_demonstrativo_financeiro_service \
    .test_dados_demonstrativo_financeiro_service import (
        dados_demonstrativo,
    )

pytestmark = pytest.mark.django_db


def _texto(html):
    return ' '.join(html.split())


def _ativa_historico_v2():
    get_waffle_flag_model().objects.update_or_create(
        name='historico-de-membros-v2',
        defaults={'everyone': True},
    )


def _composicao_com_tesoureiro_e_conselheiro(associacao):
    hoje = date.today()
    mandato = baker.make(
        'mandatos.Mandato',
        referencia_mandato='mandato documentos pc',
        data_inicial=hoje - timedelta(days=10),
        data_final=hoje + timedelta(days=10),
    )
    composicao = baker.make(
        'mandatos.ComposicaoVacancia',
        associacao=associacao,
        mandato=mandato,
    )
    tesoureiro = baker.make('mandatos.OcupanteCargo', nome='Carlos Tesoureiro')
    conselheiro = baker.make('mandatos.OcupanteCargo', nome='Maria Conselheira')
    for ocupante, cargo in ((tesoureiro, 'TESOUREIRO'), (conselheiro, 'CONSELHEIRO_1')):
        baker.make(
            'mandatos.CargoComposicaoVacancia',
            composicao=composicao,
            ocupante_do_cargo=ocupante,
            cargo_associacao=cargo,
            data_inicio_no_cargo=hoje - timedelta(days=5),
            data_fim_no_cargo=hoje + timedelta(days=5),
        )


def _prestacao_com_substituto():
    return SimpleNamespace(
        status_presidente='AUSENTE',
        cargo_substituto_presidente_ausente='TESOUREIRO',
        cargo_conselheiro_assinatura='CONSELHEIRO_1',
    )


def _contexto_relacao(identificacao):
    return {
        'base_static_url': '',
        'dados': {
            'cabecalho': {
                'recurso': 'PTRF',
                'recurso_nome_exibicao': 'PTRF',
                'periodo_referencia': '2025.1',
                'periodo_data_inicio': '01/01/2025',
                'periodo_data_fim': '30/04/2025',
                'conta': 'Cheque',
            },
            'identificacao_apm': identificacao,
            'data_geracao': '13/11/2026',
            'data_geracao_documento': 'Documento final',
            'previa': False,
            'relacao_de_bens_adquiridos_ou_produzidos': {
                'valor_total': '0,00',
                'linhas': [],
            },
        },
    }


def test_demonstrativo_grava_nome_e_cargo_do_substituto_e_do_conselheiro(
    associacao,
    demonstrativo_financeiro_factory,
):
    _ativa_historico_v2()
    _composicao_com_tesoureiro_e_conselheiro(associacao)
    acao = baker.make('AcaoAssociacao', associacao=associacao)

    identificacao = cria_identificacao_demonstrativo([acao], _prestacao_com_substituto())

    assert identificacao['presidente_diretoria_executiva'] == 'Carlos Tesoureiro'
    assert identificacao['cargo_substituto_presidente_ausente'] == 'Tesoureiro'
    assert identificacao['presidente_conselho_fiscal'] == 'Maria Conselheira'
    assert identificacao['cargo_conselheiro_assinatura'] == 'Conselheiro'

    payload = copy.deepcopy(dados_demonstrativo)
    payload['identificacao_apm'] = identificacao
    payload['cabecalho']['recurso'] = 'PTRF'
    payload['cabecalho']['recurso_nome_exibicao'] = 'PTRF'
    payload['previa'] = False
    payload['existe_saldo_reprogramado'] = False
    demonstrativo = demonstrativo_financeiro_factory.create()
    PersistenciaDadosDemoFinanceiro(dados=payload, demonstrativo=demonstrativo)

    gravado = DadosDemonstrativoFinanceiro.objects.get(demonstrativo=demonstrativo)
    assert gravado.presidente_diretoria_executiva == 'Carlos Tesoureiro'
    assert gravado.cargo_substituto_presidente_ausente == 'Tesoureiro'
    assert gravado.presidente_conselho_fiscal == 'Maria Conselheira'
    assert gravado.cargo_conselheiro_assinatura == 'Conselheiro'

    html = _texto(get_template('pdf/demonstrativo_financeiro/pdf-horizontal.html').render({
        'base_static_url': '',
        'dados': payload,
    }))
    assert 'Assinatura do Tesoureiro da Associação' in html
    assert 'Carlos Tesoureiro' in html
    assert 'Assinatura do Conselheiro da Associação' in html
    assert 'Maria Conselheira' in html


def test_demonstrativo_mantem_cargo_de_presidente_do_conselho_quando_nao_ha_selecao():
    payload = copy.deepcopy(dados_demonstrativo)
    payload['previa'] = False
    payload['existe_saldo_reprogramado'] = False
    payload['cabecalho']['recurso'] = 'PTRF'
    payload['cabecalho']['recurso_nome_exibicao'] = 'PTRF'
    payload['identificacao_apm'].update({
        'presidente_diretoria_executiva': 'Ana Presidente',
        'presidente_conselho_fiscal': 'Paulo Conselho',
        'cargo_substituto_presidente_ausente': 'Presidente da Diretoria Executiva',
        'cargo_conselheiro_assinatura': None,
    })
    html = _texto(get_template('pdf/demonstrativo_financeiro/pdf-horizontal.html').render({
        'base_static_url': '',
        'dados': payload,
    }))

    assert 'Assinatura do Presidente da Diretoria Executiva da Associação' in html
    assert 'Ana Presidente' in html
    assert 'Assinatura do Presidente do Conselho Fiscal da Associação' in html
    assert 'Paulo Conselho' in html


def test_relacao_de_bens_exibe_nome_e_cargo_do_substituto(associacao):
    _ativa_historico_v2()
    _composicao_com_tesoureiro_e_conselheiro(associacao)
    conta = SimpleNamespace(associacao=associacao)

    identificacao = cria_identificacao_relacao_bens(conta, _prestacao_com_substituto())

    assert identificacao['presidente_diretoria_executiva'] == 'Carlos Tesoureiro'
    assert identificacao['cargo_substituto_presidente_ausente'] == 'Tesoureiro'

    for template in ('pdf/relacao_de_bens/pdf.html', 'pdf/relacao_de_bens/pdf-v2.html'):
        html = _texto(get_template(template).render(_contexto_relacao(identificacao)))
        assert 'Assinatura do Tesoureiro da Associação' in html
        assert 'Carlos Tesoureiro' in html
