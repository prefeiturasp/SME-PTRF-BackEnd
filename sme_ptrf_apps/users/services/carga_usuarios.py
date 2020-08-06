import csv
import logging

from django.contrib.auth import get_user_model

from sme_ptrf_apps.core.models import Unidade
from sme_ptrf_apps.users.models import Visao

logger = logging.getLogger(__name__)

User = get_user_model()


def processa_importacao_usuarios(reader):
    try:
        for index, row in enumerate(reader):
            if index != 0:
                logger.info('Linha %s: %s', index, row)

                unidade = Unidade.objects.filter(codigo_eol=row[2].strip()).first()

                if unidade:
                    visao = Visao.objects.filter(nome=row[1].strip()).first()
                    if not visao:
                        visao = Visao.objects.create(nome=row[1].strip())

                    u = User.objects.filter(username=row[0].strip()).first()
                    if not u:
                        u = User.objects.create(username=row[0].strip())

                    if not u.unidades.filter(codigo_eol=row[2].strip()).first():
                        u.unidades.add(unidade)

                    if not u.visoes.filter(nome=row[1].strip()).first():
                        u.visoes.add(visao)
                    u.save()
                    logger.info('Usuário para o rf %s criado com sucesso.', row[0].strip())
                    continue

                logger.info('Associação para o CNPJ %s não encontrado.', row[1].strip())
    except Exception as e:
        logging.info('Error: %s', str(e))


def carrega_usuarios(arquivo):
    logger.info('Carregando arquivo de usuários.')

    with open(arquivo.conteudo.path, 'r', encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=',')
        processa_importacao_usuarios(reader)
