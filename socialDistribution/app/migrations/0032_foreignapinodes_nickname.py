# Generated by Django 4.1.7 on 2023-03-23 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_alter_author_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='foreignapinodes',
            name='nickname',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
