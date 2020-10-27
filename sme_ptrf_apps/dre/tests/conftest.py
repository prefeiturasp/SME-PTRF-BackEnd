import pytest
from freezegun import freeze_time
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker


@pytest.fixture
def grupo_verificacao_regularidade_documentos():
    return baker.make('GrupoVerificacaoRegularidade', titulo='Documentos')


@pytest.fixture
def lista_verificacao_regularidade_documentos_associacao(grupo_verificacao_regularidade_documentos):
    return baker.make(
        'ListaVerificacaoRegularidade',
        titulo='Documentos da Associação',
        grupo=grupo_verificacao_regularidade_documentos
    )


@pytest.fixture
def item_verificacao_regularidade_documentos_associacao_cnpj(lista_verificacao_regularidade_documentos_associacao):
    return baker.make(
        'ItemVerificacaoRegularidade',
        descricao='CNPJ',
        lista=lista_verificacao_regularidade_documentos_associacao
    )


@pytest.fixture
def verificacao_regularidade_associacao_documento_cnpj(grupo_verificacao_regularidade_documentos, lista_verificacao_regularidade_documentos_associacao,item_verificacao_regularidade_documentos_associacao_cnpj, associacao):
    return baker.make(
        'VerificacaoRegularidadeAssociacao',
        associacao=associacao,
        grupo_verificacao=grupo_verificacao_regularidade_documentos,
        lista_verificacao=lista_verificacao_regularidade_documentos_associacao,
        item_verificacao=item_verificacao_regularidade_documentos_associacao_cnpj,
        regular=True
    )


@pytest.fixture
def tecnico_dre(dre):
    return baker.make(
        'TecnicoDre',
        dre=dre,
        nome='José Testando',
        rf='271170',
        email='tecnico.sobrenome@sme.prefeitura.sp.gov.br',
        telefone='1259275127'
    )


@pytest.fixture
def faq_categoria():
    return baker.make(
        'FaqCategoria',
        nome='Geral'
    )


@pytest.fixture
def faq_categoria_02():
    return baker.make(
        'FaqCategoria',
        nome='Associações'
    )


@pytest.fixture
def faq(faq_categoria):
    return baker.make(
        'Faq',
        pergunta='Pergunta 01 - Cat Geral 01',
        resposta='Esta é a resposta da Pergunta 01',
        categoria=faq_categoria
    )


@pytest.fixture
def faq_02(faq_categoria_02):
    return baker.make(
        'Faq',
        pergunta='Pergunta 02 - Cat Associações 01',
        resposta='Esta é a resposta da Pergunta 02',
        categoria=faq_categoria_02
    )


@pytest.fixture
def atribuicao(tecnico_dre, unidade, periodo):
    return baker.make(
        'Atribuicao',
        tecnico=tecnico_dre,
        unidade=unidade,
        periodo=periodo,
    )

@pytest.fixture
def arquivo():
    return SimpleUploadedFile(f'arquivo.txt', bytes(f'CONTEUDO TESTE TESTE TESTE', encoding="utf-8"))


@pytest.fixture
@freeze_time('2020-10-27 13:59:00')
def relatorio_dre_consolidado_gerado_total(periodo, dre, tipo_conta_cartao, arquivo):
    return baker.make(
        'RelatorioConsolidadoDre',
        dre=dre,
        tipo_conta=tipo_conta_cartao,
        periodo=periodo,
        arquivo=arquivo,
        status='GERADO_TOTAL'
    )
