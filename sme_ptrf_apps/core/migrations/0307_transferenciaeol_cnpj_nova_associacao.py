# Generated by Django 2.2.10 on 2023-03-08 07:24

from django.db import migrations, models
import sme_ptrf_apps.core.models.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0306_transferenciaeol'),
    ]

    operations = [
        migrations.AddField(
            model_name='transferenciaeol',
            name='cnpj_nova_associacao',
            field=models.CharField(blank=True, default='', help_text='CNPJ da nova associação.', max_length=20, validators=[sme_ptrf_apps.core.models.validators.cnpj_validation], verbose_name='CNPJ'),
        ),
    ]