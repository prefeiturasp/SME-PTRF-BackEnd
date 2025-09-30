# tests/factories.py
import factory
from django.core.files.uploadedfile import SimpleUploadedFile


class PDFFactory(factory.Factory):
    class Meta:
        model = SimpleUploadedFile

    name = "comprovante.pdf"
    content = factory.LazyAttribute(
        lambda _: bytes("CONTEUDO TESTE TESTE TESTE", encoding="utf-8")
    )
    content_type = "application/pdf"
