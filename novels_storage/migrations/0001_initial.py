# Generated by Django 5.1.1 on 2024-09-20 14:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Novel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
                ('summary', models.TextField(blank=True, max_length=16256, null=True)),
                ('novel_directory', models.CharField(blank=True, max_length=2048, null=True)),
                ('chapter_link_pages_directory', models.CharField(blank=True, max_length=2048, null=True)),
                ('chapter_pages_directory', models.CharField(blank=True, max_length=2048, null=True)),
                ('initialized', models.BooleanField(default=False)),
                ('is_being_updated', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='NovelAuthor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='NovelCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='NovelCompletionStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='NovelLanguage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='NovelTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('website_directory', models.CharField(blank=True, max_length=2048, null=True)),
                ('novel_link_pages_directory', models.CharField(blank=True, max_length=8096, null=True)),
                ('novels_directory', models.CharField(blank=True, max_length=2048, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_published', models.DateField()),
                ('name', models.CharField(max_length=512)),
                ('number', models.CharField(max_length=128)),
                ('text', models.TextField(max_length=32512)),
                ('novel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chapters', to='novels_storage.novel')),
            ],
        ),
        migrations.AddField(
            model_name='novel',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='novels', to='novels_storage.novelauthor'),
        ),
        migrations.AddField(
            model_name='novel',
            name='categories',
            field=models.ManyToManyField(related_name='novels', to='novels_storage.novelcategory'),
        ),
        migrations.AddField(
            model_name='novel',
            name='completion_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='novels', to='novels_storage.novelcompletionstatus'),
        ),
        migrations.AddField(
            model_name='novel',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='novels', to='novels_storage.novellanguage'),
        ),
        migrations.AddField(
            model_name='novel',
            name='tags',
            field=models.ManyToManyField(related_name='novels', to='novels_storage.noveltag'),
        ),
        migrations.AddField(
            model_name='novel',
            name='website',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='novels', to='novels_storage.website'),
        ),
    ]
