import hashlib
import json

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class AtaParecerTecnicoSnapshot(ModeloBase):
    history = AuditlogHistoryField()

    ORIGEM_PUBLICACAO = "PUBLICACAO"
    ORIGEM_MANUAL = "MANUAL"
    ORIGEM_TELA = "TELA"
    ORIGEM_MIGRACAO = "MIGRACAO"

    ORIGEM_CHOICES = (
        (ORIGEM_PUBLICACAO, "Publicacao"),
        (ORIGEM_MANUAL, "Manual"),
        (ORIGEM_TELA, "Tela"),
        (ORIGEM_MIGRACAO, "Migracao"),
    )

    ata = models.OneToOneField(
        "AtaParecerTecnico",
        on_delete=models.CASCADE,
        related_name="snapshot",
    )
    dados = models.JSONField(default=dict)
    schema_version = models.PositiveSmallIntegerField(default=1)
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES, default=ORIGEM_PUBLICACAO)
    hash_dados = models.CharField(max_length=64)
    congelado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Snapshot da Ata de Parecer Técnico ID: {self.ata_id} - Versão {self.schema_version}"

    class Meta:
        verbose_name = "Ata de Parecer Tecnico - Snapshot"
        verbose_name_plural = "Atas de Parecer Tecnico - Snapshots"

    @staticmethod
    def normalizar_dados(dados):
        # Converte UUID/date/Decimal e similares para tipos JSON puros.
        payload = json.dumps(dados, ensure_ascii=False, cls=DjangoJSONEncoder)
        return json.loads(payload)

    @classmethod
    def calcular_hash(cls, dados):
        dados_normalizados = cls.normalizar_dados(dados)
        payload = json.dumps(
            dados_normalizados,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            cls=DjangoJSONEncoder,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def criar_se_nao_existir(cls, ata, dados, schema_version=1, origem=ORIGEM_PUBLICACAO):
        snapshot = cls.objects.filter(ata=ata).first()
        if snapshot:
            return snapshot, False

        dados_normalizados = cls.normalizar_dados(dados)

        snapshot = cls.objects.create(
            ata=ata,
            dados=dados_normalizados,
            schema_version=schema_version,
            origem=origem,
            hash_dados=cls.calcular_hash(dados_normalizados),
        )
        return snapshot, True


auditlog.register(AtaParecerTecnicoSnapshot)
