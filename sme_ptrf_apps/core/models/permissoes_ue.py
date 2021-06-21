from django.db import models

"""
Esses modelos existem apenas para criação das permissions usadas
para a gestão de acesso de cada funcionalidade da aplicação.

Nenhuma tabela será criada para esses modelos no banco de dados.

Cada modelo representa uma funcionalidade da aplicação e define as permissões usadas nessa funcionalidade.
"""


class FuncUeResumoDosRecursos(models.Model):
    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[UE] Resumo dos recursos"
        verbose_name_plural = "[UE] Resumo dos recursos"

        permissions = (
            ('access_painel_recursos_ue', '[UE] Pode ver resumo dos recursos.'),
        )


class FuncUeGastosDaEscola(models.Model):
    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[UE] Gastos da Escola"
        verbose_name_plural = "[UE] Gastos da Escola"

        permissions = (
            ('access_despesa', '[UE] Pode acessar Gastos da Escola.'),
            ('add_despesa', '[UE] Pode incluir Gastos da Escola.'),
            ('change_despesa', '[UE] Pode editar Gastos da Escola.'),
            ('delete_despesa', '[UE] Pode excluir Gastos da Escola.'),
        )


class FuncUeCreditosDaEscola(models.Model):
    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[UE] Créditos da Escola"
        verbose_name_plural = "[UE] Créditos da Escola"

        permissions = (
            ('access_receita', '[UE] Pode acessar Créditos da Escola.'),
            ('add_valores_reprogramados', '[UE] Pode implantar valores reprogramados em Créditos da Escola.'),
            ('add_receita', '[UE] Pode incluir Créditos da Escola.'),
            ('change_receita', '[UE] Pode editar Créditos da Escola.'),
            ('delete_receita', '[UE] Pode excluir Créditos da Escola.'),
        )


class FuncUeDadosDaEscola(models.Model):
    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[UE] Dados da Associação"
        verbose_name_plural = "[UE] Dados da Associação"

        permissions = (
            ('access_dados_associacao', '[UE] Pode acessar Dados da Associação.'),
            ('change_associacao', '[UE] Pode editar Dados da Associação.'),
        )


class FuncUePrestacaoDeContas(models.Model):
    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[UE] Prestação de contas"
        verbose_name_plural = "[UE] Prestação de contas"

        permissions = (
            ('access_prestacao_contas', '[UE] Pode acessar Prestação de Contas:Geração de documentos.'),
            ('concluir_periodo_prestacao_contas', '[UE] Pode concluir período em Prestação de Contas.'),
            ('gerar_previas_prestacao_contas', '[UE] Pode gerar prévias em Prestação de Contas.'),
            ('baixar_documentos_prestacao_contas', '[UE] Pode baixar documentos de Prestação de Contas.'),
            ('change_ata_prestacao_contas', '[UE] Pode atualizar atas de Prestação de Contas.'),
        )


class FuncUeConciliacaoBancaria(models.Model):
    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[UE] Conciliação bancária"
        verbose_name_plural = "[UE] Conciliação bancária"

        permissions = (
            ('access_conciliacao_bancaria', '[UE] Pode acessar Conciliação Bancária.'),
            ('change_conciliacao_bancaria', '[UE] Pode atualizar Conciliação Bancária.'),
        )


class FuncUeGerais(models.Model):
    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[Global]"
        verbose_name_plural = "[Global]"

        permissions = (
            ('view_default', '[Global] Pode acessar as funcionalidades de livre acesso.'),
        )


class FuncUeGestaoPerfis(models.Model):
    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[UE] Gestão de perfis"
        verbose_name_plural = "[UE] Gestão de perfis"

        permissions = (
            ('access_gestao_perfis_ue', '[UE] Pode acessar Gestão de Perfis da UE.'),
        )


class FuncUeRecebimentoDeNotificacoes(models.Model):
    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[UE] Recebimento de notificações"
        verbose_name_plural = "[UE] Recebimento de notificações"

        permissions = (
            ('recebe_notificacao_inicio_periodo_prestacao_de_contas', '[UE] Pode receber Notificação Início Período Prestação De Contas.'),
            ('recebe_notificacao_pendencia_envio_prestacao_de_contas', '[UE] Pode receber Notificação pendência envio Prestação De Contas.'),
            ('recebe_notificacao_proximidade_inicio_prestacao_de_contas', '[UE] Pode receber Notificação Proximidade Início Prestação De Contas.'),
            ('recebe_notificacao_prestacao_de_contas_devolvida_para_acertos', '[UE] Pode receber Notificação Prestação de Contas Devolvida para Acertos'),
            ('recebe_notificacao_proximidade_fim_periodo_prestacao_de_contas', '[UE] Pode receber Notificação Proximidade Fim Período Prestação de Contas'),
            ('recebe_notificacao_atraso_entrega_ajustes_prestacao_de_contas', '[UE] Pode receber Notificação Atraso Entrega Ajustes Prestação de Contas'),
        )
