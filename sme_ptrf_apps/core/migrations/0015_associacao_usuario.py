# Generated by Django 2.2.10 on 2020-04-29 22:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0014_auto_20200420_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='associacao',
            name='usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='associacoes', to=settings.AUTH_USER_MODEL),
        ),
    ]
