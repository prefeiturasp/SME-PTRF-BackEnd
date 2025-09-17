import pytest
import datetime

from sme_ptrf_apps.sme.services.exporta_status_prestacoes_conta_service import ExportacoesStatusPrestacoesContaService

pytestmark = pytest.mark.django_db

resultado_esperado = [
    ['123456', 'Escola Teste', 'Escola Teste', 'DRE teste', '2019.2', 'APROVADA_RESSALVA',
     'Motivo aprovação 1; Motivo aprovação 2; Teste outro motivo aprovação ressalva', 'Recomendação teste', ''],
    ['123456', 'Escola Teste', 'Outra', 'DRE teste', '2019.2', 'REPROVADA', '', '',
     'Motivo reprovação 1; Motivo reprovação 2; Teste outro motivo reprovação']
]

resultado_pcs_nao_apresentadas = [
    ['123456', 'Escola Teste', 'Escola Teste', 'DRE teste', '2019.3', 'NAO_APRESENTADA'],
    ['123456', 'Escola Teste', 'Outra', 'DRE teste', '2019.3', 'NAO_APRESENTADA'],
    ['123456', 'Escola Teste', 'Outra', 'DRE teste', '2020.1', 'NAO_APRESENTADA']]


def test_dados_esperados_csv(queryset_ordered):
    dados = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered
    ).monta_dados()

    assert dados == resultado_esperado


def test_dados_esperados_csv_visao_dre(queryset_ordered, dre):
    dados = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered,
        dre_uuid=f"{dre.uuid}"

    ).monta_dados()

    assert dados == resultado_esperado


def test_dados_esperados_csv_visao_dre_sem_pcs(queryset_ordered_dre_sem_pcs, dre_ipiranga):
    dados = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered_dre_sem_pcs,
        dre_uuid=f"{dre_ipiranga.uuid}"

    ).monta_dados()

    assert dados == []


def test_dados_esperados_pcs_nao_apresentadas_csv(queryset_ordered, periodo_factory):
    data_inicio = datetime.date(2019, 1, 10)
    data_final = datetime.date(2020, 12, 29)

    periodo_2019_3 = periodo_factory.create(referencia='2019.3',
                                            data_inicio_realizacao_despesas=datetime.date(2019, 12, 1),
                                            data_fim_realizacao_despesas=datetime.date(2019, 12, 31))

    periodo_factory.create(periodo_anterior=periodo_2019_3, referencia='2020.1',
                           data_inicio_realizacao_despesas=datetime.date(2020, 1, 1),
                           data_fim_realizacao_despesas=datetime.date(2020, 12, 31))

    servico = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered,
        data_inicio=data_inicio,
        data_final=data_final
    )

    servico.define_periodos_selecionados_no_range_do_filtro_de_data()
    pcs_nao_apresentadas = servico.monta_dados_pcs_nao_apresentadas()

    # Existem apenas 3 "pcs" não apresentadas, já que uma foi encerrada no periodo 2019.3
    assert resultado_pcs_nao_apresentadas == pcs_nao_apresentadas


def test_dados_esperados_pcs_nao_apresentadas_csv_visao_dre(queryset_ordered, periodo_factory, dre):
    data_inicio = datetime.date(2019, 1, 10)
    data_final = datetime.date(2020, 12, 29)

    periodo_2019_3 = periodo_factory.create(referencia='2019.3',
                                            data_inicio_realizacao_despesas=datetime.date(2019, 12, 1),
                                            data_fim_realizacao_despesas=datetime.date(2019, 12, 31))

    periodo_factory.create(periodo_anterior=periodo_2019_3, referencia='2020.1',
                           data_inicio_realizacao_despesas=datetime.date(2020, 1, 1),
                           data_fim_realizacao_despesas=datetime.date(2020, 12, 31))

    servico = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered,
        data_inicio=data_inicio,
        data_final=data_final,
        dre_uuid=f"{dre.uuid}"
    )

    servico.define_periodos_selecionados_no_range_do_filtro_de_data()
    pcs_nao_apresentadas = servico.monta_dados_pcs_nao_apresentadas()

    # Existem apenas 3 "pcs" não apresentadas, já que uma foi encerrada no periodo 2019.3
    assert resultado_pcs_nao_apresentadas == pcs_nao_apresentadas


def test_dados_esperados_pcs_nao_apresentadas_csv_visao_dre_sem_pcs(queryset_ordered_dre_sem_pcs, periodo_factory, dre_ipiranga):
    data_inicio = datetime.date(2019, 1, 10)
    data_final = datetime.date(2020, 12, 29)

    periodo_2019_3 = periodo_factory.create(referencia='2019.3',
                                            data_inicio_realizacao_despesas=datetime.date(2019, 12, 1),
                                            data_fim_realizacao_despesas=datetime.date(2019, 12, 31))

    periodo_factory.create(periodo_anterior=periodo_2019_3, referencia='2020.1',
                           data_inicio_realizacao_despesas=datetime.date(2020, 1, 1),
                           data_fim_realizacao_despesas=datetime.date(2020, 12, 31))

    servico = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered_dre_sem_pcs,
        data_inicio=data_inicio,
        data_final=data_final,
        dre_uuid=f"{dre_ipiranga.uuid}"
    )

    servico.define_periodos_selecionados_no_range_do_filtro_de_data()
    pcs_nao_apresentadas = servico.monta_dados_pcs_nao_apresentadas()

    assert pcs_nao_apresentadas == []


def test_cabecalho(queryset_ordered):
    dados = ExportacoesStatusPrestacoesContaService(queryset=queryset_ordered)

    cabecalho = [cabecalho[0] for cabecalho in dados.cabecalho]

    resultado_esperado = [
        'Código EOL',
        'Nome Unidade',
        'Nome Associação',
        'DRE',
        'Referência do Período da PC',
        'Status da PC',
        'Descrição do motivo aprovação com ressalvas',
        'Recomendações da aprovação com resalvas',
        'Descrição do motivo de reprovação',
    ]

    assert cabecalho == resultado_esperado


def test_rodape(ambiente):
    dados = ExportacoesStatusPrestacoesContaService().texto_rodape()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo gerado pelo {ambiente.prefixo} em {data_atual}"

    assert dados == resultado_esperado


def test_info_arquivo_gerado(ambiente):
    dados = ExportacoesStatusPrestacoesContaService(user='12345').texto_info_arquivo_gerado()

    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    resultado_esperado = f"Arquivo solicitado via {ambiente.prefixo} pelo usuário 12345 em {data_atual}"

    assert dados == resultado_esperado


def test_filtra_range_data_fora_do_range(queryset_ordered):
    data_inicio = datetime.date(2020, 2, 10)
    data_final = datetime.date(2020, 5, 10)

    queryset_filtrado = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == 0


def test_filtra_range_data_dentro_do_range(queryset_ordered):
    data_inicio = datetime.date.today()
    data_final = datetime.date.today()

    queryset_filtrado = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered,
        data_inicio=data_inicio,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)


def test_filtra_range_data_com_data_inicio_e_sem_data_final(queryset_ordered):
    data_inicio = datetime.date.today()

    queryset_filtrado = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered,
        data_inicio=data_inicio
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)


def test_filtra_range_data_sem_data_inicio_e_com_data_final(queryset_ordered):
    data_final = datetime.date.today()

    queryset_ordered[0].criado_em = datetime.date(2020, 1, 1)

    queryset_filtrado = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered,
        data_final=data_final
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)


def test_filtra_range_data_sem_data_inicio_e_sem_data_final(queryset_ordered):
    queryset_filtrado = ExportacoesStatusPrestacoesContaService(
        queryset=queryset_ordered
    ).filtra_range_data('criado_em')

    assert queryset_filtrado.count() == len(queryset_ordered)
