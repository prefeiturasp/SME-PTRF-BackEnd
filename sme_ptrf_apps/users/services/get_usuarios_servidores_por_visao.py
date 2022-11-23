from django.contrib.auth import get_user_model
User = get_user_model()


def get_usuarios_servidores_por_visao(visao):
    usuarios = User.objects.filter(
        e_servidor=True,
        visoes=visao
    ).order_by('username')

    usuarios_list = []

    if usuarios:
        for usuario in usuarios:
            obj = {
                'usuario': f'{usuario.username} - {usuario.name}',
                'username': f'{usuario.username}',
                'nome': f'{usuario.name}',
            }
            usuarios_list.append(obj)

    return usuarios_list
