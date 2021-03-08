from sme_ptrf_apps.users.models import Grupo

'''
Para executar o script no terminal:

    > python manage.py shell_plus

    :from sme_ptrf_apps.contrib.exporta_grupos_csv import exporta_grupos
    :exporta_grupos()

'''


def exporta_grupos():
    import csv

    with open('grupos.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Nome", "Descricao", "Visoes", "Permissoes"])
        for grupo in Grupo.objects.all():
            visoes = ""
            for visao in grupo.visoes.all():
                visoes = f'{visoes}{"|" if visoes else ""}{visao.nome}'

            permissoes = ""
            for permissao in grupo.permissions.all():
                permissoes = f'{permissoes}{"|" if permissoes else ""}{permissao.codename}'
            writer.writerow([grupo.name, grupo.descricao, visoes, permissoes])


def exporta_permissoes():
    import csv
    from django.contrib.auth.models import Permission

    with open('permissoes.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Nome", "Descricao"])
        for permissao in Permission.objects.all():
            writer.writerow([permissao.codename, permissao.name])
