# Generated by Django 5.0.7 on 2025-01-25 02:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsapp', '0004_earningmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='earningmodel',
            name='member',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='cmsapp.membermodel', verbose_name=''),
            preserve_default=False,
        ),
    ]
