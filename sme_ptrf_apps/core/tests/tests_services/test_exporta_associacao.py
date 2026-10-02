from unittest.mock import MagicMock, patch

from sme_ptrf_apps.core.services import exporta_associacao as servico


def _planilha_com_flags(flags_ativas):
    associacao = MagicMock()
    workbook, _ = _aba_membros()

    def flag_is_active(request, nome):
        return nome in flags_ativas

    with patch.object(servico, 'load_workbook', return_value=workbook), \
            patch.object(servico, 'dados_basicos'), \
            patch.object(servico, 'contas'), \
            patch.object(servico, 'flag_is_active', side_effect=flag_is_active), \
            patch.object(servico, 'membros_historico') as historico, \
            patch.object(servico, 'membros_v2') as membros_v1, \
            patch.object(servico, 'membros') as membros_legado:
        resultado = servico.gerar_planilha(associacao, request=MagicMock())

    return resultado, historico, membros_v1, membros_legado


def test_gerar_planilha_com_flag_v2_usa_historico():
    _, historico, membros_v1, membros_legado = _planilha_com_flags({'historico-de-membros-v2'})

    historico.assert_called_once()
    membros_v1.assert_not_called()
    membros_legado.assert_not_called()


def test_gerar_planilha_prioriza_historico_v2_sobre_v1():
    _, historico, membros_v1, membros_legado = _planilha_com_flags({
        'historico-de-membros-v2',
        'historico-de-membros',
    })

    historico.assert_called_once()
    membros_v1.assert_not_called()
    membros_legado.assert_not_called()


def test_gerar_planilha_sem_flag_usa_membros_da_associacao():
    _, historico, membros_v1, membros_legado = _planilha_com_flags(set())

    membros_legado.assert_called_once()
    historico.assert_not_called()
    membros_v1.assert_not_called()


def test_membros_ocupados_ignora_cargo_vago():
    cargos = {
        'diretoria_executiva': [
            {
                'cargo_associacao': 'PRESIDENTE_DIRETORIA_EXECUTIVA',
                'ocupante_do_cargo': {
                    'nome': 'Vitor Yoshi Yashinaga',
                    'representacao': 'SERVIDOR',
                    'codigo_identificacao': '754703',
                    'cargo_educacao': 'DIRETOR DE ESCOLA',
                    'email': 'vitor@email.com',
                },
            },
            {
                'cargo_associacao': 'SECRETARIO',
                'ocupante_do_cargo': {'nome': None},
            },
        ],
        'conselho_fiscal': [],
    }

    membros = servico._membros_ocupados(cargos)

    assert len(membros) == 1
    assert membros[0]['cargo_associacao'] == 'PRESIDENTE_DIRETORIA_EXECUTIVA'
    assert membros[0]['nome'] == 'Vitor Yoshi Yashinaga'
    assert membros[0]['email'] == 'vitor@email.com'


def test_escrever_membros_preenche_a_linha_do_cargo():
    celulas = {
        coluna: MagicMock()
        for coluna in range(6)
    }
    linhas = [MagicMock() for _ in range(2)]
    linhas[1].__getitem__.side_effect = lambda coluna: celulas[coluna]
    worksheet = MagicMock()
    worksheet.rows = linhas
    workbook = MagicMock()
    workbook.worksheets = [MagicMock(), worksheet]

    servico._escrever_membros(workbook, [{
        'cargo_associacao': 'PRESIDENTE_DIRETORIA_EXECUTIVA',
        'nome': 'Vitor Yoshi Yashinaga',
        'representacao': 'SERVIDOR',
        'codigo_identificacao': '754703',
        'cargo_educacao': 'DIRETOR DE ESCOLA',
        'email': 'vitor@email.com',
    }])

    assert celulas[servico.NOME_MEMBRO].value == 'Vitor Yoshi Yashinaga'
    assert celulas[servico.REPRESENTACAO].value == 'Servidor'
    assert celulas[servico.RF_EOL].value == '754703'
    assert celulas[servico.CARGO_EDUCACAO].value == 'DIRETOR DE ESCOLA'
    assert celulas[servico.EMAIL_MEMBRO].value == 'viXXXXXXXXXXXom'


def _aba_membros():
    linhas = []
    for _ in range(15):
        celulas = [MagicMock() for _ in range(6)]
        linha = MagicMock()
        linha.__getitem__.side_effect = lambda coluna, celulas=celulas: celulas[coluna]
        linhas.append((linha, celulas))
    worksheet = MagicMock()
    worksheet.rows = [linha for linha, _ in linhas]
    workbook = MagicMock()
    workbook.worksheets = [MagicMock(), worksheet]
    return workbook, [celulas for _, celulas in linhas]


def test_gerar_planilha_remove_numeracao_e_renomeia_email():
    workbook, linhas = _aba_membros()

    with patch.object(servico, 'load_workbook', return_value=workbook), \
            patch.object(servico, 'dados_basicos'), \
            patch.object(servico, 'contas'), \
            patch.object(servico, 'flag_is_active', return_value=False), \
            patch.object(servico, 'membros'):
        servico.gerar_planilha(MagicMock(), request=MagicMock())

    assert linhas[0][servico.EMAIL_MEMBRO].value == 'E-mail'
    for cargo in ('VOGAL_1', 'VOGAL_2', 'VOGAL_3', 'VOGAL_4', 'VOGAL_5'):
        assert linhas[servico.CARGOS[cargo]][servico.CARGO].value == 'Vogal'
    for cargo in ('CONSELHEIRO_1', 'CONSELHEIRO_2', 'CONSELHEIRO_3', 'CONSELHEIRO_4'):
        assert linhas[servico.CARGOS[cargo]][servico.CARGO].value == 'Conselheiro'


def test_representacao_pai_ou_responsavel_sem_underscore():
    assert servico._representacao_para_planilha('PAI_RESPONSAVEL') == 'Pai ou responsável'
    assert servico._representacao_para_planilha('SERVIDOR') == 'Servidor'


def test_email_sme_permanece_visivel_e_outro_dominio_e_anonimizado():
    sme = 'anderson.mendes@sme.prefeitura.sp.gov.br'
    gmail = 'victoryoshinaga@gmail.com'

    assert servico._email_para_planilha(sme) == sme
    assert servico._email_para_planilha(gmail) == 'vi' + ('X' * 21) + 'om'
    assert servico._email_para_planilha('') == ''
