# Generated by Django 3.2.4 on 2021-06-21 13:37

import chat.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('uploaded_by', models.CharField(blank=True, max_length=255, null=True, verbose_name='name')),
                ('file', models.FileField(upload_to=chat.models.user_directory_path, verbose_name='File')),
                ('upload_date', models.DateTimeField(auto_now_add=True, verbose_name='Upload date')),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='message', to='chat.uploadedfile', verbose_name='File'),
        ),
    ]
