from unittest.mock import patch

import pytest

from sme_ptrf_apps.core.tasks.enviar_emails_alertas_paginas import enviar_emails_alertas_paginas_async

pytestmark = pytest.mark.django_db

TASK = 'sme_ptrf_apps.core.tasks.enviar_emails_alertas_paginas'


def test_dispatcher_enfileira_uma_task_por_usuario():
    with patch(f'{TASK}.AlertaPaginaEmailService.registrar_disparos_do_dia', return_value=[(1, 10), (1, 11)]), \
            patch(f'{TASK}.enviar_email_alerta_pagina_usuario_async.delay') as mock_delay:
        total = enviar_emails_alertas_paginas_async()

    assert total == 2
    assert [c.args for c in mock_delay.call_args_list] == [(1, 10), (1, 11)]
