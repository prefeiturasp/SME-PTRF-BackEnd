# Generated by Django 2.2.10 on 2023-03-24 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dre', '0077_update_m2m_pcs_do_consolidado'),
    ]

    operations = [
        migrations.AddField(
            model_name='lauda',
            name='sem_movimentacao',
            field=models.BooleanField(default=False, verbose_name='Sem movimentação?'),
        ),
    ]
