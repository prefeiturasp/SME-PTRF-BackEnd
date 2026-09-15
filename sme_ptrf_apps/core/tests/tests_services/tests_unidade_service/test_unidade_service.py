from unittest.mock import MagicMock, patch

import pytest
from model_bakery import baker

from sme_ptrf_apps.core.models import Unidade
from sme_ptrf_apps.core.services.unidade_service import (
    atualiza_dados_pessoais_unidade,
    atualiza_dados_unidade,
    atualiza_diretor_unidade,
    consulta_unidade,
    monta_unidade_para_atribuicao,
)

pytestmark = pytest.mark.django_db

MODULE = 'sme_ptrf_apps.core.services.unidade_service'


# monta_unidade_para_atribuicao

def test_monta_unidade_para_atribuicao_sem_atribuicao(dre, unidade, periodo_2020_1):
    result = monta_unidade_para_atribuicao(Unidade.objects.all(), str(dre.uuid), str(periodo_2020_1.uuid))

    assert len(result) == 1
    item = result[0]
    assert item['uuid'] == str(unidade.uuid)
    assert item['codigo_eol'] == unidade.codigo_eol
    assert item['nome'] == f'{unidade.tipo_unidade} {unidade.nome}'
    assert item['atribuicao'] == {'id': '', 'tecnico': {}}


def test_monta_unidade_para_atribuicao_com_atribuicao(dre, unidade, periodo_2020_1):
    tecnico = baker.make('TecnicoDre', dre=dre, nome='Fulano de Tal', rf='1234567')
    atribuicao = baker.make(
        'Atribuicao',
        unidade=unidade,
        periodo=periodo_2020_1,
        tecnico=tecnico,
    )

    result = monta_unidade_para_atribuicao(Unidade.objects.all(), str(dre.uuid), str(periodo_2020_1.uuid))

    assert len(result) == 1
    item = result[0]
    assert item['atribuicao']['id'] == atribuicao.id
    assert item['atribuicao']['tecnico']['nome'] == 'Fulano de Tal'


def test_monta_unidade_para_atribuicao_filtra_por_dre(dre, dre_ipiranga, unidade, periodo_2020_1):
    outra_unidade = baker.make(
        'Unidade', nome='Outra escola', tipo_unidade='CEU', codigo_eol='555555', dre=dre_ipiranga,
    )

    result = monta_unidade_para_atribuicao(Unidade.objects.all(), str(dre.uuid), str(periodo_2020_1.uuid))

    uuids = [item['uuid'] for item in result]
    assert str(unidade.uuid) in uuids
    assert str(outra_unidade.uuid) not in uuids


# atualiza_dados_unidade

def test_atualiza_dados_unidade_chama_as_duas_atualizacoes(associacao):
    with patch(f'{MODULE}.atualiza_dados_pessoais_unidade') as mock_pessoais, \
            patch(f'{MODULE}.atualiza_diretor_unidade') as mock_diretor:
        atualiza_dados_unidade(associacao)

    mock_pessoais.assert_called_once_with(associacao.unidade)
    mock_diretor.assert_called_once_with(associacao.unidade)


# atualiza_dados_pessoais_unidade

def _mock_response(json_data):
    mock = MagicMock()
    mock.json.return_value = json_data
    return mock


def test_atualiza_dados_pessoais_unidade_sem_nome_nao_atualiza(unidade):
    nome_original = unidade.nome

    with patch(f'{MODULE}.SmeIntegracaoService.get_dados_unidade_eol') as mock_get:
        mock_get.return_value = _mock_response({'nome': ''})

        atualiza_dados_pessoais_unidade(unidade)

    unidade.refresh_from_db()
    assert unidade.nome == nome_original


def test_atualiza_dados_pessoais_unidade_atualiza_com_sigla_tipo_escola(unidade):
    dados = {
        'nome': 'Escola Nova',
        'email': 'nova@sme.sp.gov.br',
        'telefone': '11999999999',
        'numero': '100',
        'tipoLogradouro': 'Rua',
        'logradouro': 'das Flores',
        'bairro': 'Centro',
        'cep': 1234567,
        'siglaTipoEscola': ' EMEF ',
    }

    with patch(f'{MODULE}.SmeIntegracaoService.get_dados_unidade_eol') as mock_get:
        mock_get.return_value = _mock_response(dados)

        atualiza_dados_pessoais_unidade(unidade)

    unidade.refresh_from_db()
    assert unidade.nome == 'Escola Nova'
    assert unidade.tipo_unidade == 'EMEF'
    assert unidade.cep == '01234567'


def test_atualiza_dados_pessoais_unidade_sem_sigla_tipo_escola_usa_ceu(unidade):
    dados = {
        'nome': 'Escola Nova',
        'cep': 1234567,
        'siglaTipoEscola': None,
    }

    with patch(f'{MODULE}.SmeIntegracaoService.get_dados_unidade_eol') as mock_get:
        mock_get.return_value = _mock_response(dados)

        atualiza_dados_pessoais_unidade(unidade)

    unidade.refresh_from_db()
    assert unidade.tipo_unidade == 'CEU'


def test_atualiza_dados_pessoais_unidade_exception_nao_propaga(unidade):
    with patch(f'{MODULE}.SmeIntegracaoService.get_dados_unidade_eol') as mock_get:
        mock_get.side_effect = Exception('erro de conexão')

        # não deve levantar exceção
        atualiza_dados_pessoais_unidade(unidade)


# atualiza_diretor_unidade

def test_atualiza_diretor_unidade_com_resultado(unidade):
    with patch(f'{MODULE}.requests.get') as mock_get:
        mock_get.return_value = _mock_response([{'nomeServidor': 'Maria Diretora'}])

        atualiza_diretor_unidade(unidade)

    assert unidade.diretor_nome == 'Maria Diretora'


def test_atualiza_diretor_unidade_sem_resultado(unidade):
    diretor_original = unidade.diretor_nome

    with patch(f'{MODULE}.requests.get') as mock_get:
        mock_get.return_value = _mock_response([])

        atualiza_diretor_unidade(unidade)

    assert unidade.diretor_nome == diretor_original


def test_atualiza_diretor_unidade_exception_nao_propaga(unidade):
    with patch(f'{MODULE}.requests.get') as mock_get:
        mock_get.side_effect = Exception('timeout')

        # não deve levantar exceção
        atualiza_diretor_unidade(unidade)


# consulta_unidade

def test_consulta_unidade_codigo_eol_invalido():
    result = consulta_unidade('123')

    assert result['erro'] == 'codigo_eol_inválido'


def test_consulta_unidade_ja_cadastrada(associacao):
    result = consulta_unidade(associacao.unidade.codigo_eol)

    assert result['erro'] == 'codigo_eol_ja_cadastrado'


def test_consulta_unidade_encontrada_sem_associacao(unidade):
    result = consulta_unidade(unidade.codigo_eol)

    assert 'erro' not in result
    assert result['codigo_eol'] == unidade.codigo_eol
    assert result['nome'] == unidade.nome
    assert result['nome_dre'] == unidade.dre.nome
    assert result['tipo_unidade'] == unidade.tipo_unidade
    assert result['cep'] == unidade.cep.zfill(8)


def test_consulta_unidade_encontrada_sem_dre():
    unidade_sem_dre = baker.make(
        'Unidade', nome='Escola sem dre', tipo_unidade='CEU', codigo_eol='222222', dre=None, cep='1234567',
    )

    result = consulta_unidade(unidade_sem_dre.codigo_eol)

    assert result['nome_dre'] == ''


def test_consulta_unidade_nao_encontrada_consulta_servico(unidade):
    dados = {
        'codigo': '333333',
        'nome': 'Escola Nova EOL',
        'nomeDRE': 'DRE Nova',
        'siglaTipoEscola': ' EMEF ',
        'email': 'x@y.com',
        'telefone': '1199999999',
        'numero': '10',
        'tipoLogradouro': 'Rua',
        'logradouro': 'das Palmeiras',
        'bairro': 'Centro',
        'cep': 1234567,
    }

    with patch(f'{MODULE}.SmeIntegracaoService.get_dados_unidade_eol') as mock_get:
        mock_get.return_value = _mock_response(dados)

        result = consulta_unidade('333333')

    assert 'erro' not in result
    assert result['codigo_eol'] == '333333'
    assert result['nome'] == 'Escola Nova EOL'
    assert result['nome_dre'] == 'DRE Nova'
    assert result['tipo_unidade'] == 'EMEF'
    assert result['cep'] == '01234567'


def test_consulta_unidade_nao_encontrada_sem_sigla_tipo_escola():
    dados = {
        'codigo': '444444',
        'nome': 'Escola Nova EOL',
        'siglaTipoEscola': None,
        'cep': 1234567,
    }

    with patch(f'{MODULE}.SmeIntegracaoService.get_dados_unidade_eol') as mock_get:
        mock_get.return_value = _mock_response(dados)

        result = consulta_unidade('444444')

    assert result['tipo_unidade'] == ''


def test_consulta_unidade_codigo_nao_encontrado_no_servico():
    dados = {'codigo': None}

    with patch(f'{MODULE}.SmeIntegracaoService.get_dados_unidade_eol') as mock_get:
        mock_get.return_value = _mock_response(dados)

        result = consulta_unidade('555555')

    assert result['erro'] == 'erro'
    assert result['mensagem'] == 'Código EOL não encontrado'


def test_consulta_unidade_erro_generico_ao_consultar_servico():
    with patch(f'{MODULE}.SmeIntegracaoService.get_dados_unidade_eol') as mock_get:
        mock_get.side_effect = Exception('erro de conexão')

        result = consulta_unidade('666666')

    assert result['erro'] == 'erro'
    assert 'erro de conexão' in result['mensagem']
