from rest_framework import exceptions
from rest_framework.permissions import SAFE_METHODS, BasePermission

from sme_ptrf_apps.core.models import Associacao, PrestacaoConta
from sme_ptrf_apps.despesas.models import Despesa
from sme_ptrf_apps.receitas.models import Receita
from sme_ptrf_apps.dre.models import Atribuicao, RelatorioConsolidadoDRE


class PermissaoCRUD(BasePermission):
    perms_map = {
        'GET': ['view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['add_%(model_name)s'],
        'PUT': ['change_%(model_name)s'],
        'PATCH': ['change_%(model_name)s'],
        'DELETE': ['delete_%(model_name)s'],
    }

    def get_required_permissions(self, method, model_cls):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            'model_name': model_cls._meta.model_name
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]

    def get_user_permissions(self, user):
        perms = []
        for group in user.groups.all():
            for permission in group.permissions.all():
                perms.append(permission.codename)

        return perms

    def has_perm(self, perm, obj):
        user_permissions = self.get_user_permissions(obj)
        return perm in user_permissions

    def has_perms(self, perm_list, obj=None):
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.
        """
        return any(self.has_perm(perm, obj) for perm in perm_list)

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method, view.queryset.model)
        return self.has_perms(perms, request.user)


class PermissaoReceita(PermissaoCRUD):
    perms_map = {
        'GET': ['view_%(model_name)s'],
        'OPTIONS': ['view_%(model_name)s'],
        'HEAD': ['view_%(model_name)s'],
        'POST': ['add_%(model_name)s'],
        'PUT': ['change_%(model_name)s'],
        'PATCH': ['change_%(model_name)s'],
        'DELETE': ['delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method, Receita)
        return self.has_perms(perms, request.user)


class PermissaoDespesa(PermissaoCRUD):
    perms_map = {
        'GET': ['view_%(model_name)s'],
        'OPTIONS': ['view_%(model_name)s'],
        'HEAD': ['view_%(model_name)s'],
        'POST': ['add_%(model_name)s'],
        'PUT': ['change_%(model_name)s'],
        'PATCH': ['change_%(model_name)s'],
        'DELETE': ['delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method, Despesa)
        return self.has_perms(perms, request.user)


class PermissaoAssociacao(PermissaoCRUD):
    perms_map = {
        'GET': ['view_%(model_name)s'],
        'OPTIONS': ['view_%(model_name)s'],
        'HEAD': ['view_%(model_name)s'],
        'POST': ['add_%(model_name)s', 'change_%(model_name)s'],
        'PUT': ['change_%(model_name)s'],
        'PATCH': ['change_%(model_name)s'],
        'DELETE': ['delete_%(model_name)s', 'change_%(model_name)s'],
    }

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method, Associacao)
        return self.has_perms(perms, request.user)


class PermissaoPrestacaoConta(PermissaoCRUD):
    perms_map = {
        'GET': ['view_%(model_name)s'],
        'OPTIONS': ['view_%(model_name)s'],
        'HEAD': ['view_%(model_name)s'],
        'POST': ['add_%(model_name)s'],
        'PUT': ['change_%(model_name)s'],
        'PATCH': ['change_%(model_name)s'],
        'DELETE': ['delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            perms = self.get_required_permissions(request.method, PrestacaoConta)
            return self.has_perms(perms, request.user)
        return True


class PermissaoExportarDadosAssociacao(PermissaoCRUD):
    perms_map = {
        'GET': ['view_associacao'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': [],
        'PUT': [],
        'PATCH': [],
        'DELETE': [],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            perms = self.get_required_permissions(request.method)
            return self.has_perms(perms, request.user)
        return False


class PermissaoDashboardDre(PermissaoCRUD):
    perms_map = {
        'GET': ['access_acompanhamento_pcs_dre'],
        'OPTIONS': ['access_acompanhamento_pcs_dre'],
        'HEAD': ['access_acompanhamento_pcs_dre'],
        'POST': ['access_acompanhamento_pcs_dre'],
        'PUT': ['access_acompanhamento_pcs_dre'],
        'PATCH': ['access_acompanhamento_pcs_dre'],
        'DELETE': ['access_acompanhamento_pcs_dre'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoAssociacaoDre(PermissaoCRUD):
    perms_map = {
        'GET': ['access_associacao_dre'],
        'OPTIONS': ['access_associacao_dre'],
        'HEAD': ['access_associacao_dre'],
        'POST': ['access_associacao_dre'],
        'PUT': ['access_associacao_dre'],
        'PATCH': ['access_associacao_dre'],
        'DELETE': ['access_associacao_dre'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoDadosUnidadeDre(PermissaoCRUD):
    perms_map = {
        'GET': ['access_associacao_dre'],
        'OPTIONS': ['access_associacao_dre'],
        'HEAD': ['access_associacao_dre'],
        'POST': ['access_associacao_dre'],
        'PUT': ['access_associacao_dre'],
        'PATCH': ['access_associacao_dre'],
        'DELETE': ['access_associacao_dre'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoRegularidadeDre(PermissaoCRUD):
    perms_map = {
        'GET': ['access_associacao_dre'],
        'OPTIONS': ['access_associacao_dre'],
        'HEAD': ['access_associacao_dre'],
        'POST': ['access_associacao_dre'],
        'PUT': ['access_associacao_dre'],
        'PATCH': ['access_associacao_dre'],
        'DELETE': ['access_associacao_dre'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoSituacaoFinanceira(PermissaoCRUD):
    perms_map = {
        'GET': ['access_associacao_dre'],
        'OPTIONS': ['access_associacao_dre'],
        'HEAD': ['access_associacao_dre'],
        'POST': ['access_associacao_dre'],
        'PUT': ['access_associacao_dre'],
        'PATCH': ['access_associacao_dre'],
        'DELETE': ['access_associacao_dre'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoDadosDiretoriaDre(PermissaoCRUD):
    perms_map = {
        'GET': ['access_dados_diretoria'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': [],
        'PUT': [],
        'PATCH': [],
        'DELETE': [],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            perms = self.get_required_permissions(request.method)
            return self.has_perms(perms, request.user)
        return True


class PermissaoViewRelatorioConsolidadoDre(PermissaoCRUD):
    perms_map = {
        'GET': ['access_relatorio_consolidado_dre'],
        'OPTIONS': ['access_relatorio_consolidado_dre'],
        'HEAD': ['access_relatorio_consolidado_dre'],
        'POST': ['access_relatorio_consolidado_dre'],
        'PUT': ['access_relatorio_consolidado_dre'],
        'PATCH': ['access_relatorio_consolidado_dre'],
        'DELETE': ['access_relatorio_consolidado_dre'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoGerarRelatorioConsolidadoDre(PermissaoCRUD):
    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['gerar_relatorio_consolidado_dre'],
        'PUT': [],
        'PATCH': [],
        'DELETE': [],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoEditarRelatorioConsolidadoDre(PermissaoCRUD):
    """Está sendo usado para tratar a permissão para salvar justificativas"""
    perms_map = {
        'GET': ['change_relatorio_consolidado_dre', 'view_relatorio_consolidado_dre'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['change_relatorio_consolidado_dre'],
        'PUT': ['change_relatorio_consolidado_dre'],
        'PATCH': ['change_relatorio_consolidado_dre'],
        'DELETE': ['change_relatorio_consolidado_dre'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoVerConciliacaoBancaria(PermissaoCRUD):
    perms_map = {
        'GET': ['view_conciliacao'],
        'OPTIONS': ['view_conciliacao'],
        'HEAD': ['view_conciliacao'],
        'POST': [],
        'PUT': [],
        'PATCH': [],
        'DELETE': [],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoEditarConciliacaoBancaria(PermissaoCRUD):
    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['change_conciliacao'],
        'PUT': ['change_conciliacao'],
        'PATCH': ['change_conciliacao'],
        'DELETE': ['change_conciliacao'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoConciliacaoBancaria(PermissaoCRUD):
    perms_map = {
        'GET': ['view_conciliacao'],
        'OPTIONS': ['view_conciliacao'],
        'HEAD': ['view_conciliacao'],
        'POST': [],
        'PUT': [],
        'PATCH': ['change_conciliacao'],
        'DELETE': [],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoAtribuicao(PermissaoCRUD):
    perms_map = {
        'GET': ['view_%(model_name)s'],
        'OPTIONS': ['view_%(model_name)s'],
        'HEAD': ['view_%(model_name)s'],
        'POST': ['add_%(model_name)s'],
        'PUT': ['change_%(model_name)s'],
        'PATCH': ['change_%(model_name)s'],
        'DELETE': ['delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method, Atribuicao)
        return self.has_perms(perms, request.user)


class PermissaoRelatorioConsolidadoDre(PermissaoCRUD):
    perms_map = {
        'GET': ['view_relatorio_consolidado_dre'],
        'OPTIONS': ['view_relatorio_consolidado_dre'],
        'HEAD': ['view_relatorio_consolidado_dre'],
        'POST': ['create_relatorio_consolidado_dre'],
        'PUT': ['change_relatorio_consolidado_dre'],
        'PATCH': ['change_relatorio_consolidado_dre'],
        'DELETE': [],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoApiUe(PermissaoCRUD):
    """
    Recursos de API da visão de Unidade Escolar são acessíveis também para as visões de DRE e SME
    """
    perms_map = {
        'GET': ['ue_leitura', 'ue_gravacao', 'dre_leitura', 'dre_gravacao', 'sme_leitura', 'sme_gravacao'],
        'OPTIONS': ['ue_leitura', 'ue_gravacao', 'dre_leitura', 'dre_gravacao', 'sme_leitura', 'sme_gravacao'],
        'HEAD': ['ue_leitura', 'ue_gravacao', 'dre_leitura', 'dre_gravacao', 'sme_leitura', 'sme_gravacao'],
        'POST': ['ue_gravacao', 'dre_gravacao', 'sme_gravacao'],
        'PUT': ['ue_gravacao', 'dre_gravacao', 'sme_gravacao'],
        'PATCH': ['ue_gravacao', 'dre_gravacao', 'sme_gravacao'],
        'DELETE': ['ue_gravacao', 'dre_gravacao', 'sme_gravacao'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoApiDre(PermissaoCRUD):
    """
    Recursos de API da visão de DRE são acessíveis também para a visão de SME e não para a de UE.
    """
    perms_map = {
        'GET': ['dre_leitura', 'dre_gravacao', 'sme_leitura', 'sme_gravacao'],
        'OPTIONS': ['dre_leitura', 'dre_gravacao', 'sme_leitura', 'sme_gravacao'],
        'HEAD': ['dre_leitura', 'dre_gravacao', 'sme_leitura', 'sme_gravacao'],
        'POST': ['dre_gravacao', 'sme_gravacao'],
        'PUT': ['dre_gravacao', 'sme_gravacao'],
        'PATCH': ['dre_gravacao', 'sme_gravacao'],
        'DELETE': ['dre_gravacao', 'sme_gravacao'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoAPITodosComLeituraOuGravacao(PermissaoCRUD):
    perms_map = {
        'GET': ['ue_leitura', 'ue_gravacao', 'dre_leitura', 'dre_gravacao', 'sme_leitura', 'sme_gravacao'],
        'OPTIONS': ['ue_leitura', 'ue_gravacao', 'dre_leitura', 'dre_gravacao', 'sme_leitura', 'sme_gravacao'],
        'HEAD': ['ue_leitura', 'ue_gravacao', 'dre_leitura', 'dre_gravacao', 'sme_leitura', 'sme_gravacao'],
        'POST': ['ue_leitura', 'ue_gravacao', 'dre_leitura', 'dre_gravacao', 'sme_leitura', 'sme_gravacao'],
        'PUT': ['ue_leitura', 'ue_gravacao', 'dre_leitura', 'dre_gravacao', 'sme_leitura', 'sme_gravacao'],
        'PATCH': ['ue_leitura', 'ue_gravacao', 'dre_leitura', 'dre_gravacao', 'sme_leitura', 'sme_gravacao'],
        'DELETE': ['ue_leitura', 'ue_gravacao', 'dre_leitura', 'dre_gravacao', 'sme_leitura', 'sme_gravacao'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoAPITodosComGravacao(PermissaoCRUD):
    perms_map = {
        'GET': ['ue_gravacao', 'dre_gravacao', 'sme_gravacao'],
        'OPTIONS': ['ue_gravacao', 'dre_gravacao', 'sme_gravacao'],
        'HEAD': ['ue_gravacao', 'dre_gravacao', 'sme_gravacao'],
        'POST': ['ue_gravacao', 'dre_gravacao', 'sme_gravacao'],
        'PUT': ['ue_gravacao', 'dre_gravacao', 'sme_gravacao'],
        'PATCH': ['ue_gravacao', 'dre_gravacao', 'sme_gravacao'],
        'DELETE': ['ue_gravacao', 'dre_gravacao', 'sme_gravacao'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoAPIApenasDreComGravacao(PermissaoCRUD):
    perms_map = {
        'GET': ['dre_gravacao'],
        'OPTIONS': ['dre_gravacao'],
        'HEAD': ['dre_gravacao'],
        'POST': ['dre_gravacao'],
        'PUT': ['dre_gravacao'],
        'PATCH': ['dre_gravacao'],
        'DELETE': ['dre_gravacao'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoAPIApenasDreComLeituraOuGravacao(PermissaoCRUD):
    perms_map = {
        'GET': ['dre_leitura', 'dre_gravacao'],
        'OPTIONS': ['dre_leitura', 'dre_gravacao'],
        'HEAD': ['dre_leitura', 'dre_gravacao'],
        'POST': ['dre_leitura', 'dre_gravacao'],
        'PUT': ['dre_leitura', 'dre_gravacao'],
        'PATCH': ['dre_leitura', 'dre_gravacao'],
        'DELETE': ['dre_leitura', 'dre_gravacao'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)
