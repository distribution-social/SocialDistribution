# Generated by Django 4.1.7 on 2023-03-03 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_comment_contenttype_comment_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='contentType',
            field=models.CharField(choices=[('text/markdown', 'markdown'), ('text/plain', 'plain_text')], default='text/plain', max_length=18),
        ),
    ]