# Generated by Django 5.0.7 on 2025-01-21 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsapp', '0002_rename_mouja_name_plotdetailsmodel_plot_no_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaserdetailsmodel',
            name='phone_no',
            field=models.CharField(max_length=10),
        ),
    ]
