# Generated by Django 4.1.7 on 2023-04-02 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0037_alter_author_displayname_alter_author_github_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='profileImage',
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
    ]
