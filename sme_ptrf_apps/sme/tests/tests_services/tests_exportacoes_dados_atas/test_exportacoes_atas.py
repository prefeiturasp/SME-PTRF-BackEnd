import datetime
from tempfile import NamedTemporaryFile
import pytest
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload

from sme_ptrf_apps.sme.services.exporta_atas_service import ExportacoesAtasService
from sme_ptrf_apps.core.models.ata import Ata

pytestmark = pytest.mark.django_db

def test_cabecalho():
    dados = ExportacoesAtasService()

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        'Código EOL',
        'Nome unidade',
        'Nome associação',
        'Referência do período da PC',
        'Tipo de ata',
        'Tipo de reunião',
        'Data da reunião',
        'Hora da reunião',
        'Local da reunião',
        'Convocação',
        'Presidente da reunião',
        'Cargo do presidente',
        'Secretário da reunião',
        'Cargo do secretário',
        'Justificativas de repasses pendentes',
        'Manifestações',
        'Retificações',
        'Parecer dos presentes',
        'Data e hora de preenchimento',
        'URL do arquivo PDF',
        'Status',
        'Data e hora de criação',
        'Data e hora da última atualização'
    ]

    assert cabecalho == resultado_esperado

def test_dados_esperados_csv(queryset_ordered, ambiente):
    dados = ExportacoesAtasService(queryset=queryset_ordered).monta_dados()

    linha_individual = dados[0]
    ata = queryset_ordered.first()
    
    resultado_esperado = [
        ata.associacao.unidade.codigo_eol,
        ata.associacao.unidade.nome,
        ata.associacao.nome,
        ata.periodo.referencia,
        ata.tipo_ata,
        ata.tipo_reuniao,
        ata.data_reuniao.strftime("%d/%m/%Y"),
        ata.hora_reuniao.strftime("%H:%M"),
        ata.local_reuniao,
        ata.convocacao,
        ata.presidente_reuniao,
        ata.cargo_presidente_reuniao,
        ata.secretario_reuniao,
        ata.cargo_secretaria_reuniao,
        ata.justificativa_repasses_pendentes,
        ata.comentarios,
        ata.retificacoes,
        ata.parecer_conselho,
        ata.preenchida_em.strftime("%d/%m/%Y"),
        f"https://{ambiente.prefixo}.sme.prefeitura.sp.gov.br{ata.arquivo_pdf.url}",
        ata.status_geracao_pdf,
        ata.criado_em.strftime("%d/%m/%Y às %H:%M:%S"),
        ata.alterado_em.strftime("%d/%m/%Y às %H:%M:%S"),
    ]

    assert linha_individual == resultado_esperado

def test_rodape(queryset_ordered, ambiente):
    dados = ExportacoesAtasService(
        queryset=queryset_ordered,
    ).texto_rodape()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo gerado pelo {ambiente.prefixo} em {data_atual}"

    assert dados == resultado_esperado

def test_filtra_range_data_fora_do_range(queryset_ordered):
    data_inicio = datetime.date(2020, 2, 10)
    data_final = datetime.date(2020, 5, 10)

    queryset_filtrado = ExportacoesAtasService(
        queryset=queryset_ordered,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == 0

def test_filtra_range_data_dentro_do_range(queryset_ordered):
    data_inicio = datetime.date.today()
    data_final = datetime.date.today()

    queryset_filtrado = ExportacoesAtasService(
        queryset=queryset_ordered,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)

def test_filtra_range_data_com_data_inicio_e_sem_data_final(queryset_ordered):
    data_inicio = datetime.date.today()

    queryset_filtrado = ExportacoesAtasService(
        queryset=queryset_ordered,
        data_inicio=data_inicio
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)

def test_filtra_range_data_sem_data_inicio_e_com_data_final(queryset_ordered):
    data_final = datetime.date.today()

    queryset_filtrado = ExportacoesAtasService(
        queryset=queryset_ordered,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)

def test_filtra_range_data_sem_data_inicio_e_sem_data_final(queryset_ordered):
    queryset_filtrado = ExportacoesAtasService(
        queryset=queryset_ordered
    ).filtra_range_data('criado_em')
    
    assert queryset_filtrado.count() == len(queryset_ordered)

def test_cria_registro_central_download(usuario_para_teste):
    exportacao_saldo_final = ExportacoesAtasService(
        nome_arquivo='pcs_atas.csv',
        user=usuario_para_teste.username
    )

    exportacao_saldo_final.cria_registro_central_download()
    objeto_arquivo_download = exportacao_saldo_final.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_EM_PROCESSAMENTO
    assert objeto_arquivo_download.identificador == 'pcs_atas.csv'
    assert ArquivoDownload.objects.count() == 1

def test_envia_arquivo_central_download(usuario_para_teste):
    with NamedTemporaryFile(
        mode="r+",
        newline='',
        encoding='utf-8',
        prefix='pcs_atas',
        suffix='.csv'
    ) as file:
        file.write("testando central de download")

        exportacao_atas = ExportacoesAtasService(
            nome_arquivo='pcs_atas.csv',
            user=usuario_para_teste.username
        )
        exportacao_atas.cria_registro_central_download()
        exportacao_atas.envia_arquivo_central_download(file)
        objeto_arquivo_download = exportacao_atas.objeto_arquivo_download

    assert objeto_arquivo_download.status == ArquivoDownload.STATUS_CONCLUIDO
    assert objeto_arquivo_download.identificador == 'pcs_atas.csv'
    assert ArquivoDownload.objects.count() == 1