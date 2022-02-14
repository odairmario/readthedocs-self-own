# Generated by Django 3.2.11 on 2022-01-31 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0007_update-provider-data'),
    ]

    operations = [
        migrations.AddField(
            model_name='httpexchange',
            name='request_headers_json',
            field=models.JSONField(default=None, null=True, verbose_name='Request headers'),
        ),
        migrations.AddField(
            model_name='httpexchange',
            name='response_headers_json',
            field=models.JSONField(default=None, null=True, verbose_name='Request headers'),
        ),
        migrations.AddField(
            model_name='integration',
            name='provider_data_json',
            field=models.JSONField(default=dict, verbose_name='Provider data'),
        ),
    ]
