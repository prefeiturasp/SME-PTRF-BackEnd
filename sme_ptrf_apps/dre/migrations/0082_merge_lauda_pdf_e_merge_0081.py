# Merges parallel 0080 branches: lauda PDF field vs motivos merge.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dre", "0080_lauda_arquivo_pdf"),
        ("dre", "0081_merge_20260514_1000"),
    ]

    operations = []
