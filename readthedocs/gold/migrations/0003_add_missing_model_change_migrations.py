# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-31 10:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gold', '0002_rename_last_4_digits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='golduser',
            name='level',
            field=models.CharField(choices=[('v1-org-5', '$5/mo'), ('v1-org-10', '$10/mo'), ('v1-org-15', '$15/mo'), ('v1-org-20', '$20/mo'), ('v1-org-50', '$50/mo'), ('v1-org-100', '$100/mo')], default='v1-org-5', max_length=20, verbose_name='Level'),
        ),
    ]
