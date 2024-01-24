import logging
from datetime import datetime

from datetime import date

from sme_ptrf_apps.core.choices import MembroEnum

from sme_ptrf_apps.core.models import (MembroAssociacao, RelatorioRelacaoBens, ItemRelatorioRelacaoDeBens)
from sme_ptrf_apps.mandatos.models.cargo_composicao import CargoComposicao
from sme_ptrf_apps.mandatos.services.composicao_service import ServicoComposicaoVigente
from sme_ptrf_apps.mandatos.services.mandato_service import ServicoMandatoVigente

from waffle import get_waffle_flag_model

LOGGER = logging.getLogger(__name__)


def gerar_dados_relacao_de_bens(conta_associacao=None, periodo=None, rateios=None, usuario=None, previa=False):

    try:
        LOGGER.info("GERANDO DADOS RELAÇÃO DE BENS...")

        cabecalho = cria_cabecalho(periodo, conta_associacao)
        identificacao_apm = cria_identificacao_apm(conta_associacao)
        relacao_de_bens_adquiridos_ou_produzidos = cria_relacao_de_bens_adquiridos_ou_produzidos(rateios)
        data_geracao_documento = cria_data_geracao_documento(previa=previa, usuario=usuario)
        data_geracao = date.today().strftime("%d/%m/%Y")

        dados_relacao_de_bens = {
            "cabecalho": cabecalho,
            "identificacao_apm": identificacao_apm,
            "relacao_de_bens_adquiridos_ou_produzidos": relacao_de_bens_adquiridos_ou_produzidos,
            "data_geracao_documento": data_geracao_documento,
            "previa": previa,
            "data_geracao": data_geracao
        }
    finally:
        LOGGER.info("DADOS RELAÇÃO DE BENS GERADO")

    return dados_relacao_de_bens


def cria_cabecalho(periodo, conta_associacao):
    """ GERA CABECALHO DOCUMENTO EM PDF RELACAO DE BENS """

    cabecalho = {
        "periodo_referencia": periodo.referencia,
        "periodo_data_inicio": formata_data(periodo.data_inicio_realizacao_despesas),
        "periodo_data_fim": formata_data(periodo.data_fim_realizacao_despesas),
        "conta": conta_associacao.tipo_conta.nome,
    }

    return cabecalho


def cria_identificacao_apm(conta_associacao):
    """BLOCO 1 - IDENTIFICAÇÃO DA APM/APMSUAC DA UNIDADE EDUCACIONAL DOCUMENTO EM PDF RELACAO DE BENS """
    associacao = conta_associacao.associacao

    status_presidente_associacao = associacao.status_presidente
    cargo_substituto_presidente_ausente_name = associacao.cargo_substituto_presidente_ausente

    nome_associacao = associacao.nome
    cnpj_associacao = associacao.cnpj
    codigo_eol_associacao = associacao.unidade.codigo_eol or ""
    nome_dre_associacao = associacao.unidade.dre.nome if associacao.unidade.dre else ""

    flags = get_waffle_flag_model()
    if flags.objects.filter(name='historico-de-membros', everyone=True).exists():
        servico_mandato_vigente = ServicoMandatoVigente()
        mandato_vigente = servico_mandato_vigente.get_mandato_vigente()
        servico_composicao_vigente = ServicoComposicaoVigente(associacao=associacao, mandato=mandato_vigente)
        composicao_vigente = servico_composicao_vigente.get_composicao_vigente()

        list_choices = list(CargoComposicao.CARGO_ASSOCIACAO_CHOICES)

        if mandato_vigente and composicao_vigente:
            if associacao.cargo_substituto_presidente_ausente:
                cargo_da_composicao_presidente_diretoria_executiva = CargoComposicao.objects.filter(
                    composicao=composicao_vigente,
                    cargo_associacao=associacao.cargo_substituto_presidente_ausente
                ).first()
                cargo_substituto_presidente_ausente_value = [x[1] for x in list_choices if x[0] == associacao.cargo_substituto_presidente_ausente][0]
            else:
                cargo_da_composicao_presidente_diretoria_executiva = CargoComposicao.objects.filter(
                    composicao=composicao_vigente,
                    cargo_associacao='PRESIDENTE_DIRETORIA_EXECUTIVA'
                ).first()
                cargo_substituto_presidente_ausente_value = [x[1] for x in list_choices if x[0] == 'PRESIDENTE_DIRETORIA_EXECUTIVA'][0]

            presidente_diretoria_executiva = cargo_da_composicao_presidente_diretoria_executiva.ocupante_do_cargo.nome if cargo_da_composicao_presidente_diretoria_executiva and cargo_da_composicao_presidente_diretoria_executiva.ocupante_do_cargo and cargo_da_composicao_presidente_diretoria_executiva.ocupante_do_cargo.nome else '-------'
    else:
        if status_presidente_associacao == 'PRESENTE':
            _presidente_diretoria_executiva = \
                MembroAssociacao.objects.filter(associacao=associacao,
                                                cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name).first()
            cargo_substituto_presidente_ausente_value = MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.value
        else:
            _presidente_diretoria_executiva = \
                MembroAssociacao.objects.filter(associacao=associacao, cargo_associacao=MembroEnum[
                    cargo_substituto_presidente_ausente_name].name).first()
            cargo_substituto_presidente_ausente_value = MembroEnum[cargo_substituto_presidente_ausente_name].value

        presidente_diretoria_executiva = _presidente_diretoria_executiva.nome if _presidente_diretoria_executiva else '-------'

    tipo_unidade = associacao.unidade.tipo_unidade
    nome_unidade = associacao.unidade.nome

    identificacao_apm = {
        "nome_associacao": nome_associacao,
        "cnpj_associacao": cnpj_associacao,
        "codigo_eol_associacao": codigo_eol_associacao,
        "nome_dre_associacao": nome_dre_associacao,
        "presidente_diretoria_executiva": presidente_diretoria_executiva,
        "tipo_unidade": tipo_unidade,
        "nome_unidade": nome_unidade,
        "cargo_substituto_presidente_ausente": cargo_substituto_presidente_ausente_value,
    }

    return identificacao_apm


def cria_relacao_de_bens_adquiridos_ou_produzidos(rateios):
    """ BLOCO 2 - IDENTIFICAÇÃO DOS BENS ADQUIRIDOS OU PRODUZIDOS DOCUMENTO EM PDF RELACAO DE BENS """
    if not rateios:
        return

    valor_total = sum(r.valor_rateio for r in rateios)

    linhas = []
    for _, rateio in enumerate(rateios):
        tipo_documento = rateio.despesa.tipo_documento.nome if rateio.despesa.tipo_documento else ''
        numero_documento = rateio.despesa.numero_documento
        data_documento = rateio.despesa.data_documento if rateio.despesa.data_documento else ''
        especificacao_material = \
            rateio.especificacao_material_servico.descricao if rateio.especificacao_material_servico else ''
        numero_documento_incorporacao = rateio.numero_processo_incorporacao_capital
        quantidade = rateio.quantidade_itens_capital
        valor_item = rateio.valor_item_capital
        valor_rateio = rateio.valor_rateio

        linha = {
            "tipo_documento": tipo_documento,
            "numero_documento": numero_documento,
            "especificacao_material": especificacao_material,
            "numero_documento_incorporacao": numero_documento_incorporacao,
            "quantidade": quantidade,
            "data_documento": formata_data(data_documento),
            "valor_item": valor_item,
            "valor_rateio": valor_rateio
        }
        linhas.append(linha)

    despesas = {
        "linhas": linhas,
        "valor_total": valor_total
    }
    return despesas


def cria_data_geracao_documento(usuario, previa, data=None):
    if data is None:
        data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    else:
        data_geracao = data.strftime("%d/%m/%Y %H:%M:%S")

    tipo_texto = "parcial" if previa else "final"
    quem_gerou = "" if usuario == "" else f"pelo usuário {usuario}, "
    texto = f"Documento {tipo_texto} gerado {quem_gerou}via SIG - Escola, em: {data_geracao}"

    return texto


def formata_valor(valor):
    from babel.numbers import format_currency
    sinal, valor_formatado = format_currency(valor, 'BRL', locale='pt_BR').split('\xa0')
    sinal = '-' if '-' in sinal else ''
    return f'{sinal}{valor_formatado}'


def formata_data(data):
    data_formatada = " - "
    if data:
        d = datetime.strptime(str(data), '%Y-%m-%d')
        data_formatada = d.strftime("%d/%m/%Y")

    return f'{data_formatada}'


def persistir_dados_relacao_bens(periodo, conta_associacao, rateios, relacao_bens, usuario):
    associacao = conta_associacao.associacao
    status_presidente_associacao = associacao.status_presidente
    cargo_substituto_presidente_ausente_name = associacao.cargo_substituto_presidente_ausente

    nome_associacao = associacao.nome
    cnpj_associacao = associacao.cnpj
    codigo_eol_associacao = associacao.unidade.codigo_eol or ""
    nome_dre_associacao = associacao.unidade.dre.nome if associacao.unidade.dre else ""

    flags = get_waffle_flag_model()
    if flags.objects.filter(name='historico-de-membros', everyone=True).exists():
        servico_mandato_vigente = ServicoMandatoVigente()
        mandato_vigente = servico_mandato_vigente.get_mandato_vigente()
        servico_composicao_vigente = ServicoComposicaoVigente(associacao=associacao, mandato=mandato_vigente)
        composicao_vigente = servico_composicao_vigente.get_composicao_vigente()

        list_choices = list(CargoComposicao.CARGO_ASSOCIACAO_CHOICES)

        if mandato_vigente and composicao_vigente:
            if associacao.cargo_substituto_presidente_ausente:
                cargo_da_composicao_presidente_diretoria_executiva = CargoComposicao.objects.filter(
                    composicao=composicao_vigente,
                    cargo_associacao=associacao.cargo_substituto_presidente_ausente
                ).first()
                cargo_substituto_presidente_ausente_value = [x[1] for x in list_choices if x[0] == associacao.cargo_substituto_presidente_ausente][0]
            else:
                cargo_da_composicao_presidente_diretoria_executiva = CargoComposicao.objects.filter(
                    composicao=composicao_vigente,
                    cargo_associacao='PRESIDENTE_DIRETORIA_EXECUTIVA'
                ).first()
                cargo_substituto_presidente_ausente_value = [x[1] for x in list_choices if x[0] == 'PRESIDENTE_DIRETORIA_EXECUTIVA'][0]

            presidente_diretoria_executiva = cargo_da_composicao_presidente_diretoria_executiva.ocupante_do_cargo.nome if cargo_da_composicao_presidente_diretoria_executiva and cargo_da_composicao_presidente_diretoria_executiva.ocupante_do_cargo and cargo_da_composicao_presidente_diretoria_executiva.ocupante_do_cargo.nome else '-------'
    else:
        if status_presidente_associacao == 'PRESENTE':
            _presidente_diretoria_executiva = \
                MembroAssociacao.objects.filter(associacao=associacao,
                                                cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name).first()
            cargo_substituto_presidente_ausente_value = MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.value
        else:
            _presidente_diretoria_executiva = \
                MembroAssociacao.objects.filter(associacao=associacao, cargo_associacao=MembroEnum[
                    cargo_substituto_presidente_ausente_name].name).first()
            cargo_substituto_presidente_ausente_value = MembroEnum[cargo_substituto_presidente_ausente_name].value

        presidente_diretoria_executiva = _presidente_diretoria_executiva.nome if _presidente_diretoria_executiva else '-------'

    tipo_unidade = associacao.unidade.tipo_unidade
    nome_unidade = associacao.unidade.nome

    valor_total = sum(r.valor_rateio for r in rateios)
    print(valor_total)
    relatorio = RelatorioRelacaoBens.objects.create(
        relacao_bens=relacao_bens,
        usuario=usuario,

        periodo_referencia=periodo.referencia,
        periodo_data_inicio=periodo.data_inicio_realizacao_despesas,
        periodo_data_fim=periodo.data_fim_realizacao_despesas,
        conta=conta_associacao.tipo_conta.nome,

        tipo_unidade=tipo_unidade,
        nome_unidade=nome_unidade,
        nome_associacao=nome_associacao,
        cnpj_associacao=cnpj_associacao,
        codigo_eol_associacao=codigo_eol_associacao,
        nome_dre_associacao=nome_dre_associacao,
        presidente_diretoria_executiva=presidente_diretoria_executiva,
        cargo_substituto_presidente_ausente=cargo_substituto_presidente_ausente_value,

        data_geracao=datetime.now(),
        valor_total=valor_total
    )

    for _, rateio in enumerate(rateios):
        tipo_documento = rateio.despesa.tipo_documento.nome if rateio.despesa.tipo_documento else ''
        numero_documento = rateio.despesa.numero_documento
        data_documento = rateio.despesa.data_documento if rateio.despesa.data_documento else ''
        especificacao_material = \
            rateio.especificacao_material_servico.descricao if rateio.especificacao_material_servico else ''
        numero_documento_incorporacao = rateio.numero_processo_incorporacao_capital
        quantidade = rateio.quantidade_itens_capital
        valor_item = rateio.valor_item_capital
        valor_rateio = rateio.valor_rateio

        ItemRelatorioRelacaoDeBens.objects.create(
            relatorio=relatorio,
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            data_documento=data_documento,
            especificacao_material=especificacao_material,
            numero_documento_incorporacao=numero_documento_incorporacao,
            quantidade=quantidade,
            valor_item=valor_item,
            valor_rateio=valor_rateio
        )

    LOGGER.info(f'Dados da relação bens persistidos {relatorio} com sucesso.')


def formatar_e_retornar_dados_relatorio_relacao_bens(relatorio):
    linhas = []

    for item in relatorio.bens.all():
        linha = {
            "tipo_documento": item.tipo_documento,
            "numero_documento": item.numero_documento,
            "especificacao_material": item.especificacao_material,
            "numero_documento_incorporacao": item.numero_documento_incorporacao,
            "quantidade": item.quantidade,
            "data_documento": formata_data(item.data_documento),
            "valor_item": formata_valor(item.valor_item),
            "valor_rateio": formata_valor(item.valor_rateio)
        }
        linhas.append(linha)

    dados_relacao_de_bens = {
        "cabecalho": {
            "periodo_referencia": relatorio.periodo_referencia,
            "periodo_data_inicio": formata_data(relatorio.periodo_data_inicio),
            "periodo_data_fim": formata_data(relatorio.periodo_data_fim),
            "conta": relatorio.conta,
        },
        "identificacao_apm": {
            "nome_associacao": relatorio.nome_associacao,
            "cnpj_associacao": relatorio.cnpj_associacao,
            "codigo_eol_associacao": relatorio.codigo_eol_associacao,
            "nome_dre_associacao": relatorio.nome_dre_associacao,
            "presidente_diretoria_executiva": relatorio.presidente_diretoria_executiva,
            "tipo_unidade": relatorio.tipo_unidade,
            "nome_unidade": relatorio.nome_unidade,
            "cargo_substituto_presidente_ausente": relatorio.cargo_substituto_presidente_ausente
        },
        "data_geracao": formata_data(relatorio.data_geracao.date()),
        "relacao_de_bens_adquiridos_ou_produzidos": {
            "valor_total": formata_valor(relatorio.valor_total),
            "linhas": linhas
        },
        "data_geracao_documento": cria_data_geracao_documento(relatorio.usuario, relatorio.relacao_bens.previa, relatorio.data_geracao),
        "previa": relatorio.relacao_bens.previa
    }

    return dados_relacao_de_bens

