# Generated by Django 5.1.1 on 2024-09-18 04:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spiders_manager', '0014_rename_processes_bad_content_websiteupdateinstance_bad_content_errors_faced_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='websiteupdateinstance',
            name='update_cycle',
        ),
        migrations.RemoveField(
            model_name='websiteupdateinstance',
            name='website',
        ),
        migrations.DeleteModel(
            name='SpiderInstanceProcess',
        ),
        migrations.DeleteModel(
            name='UpdateCycle',
        ),
        migrations.DeleteModel(
            name='WebsiteUpdateInstance',
        ),
    ]
