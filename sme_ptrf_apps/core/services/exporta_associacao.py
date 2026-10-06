import logging
import os

from django.contrib.staticfiles.storage import staticfiles_storage
from openpyxl import load_workbook

from waffle import flag_is_active

from ..choices.membro_associacao import RepresentacaoCargo

LOGGER = logging.getLogger(__name__)

# Worksheets
ASSOCIACAO = 0
MEMBROS = 1
CONTAS = 2

# Linhas Dados Básicos
NOME_ASSOCIACAO = 0
EOL = 1
DRE = 2
CNPJ = 3
CCM = 4
EMAIL_ASSOCIACAO = 5

# Colunas Membros
CARGO = 0
NOME_MEMBRO = 1
REPRESENTACAO = 2
RF_EOL = 3
CARGO_EDUCACAO = 4
EMAIL_MEMBRO = 5

# Linhas Membros
CARGOS = {
    'PRESIDENTE_DIRETORIA_EXECUTIVA': 1,
    'VICE_PRESIDENTE_DIRETORIA_EXECUTIVA': 2,
    'SECRETARIO': 3,
    'TESOUREIRO': 4,
    'VOGAL_1': 5,
    'VOGAL_2': 6,
    'VOGAL_3': 7,
    'VOGAL_4': 8,
    'VOGAL_5': 9,
    'PRESIDENTE_CONSELHO_FISCAL': 10,
    'CONSELHEIRO_1': 11,
    'CONSELHEIRO_2': 12,
    'CONSELHEIRO_3': 13,
    'CONSELHEIRO_4': 14,
}

# Colunas Contas da Associação
RECURSO = 1
BANCO = 2
TIPO = 3
AGENCIA = 4
NUMERO = 5

ROTULOS_CARGO_SEM_NUMERO = {
    'VOGAL_1': 'Vogal',
    'VOGAL_2': 'Vogal',
    'VOGAL_3': 'Vogal',
    'VOGAL_4': 'Vogal',
    'VOGAL_5': 'Vogal',
    'CONSELHEIRO_1': 'Conselheiro',
    'CONSELHEIRO_2': 'Conselheiro',
    'CONSELHEIRO_3': 'Conselheiro',
    'CONSELHEIRO_4': 'Conselheiro',
}

DOMINIO_EMAIL_VISIVEL = 'sme.prefeitura.sp.gov.br'


def gerar_planilha(associacao, request=None):
    LOGGER.info(f'EXPORTANDO DADOS DA ASSOCIACAO {associacao.nome}...')

    path = os.path.join(os.path.basename(staticfiles_storage.location), 'modelos')
    nome_arquivo = os.path.join(path, 'modelo_exportacao_associacao.xlsx')
    workbook = load_workbook(nome_arquivo)

    dados_basicos(workbook, associacao)

    rows_membros = list(workbook.worksheets[MEMBROS].rows)
    rows_membros[0][EMAIL_MEMBRO].value = 'E-mail'
    for cargo, rotulo in ROTULOS_CARGO_SEM_NUMERO.items():
        rows_membros[CARGOS[cargo]][CARGO].value = rotulo

    if flag_is_active(request, 'historico-de-membros-v2'):
        membros_historico(workbook, associacao)
    elif flag_is_active(request, 'historico-de-membros'):
        membros_v2(workbook, associacao)
    else:
        membros(workbook, associacao)

    contas(workbook, associacao)

    return workbook


def dados_basicos(workbook, associacao):
    worksheet = workbook.worksheets[ASSOCIACAO]
    rows = list(worksheet.rows)
    rows[NOME_ASSOCIACAO][1].value = associacao.nome
    rows[EOL][1].value = associacao.unidade.codigo_eol
    rows[DRE][1].value = associacao.unidade.dre.nome if associacao.unidade.dre else ''
    rows[CNPJ][1].value = associacao.cnpj
    rows[CCM][1].value = associacao.ccm
    rows[EMAIL_ASSOCIACAO][1].value = associacao.email


def membros(workbook, associacao):
    membros = associacao.cargos.all()
    worksheet = workbook.worksheets[MEMBROS]
    rows = list(worksheet.rows)
    for membro in membros:
        linha = CARGOS[membro.cargo_associacao]
        rows[linha][NOME_MEMBRO].value = membro.nome
        rows[linha][REPRESENTACAO].value = _representacao_para_planilha(membro.representacao)
        rows[linha][RF_EOL].value = membro.codigo_identificacao
        rows[linha][CARGO_EDUCACAO].value = membro.cargo_educacao
        rows[linha][EMAIL_MEMBRO].value = _email_para_planilha(membro.email)


def membros_v2(workbook, associacao):
    from sme_ptrf_apps.mandatos.services import ServicoMandatoVigente
    from sme_ptrf_apps.mandatos.services import ServicoComposicaoVigente, ServicoCargosDaComposicao

    servico_mandato_vigente = ServicoMandatoVigente()
    mandato_vigente = servico_mandato_vigente.get_mandato_vigente()

    servico_composicao_vigente = ServicoComposicaoVigente(associacao=associacao, mandato=mandato_vigente)
    composicao_vigente = servico_composicao_vigente.get_composicao_vigente()

    servico_cargos_da_composicao = ServicoCargosDaComposicao(composicao=composicao_vigente)
    cargos_da_composicao = servico_cargos_da_composicao.get_cargos_da_composicao_ordenado_por_cargo_associacao()

    membros_da_composicao = []

    for cargo in cargos_da_composicao['diretoria_executiva']:
        membros_da_composicao.append({
            "cargo_associacao": cargo['cargo_associacao'],
            "nome": cargo["ocupante_do_cargo"]["nome"],
            "representacao": cargo["ocupante_do_cargo"]["representacao"],
            "codigo_identificacao": cargo["ocupante_do_cargo"]["codigo_identificacao"],
            "cargo_educacao": cargo["ocupante_do_cargo"]["cargo_educacao"],
            "email": cargo["ocupante_do_cargo"]["email"]
        })

    for cargo in cargos_da_composicao['conselho_fiscal']:
        membros_da_composicao.append({
            "cargo_associacao": cargo['cargo_associacao'],
            "nome": cargo["ocupante_do_cargo"]["nome"],
            "representacao": cargo["ocupante_do_cargo"]["representacao"],
            "codigo_identificacao": cargo["ocupante_do_cargo"]["codigo_identificacao"],
            "cargo_educacao": cargo["ocupante_do_cargo"]["cargo_educacao"],
            "email": cargo["ocupante_do_cargo"]["email"]
        })

    _escrever_membros(workbook, membros_da_composicao)


def membros_historico(workbook, associacao):
    from sme_ptrf_apps.mandatos.models import ComposicaoVacancia
    from sme_ptrf_apps.mandatos.services import (
        ServicoHistoricoCargoComposicao,
        ServicoMandatoVigenteVacancia,
    )

    mandato_vigente = ServicoMandatoVigenteVacancia().get_mandato_vigente()
    if not mandato_vigente:
        LOGGER.info('EXPORTAÇÃO DE MEMBROS: flag historico-de-membros-v2 ativa, sem mandato vigente.')
        return

    composicao = ComposicaoVacancia.objects.filter(
        associacao=associacao,
        mandato=mandato_vigente,
    ).first()
    if not composicao:
        LOGGER.info(
            'EXPORTAÇÃO DE MEMBROS: flag historico-de-membros-v2 ativa, '
            'sem composição de histórico para a associação %s.',
            associacao.uuid,
        )
        return

    cargos_da_composicao = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(
        composicao_vacancia=composicao,
        data=None,
    )
    _escrever_membros(workbook, _membros_ocupados(cargos_da_composicao))


def _membros_ocupados(cargos_da_composicao):
    membros_da_composicao = []
    for grupo in ('diretoria_executiva', 'conselho_fiscal'):
        for cargo in cargos_da_composicao.get(grupo, []):
            ocupante = cargo.get('ocupante_do_cargo') or {}
            if not ocupante.get('nome'):
                continue
            membros_da_composicao.append({
                'cargo_associacao': cargo['cargo_associacao'],
                'nome': ocupante.get('nome'),
                'representacao': ocupante.get('representacao'),
                'codigo_identificacao': ocupante.get('codigo_identificacao'),
                'cargo_educacao': ocupante.get('cargo_educacao'),
                'email': ocupante.get('email'),
            })
    return membros_da_composicao


def _escrever_membros(workbook, membros_da_composicao):
    worksheet = workbook.worksheets[MEMBROS]
    rows = list(worksheet.rows)
    for membro_composicao in membros_da_composicao:
        cargo = membro_composicao.get('cargo_associacao')
        if cargo not in CARGOS:
            continue
        linha = CARGOS[cargo]
        rows[linha][NOME_MEMBRO].value = membro_composicao.get('nome') or ''
        rows[linha][REPRESENTACAO].value = _representacao_para_planilha(
            membro_composicao.get('representacao')
        )
        rows[linha][RF_EOL].value = membro_composicao.get('codigo_identificacao') or ''
        rows[linha][CARGO_EDUCACAO].value = membro_composicao.get('cargo_educacao') or ''
        rows[linha][EMAIL_MEMBRO].value = _email_para_planilha(membro_composicao.get('email'))


def _representacao_para_planilha(representacao):
    if not representacao:
        return ''
    try:
        texto = RepresentacaoCargo[representacao].value
    except KeyError:
        texto = representacao
    return texto.replace('_', ' ')


def _email_para_planilha(email):
    if not email:
        return ''
    email = email.strip()
    dominio = email.rsplit('@', 1)[-1].lower() if '@' in email else ''
    if dominio == DOMINIO_EMAIL_VISIVEL:
        return email
    if len(email) <= 4:
        return 'X' * len(email)
    return f'{email[:2]}{"X" * (len(email) - 4)}{email[-2:]}'


def contas(workbook, associacao):
    contas = associacao.contas.all()
    worksheet = workbook.worksheets[CONTAS]
    linha = 2
    for conta in contas:
        worksheet.cell(row=linha, column=RECURSO, value=conta.tipo_conta.recurso.nome_exibicao)
        worksheet.cell(row=linha, column=BANCO, value=conta.banco_nome)
        worksheet.cell(row=linha, column=TIPO, value=conta.tipo_conta.nome if conta.tipo_conta else ' ')
        worksheet.cell(row=linha, column=AGENCIA, value=conta.agencia)
        worksheet.cell(row=linha, column=NUMERO, value=conta.numero_conta)
        linha += 1
