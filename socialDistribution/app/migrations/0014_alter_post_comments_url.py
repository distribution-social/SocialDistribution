# Generated by Django 4.1.6 on 2023-03-02 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_remove_post_categories'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='comments_url',
            field=models.URLField(),
        ),
    ]
