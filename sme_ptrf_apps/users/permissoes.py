from rest_framework import exceptions
from rest_framework.permissions import BasePermission


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


class PermissaoAPIApenasSmeComGravacao(PermissaoCRUD):
    perms_map = {
        'GET': ['sme_gravacao'],
        'OPTIONS': ['sme_gravacao'],
        'HEAD': ['sme_gravacao'],
        'POST': ['sme_gravacao'],
        'PUT': ['sme_gravacao'],
        'PATCH': ['sme_gravacao'],
        'DELETE': ['sme_gravacao'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)


class PermissaoAPIApenasSmeComLeituraOuGravacao(PermissaoCRUD):
    perms_map = {
        'GET': ['sme_leitura', 'sme_gravacao'],
        'OPTIONS': ['sme_leitura', 'sme_gravacao'],
        'HEAD': ['sme_leitura', 'sme_gravacao'],
        'POST': ['sme_leitura', 'sme_gravacao'],
        'PUT': ['sme_leitura', 'sme_gravacao'],
        'PATCH': ['sme_leitura', 'sme_gravacao'],
        'DELETE': ['sme_leitura', 'sme_gravacao'],
    }

    def get_required_permissions(self, method):
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return self.has_perms(perms, request.user)
