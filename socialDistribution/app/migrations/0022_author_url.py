# Generated by Django 4.1.7 on 2023-03-21 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_merge_20230303_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='url',
            field=models.URLField(null=True, unique=True),
        ),
    ]
