# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2018-03-15 16:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redirects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redirect',
            name='redirect_type',
            field=models.CharField(choices=[('prefix', 'Prefix Redirect'), ('page', 'Page Redirect'), ('exact', 'Exact Redirect'), ('sphinx_html', 'Sphinx HTMLDir -> HTML'), ('sphinx_htmldir', 'Sphinx HTML -> HTMLDir')], help_text='The type of redirect you wish to use.', max_length=255, verbose_name='Redirect Type'),
        ),
        migrations.AlterField(
            model_name='redirect',
            name='to_url',
            field=models.CharField(blank=True, db_index=True, help_text='Absolute or relative URL. Examples: <b>/tutorial/install.html</b>', max_length=255, verbose_name='To URL'),
        ),
    ]
