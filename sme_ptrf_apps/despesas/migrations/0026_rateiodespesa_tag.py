# Generated by Django 2.2.10 on 2020-07-24 16:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_tag'),
        ('despesas', '0025_tipodocumento_numero_documento_digitado'),
    ]

    operations = [
        migrations.AddField(
            model_name='rateiodespesa',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rateios', to='core.Tag'),
        ),
    ]
