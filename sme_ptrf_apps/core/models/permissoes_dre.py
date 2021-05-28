from django.db import models

"""
Esses modelos existem apenas para criação das permissions usadas
para a gestão de acesso de cada funcionalidade da aplicação.

Nenhuma tabela será criada para esses modelos no banco de dados.

Cada modelo representa uma funcionalidade da aplicação e define as permissões usadas nessa funcionalidade.
"""


class FuncDreAssociacoesDaDre(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[DRE] Associações da DRE"
        verbose_name_plural = "[DRE] Associações da DRE"

        permissions = (
            ('access_associacao_dre', '[DRE] Pode acessar Associações da DRE.'),
            ('access_dados_unidade_dre', '[DRE] Pode acessar dados de uma unidade.'),
            ('access_regularidade_dre', '[DRE] Pode acessar regularidade de uma unidade.'),
            ('access_situacao_financeira_dre', '[DRE] Pode acessar a situação financeira de uma unidade.'),
            ('change_regularidade', '[DRE] Pode atualizar a regularidade de uma unidade.'),
        )


class FuncDreDadosDaDiretoria(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[DRE] Dados da diretoria"
        verbose_name_plural = "[DRE] Dados da diretoria"

        permissions = (
            ('access_dados_diretoria', '[DRE] Pode acessar Dados da Diretoria.'),
            ('change_dados_diretoria', '[DRE] Pode atualizar Dados da Diretoria.'),
        )


class FuncDreFaqDre(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[DRE] FAQ"
        verbose_name_plural = "[DRE] FAQ"

        permissions = (
            ('access_faq_dre', '[DRE] Pode acessar FAQ.'),
        )


class FuncDreAcompanhamentoDePcs(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[DRE] Acompanhamento de PCs"
        verbose_name_plural = "[DRE] Acompanhamento de PCs"

        permissions = (
            ('access_acompanhamento_pcs_dre', '[DRE] Pode acessar Acompanhamento de PCs.'),
        )


class FuncDreRelatorioConsolidado(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[DRE] Relatório consolidado"
        verbose_name_plural = "[DRE] Relatório consolidado"

        permissions = (
            ('access_relatorio_consolidado_dre', '[DRE] Pode acessar Relatório Consolidado.'),
            ('change_relatorio_consolidado_dre', '[DRE] Pode atualizar informações dos Relatórios Consolidados.'),
            ('gerar_relatorio_consolidado_dre', '[DRE] Pode gerar Relatório Consolidado.'),
        )


class FuncDreGestaoPerfis(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[DRE] Gestão de perfis"
        verbose_name_plural = "[DRE] Gestão de perfis"

        permissions = (
            ('access_gestao_perfis_dre', '[DRE] Pode acessar Gestão de Perfis da DRE.'),
        )


class FuncDreAtribuicaoPorUe(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[DRE] Atribuição por UE"
        verbose_name_plural = "[DRE] Atribuições por UE"

        permissions = (
            ('access_atribuicao_por_ue', '[DRE] Pode acessar Atribuição por UE.'),
            ('change_atribuicao_por_ue', '[DRE] Pode atualizar Atribuição por UE.'),
        )
