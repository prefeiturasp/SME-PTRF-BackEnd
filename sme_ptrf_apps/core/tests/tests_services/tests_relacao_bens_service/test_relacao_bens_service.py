import pytest

from model_bakery import baker
from datetime import date
from decimal import Decimal
from sme_ptrf_apps.core.services.relacao_bens_dados_service import persistir_dados_relacao_bens, formatar_e_retornar_dados_relatorio_relacao_bens
from sme_ptrf_apps.core.services.relacao_bens import apagar_previas_relacao_de_bens, RelacaoBensService
from sme_ptrf_apps.core.models import RelacaoBens, RelatorioRelacaoBens, ItemRelatorioRelacaoDeBens, ItemRelatorioBemProduzidoRateio
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido

pytestmark = pytest.mark.django_db

dados_relacao_bens = {
  "cabecalho": {
    "periodo_referencia": "2023.2",
    "periodo_data_inicio": "2023-5-1",
    "periodo_data_fim": "2023-8-31",
    "conta": "Cheque"
  },
  "identificacao_apm": {
    "nome_associacao": "APM DA EMEF JOAO DA SILVA",
    "cnpj_associacao": "04442788000147",
    "codigo_eol_associacao": "019305",
    "nome_dre_associacao": "DIRETORIA REGIONAL DE EDUCACAO CAPELA DO SOCORRO",
    "presidente_diretoria_executiva": "GERALDO NUNES AGUILAR",
    "tipo_unidade": "EMEF",
    "nome_unidade": "JOAO DA SILVA",
    "cargo_substituto_presidente_ausente": "Presidente da Diretoria Executiva"
  },
  "relacao_de_bens_adquiridos_ou_produzidos": {
    "linhas": [
      {
        "tipo_documento": "DANFE",
        "numero_documento": "83601",
        "especificacao_material": "Caixa acustica",
        "numero_documento_incorporacao": "6016.2023/0108658-6",
        "quantidade": 1,
        "data_documento": "2023-6-28",
        "valor_item": 2000,
        "valor_rateio": 2000
      },
      {
        "tipo_documento": "DANFE",
        "numero_documento": "83601",
        "especificacao_material": "Caixa acustica",
        "numero_documento_incorporacao": "6016.2023/0108658-6",
        "quantidade": 1,
        "data_documento": "2023-06-28",
        "valor_item": 2400,
        "valor_rateio": 2400
      },
      {
        "tipo_documento": "DANFE",
        "numero_documento": "137865",
        "especificacao_material": "Gravador digital dvr",
        "numero_documento_incorporacao": "6016.2023/0108658-6",
        "quantidade": 1,
        "data_documento": "2023-7-4",
        "valor_item": 3019.777,
        "valor_rateio": 3019.77
      },
      {
        "tipo_documento": "DANFE",
        "numero_documento": "137865",
        "especificacao_material": "Modulo de potencia",
        "numero_documento_incorporacao": "6016.2023/0108658-6",
        "quantidade": 1,
        "data_documento": "2023-7-4",
        "valor_item": 429.56,
        "valor_rateio": 429.56
      },
      {
        "tipo_documento": "DANFE",
        "numero_documento": "137865",
        "especificacao_material": "Vídeo porteiro",
        "numero_documento_incorporacao": "6016.2023/0108658-6",
        "quantidade": 1,
        "data_documento": "2023-7-4",
        "valor_item": 648.91,
        "valor_rateio": 648.91
      }
    ],
    "valor_total": 8498.24
  }
}

def test_persistir_relatorio_relacao_bens(periodo, conta_associacao, despesa, 
                                          rateio_despesa_01, rateio_despesa_02, 
                                          usuario, relacao_bens_factory, bem_produzido_factory
                                        ):
    relacao_bens = relacao_bens_factory.create()

    bem_completo = bem_produzido_factory.create(
        associacao=conta_associacao.associacao, 
        status=BemProduzido.STATUS_COMPLETO
    )

    persistir_dados_relacao_bens(periodo, conta_associacao, despesa.rateios.all(), [bem_completo], relacao_bens, usuario)
    relatorio = RelatorioRelacaoBens.objects.get(relacao_bens=relacao_bens)

    assert relatorio

@pytest.fixture
def rateio_despesa_01(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_custeio, tipo_custeio_material, especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=200.00,
        valor_original=200.00,
        quantidade_itens_capital=2,
        valor_item_capital=100.00
    )


@pytest.fixture
def rateio_despesa_02(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_custeio, tipo_custeio, tipo_custeio_material, especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio,
        valor_rateio=100.00,
        valor_original=100.00,
    )

def test_persistir_relatorio_final_relacao_bens_com_relatorios_anteriores(periodo, conta_associacao, 
                                                                          despesa, rateio_despesa_01, rateio_despesa_02, usuario, 
                                                                          relacao_bens_factory, item_relatorio_relacao_de_bens_factory, 
                                                                          relatorio_relacao_bens_factory, bem_produzido_factory):
    relacao_bens_anterior = relacao_bens_factory.create()
    relatorio_anterior = relatorio_relacao_bens_factory.create(relacao_bens=relacao_bens_anterior)
    item_relatorio_relacao_de_bens_factory.create(relatorio=relatorio_anterior)

    apagar_previas_relacao_de_bens(relacao_bens_anterior.periodo_previa, relacao_bens_anterior.conta_associacao)

    relacao_bens = relacao_bens_factory.create()
    bem_completo = bem_produzido_factory.create(associacao=conta_associacao.associacao, status=BemProduzido.STATUS_COMPLETO)

    persistir_dados_relacao_bens(periodo, conta_associacao, despesa.rateios.all(), [bem_completo], relacao_bens, usuario)

    relatorio = RelatorioRelacaoBens.objects.filter(relacao_bens=relacao_bens)

    assert relatorio.count() == 1


def test_formatar_e_retornar_dados_relatorio_relacao_bens(relacao_bens_factory, item_relatorio_relacao_de_bens_factory,
                                                          relatorio_relacao_bens_factory):
    relacao_bens = relacao_bens_factory.create()
    relatorio_instance = relatorio_relacao_bens_factory.create(relacao_bens=relacao_bens)
    item_relatorio_relacao_de_bens_factory.create(relatorio=relatorio_instance)

    recurso_nome = relacao_bens.conta_associacao.tipo_conta.recurso.nome
    recurso_nome_exibicao = relacao_bens.conta_associacao.tipo_conta.recurso.nome_exibicao

    resultado = formatar_e_retornar_dados_relatorio_relacao_bens(
        relatorio_instance,
        recurso_nome,
        recurso_nome_exibicao,
    )

    assert 'cabecalho' in resultado
    assert 'periodo_referencia' in resultado['cabecalho']
    assert 'periodo_data_inicio' in resultado['cabecalho']
    assert 'periodo_data_fim' in resultado['cabecalho']
    assert 'conta' in resultado['cabecalho']

    assert 'identificacao_apm' in resultado
    assert 'nome_associacao' in resultado['identificacao_apm']
    assert 'cnpj_associacao' in resultado['identificacao_apm']
    assert 'codigo_eol_associacao' in resultado['identificacao_apm']
    assert 'nome_dre_associacao' in resultado['identificacao_apm']
    assert 'presidente_diretoria_executiva' in resultado['identificacao_apm']
    assert 'tipo_unidade' in resultado['identificacao_apm']
    assert 'nome_unidade' in resultado['identificacao_apm']
    assert  'cargo_substituto_presidente_ausente' in resultado['identificacao_apm']

    assert 'data_geracao' in resultado
    assert 'relacao_de_bens_adquiridos_ou_produzidos' in resultado
    assert 'valor_total' in resultado['relacao_de_bens_adquiridos_ou_produzidos']
    assert 'linhas' in resultado['relacao_de_bens_adquiridos_ou_produzidos']
    assert len(resultado['relacao_de_bens_adquiridos_ou_produzidos']['linhas']) == 1
    assert 'data_geracao_documento' in resultado
    assert 'previa' in resultado


def test_relacao_bens_possui_bens_adquiridos_e_produzidos(
    periodo_factory,
    associacao_factory,
    conta_associacao_factory,
    acao_factory,
    acao_associacao_factory,
    despesa_factory,
    rateio_despesa_factory,
    bem_produzido_factory,
    bem_produzido_item_factory,
    bem_produzido_despesa_factory,
    bem_produzido_rateio_factory,
    flag_factory
):
    # Configuração do Período e Associações
    periodo = periodo_factory.create(
        data_inicio_realizacao_despesas=date(2026, 1, 1),
        data_fim_realizacao_despesas=date(2026, 12, 31)
    )
    associacao = associacao_factory.create()
    conta_associacao = conta_associacao_factory.create(associacao=associacao)
    acao = acao_factory.create()
    acao_associacao = acao_associacao_factory(acao=acao, associacao=associacao)

    # Ativação Flag
    flag_factory.create(
        name='situacao-patrimonial',
        everyone=True,
    )

    despesa_adquirida = despesa_factory.create(
        data_transacao=date(2026, 4, 15),
        valor_total=120.00,
        associacao=associacao
    )
    rateio_adquirido = rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_adquirida,
        associacao=associacao,
        valor_rateio=120.00,
        aplicacao_recurso='CAPITAL',
        nao_exibir_em_rel_bens=False
    )

    bem_produzido = bem_produzido_factory.create(
        status='COMPLETO'
    )
    bem_produzido_item_factory.create(
        bem_produzido=bem_produzido,    
        quantidade=5,
        valor_individual=100.00
    )
    despesa_produzido = despesa_factory.create(
        data_transacao=date(2026, 4, 24),
        valor_total=120.00,
        associacao=associacao
    )
    despesa_bp = bem_produzido_despesa_factory.create(
        bem_produzido=bem_produzido,
        despesa=despesa_produzido
    )
    rateio_despesa_bp = rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_produzido,
        associacao=associacao,
        valor_rateio=120.00,
        aplicacao_recurso='CAPITAL',
        nao_exibir_em_rel_bens=True,
    )
    bem_produzido_rateio_factory.create(
        bem_produzido_despesa=despesa_bp,
        rateio=rateio_despesa_bp
    )

    service = RelacaoBensService(periodo=periodo, conta_associacao=conta_associacao)
    possui_bens, rateios, bens_produzidos = service.possui_relacao_bens_no_periodo()

    assert possui_bens is True
    assert rateios.count() == 1
    assert rateios.first() == rateio_adquirido
    assert bens_produzidos.count() == 1
    assert bens_produzidos.first() == bem_produzido


def test_persistir_dados_relacao_bens_com_bem_produzido(
    periodo_factory,
    associacao_factory,
    conta_associacao_factory,
    acao_factory,
    acao_associacao_factory,
    despesa_factory,
    rateio_despesa_factory,
    bem_produzido_factory,
    bem_produzido_item_factory,
    bem_produzido_despesa_factory,
    bem_produzido_rateio_factory,
    relacao_bens_factory,
    usuario_factory,
):
    periodo = periodo_factory.create(
        referencia="2026.1",
        data_inicio_realizacao_despesas=date(2026, 1, 1),
        data_fim_realizacao_despesas=date(2026, 6, 30),
    )

    associacao = associacao_factory.create(
        status_presidente="PRESENTE",
    )

    conta_associacao = conta_associacao_factory.create(
        associacao=associacao
    )

    acao = acao_factory.create(
        nome="PTRF"
    )

    acao_associacao = acao_associacao_factory.create(
        acao=acao,
        associacao=associacao,
    )

    bem_produzido = bem_produzido_factory.create(
        status="COMPLETO"
    )

    item_bem_produzido = bem_produzido_item_factory.create(
        bem_produzido=bem_produzido,
        quantidade=5,
        valor_individual=Decimal("100.00"),
        num_processo_incorporacao="PROC-002",
    )

    despesa = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2026, 4, 24),
        data_documento=date(2026, 4, 24),
        numero_documento="NF-002",
        valor_total=Decimal("120.00"),
    )

    despesa_bem = bem_produzido_despesa_factory.create(
        bem_produzido=bem_produzido,
        despesa=despesa,
    )

    rateio = rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa,
        associacao=associacao,
        valor_rateio=Decimal("120.00"),
        aplicacao_recurso="CAPITAL",
        nao_exibir_em_rel_bens=True,
    )

    bem_produzido_rateio_factory.create(
        bem_produzido_despesa=despesa_bem,
        rateio=rateio,
    )

    relacao_bens = relacao_bens_factory.create()

    usuario = usuario_factory.create()

    valor_total_produzido = bem_produzido.valor_total_utilizado(False)

    persistir_dados_relacao_bens(
        periodo=periodo,
        conta_associacao=conta_associacao,
        rateios=[],
        bens_produzidos=[bem_produzido],
        relacao_bens=relacao_bens,
        usuario=usuario,
    )

    relatorio = RelatorioRelacaoBens.objects.get(
        relacao_bens=relacao_bens
    )

    assert relatorio.valor_total == valor_total_produzido

    assert ItemRelatorioRelacaoDeBens.objects.filter(
        relatorio=relatorio,
        tipo_bem=ItemRelatorioRelacaoDeBens.TipoBem.PRODUZIDO,
    ).count() == 1

    item = ItemRelatorioRelacaoDeBens.objects.get(
        relatorio=relatorio,
        tipo_bem=ItemRelatorioRelacaoDeBens.TipoBem.PRODUZIDO,
    )

    assert item.bem_produzido_id == bem_produzido.id
    assert item.numero_documento_incorporacao == "PROC-002"
    assert item.quantidade == 5
    assert item.valor_item == Decimal("100.00")
    assert item.valor_rateio == item_bem_produzido.valor_total

    assert ItemRelatorioBemProduzidoRateio.objects.filter(
        relatorio=relatorio,
        bem_produzido_id=bem_produzido.id,
    ).count() == 1

    rateio_persistido = ItemRelatorioBemProduzidoRateio.objects.get(
        relatorio=relatorio,
        bem_produzido_id=bem_produzido.id,
    )

    assert rateio_persistido.numero_documento == "NF-002"
    assert rateio_persistido.data_documento == date(2026, 4, 24)
    assert rateio_persistido.acao == acao.nome
    assert rateio_persistido.valor_rateio == Decimal("120.00")


def test_persistir_dados_relacao_bens_com_adquirido_e_produzido_soma_valor_total(
    periodo_factory,
    associacao_factory,
    conta_associacao_factory,
    acao_factory,
    acao_associacao_factory,
    despesa_factory,
    rateio_despesa_factory,
    bem_produzido_factory,
    bem_produzido_item_factory,
    bem_produzido_despesa_factory,
    bem_produzido_rateio_factory,
    relacao_bens_factory,
    usuario_factory,
):
    periodo = periodo_factory.create(
        referencia="2026.1",
        data_inicio_realizacao_despesas=date(2026, 1, 1),
        data_fim_realizacao_despesas=date(2026, 6, 30),
    )

    associacao = associacao_factory.create(
        status_presidente="PRESENTE",
    )

    conta_associacao = conta_associacao_factory.create(
        associacao=associacao
    )

    acao = acao_factory.create()

    acao_associacao = acao_associacao_factory.create(
        acao=acao,
        associacao=associacao,
    )

    despesa_adquirida = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2026, 4, 15),
        data_documento=date(2026, 4, 15),
        valor_total=Decimal("120.00"),
    )

    rateio_adquirido = rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_adquirida,
        associacao=associacao,
        valor_rateio=Decimal("120.00"),
        aplicacao_recurso="CAPITAL",
        nao_exibir_em_rel_bens=False,
    )

    bem_produzido = bem_produzido_factory.create(
        status="COMPLETO"
    )

    bem_produzido_item_factory.create(
        bem_produzido=bem_produzido,
        quantidade=5,
        valor_individual=Decimal("100.00"),
    )

    despesa_produzida = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2026, 4, 24),
        data_documento=date(2026, 4, 24),
        valor_total=Decimal("120.00"),
    )

    despesa_bem = bem_produzido_despesa_factory.create(
        bem_produzido=bem_produzido,
        despesa=despesa_produzida,
    )

    rateio_produzido = rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_produzida,
        associacao=associacao,
        valor_rateio=Decimal("120.00"),
        aplicacao_recurso="CAPITAL",
        nao_exibir_em_rel_bens=True,
    )

    bem_produzido_rateio_factory.create(
        bem_produzido_despesa=despesa_bem,
        rateio=rateio_produzido,
    )

    relacao_bens = relacao_bens_factory.create(versao=RelacaoBens.VERSAO_PREVIA)

    usuario = usuario_factory.create()

    valor_total_produzido = bem_produzido.valor_total_utilizado(False)

    persistir_dados_relacao_bens(
        periodo=periodo,
        conta_associacao=conta_associacao,
        rateios=[rateio_adquirido],
        bens_produzidos=[bem_produzido],
        relacao_bens=relacao_bens,
        usuario=usuario,
    )

    relatorio = RelatorioRelacaoBens.objects.get(
        relacao_bens=relacao_bens
    )

    valor_total_esperado = (
        Decimal("120.00") + valor_total_produzido
    )

    assert relatorio.valor_total == valor_total_esperado

    assert ItemRelatorioRelacaoDeBens.objects.filter(
        relatorio=relatorio
    ).count() == 2

    assert ItemRelatorioRelacaoDeBens.objects.filter(
        relatorio=relatorio,
        tipo_bem=ItemRelatorioRelacaoDeBens.TipoBem.ADQUIRIDO,
    ).count() == 1

    assert ItemRelatorioRelacaoDeBens.objects.filter(
        relatorio=relatorio,
        tipo_bem=ItemRelatorioRelacaoDeBens.TipoBem.PRODUZIDO,
    ).count() == 1


def test_formatar_relacao_bens_sem_flag_situacao_patrimonial_retorna_apenas_adquiridos(
    periodo_factory,
    associacao_factory,
    conta_associacao_factory,
    acao_factory,
    acao_associacao_factory,
    despesa_factory,
    rateio_despesa_factory,
    bem_produzido_factory,
    bem_produzido_item_factory,
    bem_produzido_despesa_factory,
    bem_produzido_rateio_factory,
    relacao_bens_factory,
    usuario_factory,
):
    periodo = periodo_factory.create(
        referencia="2026.1",
        data_inicio_realizacao_despesas=date(2026, 1, 1),
        data_fim_realizacao_despesas=date(2026, 6, 30),
    )

    associacao = associacao_factory.create(
        status_presidente="PRESENTE",
    )

    conta_associacao = conta_associacao_factory.create(
        associacao=associacao
    )

    acao = acao_factory.create(
        nome="PTRF"
    )

    acao_associacao = acao_associacao_factory.create(
        acao=acao,
        associacao=associacao,
    )

    despesa_adquirida = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2026, 4, 15),
        data_documento=date(2026, 4, 15),
        numero_documento="NF-ADQUIRIDO",
        valor_total=Decimal("120.00"),
    )

    rateio_adquirido = rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_adquirida,
        associacao=associacao,
        valor_rateio=Decimal("120.00"),
        aplicacao_recurso="CAPITAL",
        nao_exibir_em_rel_bens=False,
    )

    bem_produzido = bem_produzido_factory.create(
        status="COMPLETO"
    )

    bem_produzido_item_factory.create(
        bem_produzido=bem_produzido,
        quantidade=5,
        valor_individual=Decimal("100.00"),
    )

    despesa_produzida = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2026, 4, 24),
        data_documento=date(2026, 4, 24),
        numero_documento="NF-PRODUZIDO",
        valor_total=Decimal("120.00"),
    )

    despesa_bem = bem_produzido_despesa_factory.create(
        bem_produzido=bem_produzido,
        despesa=despesa_produzida,
    )

    rateio_produzido = rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_produzida,
        associacao=associacao,
        valor_rateio=Decimal("120.00"),
        aplicacao_recurso="CAPITAL",
        nao_exibir_em_rel_bens=True,
    )

    bem_produzido_rateio_factory.create(
        bem_produzido_despesa=despesa_bem,
        rateio=rateio_produzido,
    )

    relacao_bens = relacao_bens_factory.create()

    usuario = usuario_factory.create()

    persistir_dados_relacao_bens(
        periodo=periodo,
        conta_associacao=conta_associacao,
        rateios=[rateio_adquirido],
        bens_produzidos=[bem_produzido],
        relacao_bens=relacao_bens,
        usuario=usuario,
    )

    relatorio = RelatorioRelacaoBens.objects.get(
        relacao_bens=relacao_bens
    )

    resultado = formatar_e_retornar_dados_relatorio_relacao_bens(
        relatorio=relatorio,
        recurso_nome="PTRF",
        recurso_nome_exibicao="PTRF",
    )

    linhas = resultado[
        "relacao_de_bens_adquiridos_ou_produzidos"
    ]["linhas"]

    assert len(linhas) == 1

    assert linhas[0]["tipo_bem"] == (
        ItemRelatorioRelacaoDeBens.TipoBem.ADQUIRIDO
    )

    assert linhas[0]["numero_documento"] == "NF-ADQUIRIDO"

    assert resultado["cabecalho"]["recurso"] == "PTRF"
    assert resultado["cabecalho"]["periodo_referencia"] == periodo.referencia
    assert resultado["identificacao_apm"]["nome_associacao"] == associacao.nome
    assert resultado["previa"] is False


def test_formatar_relacao_bens_com_flag_situacao_patrimonial_retorna_adquiridos_e_produzidos(
    periodo_factory,
    associacao_factory,
    conta_associacao_factory,
    acao_factory,
    acao_associacao_factory,
    despesa_factory,
    rateio_despesa_factory,
    bem_produzido_factory,
    bem_produzido_item_factory,
    bem_produzido_despesa_factory,
    bem_produzido_rateio_factory,
    relacao_bens_factory,
    usuario_factory,
    flag_factory,
):
    periodo = periodo_factory.create(
        referencia="2026.1",
        data_inicio_realizacao_despesas=date(2026, 1, 1),
        data_fim_realizacao_despesas=date(2026, 6, 30),
    )

    associacao = associacao_factory.create(
        status_presidente="PRESENTE",
    )

    conta_associacao = conta_associacao_factory.create(
        associacao=associacao
    )

    acao = acao_factory.create(
        nome="PTRF"
    )

    acao_associacao = acao_associacao_factory.create(
        acao=acao,
        associacao=associacao,
    )

    flag_factory.create(
        name="situacao-patrimonial",
        everyone=True,
    )

    despesa_adquirida = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2026, 4, 15),
        data_documento=date(2026, 4, 15),
        numero_documento="NF-ADQUIRIDO",
        valor_total=Decimal("120.00"),
    )

    rateio_adquirido = rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_adquirida,
        associacao=associacao,
        valor_rateio=Decimal("120.00"),
        aplicacao_recurso="CAPITAL",
        nao_exibir_em_rel_bens=False,
    )

    bem_produzido = bem_produzido_factory.create(
        status="COMPLETO"
    )

    bem_produzido_item_factory.create(
        bem_produzido=bem_produzido,
        quantidade=2,
        valor_individual=Decimal("100.00"),
        num_processo_incorporacao="PROC-001",
    )

    bem_produzido_item_factory.create(
        bem_produzido=bem_produzido,
        quantidade=3,
        valor_individual=Decimal("50.00"),
        num_processo_incorporacao="PROC-002",
    )

    despesa_produzida = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2026, 4, 24),
        data_documento=date(2026, 4, 24),
        numero_documento="NF-PRODUZIDO",
        valor_total=Decimal("120.00"),
    )

    despesa_bem = bem_produzido_despesa_factory.create(
        bem_produzido=bem_produzido,
        despesa=despesa_produzida,
    )

    rateio_produzido = rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_produzida,
        associacao=associacao,
        valor_rateio=Decimal("120.00"),
        aplicacao_recurso="CAPITAL",
        nao_exibir_em_rel_bens=True,
    )

    bem_produzido_rateio_factory.create(
        bem_produzido_despesa=despesa_bem,
        rateio=rateio_produzido,
    )

    relacao_bens = relacao_bens_factory.create(
        versao=RelacaoBens.VERSAO_PREVIA
    )

    usuario = usuario_factory.create()

    persistir_dados_relacao_bens(
        periodo=periodo,
        conta_associacao=conta_associacao,
        rateios=[rateio_adquirido],
        bens_produzidos=[bem_produzido],
        relacao_bens=relacao_bens,
        usuario=usuario,
    )

    relatorio = RelatorioRelacaoBens.objects.get(
        relacao_bens=relacao_bens
    )

    resultado = formatar_e_retornar_dados_relatorio_relacao_bens(
        relatorio=relatorio,
        recurso_nome="PTRF",
        recurso_nome_exibicao="PTRF",
    )

    linhas = resultado[
        "relacao_de_bens_adquiridos_ou_produzidos"
    ]["linhas"]

    assert len(linhas) == 2

    linha_adquirido = next(
        linha
        for linha in linhas
        if linha["tipo_bem"]
        == ItemRelatorioRelacaoDeBens.TipoBem.ADQUIRIDO
    )

    linha_produzido = next(
        linha
        for linha in linhas
        if linha["tipo_bem"]
        == ItemRelatorioRelacaoDeBens.TipoBem.PRODUZIDO
    )

    assert linha_adquirido["numero_documento"] == "NF-ADQUIRIDO"

    assert linha_produzido["bem_produzido_id"] == bem_produzido.id

    assert len(linha_produzido["items"]) == 2
    assert len(linha_produzido["rateios"]) == 1
    assert len(linha_produzido["linhas_tabela"]) == 2

    assert linha_produzido["rateios"][0]["numero_documento"] == (
        "NF-PRODUZIDO"
    )

    assert linha_produzido["rateios"][0]["acao"] == acao.nome

    assert linha_produzido["linhas_tabela"][0][0] is not None
    assert linha_produzido["linhas_tabela"][0][1] is not None

    assert linha_produzido["linhas_tabela"][1][0] is not None
    assert linha_produzido["linhas_tabela"][1][1] is None

def test_formatar_relacao_bens_ordena_bens_adquiridos_por_data_documento_decrescente(
    periodo_factory,
    associacao_factory,
    conta_associacao_factory,
    acao_factory,
    acao_associacao_factory,
    despesa_factory,
    rateio_despesa_factory,
    relacao_bens_factory,
    usuario_factory,
):
    periodo = periodo_factory.create(
        referencia="2026.1",
        data_inicio_realizacao_despesas=date(2026, 1, 1),
        data_fim_realizacao_despesas=date(2026, 12, 31),
    )

    associacao = associacao_factory.create(
        status_presidente="PRESENTE",
    )

    conta_associacao = conta_associacao_factory.create(
        associacao=associacao
    )

    acao = acao_factory.create()

    acao_associacao = acao_associacao_factory.create(
        acao=acao,
        associacao=associacao,
    )

    despesa_antiga = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2026, 2, 10),
        data_documento=date(2026, 2, 10),
        numero_documento="NF-ANTIGA",
        valor_total=Decimal("100.00"),
    )

    rateio_antigo = rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_antiga,
        associacao=associacao,
        valor_rateio=Decimal("100.00"),
        aplicacao_recurso="CAPITAL",
    )

    despesa_recente = despesa_factory.create(
        associacao=associacao,
        data_transacao=date(2026, 8, 20),
        data_documento=date(2026, 8, 20),
        numero_documento="NF-RECENTE",
        valor_total=Decimal("200.00"),
    )

    rateio_recente = rateio_despesa_factory.create(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa_recente,
        associacao=associacao,
        valor_rateio=Decimal("200.00"),
        aplicacao_recurso="CAPITAL",
    )

    relacao_bens = relacao_bens_factory.create(
        versao=RelacaoBens.VERSAO_PREVIA
    )

    usuario = usuario_factory.create()

    persistir_dados_relacao_bens(
        periodo=periodo,
        conta_associacao=conta_associacao,
        rateios=[
            rateio_antigo,
            rateio_recente,
        ],
        bens_produzidos=[],
        relacao_bens=relacao_bens,
        usuario=usuario,
    )

    relatorio = RelatorioRelacaoBens.objects.get(
        relacao_bens=relacao_bens
    )

    resultado = formatar_e_retornar_dados_relatorio_relacao_bens(
        relatorio=relatorio,
        recurso_nome="PTRF",
        recurso_nome_exibicao="PTRF",
    )

    linhas = resultado[
        "relacao_de_bens_adquiridos_ou_produzidos"
    ]["linhas"]

    assert len(linhas) == 2

    assert linhas[0]["numero_documento"] == "NF-RECENTE"
    assert linhas[1]["numero_documento"] == "NF-ANTIGA"
