# Generated by Django 2.2.3 on 2020-05-16 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20200516_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='emotion',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]