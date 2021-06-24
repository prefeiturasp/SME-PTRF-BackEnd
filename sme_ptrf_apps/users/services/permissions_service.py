from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models import Q
User = get_user_model()


def get_users_by_permission(permissao):
    try:
        perm = Permission.objects.get(codename=permissao)
        users = User.objects.filter(Q(groups__permissions=perm) | Q(user_permissions=perm)).distinct()
        return users
    except (ValueError, Permission.DoesNotExist, User.DoesNotExist):
        return False




