# Generated by Django 2.2.11 on 2020-03-18 18:27

from django.db import migrations


def forwards_func(apps, schema_editor):
    """Migrate all protected versions to be hidden."""
    Version = apps.get_model('builds', 'Version')
    Version.objects.filter(privacy_level='protected').update(hidden=True)


class Migration(migrations.Migration):

    dependencies = [
        ('builds', '0015_add_hidden_field_to_version'),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
