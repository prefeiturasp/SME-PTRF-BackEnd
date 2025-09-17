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


class FuncUeAnaliseDre(models.Model):
    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[UE] Análise DRE"
        verbose_name_plural = "[UE] Análises DRE"

        permissions = (
            ('access_analise_dre', '[UE] Pode acessar Análise DRE.'),
            ('change_analise_dre', '[UE] Pode atualizar Análise DRE.'),
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
            ('recebe_notificacao_proximidade_fim_prazo_ajustes_prestacao_de_contas', '[UE] Pode receber Notificação Proximidade Fim Prazo Ajustes Prestação de Contas'),
            ('recebe_notificacao_comentario_em_pc', '[UE] Pode receber Notificação de Comentários'),
            ('recebe_notificacao_aprovacao_pc', '[UE] Pode receber Notificação Prestação de Contas Aprovada'),
            ('recebe_notificacao_reprovacao_pc_nao_incluindo_motivos', '[UE] Pode receber Notificação Prestação de Contas Reprovada Não Incluindo Motivos'),
            ('recebe_notificacao_reprovacao_pc_incluindo_motivos', '[UE] Pode receber Notificação Prestação de Contas Reprovada Incluindo Motivos'),
            ('recebe_notificacao_automatica_inativacao_conta', '[UE] Pode receber Notificação Encerramento de Conta Bancária'),
            ('recebe_notificacao_resultado_encerramento_conta', '[UE] Pode receber Notificação Resultado Encerramento de Conta Bancária'),
            ('recebe_notificacao_geracao_ata_apresentacao', '[UE] Pode receber Notificação Geração Ata de Apresentação'),
            ('recebe_notificacao_geracao_ata_retificacao', '[UE] Pode receber Notificação Geração Ata de Retificação'),
            ('recebe_notificacao_conclusao_reprovada_pc_nao_apresentada', '[UE] Pode receber Notificação Prestação de Contas Reprovada Não Apresentação'),
        )


class FuncValoresReprogramadosUE(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[UE] Valor Reprogramado"
        verbose_name_plural = "[UE] Valores Reprogramados"

        permissions = (
            ('access_valores_reprogramados_ue', '[UE] Pode acessar Valores Reprogramados.'),
            ('change_valores_reprogramados_ue', '[UE] Pode atualizar Valores Reprogramados.'),
        )

class FuncUeGestaoUsuarios(models.Model):
    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[UE] Gestão de usuários"
        verbose_name_plural = "[UE] Gestão de usuários"

        permissions = (
            ('access_gestao_usuarios_ue', '[UE] Pode acessar Gestão de Usuários da UE.'),
            ('change_gestao_usuarios_ue', '[UE] Pode atualizar Gestão de Usuários da UE.'),
        )


# Nova versão com mandato e composições
class FuncUeMembrosDaAssociacao(models.Model):
    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[UE] Membro da Associação"
        verbose_name_plural = "[UE] Membros da Associação"

        permissions = (
            ('access_membros_da_associacao', '[UE] Pode acessar Membros da Associação.'),
            ('change_membros_da_associacao', '[UE] Pode editar Membros da Associação.'),
        )
        
class FuncUePlanoAnualDeAtividade(models.Model):
    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[UE] Plano anual de atividade"
        verbose_name_plural = "[UE] Plano anual de atividade"

        permissions = (
            ('access_paa', '[UE] Pode acessar Plano Anual de Atividade.'),
            ('change_paa', '[UE] Pode editar Plano Anual de Atividade".'),
        )

class FuncUeSituacaoPatrimonial(models.Model):
    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[UE] Situação Patrimonial"
        verbose_name_plural = "[UE] Situação Patrimonial"

        permissions = (
            ('access_situacao_patrimonial', '[UE] Pode acessar Situação Patrimonial.'),
            ('change_situacao_patrimonial', '[UE] Pode editar Situação Patrimonial".'),
        )