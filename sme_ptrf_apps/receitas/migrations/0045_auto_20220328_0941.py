# Generated by Django 2.2.10 on 2022-03-28 09:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('receitas', '0044_auto_20220322_1435'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='motivoestorno',
            unique_together={('motivo',)},
        ),
    ]
