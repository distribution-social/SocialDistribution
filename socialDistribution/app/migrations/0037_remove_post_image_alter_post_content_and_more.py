# Generated by Django 4.1.7 on 2023-03-30 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0036_comment_contenttype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='image',
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='content_type',
            field=models.CharField(choices=[('text/markdown', 'text/markdown'), ('text/plain', 'text/plain'), ('image/png', 'image/png'), ('image/jpeg', 'image/jpeg')], max_length=18),
        ),
    ]