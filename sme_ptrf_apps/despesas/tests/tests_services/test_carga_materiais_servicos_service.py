"""
Testes para CargaMateriaisServicosService: parsing/validação de linhas do CSV,
criação/atualização de EspecificacaoMaterialServico e cálculo do status do arquivo de carga.
"""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from sme_ptrf_apps.despesas.models import EspecificacaoMaterialServico
from sme_ptrf_apps.despesas.services.carga_materiais_servicos_service import (
    CargaMateriaisServicosException,
    CargaMateriaisServicosService,
)
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO

from sme_ptrf_apps.core.choices.tipos_carga import CARGA_MATERIAIS_SERVICOS
from sme_ptrf_apps.core.models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    PROCESSADO_COM_ERRO,
    SUCESSO,
)

pytestmark = pytest.mark.django_db

CABECALHO_CAMPOS = list(CargaMateriaisServicosService.CABECALHOS.values())
CABECALHO = ';'.join(CABECALHO_CAMPOS)


def monta_linha(id_registro='', descricao='Papel A4', aplicacao='CUSTEIO', id_tipo_custeio='',
                nome_tipo_custeio='', ativa='Sim', delimitador=';') -> str:
    """Monta uma linha de CSV na ordem de colunas esperada pelo serviço de carga."""
    campos = [str(id_registro), descricao, aplicacao, str(id_tipo_custeio), nome_tipo_custeio, ativa]
    return delimitador.join(campos)


def monta_csv(linhas: list, cabecalho: str = CABECALHO) -> bytes:
    """Monta o conteúdo (bytes utf-8) de um arquivo CSV a partir de um cabeçalho e uma lista de linhas."""
    conteudo = '\n'.join([cabecalho] + linhas)
    return bytes(conteudo, encoding='utf-8')


@pytest.fixture
def service():
    return CargaMateriaisServicosService()


@pytest.fixture
def tipo_custeio_material(tipo_custeio_factory):
    return tipo_custeio_factory(nome='Material')


@pytest.fixture
def especificacao_existente(especificacao_material_servico_factory, tipo_custeio_material):
    return especificacao_material_servico_factory(
        descricao='Descrição antiga',
        aplicacao_recurso=APLICACAO_CUSTEIO,
        tipo_custeio=tipo_custeio_material,
        ativa=False,
    )


class TestInicializaLogsEContadores:
    def test_inicializa_log_reseta_estado(self, service):
        service.logs = 'algo registrado antes'
        service.importados = 5
        service.erros = 2

        service.inicializa_log()

        assert service.logs == ''
        assert service.importados == 0
        assert service.erros == 0

    def test_loga_erro_incrementa_contador_e_grava_mensagem(self, service):
        service.inicializa_log()

        service.loga_erro_carga_materiais_servicos('falha ao processar', linha=3)

        assert service.erros == 1
        assert 'Linha: 3 Erro: falha ao processar' in service.logs

    def test_loga_sucesso_incrementa_contador_de_importados(self, service):
        service.inicializa_log()

        service.loga_sucesso_carga_materiais_servicos()

        assert service.importados == 1


class TestCarregaEValidaDadosTipoCusteio:
    def test_linha_valida_custeio_retorna_dados_e_atualiza_linha_index(self, service, tipo_custeio_material):
        linha = ['', 'Papel A4', APLICACAO_CUSTEIO, str(tipo_custeio_material.id), tipo_custeio_material.nome, 'Sim']

        dados = service.carrega_e_valida_dados_tipo_custeio(linha_conteudo=linha, linha_index=1)

        assert dados == {
            'id': None,
            'descricao': 'Papel A4',
            'aplicacao_recurso': APLICACAO_CUSTEIO,
            'tipo_custeio_id': str(tipo_custeio_material.id),
            'ativa': True,
        }
        assert service.linha_index == 1

    def test_linha_valida_capital_nao_exige_tipo_custeio(self, service):
        linha = ['5', 'Ar condicionado', APLICACAO_CAPITAL, '', '', 'Não']

        dados = service.carrega_e_valida_dados_tipo_custeio(linha_conteudo=linha, linha_index=2)

        assert dados['id'] == 5
        assert dados['tipo_custeio_id'] is None
        assert dados['ativa'] is False

    def test_tipo_custeio_inexistente_gera_excecao(self, service):
        linha = ['', 'Papel A4', APLICACAO_CUSTEIO, '999999', 'Inexistente', 'Sim']

        with pytest.raises(CargaMateriaisServicosException, match='id do tipo de custeio 999999 é inválido'):
            service.carrega_e_valida_dados_tipo_custeio(linha_conteudo=linha, linha_index=1)

    def test_aplicacao_invalida_gera_excecao(self, service):
        linha = ['', 'Papel A4', 'OUTRO', '', '', 'Sim']

        with pytest.raises(CargaMateriaisServicosException, match='deveria ser no padrão string de CAPITAL ou CUSTEIO'):
            service.carrega_e_valida_dados_tipo_custeio(linha_conteudo=linha, linha_index=1)

    def test_custeio_sem_id_tipo_custeio_gera_excecao(self, service):
        linha = ['', 'Papel A4', APLICACAO_CUSTEIO, '', '', 'Sim']

        with pytest.raises(CargaMateriaisServicosException, match='sem o campo ID preenchido'):
            service.carrega_e_valida_dados_tipo_custeio(linha_conteudo=linha, linha_index=1)

    def test_id_tipo_custeio_nao_numerico_propaga_value_error(self, service):
        """Documenta comportamento atual: o método só trata TipoCusteio.DoesNotExist, então um
        ID não numérico propaga ValueError em vez de CargaMateriaisServicosException. A linha ainda
        é reportada como erro porque processa_materiais_servicos captura Exception de forma ampla."""
        linha = ['', 'Papel A4', APLICACAO_CUSTEIO, 'abc', 'Nome', 'Sim']

        with pytest.raises(ValueError):
            service.carrega_e_valida_dados_tipo_custeio(linha_conteudo=linha, linha_index=1)


class TestCriaOuAtualizaEspecificacaoMaterialServico:
    def test_cria_novo_registro_quando_id_nao_informado(self, service, tipo_custeio_material):
        service.dados_materiais_servicos = {
            'id': None,
            'descricao': 'Novo material',
            'aplicacao_recurso': APLICACAO_CUSTEIO,
            'tipo_custeio_id': tipo_custeio_material.id,
            'ativa': True,
        }

        service.cria_ou_atualiza_especificacao_material_servico()

        especificacao = EspecificacaoMaterialServico.objects.get(descricao='Novo material')
        assert especificacao.tipo_custeio_id == tipo_custeio_material.id
        assert especificacao.ativa is True

    def test_atualiza_registro_existente_quando_id_informado(self, service, especificacao_existente,
                                                             tipo_custeio_material):
        service.dados_materiais_servicos = {
            'id': especificacao_existente.id,
            'descricao': 'Descrição atualizada',
            'aplicacao_recurso': APLICACAO_CUSTEIO,
            'tipo_custeio_id': tipo_custeio_material.id,
            'ativa': True,
        }

        service.cria_ou_atualiza_especificacao_material_servico()

        especificacao_existente.refresh_from_db()
        assert especificacao_existente.descricao == 'Descrição atualizada'
        assert especificacao_existente.ativa is True
        assert EspecificacaoMaterialServico.objects.count() == 1


class TestAtualizaStatusArquivo:
    def test_sucesso_quando_ha_importados_e_nenhum_erro(self, service, arquivo_factory):
        arquivo = arquivo_factory(identificador='carga-status-sucesso')
        service.importados = 2
        service.erros = 0

        service.atualiza_status_arquivo(arquivo)

        arquivo.refresh_from_db()
        assert arquivo.status == SUCESSO
        assert '2 linha(s) importada(s) com sucesso. 0 erro(s) reportado(s).' in arquivo.log

    def test_processado_com_erro_quando_ha_importados_e_erros(self, service, arquivo_factory):
        arquivo = arquivo_factory(identificador='carga-status-parcial')
        service.importados = 1
        service.erros = 1

        service.atualiza_status_arquivo(arquivo)

        arquivo.refresh_from_db()
        assert arquivo.status == PROCESSADO_COM_ERRO

    def test_erro_quando_nenhuma_linha_importada(self, service, arquivo_factory):
        arquivo = arquivo_factory(identificador='carga-status-erro')
        service.importados = 0
        service.erros = 3

        service.atualiza_status_arquivo(arquivo)

        arquivo.refresh_from_db()
        assert arquivo.status == ERRO


class TestVerificaEstruturaCabecalho:
    def test_cabecalho_correto_retorna_true(self):
        assert CargaMateriaisServicosService.verifica_estrutura_cabecalho(CABECALHO_CAMPOS) is True

    def test_cabecalho_incorreto_gera_excecao(self):
        cabecalho_incorreto = ['Id'] + CABECALHO_CAMPOS[1:]

        with pytest.raises(CargaMateriaisServicosException, match='Título da coluna 0 errado'):
            CargaMateriaisServicosService.verifica_estrutura_cabecalho(cabecalho_incorreto)


class TestProcessaMateriaisServicos:
    def test_processa_com_sucesso_cria_e_atualiza_registros(self, service, arquivo_factory, tipo_custeio_material,
                                                            especificacao_existente):
        reader = [
            CABECALHO_CAMPOS,
            ['', 'Papel A4', APLICACAO_CUSTEIO, str(tipo_custeio_material.id), tipo_custeio_material.nome, 'Sim'],
            [str(especificacao_existente.id), 'Descrição atualizada', APLICACAO_CUSTEIO,
             str(tipo_custeio_material.id), tipo_custeio_material.nome, 'Sim'],
        ]
        arquivo = arquivo_factory(identificador='carga-processa-sucesso')

        service.processa_materiais_servicos(reader=reader, arquivo=arquivo)

        arquivo.refresh_from_db()
        assert arquivo.status == SUCESSO
        assert service.importados == 2
        assert service.erros == 0
        assert EspecificacaoMaterialServico.objects.filter(descricao='Papel A4').exists()
        especificacao_existente.refresh_from_db()
        assert especificacao_existente.descricao == 'Descrição atualizada'

    def test_processa_linha_invalida_reporta_erro_e_nao_interrompe_as_demais(self, service, arquivo_factory,
                                                                             tipo_custeio_material):
        reader = [
            CABECALHO_CAMPOS,
            ['', 'Papel A4', 'OUTRO', '', '', 'Sim'],
            ['', 'Caneta', APLICACAO_CUSTEIO, str(tipo_custeio_material.id), tipo_custeio_material.nome, 'Sim'],
        ]
        arquivo = arquivo_factory(identificador='carga-processa-linha-invalida')

        service.processa_materiais_servicos(reader=reader, arquivo=arquivo)

        arquivo.refresh_from_db()
        assert arquivo.status == PROCESSADO_COM_ERRO
        assert service.importados == 1
        assert service.erros == 1
        assert 'Linha: 1' in arquivo.log
        assert EspecificacaoMaterialServico.objects.filter(descricao='Caneta').exists()
        assert not EspecificacaoMaterialServico.objects.filter(descricao='Papel A4').exists()

    def test_processa_cabecalho_incorreto_gera_status_erro_sem_processar_linhas(self, service, arquivo_factory):
        reader = [
            ['Id'] + CABECALHO_CAMPOS[1:],
            ['', 'Papel A4', APLICACAO_CUSTEIO, '', '', 'Sim'],
        ]
        arquivo = arquivo_factory(identificador='carga-processa-cabecalho-incorreto')

        service.processa_materiais_servicos(reader=reader, arquivo=arquivo)

        arquivo.refresh_from_db()
        assert arquivo.status == ERRO
        assert service.importados == 0
        assert 'Título da coluna 0 errado' in arquivo.log
        assert EspecificacaoMaterialServico.objects.count() == 0


class TestCarregaMateriaisServicos:
    def test_delimitador_diferente_do_declarado_gera_erro_sem_processar(self, service, arquivo_factory,
                                                                        tipo_custeio_material):
        conteudo = SimpleUploadedFile(
            'materiais_servicos.csv',
            monta_csv([monta_linha(id_tipo_custeio=tipo_custeio_material.id,
                                   nome_tipo_custeio=tipo_custeio_material.nome)]))
        arquivo = arquivo_factory(
            identificador='carga-delimitador-diferente',
            conteudo=conteudo,
            tipo_carga=CARGA_MATERIAIS_SERVICOS,
            tipo_delimitador=DELIMITADOR_VIRGULA,
        )

        service.carrega_materiais_servicos(arquivo)

        arquivo.refresh_from_db()
        assert arquivo.status == ERRO
        assert 'Formato definido (DELIMITADOR_VIRGULA) é diferente do formato do arquivo csv ' \
               '(DELIMITADOR_PONTO_VIRGULA)' in arquivo.log
        assert EspecificacaoMaterialServico.objects.count() == 0

    def test_delimitador_nao_suportado_gera_erro_generico(self, service, arquivo_factory):
        conteudo = SimpleUploadedFile('materiais_servicos.csv', monta_csv([], cabecalho='|'.join(CABECALHO_CAMPOS)))
        arquivo = arquivo_factory(
            identificador='carga-delimitador-invalido',
            conteudo=conteudo,
            tipo_carga=CARGA_MATERIAIS_SERVICOS,
            tipo_delimitador=DELIMITADOR_PONTO_VIRGULA,
        )

        service.carrega_materiais_servicos(arquivo)

        arquivo.refresh_from_db()
        assert 'Erro ao processar materiais e serviços' in arquivo.log
        assert arquivo.status == ERRO

    def test_carga_com_sucesso_cria_registros_e_seta_ultima_execucao(self, service, arquivo_factory,
                                                                     tipo_custeio_material):
        conteudo = SimpleUploadedFile(
            'materiais_servicos.csv',
            monta_csv([
                monta_linha(descricao='Papel A4', aplicacao=APLICACAO_CUSTEIO,
                            id_tipo_custeio=tipo_custeio_material.id, nome_tipo_custeio=tipo_custeio_material.nome),
                monta_linha(descricao='Ar condicionado', aplicacao=APLICACAO_CAPITAL, ativa='Não'),
            ]))
        arquivo = arquivo_factory(
            identificador='carga-sucesso',
            conteudo=conteudo,
            tipo_carga=CARGA_MATERIAIS_SERVICOS,
            tipo_delimitador=DELIMITADOR_PONTO_VIRGULA,
        )

        service.carrega_materiais_servicos(arquivo)

        arquivo.refresh_from_db()
        assert arquivo.status == SUCESSO
        assert arquivo.ultima_execucao is not None
        assert EspecificacaoMaterialServico.objects.filter(descricao='Papel A4', ativa=True).exists()
        assert EspecificacaoMaterialServico.objects.filter(descricao='Ar condicionado', ativa=False).exists()

    def test_carga_com_cabecalho_incorreto_gera_status_erro(self, service, arquivo_factory):
        conteudo = SimpleUploadedFile(
            'materiais_servicos.csv',
            monta_csv([monta_linha()], cabecalho=';'.join(['Id'] + CABECALHO_CAMPOS[1:])))
        arquivo = arquivo_factory(
            identificador='carga-cabecalho-incorreto',
            conteudo=conteudo,
            tipo_carga=CARGA_MATERIAIS_SERVICOS,
            tipo_delimitador=DELIMITADOR_PONTO_VIRGULA,
        )

        service.carrega_materiais_servicos(arquivo)

        arquivo.refresh_from_db()
        assert arquivo.status == ERRO
        assert 'Título da coluna 0 errado' in arquivo.log
        assert EspecificacaoMaterialServico.objects.count() == 0
