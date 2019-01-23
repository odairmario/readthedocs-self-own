# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-16 18:30
import uuid

import django.db.models.deletion
import jsonfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='HttpExchange',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('object_id', models.PositiveIntegerField()),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Date')),
                ('request_headers', jsonfield.fields.JSONField(verbose_name='Request headers')),
                ('request_body', models.TextField(verbose_name='Request body')),
                ('response_headers', jsonfield.fields.JSONField(verbose_name='Request headers')),
                ('response_body', models.TextField(verbose_name='Response body')),
                ('status_code', models.IntegerField(default=200, verbose_name='Status code')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
