from datetime import datetime
from unittest.mock import MagicMock

from django.contrib.admin.sites import AdminSite

from sme_ptrf_apps.core import admin as core_admin
from sme_ptrf_apps.core import models

site = AdminSite()

recurso_admin = core_admin.RecursoAdmin(models.Recurso, site)
solicitacao_encerramento_admin = core_admin.SolicitacaoEncerramentoContaAssociacaoAdmin(
    models.SolicitacaoEncerramentoContaAssociacao, site)
associacao_admin = core_admin.AssociacaoAdmin(models.Associacao, site)
fechamento_periodo_admin = core_admin.FechamentoPeriodoAdmin(models.FechamentoPeriodo, site)
prestacao_conta_admin = core_admin.PrestacaoContaAdmin(models.PrestacaoConta, site)
ata_admin = core_admin.AtaAdmin(models.Ata, site)
observacao_conciliacao_admin = core_admin.ObservacaoConciliacaoAdmin(models.ObservacaoConciliacao, site)
notificacao_admin = core_admin.NotificacaoAdmin(models.Notificacao, site)
devolucao_prestacao_conta_admin = core_admin.DevolucaoPrestacaoContaAdmin(models.DevolucaoPrestacaoConta, site)
analise_conta_prestacao_conta_admin = core_admin.AnaliseContaPrestacaoContaAdmin(
    models.AnaliseContaPrestacaoConta, site)
comentario_analise_prestacao_admin = core_admin.ComentarioAnalisePrestacaoAdmin(
    models.ComentarioAnalisePrestacao, site)
previsao_repasse_sme_admin = core_admin.PrevisaoRepasseSmeAdmin(models.PrevisaoRepasseSme, site)
parametros_admin = core_admin.ParametrosAdmin(models.Parametros, site)
demonstrativo_financeiro_admin = core_admin.DemonstrativoFinanceiroAdmin(models.DemonstrativoFinanceiro, site)
relacao_bens_admin = core_admin.RelacaoBensAdmin(models.RelacaoBens, site)
arquivo_download_admin = core_admin.ArquivoDownloadAdmin(models.ArquivoDownload, site)
analise_prestacao_conta_admin = core_admin.AnalisePrestacaoContaAdmin(models.AnalisePrestacaoConta, site)
analise_lancamento_prestacao_conta_admin = core_admin.AnaliseLancamentoPrestacaoContaAdmin(
    models.AnaliseLancamentoPrestacaoConta, site)
solicitacao_acerto_lancamento_admin = core_admin.SolicitacaoAcertoLancamentoAdmin(
    models.SolicitacaoAcertoLancamento, site)
analise_documento_prestacao_conta_admin = core_admin.AnaliseDocumentoPrestacaoContaAdmin(
    models.AnaliseDocumentoPrestacaoConta, site)
solicitacao_acerto_documento_admin = core_admin.SolicitacaoAcertoDocumentoAdmin(
    models.SolicitacaoAcertoDocumento, site)
presente_ata_admin = core_admin.PresenteAtaAdmin(models.Participante, site)
valores_reprogramados_admin = core_admin.ValoresReprogramadosAdmin(models.ValoresReprogramados, site)
devolucao_ao_tesouro_admin = core_admin.DevolucaoAoTesouroAdmin(models.DevolucaoAoTesouro, site)
solicitacao_devolucao_admin = core_admin.SolicitacaoDevolucaoPrestacaoContaAdmin(
    models.SolicitacaoDevolucaoAoTesouro, site)
task_celery_admin = core_admin.TaskCeleryAdmin(models.TaskCelery, site)
pc_reprovada_nao_apresentacao_admin = core_admin.PrestacaoContaReprovadaNaoApresentacaoAdmin(
    models.PrestacaoContaReprovadaNaoApresentacao, site)
fique_de_olho_admin = core_admin.FiqueDeOlhoAdmin(models.FiqueDeOlho, site)


# RecursoAdmin
def test_recurso_admin_cor_preview():
    obj = MagicMock(cor='#FF0000')
    resultado = recurso_admin.cor_preview(obj)
    assert '#FF0000' in str(resultado)
    assert 'background' in str(resultado)


# SolicitacaoEncerramentoContaAssociacaoAdmin
def test_solicitacao_encerramento_get_codigo_eol():
    obj = MagicMock()
    obj.conta_associacao.associacao.unidade.codigo_eol = '123456'
    assert solicitacao_encerramento_admin.get_codigo_eol(obj) == '123456'
    assert solicitacao_encerramento_admin.get_codigo_eol(None) == ''


# AssociacaoAdmin
def test_associacao_admin_get_nome_escola():
    obj = MagicMock()
    obj.unidade.nome = 'EMEF Teste'
    assert associacao_admin.get_nome_escola(obj) == 'EMEF Teste'
    assert associacao_admin.get_nome_escola(None) == ''


def test_associacao_admin_get_periodo_inicial_referencia():
    obj = MagicMock()
    obj.periodo_inicial.referencia = '2024.1'
    assert associacao_admin.get_periodo_inicial_referencia(obj) == '2024.1'
    obj_sem_periodo = MagicMock(periodo_inicial=None)
    assert associacao_admin.get_periodo_inicial_referencia(obj_sem_periodo) == ''


# FechamentoPeriodoAdmin
def test_fechamento_periodo_admin_getters():
    obj = MagicMock()
    obj.acao_associacao.acao.nome = 'PTRF'
    obj.conta_associacao.tipo_conta.nome = 'Cheque'
    obj.associacao.unidade.codigo_eol = '111111'

    assert fechamento_periodo_admin.get_nome_acao(obj) == 'PTRF'
    assert fechamento_periodo_admin.get_nome_conta(obj) == 'Cheque'
    assert fechamento_periodo_admin.get_eol_unidade(obj) == '111111'

    obj_vazio = MagicMock(acao_associacao=None, conta_associacao=None, associacao=None)
    assert fechamento_periodo_admin.get_nome_acao(obj_vazio) == ''
    assert fechamento_periodo_admin.get_nome_conta(obj_vazio) == ''
    assert fechamento_periodo_admin.get_eol_unidade(obj_vazio) == ''


# PrestacaoContaAdmin
def test_prestacao_conta_admin_getters():
    obj = MagicMock()
    obj.associacao.unidade.codigo_eol = '222222'
    obj.associacao.unidade.nome = 'EMEF Fulano'
    obj.consolidado_dre.referencia = 'Publicação 1'
    obj.periodo.referencia = '2024.1'

    assert prestacao_conta_admin.get_eol_unidade(obj) == '222222'
    assert prestacao_conta_admin.get_nome_unidade(obj) == 'EMEF Fulano'
    assert prestacao_conta_admin.get_relatorio_referencia(obj) == 'Publicação 1'
    assert prestacao_conta_admin.get_periodo_referencia(obj) == '2024.1'

    obj_vazio = MagicMock(associacao=None, consolidado_dre=None, periodo=None)
    assert prestacao_conta_admin.get_eol_unidade(obj_vazio) == ''
    assert prestacao_conta_admin.get_nome_unidade(obj_vazio) == ''
    assert prestacao_conta_admin.get_relatorio_referencia(obj_vazio) == ''
    assert prestacao_conta_admin.get_periodo_referencia(obj_vazio) == ''


# AtaAdmin
def test_ata_admin_getters():
    obj = MagicMock()
    obj.associacao.unidade.codigo_eol = '333333'
    obj.associacao.unidade.nome = 'EMEF Ata'
    obj.periodo.referencia = '2024.1'
    obj.presidente_da_reuniao.nome = 'Presidente'
    obj.secretario_da_reuniao.nome = 'Secretário'

    assert ata_admin.get_eol_unidade(obj) == '333333 - EMEF Ata'
    assert ata_admin.get_referencia_periodo(obj) == '2024.1'
    assert ata_admin.get_presidente(obj) == 'Presidente'
    assert ata_admin.get_secretario(obj) == 'Secretário'

    obj_vazio = MagicMock(associacao=None, periodo=None, presidente_da_reuniao=None, secretario_da_reuniao=None)
    assert ata_admin.get_eol_unidade(obj_vazio) == ''
    assert ata_admin.get_referencia_periodo(obj_vazio) == ''
    assert ata_admin.get_presidente(obj_vazio) == ''
    assert ata_admin.get_secretario(obj_vazio) == ''


# ObservacaoConciliacaoAdmin
def test_observacao_conciliacao_admin_getters():
    obj = MagicMock()
    obj.associacao.unidade.codigo_eol = '444444'
    obj.associacao.unidade.nome = 'EMEF Conciliação'
    obj.conta_associacao.tipo_conta.nome = 'Poupança'

    assert observacao_conciliacao_admin.get_unidade(obj) == '444444 - EMEF Conciliação'
    assert observacao_conciliacao_admin.get_nome_conta(obj) == 'Poupança'

    obj_vazio = MagicMock(associacao=None, conta_associacao=None)
    assert observacao_conciliacao_admin.get_unidade(obj_vazio) == ''
    assert observacao_conciliacao_admin.get_nome_conta(obj_vazio) == ''


# NotificacaoAdmin
def test_notificacao_admin_get_codigo_eol():
    obj = MagicMock()
    obj.unidade.codigo_eol = '555555'
    assert notificacao_admin.get_codigo_eol(obj) == '555555'
    assert notificacao_admin.get_codigo_eol(MagicMock(unidade=None)) == ''


def test_notificacao_admin_get_referencia_pc():
    obj = MagicMock()
    obj.prestacao_conta.periodo.referencia = '2024.1'
    assert notificacao_admin.get_referencia_pc(obj) == '2024.1'
    assert notificacao_admin.get_referencia_pc(MagicMock(prestacao_conta=None)) == ''


# DevolucaoPrestacaoContaAdmin
def test_devolucao_prestacao_conta_admin_getters():
    obj = MagicMock()
    obj.prestacao_conta.associacao.nome = 'Associação X'
    obj.prestacao_conta.periodo.referencia = '2024.1'

    assert devolucao_prestacao_conta_admin.get_associacao(obj) == 'Associação X'
    assert devolucao_prestacao_conta_admin.get_referencia_periodo(obj) == '2024.1'

    obj_vazio = MagicMock(prestacao_conta=None)
    assert devolucao_prestacao_conta_admin.get_associacao(obj_vazio) == ''
    assert devolucao_prestacao_conta_admin.get_referencia_periodo(obj_vazio) == ''


# AnaliseContaPrestacaoContaAdmin
def test_analise_conta_prestacao_conta_admin_getters():
    obj = MagicMock()
    obj.prestacao_conta.associacao.nome = 'Associação Y'
    obj.prestacao_conta.associacao.unidade.codigo_eol = '666666'
    obj.prestacao_conta.periodo.referencia = '2024.1'
    obj.analise_prestacao_conta.id = 10

    assert analise_conta_prestacao_conta_admin.get_associacao(obj) == 'Associação Y'
    assert analise_conta_prestacao_conta_admin.get_unidade_codigo_eol(obj) == '666666'
    assert analise_conta_prestacao_conta_admin.get_referencia_periodo(obj) == '2024.1'
    assert analise_conta_prestacao_conta_admin.get_id_analise_prestacao_contas(obj) == 10

    obj_vazio = MagicMock(prestacao_conta=None, analise_prestacao_conta=None)
    assert analise_conta_prestacao_conta_admin.get_associacao(obj_vazio) == ''
    assert analise_conta_prestacao_conta_admin.get_unidade_codigo_eol(obj_vazio) == ''
    assert analise_conta_prestacao_conta_admin.get_referencia_periodo(obj_vazio) == ''
    assert analise_conta_prestacao_conta_admin.get_id_analise_prestacao_contas(obj_vazio) == ''


# ComentarioAnalisePrestacaoAdmin
def test_comentario_analise_prestacao_get_associacao():
    obj_com_pc = MagicMock()
    obj_com_pc.prestacao_conta.associacao.nome = 'Associação PC'
    assert comentario_analise_prestacao_admin.get_associacao(obj_com_pc) == 'Associação PC'

    obj_com_associacao = MagicMock(prestacao_conta=None)
    obj_com_associacao.associacao.nome = 'Associação direta'
    assert comentario_analise_prestacao_admin.get_associacao(obj_com_associacao) == 'Associação direta'

    obj_vazio = MagicMock(prestacao_conta=None, associacao=None)
    assert comentario_analise_prestacao_admin.get_associacao(obj_vazio) == ''


def test_comentario_analise_prestacao_get_referencia_periodo():
    obj_com_pc = MagicMock()
    obj_com_pc.prestacao_conta.periodo.referencia = '2024.1'
    assert comentario_analise_prestacao_admin.get_referencia_periodo(obj_com_pc) == '2024.1'

    obj_com_periodo = MagicMock(prestacao_conta=None)
    obj_com_periodo.periodo.referencia = '2024.2'
    assert comentario_analise_prestacao_admin.get_referencia_periodo(obj_com_periodo) == '2024.2'

    obj_vazio = MagicMock(prestacao_conta=None, periodo=None)
    assert comentario_analise_prestacao_admin.get_referencia_periodo(obj_vazio) == ''


def test_comentario_analise_prestacao_get_codigo_eol_unidade():
    obj_com_pc = MagicMock()
    obj_com_pc.prestacao_conta.associacao.unidade.codigo_eol = '777777'
    assert comentario_analise_prestacao_admin.get_codigo_eol_unidade(obj_com_pc) == '777777'

    obj_com_associacao = MagicMock(prestacao_conta=None)
    obj_com_associacao.associacao.unidade.codigo_eol = '888888'
    assert comentario_analise_prestacao_admin.get_codigo_eol_unidade(obj_com_associacao) == '888888'

    obj_vazio = MagicMock(prestacao_conta=None, associacao=None)
    assert comentario_analise_prestacao_admin.get_codigo_eol_unidade(obj_vazio) == ''


# PrevisaoRepasseSmeAdmin
def test_previsao_repasse_sme_admin_get_codigo_eol():
    obj = MagicMock()
    obj.associacao.unidade.codigo_eol = '999999'
    assert previsao_repasse_sme_admin.get_codigo_eol(obj) == '999999'
    assert previsao_repasse_sme_admin.get_codigo_eol(MagicMock(associacao=None)) == ''


# ParametrosAdmin
def test_parametros_admin_getters():
    obj = MagicMock(
        tempo_notificar_nao_demonstrados=10,
        dias_antes_inicio_periodo_pc_para_notificacao=5,
        dias_antes_fim_periodo_pc_para_notificacao=3,
        dias_antes_fim_prazo_ajustes_pc_para_notificacao=7,
    )
    assert parametros_admin.get_tempo_notificar_nao_demonstrados(obj) == 10
    assert parametros_admin.get_dias_antes_inicio_periodo_pc_para_notificacao(obj) == 5
    assert parametros_admin.get_dias_antes_fim_periodo_pc_para_notificacao(obj) == 3
    assert parametros_admin.get_dias_antes_fim_prazo_ajustes_pc_para_notificacao(obj) == 7


# DemonstrativoFinanceiroAdmin
def test_demonstrativo_financeiro_admin_getters():
    obj = MagicMock()
    obj.conta_associacao.tipo_conta.nome = 'Cheque'
    obj.conta_associacao.associacao.nome = 'Associação DF'
    obj.conta_associacao.associacao.unidade.dre.nome = 'DRE Teste'
    obj.prestacao_conta.periodo.referencia = '2024.1'

    assert demonstrativo_financeiro_admin.get_nome_conta(obj) == 'Cheque'
    assert demonstrativo_financeiro_admin.get_nome_associacao(obj) == 'Associação DF'
    assert demonstrativo_financeiro_admin.get_periodo(obj) == '2024.1'
    assert demonstrativo_financeiro_admin.get_nome_dre(obj) == 'DRE Teste'

    obj_periodo_previa = MagicMock(prestacao_conta=None)
    obj_periodo_previa.periodo_previa.referencia = '2024.2'
    assert demonstrativo_financeiro_admin.get_periodo(obj_periodo_previa) == '2024.2'

    obj_vazio = MagicMock(conta_associacao=None)
    assert demonstrativo_financeiro_admin.get_nome_conta(obj_vazio) == ''
    assert demonstrativo_financeiro_admin.get_nome_associacao(obj_vazio) == ''
    assert demonstrativo_financeiro_admin.get_nome_dre(obj_vazio) == ''


# RelacaoBensAdmin
def test_relacao_bens_admin_getters():
    obj = MagicMock()
    obj.conta_associacao.tipo_conta.nome = 'Cheque'
    obj.conta_associacao.associacao.nome = 'Associação RB'
    obj.conta_associacao.associacao.unidade.dre.nome = 'DRE Teste'
    obj.prestacao_conta.periodo.referencia = '2024.1'

    assert relacao_bens_admin.get_nome_conta(obj) == 'Cheque'
    assert relacao_bens_admin.get_nome_associacao(obj) == 'Associação RB'
    assert relacao_bens_admin.get_periodo(obj) == '2024.1'
    assert relacao_bens_admin.get_nome_dre(obj) == 'DRE Teste'

    obj_periodo_previa = MagicMock(prestacao_conta=None)
    obj_periodo_previa.periodo_previa.referencia = '2024.2'
    assert relacao_bens_admin.get_periodo(obj_periodo_previa) == '2024.2'

    obj_vazio = MagicMock(conta_associacao=None)
    assert relacao_bens_admin.get_nome_conta(obj_vazio) == ''
    assert relacao_bens_admin.get_nome_associacao(obj_vazio) == ''
    assert relacao_bens_admin.get_nome_dre(obj_vazio) == ''


# ArquivoDownloadAdmin
def test_arquivo_download_admin_get_nome_usuario():
    obj_completo = MagicMock()
    obj_completo.usuario.username = 'jsilva'
    obj_completo.usuario.name = 'João Silva'
    assert arquivo_download_admin.get_nome_usuario(obj_completo) == 'jsilva - João Silva'

    obj_so_username = MagicMock()
    obj_so_username.usuario.username = 'jsilva'
    obj_so_username.usuario.name = ''
    assert arquivo_download_admin.get_nome_usuario(obj_so_username) == 'jsilva'

    obj_so_name = MagicMock()
    obj_so_name.usuario.username = ''
    obj_so_name.usuario.name = 'João Silva'
    assert arquivo_download_admin.get_nome_usuario(obj_so_name) == 'João Silva'

    obj_sem_usuario = MagicMock(usuario=None)
    assert arquivo_download_admin.get_nome_usuario(obj_sem_usuario) == '-'


def test_arquivo_download_admin_get_dre_nome():
    obj = MagicMock()
    obj.dre.nome = 'DRE Teste'
    assert arquivo_download_admin.get_dre_nome(obj) == 'DRE Teste'
    assert arquivo_download_admin.get_dre_nome(MagicMock(dre=None)) == '-'


# AnalisePrestacaoContaAdmin
def test_analise_prestacao_conta_admin_getters():
    obj = MagicMock()
    obj.prestacao_conta.associacao.nome = 'Associação APC'
    obj.prestacao_conta.associacao.unidade.codigo_eol = '101010'
    obj.prestacao_conta.associacao.unidade.nome = 'EMEF APC'
    obj.prestacao_conta.periodo.referencia = '2024.1'

    assert analise_prestacao_conta_admin.get_associacao(obj) == 'Associação APC'
    assert analise_prestacao_conta_admin.get_unidade(obj) == '101010 - EMEF APC'
    assert analise_prestacao_conta_admin.get_referencia_periodo(obj) == '2024.1'

    obj_vazio = MagicMock(prestacao_conta=None)
    assert analise_prestacao_conta_admin.get_associacao(obj_vazio) == ''
    assert analise_prestacao_conta_admin.get_unidade(obj_vazio) == ''
    assert analise_prestacao_conta_admin.get_referencia_periodo(obj_vazio) == ''


# AnaliseLancamentoPrestacaoContaAdmin
def test_analise_lancamento_prestacao_conta_admin_getters():
    obj = MagicMock()
    obj.analise_prestacao_conta.prestacao_conta.associacao.unidade.codigo_eol = '111111'
    obj.analise_prestacao_conta.prestacao_conta.associacao.unidade.nome = 'EMEF ALPC'
    obj.analise_prestacao_conta.prestacao_conta.periodo.referencia = '2024.1'
    obj.analise_prestacao_conta.pk = 5

    assert analise_lancamento_prestacao_conta_admin.get_unidade(obj) == '111111 - EMEF ALPC'
    assert analise_lancamento_prestacao_conta_admin.get_periodo(obj) == '2024.1'
    assert analise_lancamento_prestacao_conta_admin.get_analise_pc(obj) == '#5'

    obj_vazio = MagicMock(analise_prestacao_conta=None)
    assert analise_lancamento_prestacao_conta_admin.get_unidade(obj_vazio) == '-'
    assert analise_lancamento_prestacao_conta_admin.get_analise_pc(obj_vazio) == ''


# SolicitacaoAcertoLancamentoAdmin
def test_solicitacao_acerto_lancamento_admin_getters():
    obj = MagicMock()
    analise = obj.analise_lancamento.analise_prestacao_conta
    analise.prestacao_conta.associacao.unidade.codigo_eol = '222222'
    analise.prestacao_conta.associacao.unidade.tipo_unidade = 'EMEF'
    analise.prestacao_conta.associacao.unidade.nome = 'EMEF SAL'
    analise.prestacao_conta.periodo.referencia = '2024.1'
    analise.pk = 7
    obj.analise_lancamento.tipo_lancamento = 'GASTO'
    obj.analise_lancamento.despesa = 'Despesa X'

    assert solicitacao_acerto_lancamento_admin.get_unidade(obj) == '222222 - EMEF - EMEF SAL'
    assert solicitacao_acerto_lancamento_admin.tipo_lancamento(obj) == 'GASTO'
    assert solicitacao_acerto_lancamento_admin.get_despesa(obj) == 'Despesa X'
    assert solicitacao_acerto_lancamento_admin.get_periodo(obj) == '2024.1'
    assert solicitacao_acerto_lancamento_admin.get_analise_pc(obj) == '#7'

    obj_vazio = MagicMock(analise_lancamento=None)
    assert solicitacao_acerto_lancamento_admin.get_unidade(obj_vazio) == ''
    assert solicitacao_acerto_lancamento_admin.tipo_lancamento(obj_vazio) == ''
    assert solicitacao_acerto_lancamento_admin.get_despesa(obj_vazio) == ''


# AnaliseDocumentoPrestacaoContaAdmin
def test_analise_documento_prestacao_conta_admin_getters():
    obj = MagicMock()
    obj.analise_prestacao_conta.prestacao_conta.associacao.unidade.codigo_eol = '333333'
    obj.analise_prestacao_conta.prestacao_conta.associacao.unidade.nome = 'EMEF ADP'
    obj.analise_prestacao_conta.prestacao_conta.periodo.referencia = '2024.1'
    obj.analise_prestacao_conta.pk = 9

    assert analise_documento_prestacao_conta_admin.get_unidade(obj) == '333333 - EMEF ADP'
    assert analise_documento_prestacao_conta_admin.get_periodo(obj) == '2024.1'
    assert analise_documento_prestacao_conta_admin.get_analise_pc(obj) == '#9'


# SolicitacaoAcertoDocumentoAdmin
def test_solicitacao_acerto_documento_admin_getters():
    obj = MagicMock()
    obj.analise_documento.analise_prestacao_conta.prestacao_conta.associacao.unidade.codigo_eol = '444444'
    obj.analise_documento.analise_prestacao_conta.prestacao_conta.associacao.unidade.nome = 'EMEF SAD'
    obj.analise_documento.despesa = 'Despesa Y'
    obj.analise_documento.analise_prestacao_conta.prestacao_conta.periodo.referencia = '2024.1'
    obj.analise_documento.analise_prestacao_conta.pk = 11

    assert solicitacao_acerto_documento_admin.get_unidade(obj) == '444444 - EMEF SAD'
    assert solicitacao_acerto_documento_admin.get_despesa(obj) == 'Despesa Y'
    assert solicitacao_acerto_documento_admin.get_periodo(obj) == '2024.1'
    assert solicitacao_acerto_documento_admin.get_analise_pc(obj) == '#11'

    obj_vazio = MagicMock(analise_documento=None)
    assert solicitacao_acerto_documento_admin.get_unidade(obj_vazio) == ''
    assert solicitacao_acerto_documento_admin.get_despesa(obj_vazio) == ''


# PresenteAtaAdmin (Participante)
def test_presente_ata_admin_getters():
    obj = MagicMock()
    obj.ata.associacao.unidade.codigo_eol = '555555'
    obj.ata.associacao.unidade.nome = 'EMEF Participante'
    obj.ata.periodo.referencia = '2024.1'

    assert presente_ata_admin.get_unidade(obj) == '555555 - EMEF Participante'
    assert presente_ata_admin.get_periodo(obj) == '2024.1'

    obj_vazio = MagicMock(ata=None)
    assert presente_ata_admin.get_unidade(obj_vazio) == ''
    assert presente_ata_admin.get_periodo(obj_vazio) == ''


# ValoresReprogramadosAdmin
def test_valores_reprogramados_admin_getters():
    obj = MagicMock()
    obj.associacao.unidade.codigo_eol = '666666'
    obj.associacao.unidade.nome = 'EMEF VR'
    obj.conta_associacao.tipo_conta.nome = 'Cheque'
    obj.acao_associacao.acao.nome = 'PTRF'

    assert valores_reprogramados_admin.get_unidade(obj) == '666666 - EMEF VR'
    assert valores_reprogramados_admin.get_tipo_conta(obj) == 'Cheque'
    assert valores_reprogramados_admin.get_acao(obj) == 'PTRF'

    obj_vazio = MagicMock(associacao=None, conta_associacao=None, acao_associacao=None)
    assert valores_reprogramados_admin.get_unidade(obj_vazio) == ''
    assert valores_reprogramados_admin.get_tipo_conta(obj_vazio) == ''
    assert valores_reprogramados_admin.get_acao(obj_vazio) == ''


# DevolucaoAoTesouroAdmin
def test_devolucao_ao_tesouro_admin_getters():
    obj = MagicMock()
    obj.prestacao_conta.associacao.unidade.dre.nome = 'DRE Teste'
    obj.prestacao_conta.associacao.unidade.codigo_eol = '777777'
    obj.prestacao_conta.associacao.unidade.nome = 'EMEF DAT'
    obj.prestacao_conta.periodo.referencia = '2024.1'

    assert devolucao_ao_tesouro_admin.get_dre(obj) == 'DRE Teste'
    assert devolucao_ao_tesouro_admin.get_unidade(obj) == '777777 - EMEF DAT'
    assert devolucao_ao_tesouro_admin.get_referencia_periodo(obj) == '2024.1'

    obj_sem_pc = MagicMock(prestacao_conta=None)
    assert devolucao_ao_tesouro_admin.get_unidade(obj_sem_pc) == ''
    assert devolucao_ao_tesouro_admin.get_referencia_periodo(obj_sem_pc) == ''


# SolicitacaoDevolucaoPrestacaoContaAdmin
def test_solicitacao_devolucao_admin_getters():
    obj = MagicMock()
    sal = obj.solicitacao_acerto_lancamento
    sal.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao.unidade.codigo_eol = '888888'
    sal.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao.unidade.nome = 'EMEF SDT'
    sal.analise_lancamento.analise_prestacao_conta.prestacao_conta.periodo.referencia = '2024.1'
    sal.analise_lancamento.despesa = 'Despesa Z'

    assert solicitacao_devolucao_admin.get_unidade(obj) == '888888 - EMEF SDT'
    assert solicitacao_devolucao_admin.get_referencia_periodo(obj) == '2024.1'
    assert solicitacao_devolucao_admin.get_despesa(obj) == 'Despesa Z'

    obj_vazio = MagicMock(solicitacao_acerto_lancamento=None)
    assert solicitacao_devolucao_admin.get_unidade(obj_vazio) == ''
    assert solicitacao_devolucao_admin.get_referencia_periodo(obj_vazio) == ''
    assert solicitacao_devolucao_admin.get_despesa(obj_vazio) == ''


# TaskCeleryAdmin
def test_task_celery_admin_get_eol_unidade():
    obj = MagicMock()
    obj.associacao.unidade.codigo_eol = '999999'
    assert task_celery_admin.get_eol_unidade(obj) == '999999'
    assert task_celery_admin.get_eol_unidade(MagicMock(associacao=None)) == ''


# PrestacaoContaReprovadaNaoApresentacaoAdmin
def test_pc_reprovada_nao_apresentacao_admin_getters():
    obj = MagicMock()
    obj.associacao.unidade.codigo_eol = '121212'
    obj.associacao.unidade.nome = 'EMEF Reprovada'
    obj.periodo.referencia = '2024.1'

    assert pc_reprovada_nao_apresentacao_admin.get_eol_unidade(obj) == '121212'
    assert pc_reprovada_nao_apresentacao_admin.get_nome_unidade(obj) == 'EMEF Reprovada'
    assert pc_reprovada_nao_apresentacao_admin.get_periodo_referencia(obj) == '2024.1'

    obj_vazio = MagicMock(associacao=None, periodo=None)
    assert pc_reprovada_nao_apresentacao_admin.get_eol_unidade(obj_vazio) == ''
    assert pc_reprovada_nao_apresentacao_admin.get_nome_unidade(obj_vazio) == ''
    assert pc_reprovada_nao_apresentacao_admin.get_periodo_referencia(obj_vazio) == ''


# LogEntryAdminCustom
def test_log_entry_admin_custom_created():
    log_entry_admin = core_admin.LogEntryAdminCustom(core_admin.LogEntry, site)
    obj = MagicMock()
    obj.timestamp = datetime(2024, 5, 10, 12, 0, 0)
    resultado = log_entry_admin.created(obj)
    assert resultado.year == 2024
    assert resultado.month == 5
    assert resultado.day == 10


# FiqueDeOlhoAdmin
def test_fique_de_olho_admin_texto_preview():
    obj = MagicMock()
    obj.get_short_texto.return_value = 'Texto resumido'
    assert fique_de_olho_admin.texto_preview(obj) == 'Texto resumido'
