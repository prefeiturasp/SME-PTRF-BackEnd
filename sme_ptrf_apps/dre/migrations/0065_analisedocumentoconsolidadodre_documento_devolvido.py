# Generated by Django 2.2.10 on 2022-12-02 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dre', '0064_analiseconsolidadodre_copiado'),
    ]

    operations = [
        migrations.AddField(
            model_name='analisedocumentoconsolidadodre',
            name='documento_devolvido',
            field=models.BooleanField(default=False, verbose_name='Já foi devolvido?'),
        ),
    ]
