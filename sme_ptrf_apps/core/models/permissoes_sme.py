from django.db import models

"""
Esses modelos existem apenas para criação das permissions usadas
para a gestão de acesso de cada funcionalidade da aplicação.

Nenhuma tabela será criada para esses modelos no banco de dados.

Cada modelo representa uma funcionalidade da aplicação e define as permissões usadas nessa funcionalidade.
"""


class FuncSmePainelParametrizacoes(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[SME] Painel de Parametrizacoes"
        verbose_name_plural = "[SME] Painel de Parametrizacoes"

        permissions = (
            ('access_painel_parametrizacoes', '[SME] Pode acessar o Painel de parametrizações.'),
        )


class FuncSmeAcompanhamentoDePc(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[SME] Acompanhamento de PC"
        verbose_name_plural = "[SME] Acompanhamento de PC"

        permissions = (
            ('access_acompanhamento_pc_sme', '[SME] Pode acessar o Acompanhamento de PC.'),
        )


class FuncSmeGestaoPerfis(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[SME] Gestão de perfis"
        verbose_name_plural = "[SME] Gestão de perfis"

        permissions = (
            ('access_gestao_perfis_sme', '[SME] Pode acessar Gestão de Perfis da SME.'),
        )


class FuncSmeArquivosCarga(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[SME] Arquivos de carga"
        verbose_name_plural = "[SME] Arquivos de carga"

        permissions = (
            ('access_arquivos_carga', '[SME] Pode acessar Arquivos de Carga em parametrizações.'),
        )


class FuncSmeConsultaSaldoBancario(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[SME] Consulta Saldo Bancário"
        verbose_name_plural = "[SME] Consulta Saldos Bancários"

        permissions = (
            ('access_consulta_saldo_bancario', '[SME] Pode acessar a consulta de saldo bancário.'),
        )


class FuncSmeFornecedores(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[SME] Parametrização Cadastro de Fornecedor"
        verbose_name_plural = "[SME] Parametrizações Cadastro de Fornecedores"

        permissions = (
            ('access_fornecedores', '[SME] Pode acessar parametrizações cadastro de fornecedores.'),
            ('change_fornecedores', '[SME] Pode atualizar parametrizações cadastro de fornecedores.'),
        )


class FuncSmeSuporteUnidades(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[SME] Suporte às unidades"
        verbose_name_plural = "[SME] Suporte às unidades"

        permissions = (
            ('access_suporte_unidades_sme', '[SME] Pode acessar o suporte às unidades (SME).'),
        )


class FuncSmeExtracaoDeDados(models.Model):

    class Meta:
        managed = False
        default_permissions = ()

        verbose_name = "[SME] Extração de dados"
        verbose_name_plural = "[SME] Extração de dados"

        permissions = (
            ('access_extracao_de_dados_sme', '[SME] Pode acessar Extração de dados da SME.'),
        )


class FuncSmeAnaliseRelatoriosConsolidados(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[SME] Análise de Relatório Consolidado"
        verbose_name_plural = "[SME] Análises de Relatórios Consolidados"

        permissions = (
            ('access_analise_relatorios_consolidados_sme', '[SME] Pode acessar a Análise de Relatórios Consolidados.'),
        )
