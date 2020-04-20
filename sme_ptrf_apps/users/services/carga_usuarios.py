import csv
import logging
import os

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.storage import staticfiles_storage

from sme_ptrf_apps.core.models import Associacao

logger = logging.getLogger(__name__)

User = get_user_model()


def processa_importacao_usuarios(reader):
    try:
        for index, row in enumerate(reader):
            if index != 0:
                logger.info('Linha %s: %s', index, row)
                associacao = Associacao.objects.filter(cnpj=row[1].strip()).first()
                if associacao:
                    User.objects.update_or_create(username=row[0].strip(),
                        default={'associacao': associacao})
                    logger.info('Usuário para o rf %s criado com sucesso.', row[0].strip())
                    continue

                logger.info('Associação para o CNPJ %s não encontrado.', row[1].strip())
    except Exception as e:
        logging.info('Error: %s', str(e))


def carrega_usuarios():
    logger.info('Carregando arquivo de usuários.')

    with staticfiles_storage.open(os.path.join('cargas', 'usuarios.csv'), 'r') as f:
        reader = csv.reader(f, delimiter=',')
        processa_importacao_usuarios(reader)
