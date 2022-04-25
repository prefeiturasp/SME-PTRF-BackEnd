from sme_ptrf_apps.core.models_abstracts import ModeloBase
from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class PresenteAta(ModeloBase):
    history = AuditlogHistoryField()

    ata = models.ForeignKey('Ata', on_delete=models.CASCADE, related_name='presentes_na_ata')
    identificacao = models.CharField('Identificacão do presente (RF,CPF ou EOL)', max_length=20, blank=True, default='')
    nome = models.CharField('Nome', max_length=200, blank=True, default='')
    cargo = models.CharField('Cargo', max_length=200, blank=True, default='')
    membro = models.BooleanField('Membro ?', default=False)
    conselho_fiscal = models.BooleanField('Pertence ao conselho fiscal ?', default=False)

    def eh_conselho_fiscal(self):
        if "Presidente do conselho fiscal" in self.cargo or "Conselheiro" in self.cargo:
            self.conselho_fiscal = True
            self.save()

    @property
    def editavel(self):
        return False

    @classmethod
    def get_informacao_servidor(cls, identificador):
        from sme_ptrf_apps.core.services import TerceirizadasException, TerceirizadasService, SmeIntegracaoApiException
        from requests import ConnectTimeout, ReadTimeout

        try:
            if identificador:
                if len(identificador) == 7:
                    servidor = TerceirizadasService.get_informacao_servidor(identificador)
                    if servidor:
                        result = {
                            "mensagem": "buscando-servidor-nao-membro",
                            "nome": servidor[0]["nm_pessoa"],
                            "cargo": servidor[0]["cargo"]
                        }

                        return result
        except SmeIntegracaoApiException as e:
            print({'detail': str(e)})
        except TerceirizadasException as e:
            print({'detail': str(e)})
        except ReadTimeout:
            print({'detail': 'EOL Timeout'})
        except ConnectTimeout:
            print({'detail': 'EOL Timeout'})

        result = {
            "mensagem": "servidor-nao-encontrado",
            "nome": "",
            "cargo": ""
        }

        return result

    class Meta:
        verbose_name = "Presente da ata"
        verbose_name_plural = "17.0) Presentes das atas"


auditlog.register(PresenteAta)
