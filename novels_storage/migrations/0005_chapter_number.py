# Generated by Django 5.1.1 on 2024-09-14 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novels_storage', '0004_alter_chapter_link_alter_novel_author_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='number',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
    ]
